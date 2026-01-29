"""Integration tests for shipping API using high-level methods."""

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
class TestShippingAPI:
    """Integration tests for freight calculation using high-level API methods."""

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

    def test_calculate_freight_basic(
        self, client: AlibabaClient, sample_product_id: str
    ) -> None:
        """Test basic freight cost calculation."""
        result = client.calculate_freight(
            product_id=sample_product_id,
            quantity=10,
            destination_country="US",
            zip_code="90001",
            dispatch_location="CN",
        )

        # Validate response structure
        assert "product_id" in result
        assert "quantity" in result
        assert "destination" in result
        assert "dispatch_location" in result
        assert "options" in result
        assert result["product_id"] == sample_product_id
        assert result["quantity"] == 10

        # Validate shipping options structure
        options = result.get("options", [])
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

    def test_calculate_freight_with_fallback(self, client: AlibabaClient) -> None:
        """Test freight calculation with automatic fallback."""
        # Test fallback from CN to US to MX
        result = client.calculate_freight(
            product_id="1601206892606",
            quantity=1,
            destination_country="US",
            dispatch_location="CN",
            fallback=True,
        )

        # Validate response structure
        assert "options" in result
        assert "fallback_used" in result
        assert isinstance(result["fallback_used"], bool)

    def test_calculate_freight_no_fallback(self, client: AlibabaClient) -> None:
        """Test freight calculation with fallback disabled."""
        result = client.calculate_freight(
            product_id="1601206892606",
            quantity=1,
            destination_country="US",
            dispatch_location="CN",
            fallback=False,
        )

        # With fallback disabled, should only try CN
        assert result["fallback_used"] is False

    def test_calculate_freight_advanced(
        self, client: AlibabaClient, sample_product_id: str
    ) -> None:
        """Test advanced freight calculation with multiple products."""
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
            result = client.calculate_freight_advanced(
                e_company_id="test_company_id",
                destination_country="US",
                dispatch_location="CN",
                address=address,
                logistics_product_list=products,
            )
            # If we get a successful response, validate structure
            assert "options" in result

        except AlibabaAPIError as e:
            # Expected: API may return error for invalid test data
            # Common errors: 4015 (seller cannot ship to country), 4016 (freight template error)
            assert e.code in ["4015", "4016"], f"Unexpected error code: {e.code}"

    def test_empty_response_handling(self, client: AlibabaClient) -> None:
        """Test handling of invalid product ID."""
        # Use an invalid product ID - should get parameter error
        with pytest.raises(AlibabaAPIError) as exc_info:
            client.calculate_freight(
                product_id="invalid_product_id",
                quantity=1,
                destination_country="US",
                dispatch_location="CN",
                fallback=False,
            )

        # Should get a parameter error
        assert exc_info.value.code == "MissingParameter" or "product_id" in exc_info.value.message.lower()
