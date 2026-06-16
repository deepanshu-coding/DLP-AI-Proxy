from __future__ import annotations

from app.models.schemas import Finding


class RiskEngine:
    """Aggregate risk scores from all findings."""

    def calculate(self, findings: list[Finding]) -> int:
        return sum(f.risk for f in findings)
