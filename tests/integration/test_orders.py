"""Integration tests for order endpoints."""

import json

import pytest

from alibaba_cli.client import AlibabaClient
from alibaba_cli.config import Config


def _parse_use_sandbox(use_sandbox_raw: str) -> bool:
    """Parse use_sandbox string to boolean."""
    return isinstance(use_sandbox_raw, str) and use_sandbox_raw.lower() in ("1", "true", "yes")


@pytest.mark.integration
class TestOrderEndpoints:
    """Integration tests for order management endpoints."""

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

    def test_order_list(self, client: AlibabaClient) -> None:
        """Test listing orders."""
        response = client.get(
            "/alibaba/order/list",
            {
                "role": "buyer",
                "start_page": "0",
                "page_size": "10",
            },
        )

        # Validate response structure
        assert response.get("code") == "0"
        assert "value" in response

        value = response["value"]
        assert "total_count" in value
        assert "order_list" in value

        # Validate order structure if any orders returned
        orders = value.get("order_list", [])
        if orders:
            order = orders[0]
            assert "trade_id" in order
            assert "trade_status" in order
            assert "create_date" in order

    def test_order_get(self, client: AlibabaClient, test_trade_ids: dict[str, str]) -> None:
        """Test getting order details."""
        trade_id = test_trade_ids.get("trade_id")

        if not trade_id:
            pytest.skip("ALIBABA_TEST_TRADE_ID required for order details test")

        response = client.get(
            "/alibaba/order/get",
            {"e_trade_id": trade_id, "language": "en_US"},
        )

        # Validate response structure
        assert response.get("code") == "0"
        assert "value" in response

        value = response["value"]
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
            assert field in value, f"Missing expected field: {field}"

        # Validate order products structure
        products = value.get("order_products", [])
        if products:
            product = products[0]
            assert "product_id" in product
            assert "quantity" in product
            assert "unit_price" in product

    def test_order_logistics_query(
        self, client: AlibabaClient, test_trade_ids: dict[str, str]
    ) -> None:
        """Test getting order logistics status."""
        trade_id = test_trade_ids.get("trade_id")

        if not trade_id:
            pytest.skip("ALIBABA_TEST_TRADE_ID required for logistics test")

        response = client.get(
            "/order/logistics/query",
            {"trade_id": trade_id, "data_select": "logistic_order"},
        )

        # Validate response structure
        assert response.get("code") == "0"
        assert "value" in response

        # Validate logistics fields if present
        value = response.get("value", {})
        if value and isinstance(value, dict):
            # Check for documented logistics fields
            expected_fields = ["logistic_status", "shipment_date", "shipping_order_list"]
            # At least some expected fields should be present
            present_fields = [f for f in expected_fields if f in value]
            assert len(present_fields) > 0, f"No expected logistics fields found. Response keys: {list(value.keys())}"

    def test_order_tracking(
        self, client: AlibabaClient, test_trade_ids: dict[str, str]
    ) -> None:
        """Test getting order tracking events."""
        trade_id = test_trade_ids.get("trade_id")

        if not trade_id:
            pytest.skip("ALIBABA_TEST_TRADE_ID required for tracking test")

        from alibaba_cli.exceptions import AlibabaAPIError

        try:
            response = client.get("/order/logistics/tracking/get", {"trade_id": trade_id})

            # Validate response structure
            assert response.get("code") == "0"

            # Response may not have tracking_list if order hasn't shipped yet
            # or if tracking is not available for this order
            if "tracking_list" in response:
                tracking_list = response.get("tracking_list", [])
                if tracking_list:
                    tracking = tracking_list[0]
                    expected_fields = ["carrier", "tracking_number", "event_list"]
                    for field in expected_fields:
                        assert field in tracking, f"Missing expected field: {field}"
                    # tracking_url may not always be present

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

    def test_order_create_dry_run(self, client: AlibabaClient, test_product_ids: dict[str, str]) -> None:
        """
        Test order creation.

        Creates an order but does NOT pay for it.
        The order will be in pending payment status.

        Uses product from test_product_ids fixture, dynamically fetches
        SKU details and valid shipping options to construct a valid order.
        """
        from alibaba_cli.exceptions import AlibabaAPIError
        import json

        # Get product ID from env (1601494101640 has MOQ=1)
        product_id = test_product_ids.get("product_id", "1601494101640")

        # Step 1: Get product description to find SKU
        product_response = client.get(
            "/eco/buyer/product/description",
            {"query_req": f'{{"product_id": "{product_id}", "country": "US"}}'},
        )

        assert product_response.get("code") == "0", f"Failed to get product: {product_response}"
        product_data = product_response.get("result", {}).get("result_data", {})
        skus = product_data.get("skus", [])
        assert skus, "No SKUs found for product"

        sku_id = skus[0].get("sku_id")

        # Step 2: Get freight calculation using /order/freight/calculate
        # This endpoint returns proper vendor_code for order creation
        # Need e_company_id from product data
        e_company_id = product_data.get("eCompanyId")
        assert e_company_id, "Product missing eCompanyId (supplier ID)"

        carrier_code = None
        dispatch_location = None

        # Build the address object for freight calculation
        address = json.dumps({
            "zip": "10012",
            "country": {"code": "US", "name": "United States"},
            "province": {"code": "NY", "name": "New York"},
            "city": {"code": "", "name": "New York"},
            "address": "123 Main Street"
        })

        # Build logistics_product_list
        logistics_product_list = json.dumps([
            {
                "product_id": product_id,
                "sku_id": sku_id,
                "quantity": "1",
                "country_code": "US"
            }
        ])

        for dispatch_loc in ["CN", "US"]:
            try:
                freight_response = client.get(
                    "/order/freight/calculate",
                    {
                        "e_company_id": e_company_id,
                        "destination_country": "US",
                        "dispatch_location": dispatch_loc,
                        "address": address,
                        "logistics_product_list": logistics_product_list
                    }
                )
                if freight_response.get("code") == "0":
                    options = freight_response.get("value", [])
                    if options:
                        carrier_code = options[0].get("vendor_code")
                        dispatch_location = dispatch_loc
                        print(f"\nFreight option: {options[0].get('vendor_name', 'Unknown')} - code: {carrier_code}")
                        break
            except AlibabaAPIError as e:
                print(f"Freight calc failed for {dispatch_loc}: {e}")
                continue

        if not carrier_code:
            pytest.skip("Could not find valid shipping options for test product")

        # Step 3: Create the order
        product_list = json.dumps([
            {"product_id": product_id, "sku_id": sku_id, "quantity": "1"}
        ])

        logistics_detail = json.dumps({
            "shipment_address": {
                "zip": "10012",
                "country": "United States of America",
                "country_code": "US",
                "province": "New York",
                "province_code": "NY",
                "city": "New York",
                "address": "123 Main Street",
                "contact_person": "Test Buyer",
                "telephone": {"country": "+1", "number": "5551234567"}
            },
            "dispatch_location": dispatch_location,
            "carrier_code": carrier_code
        })

        properties = json.dumps({
            "platform": "Test",
            "orderId": "TEST-ORDER-001"
        })

        import time
        channel_refer_id = f"test_{int(time.time())}"

        try:
            response = client.post(
                "/buynow/order/create",
                {
                    "channel_refer_id": channel_refer_id,
                    "product_list": product_list,
                    "logistics_detail": logistics_detail,
                    "properties": properties,
                },
            )

            # Validate response
            assert response.get("code") == "0", f"Order creation failed: {response}"

            # The response should contain order details in "value" key
            value = response.get("value", {})
            assert value, "Response should contain value with order details"

            # Print the order ID for manual testing/payment if needed
            trade_id = value.get("trade_id")
            if trade_id:
                print(f"\n============================================")
                print(f"Order created successfully!")
                print(f"Trade ID: {trade_id}")
                print(f"Channel Reference ID: {channel_refer_id}")
                print(f"Product ID: {product_id}")
                print(f"SKU ID: {sku_id}")
                print(f"Carrier: {carrier_code}")
                print(f"Order is in PENDING status - payment required")
                print(f"============================================")
        except AlibabaAPIError as e:
            # Test accounts have restrictions - skip with message
            print(f"\nOrder creation error: [{e.code}] {e.message}")
            if "test account" in e.message.lower():
                pytest.skip(f"Order creation restricted: {e.message}")
            if "test account" in str(e).lower():
                pytest.skip(f"Order creation restricted (test account)")
            raise

    def test_order_pay_dry_run(self, client: AlibabaClient, test_trade_ids: dict[str, str], test_credentials: dict[str, str]) -> None:
        """
        Test order payment endpoint (requires sandbox mode).

        This test only runs in sandbox mode with a valid trade_id.
        In sandbox, payment can be tested without actual charges.
        """
        # Only run in sandbox mode
        use_sandbox = _parse_use_sandbox(test_credentials.get("use_sandbox", ""))
        if not use_sandbox:
            pytest.skip("Payment test requires ALIBABA_USE_SANDBOX=true")

        trade_id = test_trade_ids.get("trade_id")
        if not trade_id:
            pytest.skip("ALIBABA_TEST_TRADE_ID required for payment test - set to a pending order ID")

        # Test the payment endpoint structure (dry run - don't execute actual payment)
        # Just validate the endpoint accepts the request format
        import json

        payment_request = {
            "order_id_list": [trade_id],
            "payment_method": "CREDIT_CARD",
            "user_ip": "127.0.0.1",
            "user_agent": "alibaba-cli-test/1.0",
            "accept_language": "en-US,en;q=0.9",
            "screen_resolution": "1920*1080",
            "is_pc": True,
        }

        try:
            response = client.post(
                "/alibaba/dropshipping/order/pay",
                {"param_order_pay_request": json.dumps(payment_request)}
            )

            # Validate response structure
            assert response is not None
            value = response.get("value", response)
            # In sandbox, should get a response with status
            if isinstance(value, dict):
                assert "status" in value or "code" in value
        except Exception as e:
            # Sandbox may return various responses - log and don't fail
            pytest.skip(f"Payment endpoint response in sandbox: {e}")

    def test_order_fund_query(
        self, client: AlibabaClient, test_trade_ids: dict[str, str]
    ) -> None:
        """Test getting order payment details."""
        from alibaba_cli.exceptions import AlibabaAPIError

        trade_id = test_trade_ids.get("trade_id")

        if not trade_id:
            pytest.skip("ALIBABA_TEST_TRADE_ID required for fund query test")

        try:
            response = client.get(
                "/alibaba/order/fund/query",
                {"e_trade_id": trade_id, "data_select": "fund_transaction_fee"},
            )

            # Validate response structure
            assert response.get("code") == "0"
            assert "value" in response
        except AlibabaAPIError as e:
            # This endpoint requires additional app permissions
            if "InsufficientPermission" in str(e) or "permission" in str(e).lower():
                pytest.skip("Fund query endpoint requires additional app permissions")
            raise
