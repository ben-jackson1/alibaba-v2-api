"""Product discovery API methods."""

import json
from typing import Any


class ProductMethods:
    """
    Product-related API methods.

    This mixin class provides methods for discovering and retrieving
    product information from the Alibaba marketplace.
    """

    def _product_request(
        self,
        api_path: str,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make a product-related API request using the base client."""
        return self.get(api_path, params)

    def list_products(
        self,
        scene_id: str,
        page: int = 0,
        page_size: int = 50,
    ) -> dict[str, Any]:
        """
        Get product list by scene ID.

        Common scene IDs:
          906124611  Standard US-based fulfillment
          906168847  Cross-border fulfillment (China to US)
          907135637  Fast fulfillment from US (within 48 hours)
          907732810  Dropshipping-eligible products from Mexico
          907180667  Top-selling products from the US
          907180664  Top-selling products from Mexico

        Args:
            scene_id: Scene ID for product list
            page: Page number (default: 0)
            page_size: Items per page (default: 50, max 100)

        Returns:
            Dict with product_ids list, total, page info

        Example:
            products = client.list_products(scene_id="906124611", page=0, page_size=10)
        """
        query_req = {
            "scene_id": scene_id,
            "index": page,
            "size": min(page_size, 100),
            "product_type": "common",
        }

        response = self._product_request(
            "/eco/buyer/product/check",
            {"query_req": json.dumps(query_req)},
        )

        result = response.get("result", {})
        return {
            "product_ids": result.get("result_data", []),
            "total": result.get("result_total"),
            "page": page,
            "page_size": page_size,
            "_raw": response,
        }

    def get_product(
        self,
        product_id: str | int,
        country: str = "US",
    ) -> dict[str, Any]:
        """
        Get detailed product information.

        Args:
            product_id: Alibaba product ID
            country: Country code for product details (default: "US")

        Returns:
            Product details dict

        Example:
            product = client.get_product(product_id="1601206892606", country="US")
        """
        query_req = {"product_id": int(product_id), "country": country}

        response = self._product_request(
            "/eco/buyer/product/description",
            {"query_req": json.dumps(query_req)},
        )

        return response.get("result", {}).get("result_data", {})

    def get_product_inventory(
        self,
        product_id: str,
        sku_id: str | None = None,
        shipping_from: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Check product inventory levels.

        Args:
            product_id: Alibaba product ID
            sku_id: Specific SKU ID to check
            shipping_from: Origin country code (CN, US, MX)

        Returns:
            List of inventory items

        Example:
            inventory = client.get_product_inventory(
                product_id="1600927952535",
                shipping_from="CN"
            )
        """
        inv_req = {"product_id": product_id}
        if sku_id:
            inv_req["sku_id"] = sku_id
        if shipping_from:
            inv_req["shipping_from"] = shipping_from

        response = self._product_request(
            "/eco/buyer/product/inventory",
            {"inv_req": json.dumps(inv_req)},
        )

        return response.get("result", {}).get("result_data", [])

    def get_local_products(
        self,
        country: str,
        page: int = 0,
        page_size: int = 50,
    ) -> dict[str, Any]:
        """
        Get products from local warehouse inventory.

        Args:
            country: Warehouse country code (e.g., US, MX)
            page: Page number (default: 0)
            page_size: Items per page (default: 50)

        Returns:
            Dict with product_ids list and country

        Example:
            products = client.get_local_products(country="US", page=0, page_size=10)
        """
        req = {
            "index": page,
            "size": page_size,
            "country": country,
        }

        response = self._product_request(
            "/eco/buyer/local/product/check",
            {"req": json.dumps(req)},
        )

        result = response.get("result", {})
        return {
            "product_ids": result.get("result_data", []),
            "country": country,
            "_raw": response,
        }

    def get_crossborder_products(
        self,
        page: int = 0,
        page_size: int = 50,
    ) -> dict[str, Any]:
        """
        Get cross-border products (shipping from China).

        Args:
            page: Page number (default: 0)
            page_size: Items per page (default: 50)

        Returns:
            Dict with product_ids list

        Example:
            products = client.get_crossborder_products(page=0, page_size=10)
        """
        param0 = {
            "index": page,
            "size": page_size,
        }

        response = self._product_request(
            "/eco/buyer/crossborder/product/check",
            {"param0": json.dumps(param0)},
        )

        result = response.get("result", {})
        return {
            "product_ids": result.get("result_data", []),
            "_raw": response,
        }

    def search_products(
        self,
        scene_id: str = "906124611",
        limit: int = 5,
    ) -> dict[str, Any]:
        """
        Search for products and get full details.

        This convenience method fetches product IDs from a scene list,
        then retrieves full details for each product.

        Args:
            scene_id: Scene ID for product list (default: "906124611")
            limit: Number of products to fetch details for (default: 5)

        Returns:
            Dict with scene_id, total_found, successfully_loaded, and products list

        Example:
            results = client.search_products(scene_id="906124611", limit=3)
        """
        # Step 1: Get product IDs
        query_req = {
            "scene_id": scene_id,
            "page": 0,
            "page_size": limit,
            "size": limit,
            "index": 0,
        }

        response = self._product_request(
            "/eco/buyer/product/check",
            {"query_req": json.dumps(query_req)},
        )

        result = response.get("result", {})
        product_ids = result.get("result_data", [])

        if not product_ids:
            return {
                "scene_id": scene_id,
                "total_found": 0,
                "successfully_loaded": 0,
                "products": [],
            }

        # Step 2: Get details for each product
        products = []
        for product_id in product_ids:
            try:
                response = self._product_request(
                    "/eco/buyer/product/description",
                    {
                        "query_req": json.dumps(
                            {"product_id": str(product_id), "size": 10, "index": 0}
                        )
                    },
                )
                product_data = response.get("result", {}).get("result_data", {})
                if product_data:
                    products.append(product_data)
            except Exception:
                # Skip products that fail to load
                pass

        return {
            "scene_id": scene_id,
            "total_found": len(product_ids),
            "successfully_loaded": len(products),
            "products": products,
        }
