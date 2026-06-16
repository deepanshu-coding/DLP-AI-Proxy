from __future__ import annotations

from app.models.schemas import Finding


class SLMDetector:
    """
    Future integration point for a local Small Language Model (SLM) detector.

    Current implementation is a no-op stub that always returns clean results.
    Replace the body of `analyze` with real local model inference without
    changing the method signature or return shape — the pipeline will pick it
    up automatically via dependency injection.
    """

    async def analyze(self, text: str) -> dict: 
        """
        Analyse *text* for confidential information.

        Returns
        -------
        dict with keys:
            contains_confidential (bool)
            score (int)   — risk contribution (0–100)
            findings (list[Finding])
        """
        return {
            "contains_confidential": False,
            "score": 0,
            "findings": [],
        }
