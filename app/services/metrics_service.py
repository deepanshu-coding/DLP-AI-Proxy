from __future__ import annotations

from app.models.schemas import ContentType, Decision, MetricsResponse


class MetricsService:
    """Thread-safe (asyncio single-loop) in-memory metrics counters."""

    def __init__(self) -> None:
        self._total_requests: int = 0
        self._allowed: int = 0
        self._blocked: int = 0
        self._redacted: int = 0
        self._files_scanned: int = 0
        self._images_scanned: int = 0
        self._documents_scanned: int = 0

    def record(self, decision: Decision, content_type: ContentType) -> None:
        self._total_requests += 1
        if decision == Decision.ALLOW:
            self._allowed += 1
        elif decision == Decision.BLOCK:
            self._blocked += 1
        elif decision == Decision.REDACT:
            self._redacted += 1

        if content_type == ContentType.IMAGE:
            self._images_scanned += 1
        elif content_type == ContentType.DOCUMENT:
            self._documents_scanned += 1
        elif content_type in (ContentType.CODE, ContentType.TEXT):
            self._files_scanned += 1

    def snapshot(self) -> MetricsResponse:
        return MetricsResponse(
            total_requests=self._total_requests,
            allowed_requests=self._allowed,
            blocked_requests=self._blocked,
            redacted_requests=self._redacted,
            files_scanned=self._files_scanned,
            images_scanned=self._images_scanned,
            documents_scanned=self._documents_scanned,
        )

    def reset(self) -> None:
        """Utility for tests."""
        self.__init__()  # type: ignore[misc]


# Singleton instance shared across the application lifecycle
metrics = MetricsService()
