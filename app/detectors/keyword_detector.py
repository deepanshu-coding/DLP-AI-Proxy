from __future__ import annotations

import re

from app.models.schemas import Finding

# Keywords that signal credential-related fields
_CREDENTIAL_KEYWORDS: list[str] = [
    "password",
    "passwd",
    "secret",
    "token",
    "api_key",
    "apikey",
    "access_key",
    "private_key",
    "client_secret",
]

# Regex to match key=value, key: value, JSON "key": "value", YAML key: value, ENV KEY=VALUE
# Groups: (1) keyword, (2) value (may be empty)
_KV_PATTERN = re.compile(
    r'(?i)(?:^|["\s{,\n])('
    + "|".join(re.escape(k) for k in _CREDENTIAL_KEYWORDS)
    + r')\s*[=:]\s*["\']?([^\s"\'}\n,;]{3,})["\']?',
    re.MULTILINE,
)

# Standalone keyword occurrences (not necessarily in k=v form)
_STANDALONE_PATTERN = re.compile(
    r"(?i)\b(" + "|".join(re.escape(k) for k in _CREDENTIAL_KEYWORDS) + r")\b",
    re.MULTILINE,
)

_KV_RISK = 50
_STANDALONE_RISK = 50


class KeywordDetector:
    """Detect credential-related keywords in plain text / structured formats."""

    def detect(self, text: str) -> list[Finding]:
        findings: list[Finding] = []
        seen_matches: set[str] = set()

        # First pass: key=value / key: value patterns (higher confidence)
        for match in _KV_PATTERN.finditer(text):
            keyword = match.group(1).lower()
            value = match.group(2)
            key = f"kv:{keyword}"
            if key not in seen_matches:
                seen_matches.add(key)
                masked_value = value[:4] + "..." if len(value) > 4 else value
                findings.append(
                    Finding(
                        detector="keyword",
                        type=f"credential_keyword:{keyword}",
                        risk=_KV_RISK,
                        match=f"{keyword}='{masked_value}'",
                    )
                )

        # Second pass: standalone keywords not already caught
        for match in _STANDALONE_PATTERN.finditer(text):
            keyword = match.group(1).lower()
            key = f"kv:{keyword}"
            if key not in seen_matches:
                seen_matches.add(f"standalone:{keyword}")
                findings.append(
                    Finding(
                        detector="keyword",
                        type=f"credential_keyword:{keyword}",
                        risk=_STANDALONE_RISK,
                        match=keyword,
                    )
                )

        return findings

    def redact(self, text: str) -> str:
        """Redact values associated with credential keywords."""

        def _replace(m: re.Match[str]) -> str:
            keyword = m.group(1)
            full = m.group(0)
            # Replace just the value portion
            return full.replace(m.group(2), "[SECRET_REDACTED]")

        return _KV_PATTERN.sub(_replace, text)
