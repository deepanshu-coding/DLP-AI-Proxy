from __future__ import annotations

import uuid

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.api.content_type_helper import (
    content_type_from_filename,
    content_type_from_mime,
)
from app.engine.policy_engine import PolicyEngine
from app.engine.risk_engine import RiskEngine
from app.engine.scanner import Scanner
from app.extractors.document_extractor import DocumentExtractor
from app.extractors.image_ocr import ImageOCRExtractor
from app.extractors.text_extractor import TextExtractor
from app.models.schemas import AuditEvent, ContentType, Decision, ScanResponse
from app.services.audit_logger import AuditLogger
from app.services.forwarder import Forwarder
from app.services.metrics_service import metrics
from app.services.redactor import Redactor

router = APIRouter()

# Shared service instances
_scanner = Scanner()
_risk_engine = RiskEngine()
_policy_engine = PolicyEngine()
_redactor = Redactor()
_forwarder = Forwarder()
_audit_logger = AuditLogger()
_text_extractor = TextExtractor()
_doc_extractor = DocumentExtractor()
_image_extractor = ImageOCRExtractor()


async def _process(
    text: str,
    content_type: ContentType,
    request_id: str,
) -> ScanResponse:
    """Run the full detection → policy → redaction pipeline."""
    findings = await _scanner.scan(text)
    risk_score = _risk_engine.calculate(findings)
    decision = _policy_engine.decide(risk_score)

    if decision == Decision.REDACT:
        processed_content = _redactor.redact(text)
    elif decision == Decision.BLOCK:
        processed_content = "[CONTENT BLOCKED]"
    else:
        processed_content = text
        await _forwarder.forward(text)

    # Audit
    event = AuditEvent(
        request_id=request_id,
        content_type=content_type,
        decision=decision,
        risk_score=risk_score,
        detectors_triggered=_scanner.detectors_triggered(findings),
    )
    _audit_logger.log(event)

    # Metrics
    metrics.record(decision, content_type)

    return ScanResponse(
        request_id=request_id,
        decision=decision,
        risk_score=risk_score,
        findings=findings,
        processed_content=processed_content,
    )


@router.post("/scan", response_model=ScanResponse)
async def scan(
    content: str | None = Form(default=None),
    file: UploadFile | None = File(default=None),
) -> ScanResponse:
    """
    Scan content for confidential information.

    Accepts either:
    - A JSON body with `content` (plain text / code)
    - A multipart form upload with `file` (text, code, document, or image)
    """
    request_id = str(uuid.uuid4())

    if file is not None:
        raw_bytes = await file.read()
        filename = file.filename or ""
        mime = file.content_type or ""

        # Determine type: prefer filename extension, fall back to MIME
        ct = (
            content_type_from_filename(filename)
            if filename
            else content_type_from_mime(mime)
        )

        if ct == ContentType.IMAGE:
            try:
                text = _image_extractor.extract(raw_bytes)
            except RuntimeError as exc:
                raise HTTPException(status_code=422, detail=str(exc)) from exc
        elif ct == ContentType.DOCUMENT:
            try:
                text = _doc_extractor.extract(raw_bytes, mime)
            except Exception as exc:
                raise HTTPException(
                    status_code=422, detail=f"Document extraction failed: {exc}"
                ) from exc
        else:
            text = _text_extractor.extract(
                raw_bytes.decode("utf-8", errors="replace")
            )

        return await _process(text, ct, request_id)

    if content is not None:
        text = _text_extractor.extract(content)
        return await _process(text, ContentType.TEXT, request_id)

    raise HTTPException(
        status_code=400,
        detail="Provide either a 'content' field or a 'file' upload.",
    )


@router.post("/scan/json", response_model=ScanResponse)
async def scan_json(body: dict) -> ScanResponse:
    """
    Convenience endpoint that accepts a JSON body: {"content": "..."}
    """
    request_id = str(uuid.uuid4())
    content = body.get("content")
    if not isinstance(content, str):
        raise HTTPException(
            status_code=400, detail="'content' must be a non-empty string."
        )
    text = _text_extractor.extract(content)
    return await _process(text, ContentType.TEXT, request_id)
