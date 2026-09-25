import pytest
from repo_memory_mcp.security import assert_safe
from repo_memory_mcp.exceptions import SecretDetectedError
def test_secret_rejected():
    with pytest.raises(SecretDetectedError): assert_safe('api_key = abcdefghijklmnop')
def test_safe_text(): assert_safe('Use typed models')
