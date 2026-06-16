from __future__ import annotations

from app.detectors.keyword_detector import KeywordDetector
from app.detectors.regex_detector import RegexDetector
from app.detectors.slm_detector import SLMDetector
from app.models.schemas import Finding


class Scanner:
    """
    Run all detectors against extracted text and return aggregated findings.

    Detectors are injected to enable easy unit testing and future replacement
    (e.g. swapping DummySLMDetector for a real local inference engine).
    """

    def __init__(
        self,
        regex_detector: RegexDetector | None = None,
        keyword_detector: KeywordDetector | None = None,
        slm_detector: SLMDetector | None = None,
    ) -> None:
        self._regex = regex_detector or RegexDetector()
        self._keyword = keyword_detector or KeywordDetector()
        self._slm = slm_detector or SLMDetector()

    async def scan(self, text: str) -> list[Finding]:
        findings: list[Finding] = []

        # Synchronous detectors
        findings.extend(self._regex.detect(text))
        findings.extend(self._keyword.detect(text))

        # Async SLM detector (stub / future)
        slm_result = await self._slm.analyze(text)
        findings.extend(slm_result.get("findings", []))

        return findings

    def detectors_triggered(self, findings: list[Finding]) -> list[str]:
        return list({f.detector for f in findings})
