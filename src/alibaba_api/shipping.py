"""Shipping calculation API methods."""

import json
from typing import Any


class ShippingMethods:
    """
    Shipping-related API methods.

    This mixin class provides methods for calculating shipping costs
    and freight estimates.
    """

    def _shipping_request(
        self,
        api_path: str,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make a shipping-related API request using the base client."""
        return self.get(api_path, params)

    # pylint: disable=too-many-arguments

    def calculate_freight(
        self,
        product_id: str,
        quantity: int,
        destination_country: str,
        zip_code: str | None = None,
        dispatch_location: str = "CN",
        *,
        fallback: bool = True,
    ) -> dict[str, Any]:
        """
        Calculate basic shipping cost for a single product.

        Args:
            product_id: Alibaba product ID
            quantity: Number of items
            destination_country: Destination country code (e.g., "US")
            zip_code: Destination ZIP code
            dispatch_location: Origin location (CN, US, MX). Default: "CN"
            fallback: If True, automatically tries fallback dispatch locations
                (CN → US → MX) when primary returns no results

        Returns:
            Dict with product_id, quantity, destination, dispatch_location,
            fallback_used, and options list

        Example:
            shipping = client.calculate_freight(
                product_id="1600124642247",
                quantity=5,
                destination_country="US",
                zip_code="90001",
            )
        """
        fallback_locations = ["CN", "US", "MX"]

        # Determine which locations to try
        if dispatch_location in fallback_locations:
            start_index = fallback_locations.index(dispatch_location)
            locations_to_try = fallback_locations[start_index:]
        else:
            locations_to_try = [dispatch_location]

        response = None
        successful_location = None

        for location in locations_to_try:
            params = {
                "product_id": product_id,
                "quantity": str(quantity),
                "destination_country": destination_country,
                "dispatch_location": location,
            }

            if zip_code:
                params["zip_code"] = zip_code

            try:
                response = self._shipping_request("/shipping/freight/calculate", params)
                shipping_options = response.get("value", [])

                if shipping_options:
                    successful_location = location
                    break
                elif location == locations_to_try[0] and not fallback:
                    break
            except Exception:
                if location == locations_to_try[0] and not fallback:
                    raise
                continue

        if response is None:
            return {
                "product_id": product_id,
                "quantity": quantity,
                "destination": destination_country,
                "dispatch_location": dispatch_location,
                "fallback_used": False,
                "options": [],
                "error": "No shipping options found",
            }

        shipping_options = response.get("value", [])
        return {
            "product_id": product_id,
            "quantity": quantity,
            "destination": destination_country,
            "dispatch_location": successful_location or locations_to_try[0],
            "fallback_used": successful_location != dispatch_location
            if len(locations_to_try) > 1
            else False,
            "options": shipping_options,
            "_raw": response,
        }

    def calculate_freight_advanced(
        self,
        e_company_id: str,
        destination_country: str,
        address: dict[str, Any] | str,
        logistics_product_list: list[dict[str, Any]] | str,
        dispatch_location: str = "CN",
    ) -> dict[str, Any]:
        """
        Calculate shipping for multiple products with full address.

        Args:
            e_company_id: Supplier company ID from product details
            destination_country: Destination country code
            address: Shipping address as dict or JSON string.
                Example: {"zip": "10012", "country_code": "US", ...}
            logistics_product_list: Products to ship as list or JSON string.
                Example: [{"product_id": "1600191825486", "sku_id": "12321", "quantity": "1"}]
            dispatch_location: Origin location (CN, US, MX). Default: "CN"

        Returns:
            Dict with supplier, destination, dispatch_location, products, and options

        Example:
            shipping = client.calculate_freight_advanced(
                e_company_id="cVmhg7/xG8q3UQgcH/5Fag==",
                destination_country="US",
                address={"zip": "10012", "country_code": "US"},
                logistics_product_list=[{
                    "product_id": "1600191825486",
                    "sku_id": "12321",
                    "quantity": "1"
                }],
            )
        """
        # Parse inputs
        address_obj = json.loads(address) if isinstance(address, str) else address
        products_obj = (
            json.loads(logistics_product_list)
            if isinstance(logistics_product_list, str)
            else logistics_product_list
        )

        params = {
            "e_company_id": e_company_id,
            "destination_country": destination_country,
            "dispatch_location": dispatch_location,
            "address": json.dumps(address_obj),
            "logistics_product_list": json.dumps(products_obj),
        }

        response = self._shipping_request("/order/freight/calculate", params)

        return {
            "supplier": e_company_id,
            "destination": destination_country,
            "dispatch_location": dispatch_location,
            "products": products_obj,
            "options": response.get("value", []),
            "_raw": response,
        }
