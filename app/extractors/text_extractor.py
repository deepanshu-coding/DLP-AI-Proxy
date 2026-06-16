from __future__ import annotations


class TextExtractor:
    """Pass through plain text and source code unchanged."""

    def extract(self, raw: str) -> str:
        return raw
