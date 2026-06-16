from __future__ import annotations

from app.models.schemas import ContentType

# File extensions that map to code/text
_CODE_EXTENSIONS: set[str] = {".py", ".js", ".ts", ".java", ".go", ".env"}
_TEXT_EXTENSIONS: set[str] = {".txt", ".json", ".yaml", ".yml", ".md"}
_DOCUMENT_EXTENSIONS: set[str] = {".pdf", ".docx"}
_IMAGE_EXTENSIONS: set[str] = {".png", ".jpg", ".jpeg", ".webp"}

# MIME type fragments
_IMAGE_MIME_FRAGMENTS: set[str] = {"image/png", "image/jpeg", "image/webp", "image/jpg"}
_DOCUMENT_MIME_FRAGMENTS: set[str] = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml",
    "application/msword",
}


def content_type_from_filename(filename: str) -> ContentType:
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext in _IMAGE_EXTENSIONS:
        return ContentType.IMAGE
    if ext in _DOCUMENT_EXTENSIONS:
        return ContentType.DOCUMENT
    if ext in _CODE_EXTENSIONS:
        return ContentType.CODE
    if ext in _TEXT_EXTENSIONS:
        return ContentType.TEXT
    return ContentType.TEXT


def content_type_from_mime(mime: str) -> ContentType:
    mime_lower = mime.lower()
    if any(m in mime_lower for m in _IMAGE_MIME_FRAGMENTS):
        return ContentType.IMAGE
    if any(m in mime_lower for m in _DOCUMENT_MIME_FRAGMENTS):
        return ContentType.DOCUMENT
    return ContentType.TEXT
