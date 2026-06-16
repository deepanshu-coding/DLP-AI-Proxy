from __future__ import annotations

import io

try:
    import pytesseract
    from PIL import Image
    _OCR_AVAILABLE = True
except ImportError:
    _OCR_AVAILABLE = False


class ImageOCRExtractor:
    """Extract text from images using pytesseract."""

    def extract(self, data: bytes) -> str:
        if not _OCR_AVAILABLE:
            raise RuntimeError(
                "pytesseract / Pillow not installed. "
                "Install them to enable image OCR."
            )
        try:
            image = Image.open(io.BytesIO(data))
            text: str = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as exc:
            raise RuntimeError(f"OCR extraction failed: {exc}") from exc
