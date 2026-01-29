"""Integration tests for shipping endpoints."""

import pytest

from alibaba_cli.client import AlibabaClient
from alibaba_cli.config import Config


def _parse_use_sandbox(use_sandbox_raw: str) -> bool:
    """Parse use_sandbox string to boolean."""
    return isinstance(use_sandbox_raw, str) and use_sandbox_raw.lower() in ("1", "true", "yes")


@pytest.mark.integration
class TestShippingEndpoints:
    """Integration tests for freight calculation endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self, test_credentials: dict[str, str]) -> None:
        """Skip all tests if credentials not available."""
        if not test_credentials.get("access_token"):
            pytest.skip("ALIBABA_ACCESS_TOKEN required for shipping endpoint tests")

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

    @pytest.fixture
    def sample_product_id(self) -> str:
        """Sample product ID for testing."""
        return "1601206892606"

    def test_basic_freight_calculation(
        self, client: AlibabaClient, sample_product_id: str
    ) -> None:
        """Test basic freight cost calculation."""
        response = client.get(
            "/shipping/freight/calculate",
            {
                "product_id": sample_product_id,
                "quantity": "10",
                "destination_country": "US",
                "zip_code": "90001",
                "dispatch_location": "CN",
            },
        )

        # Validate response structure
        assert response.get("code") == "0"
        assert "value" in response

        # Validate shipping options structure
        options = response.get("value", [])
        if options:
            option = options[0]
            # Expected fields from documentation
            expected_fields = ["shipping_type", "vendor_name", "delivery_time", "fee"]
            for field in expected_fields:
                assert field in option, f"Missing expected field: {field}"

            # Validate fee structure
            if "fee" in option:
                fee = option["fee"]
                assert "amount" in fee
                assert "currency" in fee

    def test_advanced_freight_calculation(
        self, client: AlibabaClient, sample_product_id: str
    ) -> None:
        """Test advanced freight calculation with multiple products."""
        import json

        from alibaba_cli.exceptions import AlibabaAPIError

        address = {
            "zip": "10012",
            "country": {"code": "US", "name": "United States"},
            "province": {"code": "NY", "name": "New York"},
            "city": {"code": "", "name": "New York"},
            "address": "123 Main Street",
        }

        products = [{"product_id": sample_product_id, "sku_id": "105613018158", "quantity": "1"}]

        # Note: This may fail with invalid e_company_id or sku_id
        # The test validates the API accepts the request format and returns proper error
        try:
            response = client.get(
                "/order/freight/calculate",
                {
                    "e_company_id": "test_company_id",
                    "destination_country": "US",
                    "dispatch_location": "CN",
                    "address": json.dumps(address),
                    "logistics_product_list": json.dumps(products),
                },
            )
            # If we get a successful response, validate structure
            assert response is not None
        except AlibabaAPIError as e:
            # Expected: API may return error for invalid test data
            # Common errors: 4015 (seller cannot ship to country), 4016 (freight template error)
            assert e.code in ["4015", "4016"], f"Unexpected error code: {e.code}"

    def test_empty_response_handling(self, client: AlibabaClient) -> None:
        """Test handling of empty shipping responses (no available routes)."""
        from alibaba_cli.exceptions import AlibabaAPIError

        # Use an unlikely combination to potentially get no routes
        try:
            response = client.get(
                "/shipping/freight/calculate",
                {
                    "product_id": "1",  # Invalid product
                    "quantity": "1",
                    "destination_country": "US",
                    "dispatch_location": "CN",
                },
            )
            # If successful, validate structure
            options = response.get("value", [])
            assert isinstance(options, list)
        except AlibabaAPIError as e:
            # Expected: Invalid product may return freight template error
            assert e.code == "4016", f"Unexpected error code: {e.code}"
