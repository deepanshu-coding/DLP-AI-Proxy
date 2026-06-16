from __future__ import annotations

from app.detectors.keyword_detector import KeywordDetector
from app.detectors.regex_detector import RegexDetector


class Redactor:
    """Apply redaction to text using all detectors' redact methods."""

    def __init__(
        self,
        regex_detector: RegexDetector | None = None,
        keyword_detector: KeywordDetector | None = None,
    ) -> None:
        self._regex = regex_detector or RegexDetector()
        self._keyword = keyword_detector or KeywordDetector()

    def redact(self, text: str) -> str:
        # Order matters: regex first (more specific), then keyword
        text = self._regex.redact(text)
        text = self._keyword.redact(text)
        return text
