"""Pydantic models for shipping endpoints."""

from pydantic import BaseModel, Field


class Fee(BaseModel):
    """Shipping fee."""

    amount: str = Field(alias="amount")
    currency: str = Field(alias="currency")


class ShippingOption(BaseModel):
    """Shipping option from freight calculation."""

    shipping_type: str = Field(alias="shipping_type")
    vendor_code: str | None = Field(default=None, alias="vendor_code")
    vendor_name: str | None = Field(default=None, alias="vendor_name")
    trade_term: str | None = Field(default=None, alias="trade_term")
    dispatch_country: str | None = Field(default=None, alias="dispatch_country")
    destination_country: str | None = Field(default=None, alias="destination_country")
    delivery_time: str | None = Field(default=None, alias="delivery_time")
    solution_biz_type: str | None = Field(default=None, alias="solution_biz_type")
    store_type: str | None = Field(default=None, alias="store_type")
    fee: Fee | None = Field(default=None, alias="fee")


class FreightResponse(BaseModel):
    """Response from freight calculation endpoints."""

    code: str = Field(default="0")
    request_id: str | None = Field(default=None, alias="request_id")
    value: list[ShippingOption] = Field(alias="value", default_factory=list)
