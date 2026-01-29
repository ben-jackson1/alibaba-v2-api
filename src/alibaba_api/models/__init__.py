"""
Pydantic models for API response validation.

All models use field aliases to map API response names (camelCase) to Python names (snake_case).
"""

from alibaba_api.models.auth import (
    TokenResponse,
    TokenResponseWrapper,
    UserInfo,
)
from alibaba_api.models.order import (
    Amount,
    Carrier,
    CreateOrderResponse,
    FormattedDate,
    LogisticsQueryResponse,
    LogisticsQueryValue,
    OrderDetails,
    OrderListItem,
    OrderListResponse,
    OrderProduct,
    Party,
    PaymentRequestValue,
    PaymentResponse,
    ShipmentAddress,
    ShippingOrder,
    Telephone,
    TrackingEvent,
    TrackingInfo,
    TrackingResponse,
    Voucher,
)
from alibaba_api.models.product import (
    InventoryByLocation,
    InventoryItem,
    LadderPrice,
    ProductDescription,
    ProductListResponse,
    ProductListResult,
    Sku,
    SkuAttribute,
    WholesaleTrade,
)
from alibaba_api.models.shipping import (
    Fee,
    FreightResponse,
    ShippingOption,
)

__all__ = [
    # Auth
    "UserInfo",
    "TokenResponse",
    "TokenResponseWrapper",
    # Product
    "SkuAttribute",
    "LadderPrice",
    "Sku",
    "WholesaleTrade",
    "ProductDescription",
    "InventoryItem",
    "InventoryByLocation",
    "ProductListResult",
    "ProductListResponse",
    # Order
    "Amount",
    "Telephone",
    "ShipmentAddress",
    "OrderProduct",
    "FormattedDate",
    "Party",
    "Carrier",
    "OrderDetails",
    "OrderListItem",
    "OrderListResponse",
    "CreateOrderResponse",
    "PaymentRequestValue",
    "PaymentResponse",
    "TrackingEvent",
    "TrackingInfo",
    "TrackingResponse",
    "Voucher",
    "ShippingOrder",
    "LogisticsQueryValue",
    "LogisticsQueryResponse",
    # Shipping
    "Fee",
    "ShippingOption",
    "FreightResponse",
]
