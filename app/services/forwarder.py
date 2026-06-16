from __future__ import annotations

from app.models.schemas import ForwardResult


class Forwarder:
    """
    Mock downstream forwarder.

    In production this would send the (possibly redacted) content to the
    real LLM endpoint.  For the MVP it returns a static acknowledgement.
    """

    async def forward(self, content: str) -> ForwardResult:  # noqa: ARG002
        return ForwardResult(status="forwarded")
