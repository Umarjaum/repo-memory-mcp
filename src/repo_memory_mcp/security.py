import re
from .exceptions import SecretDetectedError

PATTERNS = [
    ("private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("bearer token", re.compile(r"\bbearer\s+[A-Za-z0-9._~+/=-]{16,}", re.I)),
    ("api key", re.compile(r"\b(?:api[_ -]?key|secret[_ -]?key)\s*[:=]\s*[A-Za-z0-9_./+=-]{16,}", re.I)),
    ("password", re.compile(r"\bpassword\s*[:=]\s*\S{8,}", re.I)),
    ("cloud credential", re.compile(r"\b(?:aws_access_key_id|aws_secret_access_key|google_application_credentials)\s*[:=]", re.I)),
]

def assert_safe(text: str) -> None:
    for label, pattern in PATTERNS:
        if pattern.search(text):
            raise SecretDetectedError(f"Refusing to store content that appears to contain a {label}. Remove the secret and try again.")
