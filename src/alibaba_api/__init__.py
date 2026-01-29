"""
Alibaba API Client - Python library for Alibaba.com Open Platform API v2.

This library provides:
- AlibabaClient with high-level methods for orders, products, shipping, and auth
- HMAC-SHA256 request signing
- Exception handling for API errors

Example:
    from alibaba_api import AlibabaClient, Config

    config = Config(app_key="...", app_secret="...")
    with AlibabaClient(config) as client:
        # High-level methods
        product = client.get_product(product_id="1601206892606")
        orders = client.list_orders(role="buyer", page_size=10)
        shipping = client.calculate_freight(
            product_id="1601206892606",
            quantity=10,
            destination_country="US",
        )

        # Low-level generic API call
        response = client.get("/path/to/endpoint", {"param": "value"})
"""

from alibaba_api.auth import AuthMethods
from alibaba_api.client import AlibabaClient
from alibaba_api.config import Config, get_error_message
from alibaba_api.exceptions import (
    AlibabaAPIError,
    AlibabaAuthError,
    AlibabaError,
    AlibabaNetworkError,
    AlibabaSignatureError,
    AlibabaValidationError,
)
from alibaba_api.orders import OrderMethods
from alibaba_api.products import ProductMethods
from alibaba_api.shipping import ShippingMethods
from alibaba_api.signing import build_signed_params, calculate_signature

__all__ = [
    # Client
    "AlibabaClient",
    # Config
    "Config",
    "get_error_message",
    # Exceptions
    "AlibabaError",
    "AlibabaAPIError",
    "AlibabaAuthError",
    "AlibabaNetworkError",
    "AlibabaSignatureError",
    "AlibabaValidationError",
    # Signing
    "calculate_signature",
    "build_signed_params",
    # Service mixins (for advanced usage)
    "AuthMethods",
    "OrderMethods",
    "ProductMethods",
    "ShippingMethods",
]

__version__ = "0.2.0"
