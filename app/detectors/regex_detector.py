from __future__ import annotations

import re
from dataclasses import dataclass

from app.models.schemas import Finding


@dataclass(frozen=True)
class _Pattern:
    name: str
    pattern: str
    risk: int
    placeholder: str


_PATTERNS: list[_Pattern] = [
    _Pattern(
        name="aws_access_key",
        pattern=r"(?<![A-Z0-9])(AKIA|ABIA|ACCA|ASIA)[A-Z0-9]{16}(?![A-Z0-9])",
        risk=100,
        placeholder="[AWS_ACCESS_KEY]",
    ),
    _Pattern(
        name="aws_secret_key",
        pattern=r"(?i)aws[_\-\s]?secret[_\-\s]?(?:access[_\-\s]?)?key\s*[=:]\s*[A-Za-z0-9/+=]{40}",
        risk=100,
        placeholder="[AWS_SECRET_KEY]",
    ),
    _Pattern(
        name="openai_api_key",
        pattern=r"sk-[A-Za-z0-9]{32,64}",
        risk=100,
        placeholder="[OPENAI_API_KEY]",
    ),
    _Pattern(
        name="github_token",
        pattern=r"ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{82}|gho_[A-Za-z0-9]{36}|ghs_[A-Za-z0-9]{36}",
        risk=100,
        placeholder="[GITHUB_TOKEN]",
    ),
    _Pattern(
        name="jwt_token",
        pattern=r"eyJ[A-Za-z0-9\-_]+\.eyJ[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+",
        risk=80,
        placeholder="[JWT_TOKEN]",
    ),
    _Pattern(
        name="private_key",
        pattern=r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----",
        risk=100,
        placeholder="[PRIVATE_KEY]",
    ),
    _Pattern(
        name="db_connection_string",
        pattern=(
            r"(?i)(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis|mssql|sqlserver)"
            r"://[A-Za-z0-9\-._~:/?#\[\]@!$&'()*+,;=%]+"
        ),
        risk=100,
        placeholder="[DB_CONNECTION_STRING]",
    ),
    _Pattern(
        name="bearer_token",
        pattern=r"(?i)Bearer\s+[A-Za-z0-9\-._~+/]+=*",
        risk=80,
        placeholder="[BEARER_TOKEN]",
    ),
]

# Pre-compile all patterns
_COMPILED: list[tuple[_Pattern, re.Pattern[str]]] = [
    (p, re.compile(p.pattern)) for p in _PATTERNS
]


class RegexDetector:
    """Scan text for secrets using compiled regex patterns."""

    def detect(self, text: str) -> list[Finding]:
        findings: list[Finding] = []
        for pattern, compiled in _COMPILED:
            for match in compiled.finditer(text):
                raw = match.group()
                # Mask the match: show first 6 chars + ellipsis
                masked = raw[:6] + "..." if len(raw) > 6 else raw[:3] + "..."
                findings.append(
                    Finding(
                        detector="regex",
                        type=pattern.name,
                        risk=pattern.risk,
                        match=masked,
                    )
                )
        return findings

    def redact(self, text: str) -> str:
        """Return text with all detected secrets replaced by placeholders."""
        for pattern, compiled in _COMPILED:
            text = compiled.sub(pattern.placeholder, text)
        return text
