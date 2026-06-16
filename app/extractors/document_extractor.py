from __future__ import annotations

import io

import docx
import pdfplumber


class DocumentExtractor:
    """Extract plain text from PDF and DOCX files."""

    def extract_pdf(self, data: bytes) -> str:
        text_parts: list[str] = []
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n".join(text_parts)

    def extract_docx(self, data: bytes) -> str:
        doc = docx.Document(io.BytesIO(data))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)

    def extract(self, data: bytes, mime_type: str) -> str:
        """Dispatch to the correct extractor based on MIME type."""
        if "pdf" in mime_type:
            return self.extract_pdf(data)
        if "wordprocessingml" in mime_type or "docx" in mime_type or "msword" in mime_type:
            return self.extract_docx(data)
        # Fallback: treat as utf-8 text
        return data.decode("utf-8", errors="replace")
