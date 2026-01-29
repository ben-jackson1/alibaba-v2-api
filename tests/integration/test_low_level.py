"""
Low-level smoke tests for core API functionality.

These tests verify the basic API connectivity, signing, and response parsing
work correctly. They serve as a baseline - if these fail, the issue is with
the underlying API, not the high-level wrapper methods.
"""

import pytest

from alibaba_api import AlibabaClient, Config
from alibaba_api.exceptions import AlibabaAPIError


def _parse_use_sandbox(use_sandbox_raw: str) -> bool:
    """Parse use_sandbox string to boolean."""
    return isinstance(use_sandbox_raw, str) and use_sandbox_raw.lower() in (
        "1",
        "true",
        "yes",
    )


@pytest.mark.integration
class TestLowLevelAPI:
    """Low-level smoke tests for core API functionality."""

    @pytest.fixture(autouse=True)
    def setup(self, test_credentials: dict[str, str]) -> None:
        """Skip all tests if credentials not available."""
        if not test_credentials.get("access_token"):
            pytest.skip("ALIBABA_ACCESS_TOKEN required for low-level smoke tests")

    @pytest.fixture
    def client(self, test_credentials: dict[str, str]) -> AlibabaClient:
        """Create authenticated client for testing."""
        use_sandbox = _parse_use_sandbox(test_credentials.get("use_sandbox", ""))
        config = Config(
            app_key=test_credentials["app_key"],
            app_secret=test_credentials["app_secret"],
            access_token=test_credentials["access_token"],
            use_sandbox=use_sandbox,
        )
        return AlibabaClient(config)

    def test_get_endpoint_works(self, client: AlibabaClient) -> None:
        """
        Smoke test: Verify GET requests work end-to-end.

        Tests: request signing, HTTP communication, response parsing
        Uses: A simple, reliable endpoint (product list)
        """
        response = client.get(
            "/eco/buyer/product/check",
            {
                "query_req": '{"scene_id": "906124611", "index": 0, "size": 5, "product_type": "common"}'
            },
        )

        # Verify we got a valid response
        assert response is not None
        assert response.get("code") == "0"
        assert "result" in response

    def test_post_endpoint_works(self, client: AlibabaClient) -> None:
        """
        Smoke test: Verify POST requests work end-to-end.

        Tests: POST requests with JSON body parameters
        Uses: Order list (simple POST endpoint)
        """
        response = client.post(
            "/alibaba/order/list",
            {"role": "buyer", "start_page": "0", "page_size": "5"},
        )

        # Verify we got a valid response
        assert response is not None
        assert response.get("code") == "0"
        assert "value" in response

    def test_error_handling_works(self, client: AlibabaClient) -> None:
        """
        Smoke test: Verify API errors are properly raised.

        Tests: Invalid endpoint returns proper error
        """
        with pytest.raises(AlibabaAPIError) as exc_info:
            # Use an invalid endpoint path
            client.get("/invalid/endpoint/path", {})

        # Verify we got a proper error object
        assert exc_info.value is not None
        assert hasattr(exc_info.value, "code")

    def test_signing_headers_present(self, client: AlibabaClient) -> None:
        """
        Smoke test: Verify request signing is applied.

        Tests: Signed parameters include required fields
        This doesn't validate the signature itself, just that the flow works.
        """
        response = client.get(
            "/eco/buyer/product/check",
            {"query_req": '{"scene_id": "906124611", "index": 0, "size": 5, "product_type": "common"}'},
        )

        # If signing wasn't applied, we'd get an authentication error
        assert response.get("code") == "0"
