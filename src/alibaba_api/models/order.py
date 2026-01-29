"""Pydantic models for order endpoints."""

from pydantic import BaseModel, Field


class Amount(BaseModel):
    """Monetary amount."""

    amount: str = Field(alias="amount")
    currency: str = Field(alias="currency")


class Telephone(BaseModel):
    """Telephone number."""

    country: str = Field(alias="country")
    area: str | None = Field(default=None, alias="area")
    number: str = Field(alias="number")


class ShipmentAddress(BaseModel):
    """Shipping address."""

    zip: str = Field(alias="zip")
    country: str = Field(alias="country")
    country_code: str = Field(alias="country_code")
    province: str = Field(alias="province")
    province_code: str = Field(alias="province_code")
    city: str = Field(alias="city")
    city_code: str | None = Field(default=None, alias="city_code")
    address: str = Field(alias="address")
    alternate_address: str | None = Field(default=None, alias="alternate_address")
    contact_person: str = Field(alias="contact_person")
    telephone: Telephone = Field(alias="telephone")


class OrderProduct(BaseModel):
    """Product in an order."""

    product_id: str = Field(alias="product_id")
    sku_id: str = Field(alias="sku_id")
    name: str = Field(alias="name")
    quantity: str = Field(alias="quantity")
    unit: str = Field(alias="unit")
    unit_price: Amount = Field(alias="unit_price")
    product_image: str = Field(alias="product_image")
    sku_attributes: list[dict] = Field(alias="sku_attributes", default_factory=list)


class FormattedDate(BaseModel):
    """Formatted date from API."""

    format_date: str = Field(alias="format_date")
    timestamp: str = Field(alias="timestamp")


class Party(BaseModel):
    """Order party (buyer/seller)."""

    immutable_eid: str = Field(alias="immutable_eid")
    full_name: str = Field(alias="full_name")


class Carrier(BaseModel):
    """Shipping carrier."""

    code: str = Field(alias="code")
    name: str = Field(alias="name")


class OrderDetails(BaseModel):
    """Order details from /alibaba/order/get."""

    trade_id: str = Field(alias="trade_id")
    trade_status: str = Field(alias="trade_status")
    pay_step: str | None = Field(default=None, alias="pay_step")
    fulfillment_channel: str | None = Field(default=None, alias="fulfillment_channel")
    dropshipping: str | None = Field(default=None, alias="dropshipping")
    create_date: FormattedDate = Field(alias="create_date")
    modify_date: FormattedDate = Field(alias="modify_date")
    shipping_address: ShipmentAddress = Field(alias="shipping_address")
    order_products: list[OrderProduct] = Field(alias="order_products", default_factory=list)
    product_total_amount: Amount = Field(alias="product_total_amount")
    shipment_fee: Amount = Field(alias="shipment_fee")
    total_amount: Amount = Field(alias="total_amount")
    carrier: Carrier | None = Field(default=None, alias="carrier")
    buyer: Party = Field(alias="buyer")
    seller: Party = Field(alias="seller")


class OrderListItem(BaseModel):
    """Order from list endpoint."""

    trade_id: str = Field(alias="trade_id")
    trade_status: str = Field(alias="trade_status")
    create_date: FormattedDate = Field(alias="create_date")
    modify_date: FormattedDate = Field(alias="modify_date")


class OrderListResponse(BaseModel):
    """Response from /alibaba/order/list."""

    code: str = Field(default="0")
    request_id: str | None = Field(default=None, alias="request_id")
    value: dict | None = Field(default=None, alias="value")


class CreateOrderResponse(BaseModel):
    """Response from /buynow/order/create."""

    code: str = Field(default="0")
    request_id: str | None = Field(default=None, alias="request_id")
    value: dict | None = Field(default=None, alias="value")
    trade_id: str | None = Field(default=None, alias="trade_id")
    pay_url: str | None = Field(default=None, alias="pay_url")


class PaymentRequestValue(BaseModel):
    """Value from payment response."""

    status: str = Field(alias="status")
    reason_code: str | None = Field(default=None, alias="reason_code")
    reason_message: str | None = Field(default=None, alias="reason_message")
    pay_url: str | None = Field(default=None, alias="pay_url")


class PaymentResponse(BaseModel):
    """Response from /alibaba/dropshipping/order/pay."""

    code: str = Field(default="0")
    request_id: str | None = Field(default=None, alias="request_id")
    value: PaymentRequestValue | None = Field(default=None, alias="value")


class TrackingEvent(BaseModel):
    """Tracking event."""

    event_code: str = Field(alias="event_code")
    event_name: str = Field(alias="event_name")
    event_location: str = Field(alias="event_location")
    event_time: str = Field(alias="event_time")


class TrackingInfo(BaseModel):
    """Tracking information."""

    carrier: str = Field(alias="carrier")
    tracking_number: str = Field(alias="tracking_number")
    current_event_code: str = Field(alias="current_event_code")
    tracking_url: str = Field(alias="tracking_url")
    event_list: list[TrackingEvent] = Field(alias="event_list", default_factory=list)


class TrackingResponse(BaseModel):
    """Response from /order/logistics/tracking/get."""

    code: str = Field(default="0")
    request_id: str | None = Field(default=None, alias="request_id")
    tracking_list: list[TrackingInfo] = Field(alias="tracking_list", default_factory=list)


class Voucher(BaseModel):
    """Shipping voucher."""

    tracking_number: str = Field(alias="tracking_number")
    service_provider: str = Field(alias="service_provider")
    logistics_type: str = Field(alias="logistics_type")


class ShippingOrder(BaseModel):
    """Shipping order."""

    voucher: Voucher = Field(alias="voucher")


class LogisticsQueryValue(BaseModel):
    """Value from logistics query."""

    logistic_status: str = Field(alias="logistic_status")
    shipment_date: FormattedDate = Field(alias="shipment_date")
    shipping_order_list: list[ShippingOrder] = Field(
        alias="shipping_order_list", default_factory=list
    )


class LogisticsQueryResponse(BaseModel):
    """Response from /order/logistics/query."""

    code: str = Field(default="0")
    request_id: str | None = Field(default=None, alias="request_id")
    value: LogisticsQueryValue | None = Field(default=None, alias="value")
