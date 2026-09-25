from __future__ import annotations

import re

from .exceptions import SecretDetectedError


PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "private key",
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    ),
    ("bearer token", re.compile(r"\bbearer\s+[A-Za-z0-9._~+/=-]{16,}", re.I)),
    ("OpenAI-style API key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("GitHub token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    (
        "API key",
        re.compile(
            r"\b(?:api[_ -]?key|secret[_ -]?key|access[_ -]?token)\s*[:=]\s*"
            r"['\"]?[A-Za-z0-9_./+=:-]{16,}['\"]?",
            re.I,
        ),
    ),
    (
        "password",
        re.compile(r"\bpassword\s*[:=]\s*['\"]?\S{8,}['\"]?", re.I),
    ),
    (
        "cloud credential",
        re.compile(
            r"\b(?:aws_secret_access_key|google_application_credentials|"
            r"azure_client_secret)\s*[:=]",
            re.I,
        ),
    ),
)


def assert_safe(text: str) -> None:
    """Reject likely secrets in explicitly submitted memory content."""
    for label, pattern in PATTERNS:
        if pattern.search(text):
            raise SecretDetectedError(
                f"Refusing to store content that appears to contain a {label}. "
                "Remove the secret and try again."
            )
