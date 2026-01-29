"""Unit tests for the API client."""

import json
from unittest.mock import MagicMock, patch

import httpx
import pytest

from alibaba_api.client import AlibabaClient
from alibaba_api.config import Config
from alibaba_api.exceptions import (
    AlibabaAPIError,
    AlibabaNetworkError,
    AlibabaValidationError,
)


@pytest.fixture
def config() -> Config:
    """Create test configuration."""
    return Config(
        app_key="test_app_key",
        app_secret="test_app_secret",
        access_token="test_access_token",
        use_sandbox=False,
    )


@pytest.fixture
def client(config: Config) -> AlibabaClient:
    """Create test client."""
    return AlibabaClient(config)


class TestAlibabaClient:
    """Tests for AlibabaClient class."""

    def test_init(self, config: Config) -> None:
        """Client should initialize with config."""
        client = AlibabaClient(config)
        assert client.config == config
        assert client._client.timeout == httpx.Timeout(config.timeout)
        client.close()

    def test_base_url_production(self, config: Config) -> None:
        """Production base URL should be correct."""
        assert not config.use_sandbox
        assert config.base_url == "https://openapi-api.alibaba.com/rest"

    def test_base_url_sandbox(self) -> None:
        """Sandbox base URL should be correct."""
        config = Config(
            app_key="test",
            app_secret="secret",
            use_sandbox=True,
        )
        assert config.use_sandbox
        assert config.base_url == "https://openapi-api-sandbox.alibaba.com/rest"

    def test_build_url(self, client: AlibabaClient) -> None:
        """Should build full URL correctly."""
        url = client._build_url("/test/path")
        assert url == "https://openapi-api.alibaba.com/rest/test/path"

    @patch("httpx.Client.get")
    def test_get_request_signature(self, mock_get: MagicMock, client: AlibabaClient) -> None:
        """GET request should include signature."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"code": "0", "result": "success"}
        mock_get.return_value = mock_response

        client.get("/test", {"param1": "value1"})

        # Verify GET was called
        assert mock_get.called
        call_args = mock_get.call_args
        assert "params" in call_args.kwargs

        # Verify signature params are present
        params = call_args.kwargs["params"]
        assert "app_key" in params
        assert "sign_method" in params
        assert "timestamp" in params
        assert "sign" in params
        assert params["param1"] == "value1"

    @patch("httpx.Client.post")
    def test_post_request(self, mock_post: MagicMock, client: AlibabaClient) -> None:
        """POST request should work correctly."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"code": "0", "result": "success"}
        mock_post.return_value = mock_response

        client.post("/test", {"param1": "value1"})

        # Verify POST was called with data
        assert mock_post.called
        call_args = mock_post.call_args
        assert "data" in call_args.kwargs

    def test_parse_response_success(self, client: AlibabaClient) -> None:
        """Should parse successful response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"code": "0", "result": "success"}

        result = client._parse_response(mock_response)
        assert result == {"code": "0", "result": "success"}

    def test_parse_response_api_error(self, client: AlibabaClient) -> None:
        """Should raise AlibabaAPIError for API errors."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": "130106",
            "message": "Product invalid",
            "request_id": "test123",
        }

        with pytest.raises(AlibabaAPIError) as exc_info:
            client._parse_response(mock_response)

        assert exc_info.value.code == "130106"
        assert "invalid" in exc_info.value.message.lower()
        assert exc_info.value.request_id == "test123"

    def test_parse_response_http_error(self, client: AlibabaClient) -> None:
        """Should raise AlibabaNetworkError for HTTP errors."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"error": "Not found"}
        mock_response.headers = {}

        with pytest.raises(AlibabaNetworkError) as exc_info:
            client._parse_response(mock_response)

        assert exc_info.value.status_code == 404

    def test_parse_response_non_json(self, client: AlibabaClient) -> None:
        """Should handle non-JSON responses."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Not JSON")
        mock_response.text = "plain text"

        result = client._parse_response(mock_response)
        assert result == {"data": "plain text"}

    def test_invalid_api_path(self, client: AlibabaClient) -> None:
        """Should raise error for invalid API path."""
        with pytest.raises(AlibabaValidationError):
            client.request("invalid-path", {})

    def test_context_manager(self, config: Config) -> None:
        """Should work as context manager."""
        with AlibabaClient(config) as client:
            assert client is not None
        # Client should be closed after exiting context

    @patch("httpx.Client.get")
    def test_access_token_included(self, mock_get: MagicMock, client: AlibabaClient) -> None:
        """Access token should be included in signed params."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"code": "0"}
        mock_get.return_value = mock_response

        client.get("/test")

        params = mock_get.call_args.kwargs["params"]
        assert "access_token" in params
        assert params["access_token"] == "test_access_token"

    @patch("httpx.Client.get")
    def test_access_token_override(self, mock_get: MagicMock, client: AlibabaClient) -> None:
        """Access token should be overridable."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"code": "0"}
        mock_get.return_value = mock_response

        client.get("/test", access_token="override_token")

        params = mock_get.call_args.kwargs["params"]
        assert params["access_token"] == "override_token"
