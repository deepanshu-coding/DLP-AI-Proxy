from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Decision(str, Enum):
    ALLOW = "ALLOW"
    REDACT = "REDACT"
    BLOCK = "BLOCK"


class ContentType(str, Enum):
    TEXT = "text"
    CODE = "code"
    DOCUMENT = "document"
    IMAGE = "image"


class Finding(BaseModel):
    detector: str
    type: str
    risk: int
    match: str  # partial / masked value shown in logs


class ScanRequest(BaseModel):
    content: str | None = None


class ScanResponse(BaseModel):
    request_id: str
    decision: Decision
    risk_score: int
    findings: list[Finding]
    processed_content: str


class MetricsResponse(BaseModel):
    total_requests: int = 0
    allowed_requests: int = 0
    blocked_requests: int = 0
    redacted_requests: int = 0
    files_scanned: int = 0
    images_scanned: int = 0
    documents_scanned: int = 0


class AuditEvent(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    content_type: ContentType
    decision: Decision
    risk_score: int
    detectors_triggered: list[str]
    metadata: dict[str, Any] = Field(default_factory=dict)


class ForwardResult(BaseModel):
    status: str = "forwarded"
