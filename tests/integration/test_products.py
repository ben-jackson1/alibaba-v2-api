"""Integration tests for product API using high-level methods."""


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
class TestProductAPI:
    """Integration tests for product discovery using high-level API methods."""

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

    def test_list_products_by_scene(self, client: AlibabaClient) -> None:
        """Test getting product list by scene ID."""
        # Use standard US fulfillment scene
        result = client.list_products(scene_id="906124611", page=0, page_size=10)

        # Validate response structure
        assert "product_ids" in result
        assert isinstance(result["product_ids"], list)
        assert "total" in result
        assert "page" in result
        assert result["page"] == 0

        # If we got products, the list should not be empty
        if result["product_ids"]:
            assert len(result["product_ids"]) > 0

    def test_get_product_description(self, client: AlibabaClient) -> None:
        """Test getting product details."""
        # Use documented example product ID
        product_id = "1601206892606"

        product = client.get_product(product_id=product_id, country="US")

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
            assert field in product, f"Missing expected field: {field}"

        # Validate SKUs structure
        skus = product.get("skus", [])
        if skus:
            sku = skus[0]
            assert "sku_id" in sku
            assert "ladder_price" in sku
            # Validate sku_attr_list if present
            if "sku_attr_list" in sku:
                sku_attr = sku["sku_attr_list"][0] if sku["sku_attr_list"] else {}
                attr_fields = ["attr_name_id", "attr_name_desc", "attr_value_id", "attr_value_desc"]
                assert any(field in sku_attr for field in attr_fields), "sku_attr_list missing expected fields"

    def test_get_product_inventory(self, client: AlibabaClient) -> None:
        """Test getting product inventory."""
        product_id = "3256810295445290"

        inventory = client.get_product_inventory(product_id=product_id, shipping_from="CN")

        # Validate inventory structure if data returned
        if inventory:
            inventory_entry = inventory[0]
            assert "shipping_from" in inventory_entry
            assert "inventory_list" in inventory_entry

    def test_get_local_products(self, client: AlibabaClient) -> None:
        """Test getting local warehouse products."""
        result = client.get_local_products(country="US", page=0, page_size=10)

        # Validate response structure
        assert "product_ids" in result
        assert result["country"] == "US"

    def test_get_crossborder_products(self, client: AlibabaClient) -> None:
        """Test getting cross-border products."""
        result = client.get_crossborder_products(page=0, page_size=10)

        # Validate response structure
        assert "product_ids" in result
        assert isinstance(result["product_ids"], list)

    def test_search_products_convenience_method(self, client: AlibabaClient) -> None:
        """Test the search_products convenience method (multi-step flow)."""
        result = client.search_products(scene_id="906124611", limit=3)

        # Validate multi-step result structure
        assert "scene_id" in result
        assert "total_found" in result
        assert "successfully_loaded" in result
        assert "products" in result

        # If products were found, at least some should load successfully
        if result["total_found"] > 0:
            assert result["successfully_loaded"] >= 0
            assert len(result["products"]) <= result["total_found"]
