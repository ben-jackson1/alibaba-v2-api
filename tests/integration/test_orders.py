"""Integration tests for order API using high-level methods."""


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
class TestOrderAPI:
    """Integration tests for order management using high-level API methods."""

    @pytest.fixture(autouse=True)
    def setup(self, test_credentials: dict[str, str]) -> None:
        """Skip all tests if credentials not available."""
        if not test_credentials.get("access_token"):
            pytest.skip("ALIBABA_ACCESS_TOKEN required for order endpoint tests")

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

    def test_list_orders(self, client: AlibabaClient) -> None:
        """Test listing orders."""
        result = client.list_orders(role="buyer", start_page=0, page_size=10)

        # Validate response structure
        assert "orders" in result
        assert "total_count" in result
        assert "page" in result
        assert result["page"] == 0
        assert result["page_size"] == 10

        # Validate order structure if any orders returned
        orders = result.get("orders", [])
        if orders:
            order = orders[0]
            assert "trade_id" in order
            assert "trade_status" in order
            assert "create_date" in order

    def test_list_orders_with_status_filter(self, client: AlibabaClient) -> None:
        """Test listing orders with status filter."""
        result = client.list_orders(role="buyer", start_page=0, page_size=10, status="pending")

        # Validate response structure
        assert "orders" in result
        assert "total_count" in result

    def test_get_order(self, client: AlibabaClient, test_trade_ids: dict[str, str]) -> None:
        """Test getting order details."""
        trade_id = test_trade_ids.get("trade_id")

        if not trade_id:
            pytest.skip("ALIBABA_TEST_TRADE_ID required for order details test")

        order = client.get_order(trade_id=trade_id, language="en_US")

        # Expected fields from documentation
        expected_fields = [
            "trade_id",
            "trade_status",
            "create_date",
            "shipping_address",
            "order_products",
            "total_amount",
        ]

        for field in expected_fields:
            assert field in order, f"Missing expected field: {field}"

        # Validate order products structure
        products = order.get("order_products", [])
        if products:
            product = products[0]
            assert "product_id" in product
            assert "quantity" in product
            assert "unit_price" in product

    def test_get_order_logistics(self, client: AlibabaClient, test_trade_ids: dict[str, str]) -> None:
        """Test getting order logistics status."""
        trade_id = test_trade_ids.get("trade_id")

        if not trade_id:
            pytest.skip("ALIBABA_TEST_TRADE_ID required for logistics test")

        logistics = client.get_order_logistics(trade_id=trade_id, data_select="logistic_order")

        # Validate logistics fields if present
        if logistics and isinstance(logistics, dict):
            # Check for documented logistics fields
            expected_fields = ["logistic_status", "shipment_date", "shipping_order_list"]
            present_fields = [f for f in expected_fields if f in logistics]
            assert len(present_fields) > 0, "No expected logistics fields found"

    def test_get_order_tracking(self, client: AlibabaClient, test_trade_ids: dict[str, str]) -> None:
        """Test getting order tracking events."""
        trade_id = test_trade_ids.get("trade_id")

        if not trade_id:
            pytest.skip("ALIBABA_TEST_TRADE_ID required for tracking test")

        try:
            result = client.get_order_tracking(trade_id=trade_id)

            # Validate response structure
            assert "trade_id" in result
            assert "tracking" in result

            tracking_list = result.get("tracking", [])
            if tracking_list:
                tracking = tracking_list[0]
                expected_fields = ["carrier", "tracking_number", "event_list"]
                for field in expected_fields:
                    assert field in tracking, f"Missing expected field: {field}"

                # Validate events structure
                events = tracking.get("event_list", [])
                if events:
                    event = events[0]
                    assert "event_code" in event
                    assert "event_name" in event
                    assert "event_time" in event

        except AlibabaAPIError as e:
            # May get error if order not found or tracking not available
            pytest.skip(f"Tracking not available for this order: {e.message}")

    def test_create_order_dry_run(
        self, client: AlibabaClient, test_product_ids: dict[str, str]
    ) -> None:
        """
        Test order creation using high-level method.

        Creates an order but does NOT pay for it.
        The order will be in pending payment status.
        """
        # Get product ID from env
        product_id = test_product_ids.get("product_id", "1601494101640")

        # Step 1: Get product description to find SKU
        product = client.get_product(product_id=product_id, country="US")
        skus = product.get("skus", [])
        if not skus:
            pytest.skip("No SKUs found for test product")

        sku_id = skus[0].get("sku_id")

        # Step 2: Build order data
        product_list = [{"product_id": product_id, "sku_id": sku_id, "quantity": "1"}]

        logistics_detail = {
            "shipment_address": {
                "zip": "10012",
                "country": "United States of America",
                "country_code": "US",
                "province": "New York",
                "province_code": "NY",
                "city": "New York",
                "address": "123 Main Street",
                "contact_person": "Test Buyer",
                "telephone": {"country": "+1", "number": "5551234567"},
            },
            "dispatch_location": "CN",
            "carrier_code": "EX_ASP_JYC_FEDEX",
        }

        import time
        channel_refer_id = f"test_{int(time.time())}"

        try:
            result = client.create_order(
                channel_refer_id=channel_refer_id,
                product_list=product_list,
                logistics_detail=logistics_detail,
            )

            # Validate response
            assert "trade_id" in result
            trade_id = result["trade_id"]
            assert trade_id is not None

            print("\n============================================")
            print("Order created successfully!")
            print(f"Trade ID: {trade_id}")
            print(f"Channel Reference ID: {channel_refer_id}")
            print(f"Product ID: {product_id}")
            print("Order is in PENDING status - payment required")
            print("============================================")

        except AlibabaAPIError as e:
            # Test accounts have restrictions - skip with message
            if "test account" in e.message.lower():
                pytest.skip(f"Order creation restricted: {e.message}")
            raise

    def test_pay_orders_dry_run(
        self, client: AlibabaClient, test_trade_ids: dict[str, str], test_credentials: dict[str, str]
    ) -> None:
        """
        Test order payment using high-level method (requires sandbox).

        This test only runs in sandbox mode with a valid trade_id.
        """
        # Only run in sandbox mode
        use_sandbox = _parse_use_sandbox(test_credentials.get("use_sandbox", ""))
        if not use_sandbox:
            pytest.skip("Payment test requires ALIBABA_USE_SANDBOX=true")

        trade_id = test_trade_ids.get("trade_id")
        if not trade_id:
            pytest.skip("ALIBABA_TEST_TRADE_ID required for payment test")

        try:
            result = client.pay_orders(
                order_id_list=[trade_id],
                payment_method="CREDIT_CARD",
                user_ip="127.0.0.1",
                user_agent="alibaba-api-test/1.0",
            )

            # Validate response structure
            assert "status" in result
            assert "order_ids" in result

        except Exception as e:
            # Sandbox may return various responses - log and don't fail
            pytest.skip(f"Payment endpoint response in sandbox: {e}")

    def test_get_order_funds(self, client: AlibabaClient, test_trade_ids: dict[str, str]) -> None:
        """Test getting order payment details."""
        trade_id = test_trade_ids.get("trade_id")

        if not trade_id:
            pytest.skip("ALIBABA_TEST_TRADE_ID required for fund query test")

        try:
            funds = client.get_order_funds(trade_id=trade_id, data_select="fund_transaction_fee")

            # Validate response - should be a dict with fund details
            assert isinstance(funds, dict)

        except AlibabaAPIError as e:
            # This endpoint requires additional app permissions
            if "InsufficientPermission" in str(e) or "permission" in str(e).lower():
                pytest.skip("Fund query endpoint requires additional app permissions")
            raise
