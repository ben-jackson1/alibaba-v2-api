"""Integration tests for authentication endpoints."""

import os

import pytest

from alibaba_cli.client import AlibabaClient
from alibaba_cli.config import Config


def _parse_use_sandbox(use_sandbox_raw: str) -> bool:
    """Parse use_sandbox string to boolean."""
    return isinstance(use_sandbox_raw, str) and use_sandbox_raw.lower() in ("1", "true", "yes")


@pytest.mark.integration
class TestAuthEndpoints:
    """Integration tests for authentication endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self, test_credentials: dict[str, str]) -> None:
        """Skip all tests if credentials not available."""
        if not test_credentials.get("app_key") or not test_credentials.get("app_secret"):
            pytest.skip("ALIBABA_APP_KEY and ALIBABA_APP_SECRET required for integration tests")

    def test_token_create_with_code(self, test_credentials: dict[str, str]) -> None:
        """Test token creation with authorization code."""
        code = test_credentials.get("auth_code")
        if not code:
            pytest.skip("ALIBABA_TEST_AUTH_CODE required for token creation test")

        use_sandbox = _parse_use_sandbox(test_credentials.get("use_sandbox", ""))
        config = Config(
            app_key=test_credentials["app_key"],
            app_secret=test_credentials["app_secret"],
            use_sandbox=use_sandbox,
        )

        with AlibabaClient(config) as client:
            response = client.get("/auth/token/create", {"code": code})

        # Validate response structure
        assert "access_token" in response
        assert "refresh_token" in response
        assert "expires_in" in response
        assert response.get("code") == "0"

        # Validate user_info if present
        if "user_info" in response:
            user_info = response["user_info"]
            assert "user_id" in user_info or "loginId" in user_info

    def test_token_refresh(self, test_credentials: dict[str, str]) -> None:
        """Test token refresh with refresh_token."""
        refresh_token = test_credentials.get("refresh_token")
        if not refresh_token:
            pytest.skip("ALIBABA_REFRESH_TOKEN required for token refresh test")

        use_sandbox = _parse_use_sandbox(test_credentials.get("use_sandbox", ""))
        config = Config(
            app_key=test_credentials["app_key"],
            app_secret=test_credentials["app_secret"],
            use_sandbox=use_sandbox,
        )

        with AlibabaClient(config) as client:
            response = client.get("/auth/token/refresh", {"refresh_token": refresh_token})

        # Validate response structure
        assert "access_token" in response
        assert "refresh_token" in response
        assert response.get("code") == "0"

    def test_invalid_code_error(self, test_credentials: dict[str, str]) -> None:
        """Test error handling for invalid authorization code."""
        use_sandbox = _parse_use_sandbox(test_credentials.get("use_sandbox", ""))
        config = Config(
            app_key=test_credentials["app_key"],
            app_secret=test_credentials["app_secret"],
            use_sandbox=use_sandbox,
        )

        with AlibabaClient(config) as client:
            with pytest.raises(Exception) as exc_info:
                client.get("/auth/token/create", {"code": "invalid_code_123"})

            # Should get an error response
            assert exc_info.value is not None
