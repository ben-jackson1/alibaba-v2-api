"""Order management API methods."""

from typing import Any


class OrderMethods:
    """
    Order-related API methods.

    This mixin class provides methods for managing Alibaba orders,
    including creating, listing, and paying for orders.
    """

    def _order_request(
        self,
        api_path: str,
        params: dict[str, str] | None = None,
        method: str = "GET",
    ) -> dict[str, Any]:
        """Make an order-related API request using the base client."""
        if method.upper() == "GET":
            return self.get(api_path, params)
        return self.post(api_path, params)

    # pylint: disable=too-many-arguments

    def list_orders(
        self,
        role: str = "buyer",
        status: str | None = None,
        start_page: int = 0,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """
        List orders with optional filtering.

        Args:
            role: Role for order list ("buyer" or "seller", default: "buyer")
            status: Filter by order status
            start_page: Page number (default: 0)
            page_size: Items per page (default: 20)

        Returns:
            Dict with total_count, page, page_size, and orders list

        Example:
            orders = client.list_orders(role="buyer", status="paid")
        """
        params = {
            "role": role,
            "start_page": str(start_page),
            "page_size": str(page_size),
        }
        if status:
            params["status"] = status

        response = self._order_request("/alibaba/order/list", params)
        value = response.get("value", {})

        return {
            "total_count": value.get("total_count"),
            "page": start_page,
            "page_size": page_size,
            "orders": value.get("order_list", []),
            "_raw": response,
        }

    def get_order(
        self,
        trade_id: str,
        language: str = "en_US",
    ) -> dict[str, Any]:
        """
        Get detailed order information.

        Args:
            trade_id: Alibaba order ID (trade_id)
            language: Response language (default: "en_US")

        Returns:
            Order details dict

        Example:
            order = client.get_order(trade_id="234193410001028893")
        """
        params = {"e_trade_id": trade_id, "language": language}
        response = self._order_request("/alibaba/order/get", params)

        return response.get("value", response)

    def create_order(
        self,
        channel_refer_id: str,
        product_list: list[dict[str, Any]],
        logistics_detail: dict[str, Any],
        remark: str | None = None,
    ) -> dict[str, Any]:
        """
        Create a BuyNow dropshipping order.

        Args:
            channel_refer_id: Your internal order reference ID
            product_list: List of products to order.
                Example: [{"product_id": "100001", "sku_id": "200001", "quantity": "10"}]
            logistics_detail: Shipping details dict with:
                - shipment_address: dict with address details
                - dispatch_location: Origin location code (CN, US, MX)
                - carrier_code: Shipping carrier code
            remark: Optional order notes

        Returns:
            Dict with trade_id and pay_url

        Example:
            order = client.create_order(
                channel_refer_id="ORDER-001",
                product_list=[{"product_id": "100001", "sku_id": "200001", "quantity": "10"}],
                logistics_detail={
                    "shipment_address": {
                        "zip": "10012",
                        "country_code": "US",
                        # ... other address fields
                    },
                    "dispatch_location": "CN",
                    "carrier_code": "EX_ASP_JYC_FEDEX",
                }
            )
        """
        import json

        params = {
            "channel_refer_id": channel_refer_id,
            "product_list": json.dumps(product_list),
            "logistics_detail": json.dumps(logistics_detail),
        }
        if remark:
            params["remark"] = remark

        response = self._order_request("/buynow/order/create", params, method="POST")
        value = response.get("value", response)

        return {
            "trade_id": value.get("trade_id") or response.get("trade_id"),
            "pay_url": value.get("pay_url") or response.get("pay_url"),
            "_raw": response,
        }

    def pay_orders(
        self,
        order_id_list: list[str],
        payment_method: str = "CREDIT_CARD",
        user_ip: str = "127.0.0.1",
        user_agent: str = "alibaba-api/1.0",
    ) -> dict[str, Any]:
        """
        Pay for one or more orders.

        Args:
            order_id_list: List of order IDs to pay
            payment_method: Payment method (default: "CREDIT_CARD")
            user_ip: User IP address
            user_agent: User agent string

        Returns:
            Dict with status, order_ids, reason_code, reason_message, pay_url

        Example:
            result = client.pay_orders(
                order_id_list=["234193410001028893"],
                payment_method="CREDIT_CARD",
                user_ip="192.168.1.1",
            )
        """
        import json

        payment_request = {
            "order_id_list": order_id_list,
            "payment_method": payment_method,
            "user_ip": user_ip,
            "user_agent": user_agent,
            "accept_language": "en-US,en;q=0.9",
            "screen_resolution": "1920*1080",
            "is_pc": True,
        }

        params = {"param_order_pay_request": json.dumps(payment_request)}
        response = self._order_request("/alibaba/dropshipping/order/pay", params, method="POST")

        value = response.get("value", response)
        return {
            "status": value.get("status"),
            "order_ids": order_id_list,
            "reason_code": value.get("reason_code"),
            "reason_message": value.get("reason_message"),
            "pay_url": value.get("pay_url"),
            "_raw": response,
        }

    def get_order_logistics(
        self,
        trade_id: str,
        data_select: str = "logistic_order",
    ) -> dict[str, Any]:
        """
        Get order logistics status and tracking number.

        Args:
            trade_id: Alibaba order ID
            data_select: Data selection (default: "logistic_order")

        Returns:
            Logistics information dict

        Example:
            logistics = client.get_order_logistics(trade_id="234193410001028893")
        """
        params = {"trade_id": trade_id, "data_select": data_select}
        response = self._order_request("/order/logistics/query", params)

        return response.get("value", response)

    def get_order_tracking(self, trade_id: str) -> dict[str, Any]:
        """
        Get tracking events for an order.

        Args:
            trade_id: Alibaba order ID

        Returns:
            Dict with trade_id and tracking list

        Example:
            tracking = client.get_order_tracking(trade_id="234193410001028893")
        """
        response = self._order_request("/order/logistics/tracking/get", {"trade_id": trade_id})

        return {
            "trade_id": trade_id,
            "tracking": response.get("tracking_list", []),
            "_raw": response,
        }

    def get_order_funds(
        self,
        trade_id: str,
        data_select: str = "fund_transaction_fee",
    ) -> dict[str, Any]:
        """
        Get payment and fund details for an order.

        Args:
            trade_id: Alibaba order ID
            data_select: Data selection (default: "fund_transaction_fee")

        Returns:
            Fund details dict

        Example:
            funds = client.get_order_funds(trade_id="234193410001028893")
        """
        params = {"e_trade_id": trade_id, "data_select": data_select}
        response = self._order_request("/alibaba/order/fund/query", params)

        return response.get("value", response)
