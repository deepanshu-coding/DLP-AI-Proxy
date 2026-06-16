from __future__ import annotations

from app.models.schemas import Decision

_BLOCK_THRESHOLD = 100
_REDACT_THRESHOLD = 50


class PolicyEngine:
    """Translate a risk score into an enforcement decision."""

    def decide(self, risk_score: int) -> Decision:
        if risk_score >= _BLOCK_THRESHOLD:
            return Decision.BLOCK
        if risk_score >= _REDACT_THRESHOLD:
            return Decision.REDACT
        return Decision.ALLOW
