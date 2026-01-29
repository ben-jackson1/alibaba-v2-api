"""Integration tests for authentication API using high-level methods."""


import pytest

from alibaba_api import AlibabaClient, Config


def _parse_use_sandbox(use_sandbox_raw: str) -> bool:
    """Parse use_sandbox string to boolean."""
    return isinstance(use_sandbox_raw, str) and use_sandbox_raw.lower() in (
        "1",
        "true",
        "yes",
    )


@pytest.mark.integration
class TestAuthAPI:
    """Integration tests for authentication using high-level API methods."""

    @pytest.fixture(autouse=True)
    def setup(self, test_credentials: dict[str, str]) -> None:
        """Skip all tests if credentials not available."""
        if not test_credentials.get("app_key") or not test_credentials.get("app_secret"):
            pytest.skip("ALIBABA_APP_KEY and ALIBABA_APP_SECRET required for integration tests")

    def test_create_token_with_code(self, test_credentials: dict[str, str]) -> None:
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
            result = client.create_token(code=code)

        # Validate response structure
        assert "access_token" in result
        assert "refresh_token" in result
        assert "expires_in" in result
        assert "refresh_expires_in" in result
        assert result["access_token"] is not None
        assert result["refresh_token"] is not None

        # Validate user_info if present
        if result.get("user_info"):
            user_info = result["user_info"]
            assert "user_id" in user_info or "loginId" in user_info

    def test_refresh_token(self, test_credentials: dict[str, str]) -> None:
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
            result = client.refresh_token(refresh_token=refresh_token)

        # Validate response structure
        assert "access_token" in result
        assert "refresh_token" in result
        assert "expires_in" in result
        assert "refresh_expires_in" in result

    def test_refresh_token_from_config(self, test_credentials: dict[str, str]) -> None:
        """Test token refresh using refresh_token from config."""
        refresh_token = test_credentials.get("refresh_token")
        if not refresh_token:
            pytest.skip("ALIBABA_REFRESH_TOKEN required for token refresh test")

        use_sandbox = _parse_use_sandbox(test_credentials.get("use_sandbox", ""))
        config = Config(
            app_key=test_credentials["app_key"],
            app_secret=test_credentials["app_secret"],
            refresh_token=refresh_token,
            use_sandbox=use_sandbox,
        )

        with AlibabaClient(config) as client:
            # Call without refresh_token param - should use config value
            result = client.refresh_token()

        # Validate response
        assert "access_token" in result
        assert result["access_token"] is not None

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
                client.create_token(code="invalid_code_123")

            # Should get an error response
            assert exc_info.value is not None

    def test_auth_status_property(self, test_credentials: dict[str, str]) -> None:
        """Test the auth_status property."""
        use_sandbox = _parse_use_sandbox(test_credentials.get("use_sandbox", ""))
        config = Config(
            app_key=test_credentials["app_key"],
            app_secret=test_credentials["app_secret"],
            access_token=test_credentials.get("access_token"),
            refresh_token=test_credentials.get("refresh_token"),
            use_sandbox=use_sandbox,
        )

        with AlibabaClient(config) as client:
            status = client.auth_status

        # Validate status structure
        assert "environment" in status
        assert "app_key" in status
        assert "has_access_token" in status
        assert "has_refresh_token" in status

        # Check environment is correct
        if use_sandbox:
            assert status["environment"] == "sandbox"
        else:
            assert status["environment"] == "production"

        # Check app_key is masked
        assert status["app_key"] is not None
        assert "..." in status["app_key"]

        # Check token flags
        assert status["has_access_token"] == bool(test_credentials.get("access_token"))
        assert status["has_refresh_token"] == bool(test_credentials.get("refresh_token"))
