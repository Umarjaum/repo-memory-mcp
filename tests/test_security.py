import pytest

from repo_memory_mcp.exceptions import SecretDetectedError
from repo_memory_mcp.security import assert_safe


@pytest.mark.parametrize(
    "content",
    [
        "api_key = abcdefghijklmnop",
        "Authorization: Bearer abcdefghijklmnop",
        "token=sk-abcdefghijklmnopqrstuvwx",
        "token=ghp_abcdefghijklmnopqrstuvwx",
        "AWS_ACCESS_KEY_ID=AKIA1234567890ABCDEF",
        "-----BEGIN OPENSSH PRIVATE KEY-----",
    ],
)
def test_likely_secrets_are_rejected(content):
    with pytest.raises(SecretDetectedError):
        assert_safe(content)


def test_safe_text():
    assert_safe("Use typed models and local SQLite storage")
