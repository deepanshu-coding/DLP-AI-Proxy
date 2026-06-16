from __future__ import annotations

import json
import logging
import sys

from app.models.schemas import AuditEvent

_handler = logging.StreamHandler(sys.stdout)
_handler.setFormatter(logging.Formatter("%(message)s"))

_audit_logger = logging.getLogger("cdp_proxy.audit")
_audit_logger.addHandler(_handler)
_audit_logger.setLevel(logging.INFO)
_audit_logger.propagate = False


class AuditLogger:
    """Emit structured JSON audit events."""

    def log(self, event: AuditEvent) -> None:
        _audit_logger.info(event.model_dump_json())

    def log_dict(self, data: dict) -> None:
        _audit_logger.info(json.dumps(data))
