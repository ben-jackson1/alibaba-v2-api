"""Pydantic models for product endpoints."""

from pydantic import BaseModel, Field


class SkuAttribute(BaseModel):
    """SKU attribute (e.g., Color, Size)."""

    attr_name_id: str = Field(alias="attr_name_id")
    attr_name_desc: str = Field(alias="attr_name_desc")
    attr_value_id: str = Field(alias="attr_value_id")
    attr_value_desc: str = Field(alias="attr_value_desc")
    attr_value_image: str | None = Field(default=None, alias="attr_value_image")


class LadderPrice(BaseModel):
    """Volume-based pricing tier."""

    min_quantity: str = Field(alias="min_quantity")
    max_quantity: str = Field(alias="max_quantity")
    price: str = Field(alias="price")
    currency: str = Field(alias="currency")


class Sku(BaseModel):
    """Product SKU/variant."""

    sku_id: str = Field(alias="sku_id")
    product_id: str = Field(alias="product_id")
    seller_sku_id: str = Field(alias="seller_sku_id")
    status: str = Field(alias="status")
    unit: str = Field(alias="unit")
    image: str | None = Field(default=None, alias="image")
    sku_attr_list: list[SkuAttribute] = Field(alias="sku_attr_list", default_factory=list)
    ladder_price: list[LadderPrice] = Field(alias="ladder_price", default_factory=list)


class WholesaleTrade(BaseModel):
    """Wholesale pricing information."""

    min_order_quantity: str = Field(alias="min_order_quantity")
    unit_type: str = Field(alias="unit_type")
    handling_time: str = Field(alias="handling_time")
    price: str = Field(alias="price")


class ProductDescription(BaseModel):
    """Product details from /eco/buyer/product/description."""

    product_id: str = Field(alias="product_id")
    title: str = Field(alias="title")
    description: str | None = Field(default=None, alias="description")
    detail_url: str = Field(alias="detail_url")
    main_image: str = Field(alias="main_image")
    images: list[str] = Field(alias="images", default_factory=list)
    category_id: str = Field(alias="category_id")
    category: str = Field(alias="category")
    supplier: str | None = Field(default=None, alias="supplier")
    e_company_id: str = Field(alias="eCompanyId")
    currency: str = Field(alias="currency")
    min_order_quantity: str = Field(alias="min_order_quantity")
    status: str = Field(alias="status")
    mode_id: str = Field(alias="mode_id")
    wholesale_trade: WholesaleTrade | None = Field(default=None, alias="wholesale_trade")
    skus: list[Sku] = Field(alias="skus", default_factory=list)


class InventoryItem(BaseModel):
    """Inventory item for a SKU."""

    product_id: str = Field(alias="product_id")
    sku_id: str = Field(alias="sku_id")
    inventory_count: str = Field(alias="inventory_count")
    inventory_unit: str = Field(alias="inventory_unit")


class InventoryByLocation(BaseModel):
    """Inventory grouped by shipping location."""

    shipping_from: str = Field(alias="shipping_from")
    inventory_list: list[InventoryItem] = Field(alias="inventory_list", default_factory=list)


class ProductListResult(BaseModel):
    """Result from product list endpoints."""

    result_code: str = Field(alias="result_code")
    result_msg: str = Field(alias="result_msg")
    result_data: list[int] | list[str] = Field(alias="result_data", default_factory=list)
    result_total: str | None = Field(default=None, alias="result_total")


class ProductListResponse(BaseModel):
    """Response from product list endpoints."""

    code: str = Field(default="0")
    request_id: str | None = Field(default=None, alias="request_id")
    result: ProductListResult | None = Field(default=None, alias="result")
