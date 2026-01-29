"""Integration tests for product endpoints."""

import os

import pytest

from alibaba_cli.client import AlibabaClient
from alibaba_cli.config import Config


def _parse_use_sandbox(use_sandbox_raw: str) -> bool:
    """Parse use_sandbox string to boolean."""
    return isinstance(use_sandbox_raw, str) and use_sandbox_raw.lower() in ("1", "true", "yes")


@pytest.mark.integration
class TestProductEndpoints:
    """Integration tests for product discovery endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self, test_credentials: dict[str, str]) -> None:
        """Skip all tests if credentials not available."""
        if not test_credentials.get("access_token"):
            pytest.skip("ALIBABA_ACCESS_TOKEN required for product endpoint tests")

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

    def test_product_list_by_scene(self, client: AlibabaClient) -> None:
        """Test getting product list by scene ID."""
        # Use standard US fulfillment scene
        scene_id = "906124611"

        response = client.get(
            "/eco/buyer/product/check",
            {"query_req": f'{{"scene_id": "{scene_id}", "index": 0, "size": 10, "product_type": "common"}}'},
        )

        # Validate response structure
        assert response.get("code") == "0"
        assert "result" in response
        result = response["result"]
        assert "result_data" in result
        assert isinstance(result["result_data"], list)

        # If we got products, the list should not be empty
        if result["result_data"]:
            assert len(result["result_data"]) > 0

    def test_product_description(self, client: AlibabaClient, test_product_ids: dict[str, str]) -> None:
        """Test getting product details."""
        # Use documented example product ID (env product may be unavailable)
        product_id = "1601206892606"

        # Use country parameter as discovered from working example
        response = client.get(
            "/eco/buyer/product/description",
            {"query_req": '{"product_id":' + str(product_id) + ',"country":"US"}'},
        )

        # Validate response structure
        assert response.get("code") == "0"
        assert "result" in response
        result_data = response["result"].get("result_data", {})

        # Validate expected fields from documentation
        expected_fields = [
            "product_id",
            "title",
            "detail_url",
            "main_image",
            "images",
            "eCompanyId",
            "currency",
            "min_order_quantity",
            "skus",
        ]

        for field in expected_fields:
            assert field in result_data, f"Missing expected field: {field}"

        # Validate SKUs structure
        skus = result_data.get("skus", [])
        if skus:
            sku = skus[0]
            assert "sku_id" in sku
            assert "ladder_price" in sku
            # Validate sku_attr_list if present
            if "sku_attr_list" in sku:
                sku_attr = sku["sku_attr_list"][0] if sku["sku_attr_list"] else {}
                # Expected fields from documentation
                attr_fields = ["attr_name_id", "attr_name_desc", "attr_value_id", "attr_value_desc"]
                # At least some fields should be present
                assert any(field in sku_attr for field in attr_fields), f"sku_attr_list missing expected fields, got: {list(sku_attr.keys())}"

    def test_product_inventory(self, client: AlibabaClient, test_product_ids: dict[str, str]) -> None:
        """Test getting product inventory."""
        product_id = test_product_ids.get("product_id", "3256810295445290")

        response = client.get(
            "/eco/buyer/product/inventory",
            {"inv_req": f'{{"product_id": "{product_id}", "shipping_from": "CN"}}'},
        )

        # Validate response structure
        assert response.get("code") == "0"
        assert "result" in response
        result_data = response["result"].get("result_data", [])

        # Validate inventory structure if data returned
        if result_data:
            inventory_entry = result_data[0]
            assert "shipping_from" in inventory_entry
            assert "inventory_list" in inventory_entry

    def test_local_product_list(self, client: AlibabaClient) -> None:
        """Test getting local warehouse products."""
        response = client.get(
            "/eco/buyer/local/product/check",
            {"req": '{"index": 0, "size": 10, "country": "US"}'},
        )

        # Validate response structure
        assert response.get("code") == "0"
        assert "result" in response

    def test_crossborder_product_list(self, client: AlibabaClient) -> None:
        """Test getting cross-border products."""
        response = client.get(
            "/eco/buyer/crossborder/product/check",
            {"param0": '{"index": 0, "size": 10}'},
        )

        # Validate response structure
        assert response.get("code") == "0"
        assert "result" in response
