"""Unit tests for request signing."""

from alibaba_cli.signing import build_signed_params, calculate_signature


class TestCalculateSignature:
    """Tests for calculate_signature function."""

    def test_signature_format(self) -> None:
        """Signature should be uppercase hex string."""
        result = calculate_signature("/test/path", {"key": "value"}, "secret")
        assert result.isupper()
        assert all(c in "0123456789ABCDEF" for c in result)
        assert len(result) == 64  # SHA256 = 64 hex chars

    def test_parameter_ordering(self) -> None:
        """Parameters should be sorted alphabetically."""
        sig1 = calculate_signature("/test", {"b": "2", "a": "1"}, "secret")
        sig2 = calculate_signature("/test", {"a": "1", "b": "2"}, "secret")
        assert sig1 == sig2

    def test_different_api_paths(self) -> None:
        """Different API paths should produce different signatures."""
        sig1 = calculate_signature("/api/one", {"key": "value"}, "secret")
        sig2 = calculate_signature("/api/two", {"key": "value"}, "secret")
        assert sig1 != sig2

    def test_different_params(self) -> None:
        """Different parameters should produce different signatures."""
        sig1 = calculate_signature("/test", {"key": "value1"}, "secret")
        sig2 = calculate_signature("/test", {"key": "value2"}, "secret")
        assert sig1 != sig2

    def test_empty_params(self) -> None:
        """Empty params dict should still produce valid signature."""
        result = calculate_signature("/test", {}, "secret")
        assert len(result) == 64
        assert result.isupper()

    def test_special_characters_in_params(self) -> None:
        """Special characters in values should be handled correctly."""
        result = calculate_signature(
            "/test", {"key": "value with spaces & symbols!@#"}, "secret"
        )
        assert len(result) == 64

    def test_unicode_in_params(self) -> None:
        """Unicode characters in values should be handled correctly."""
        result = calculate_signature("/test", {"key": "值"}, "secret")
        assert len(result) == 64

    def test_same_input_same_output(self) -> None:
        """Same inputs should always produce same signature."""
        params = {"app_key": "12345", "code": "test_code", "timestamp": "1234567890"}
        sig1 = calculate_signature("/auth/token/create", params, "my_secret")
        sig2 = calculate_signature("/auth/token/create", params, "my_secret")
        assert sig1 == sig2


class TestBuildSignedParams:
    """Tests for build_signed_params function."""

    def test_includes_system_params(self) -> None:
        """Should include all system parameters."""
        result = build_signed_params("/test", {}, "app_key", "app_secret")
        assert "app_key" in result
        assert result["app_key"] == "app_key"
        assert "sign_method" in result
        assert result["sign_method"] == "sha256"
        assert "timestamp" in result
        assert "sign" in result

    def test_timestamp_format(self) -> None:
        """Timestamp should be milliseconds."""
        import time

        before = int(time.time() * 1000)
        result = build_signed_params("/test", {}, "app_key", "app_secret")
        after = int(time.time() * 1000)

        timestamp = int(result["timestamp"])
        assert before <= timestamp <= after

    def test_includes_access_token_when_provided(self) -> None:
        """Should include access_token when provided."""
        result = build_signed_params(
            "/test", {}, "app_key", "app_secret", access_token="token123"
        )
        assert "access_token" in result
        assert result["access_token"] == "token123"

    def test_omits_access_token_when_not_provided(self) -> None:
        """Should not include access_token when not provided."""
        result = build_signed_params("/test", {}, "app_key", "app_secret")
        assert "access_token" not in result

    def test_merges_business_params(self) -> None:
        """Should merge business parameters with system parameters."""
        result = build_signed_params(
            "/test", {"product_id": "123", "quantity": "5"}, "app_key", "app_secret"
        )
        assert result["product_id"] == "123"
        assert result["quantity"] == "5"
        assert "app_key" in result
        assert "sign" in result

    def test_generates_valid_signature(self) -> None:
        """Generated signature should be valid uppercase hex."""
        result = build_signed_params(
            "/auth/token/create", {"code": "test"}, "app_key", "app_secret"
        )
        assert "sign" in result
        assert result["sign"].isupper()
        assert len(result["sign"]) == 64

    def test_signature_includes_all_params(self) -> None:
        """Signature should include all parameters."""
        result1 = build_signed_params(
            "/test", {"extra": "value"}, "app_key", "app_secret"
        )
        result2 = build_signed_params("/test", {}, "app_key", "app_secret")
        # Different params should produce different signatures
        assert result1["sign"] != result2["sign"]
