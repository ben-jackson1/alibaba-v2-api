"""
Base API client for Alibaba Open Platform API.

This module provides the AlibabaClient class which handles:
- Request signing via HMAC-SHA256
- HTTP communication via httpx
- Response parsing and error handling
- High-level methods for orders, products, shipping, and auth
"""

from typing import Any, Literal

import httpx

from alibaba_api.auth import AuthMethods
from alibaba_api.config import Config, get_error_message
from alibaba_api.exceptions import (
    AlibabaAPIError,
    AlibabaNetworkError,
    AlibabaValidationError,
)
from alibaba_api.orders import OrderMethods
from alibaba_api.products import ProductMethods
from alibaba_api.shipping import ShippingMethods
from alibaba_api.signing import build_signed_params


class AlibabaClient(OrderMethods, ProductMethods, ShippingMethods, AuthMethods):
    """
    Client for Alibaba.com Open Platform API v2.

    Example:
        config = Config.from_env(app_key="...", app_secret="...")
        client = AlibabaClient(config)

        # High-level methods
        product = client.get_product(product_id="1601206892606")
        orders = client.list_orders(role="buyer", page_size=10)
        shipping = client.calculate_freight(
            product_id="1601206892606",
            quantity=10,
            destination_country="US",
        )

        # Low-level generic API call
        response = client.get(
            "/eco/buyer/product/description",
            {"query_req": json.dumps({"product_id": "123"})}
        )
    """

    def __init__(
        self,
        config: Config,
    ) -> None:
        """
        Initialize the API client.

        Args:
            config: Configuration instance with credentials
        """
        self.config = config
        self._client = httpx.Client(timeout=config.timeout)

    def _build_url(self, api_path: str) -> str:
        return f"{self.config.base_url}{api_path}"

    def _parse_response(self, response: httpx.Response) -> dict[str, Any]:
        """
        Parse API response and handle errors.

        Args:
            response: HTTP response from httpx

        Returns:
            Parsed JSON response

        Raises:
            AlibabaNetworkError: For HTTP errors
            AlibabaAPIError: For API error responses
        """
        try:
            data: dict[str, Any] | str = response.json()
        except ValueError:
            data = response.text

        if response.status_code >= 400:
            request_id = response.headers.get("x-request-id")
            message = (
                data.get("message", response.text) if isinstance(data, dict) else response.text
            )
            raise AlibabaNetworkError(
                message,
                status_code=response.status_code,
                request_id=request_id,
            )

        if not isinstance(data, dict):
            return {"data": data}

        # Check for API errors (code != "0")
        code = str(data.get("code", ""))
        if code != "0":
            request_id = data.get("request_id")
            message = data.get("message", "")
            sub_code = data.get("sub_code")

            if not message:
                message = get_error_message(sub_code or code)

            raise AlibabaAPIError(
                code=code,
                message=message,
                request_id=request_id,
                sub_code=sub_code,
            )

        return data

    def request(
        self,
        api_path: str,
        params: dict[str, str] | None = None,
        method: Literal["GET", "POST"] = "GET",
        *,
        access_token: str | None = None,
    ) -> dict[str, Any]:
        """
        Make a signed request to the Alibaba API.

        Args:
            api_path: The API endpoint path (e.g., "/auth/token/create")
            params: Business parameters for the API
            method: HTTP method (GET or POST)
            access_token: Override access token for this request

        Returns:
            Parsed JSON response from the API

        Raises:
            AlibabaValidationError: If parameters are invalid
            AlibabaNetworkError: For network/HTTP errors
            AlibabaAPIError: For API error responses
        """
        if params is None:
            params = {}

        if not api_path.startswith("/"):
            raise AlibabaValidationError(f"api_path must start with '/', got: {api_path}")

        token = access_token or self.config.access_token

        signed_params = build_signed_params(
            api_path=api_path,
            params=params,
            app_key=self.config.app_key,
            app_secret=self.config.app_secret,
            access_token=token,
        )

        url = self._build_url(api_path)

        try:
            if method.upper() == "GET":
                response = self._client.get(url, params=signed_params)
            else:
                response = self._client.post(url, data=signed_params)
        except httpx.TimeoutException as e:
            raise AlibabaNetworkError(f"Request timed out after {self.config.timeout}s") from e
        except httpx.NetworkError as e:
            raise AlibabaNetworkError(f"Network error: {e}") from e

        return self._parse_response(response)

    def get(
        self,
        api_path: str,
        params: dict[str, str] | None = None,
        *,
        access_token: str | None = None,
    ) -> dict[str, Any]:
        """
        Make a GET request to the Alibaba API.

        Args:
            api_path: The API endpoint path
            params: Query parameters
            access_token: Override access token for this request

        Returns:
            Parsed JSON response
        """
        return self.request(api_path, params, "GET", access_token=access_token)

    def post(
        self,
        api_path: str,
        params: dict[str, str] | None = None,
        *,
        access_token: str | None = None,
    ) -> dict[str, Any]:
        """
        Make a POST request to the Alibaba API.

        Args:
            api_path: The API endpoint path
            params: Form data parameters
            access_token: Override access token for this request

        Returns:
            Parsed JSON response
        """
        return self.request(api_path, params, "POST", access_token=access_token)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "AlibabaClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
