"""Configuration management for Alibaba API client."""

import os
from dataclasses import dataclass


@dataclass
class Config:
    """Configuration for Alibaba API client."""

    app_key: str
    app_secret: str
    access_token: str | None = None
    refresh_token: str | None = None
    use_sandbox: bool = False
    timeout: int = 30

    @classmethod
    def from_env(cls, **overrides: str | bool | None) -> "Config":
        """
        Create configuration from environment variables with optional overrides.

        Environment variables:
            ALIBABA_APP_KEY: Application key (required)
            ALIBABA_APP_SECRET: Application secret (required)
            ALIBABA_ACCESS_TOKEN: OAuth access token (optional)
            ALIBABA_REFRESH_TOKEN: OAuth refresh token (optional)
            ALIBABA_USE_SANDBOX: Use sandbox environment (optional, "true" to enable)
            ALIBABA_TIMEOUT: Request timeout in seconds (optional, default 30)

        Args:
            **overrides: Keyword arguments to override environment variables

        Returns:
            Config instance

        Raises:
            ValueError: If required credentials are missing
        """
        app_key = overrides.get("app_key", os.getenv("ALIBABA_APP_KEY", "")) or overrides.get(
            "app_key", ""
        )
        app_secret = overrides.get(
            "app_secret", os.getenv("ALIBABA_APP_SECRET", "")
        ) or overrides.get("app_secret", "")

        if not app_key:
            raise ValueError("ALIBABA_APP_KEY is required")
        if not app_secret:
            raise ValueError("ALIBABA_APP_SECRET is required")

        # Parse use_sandbox - can be string "true"/"false" or boolean
        use_sandbox_raw = overrides.get("use_sandbox", os.getenv("ALIBABA_USE_SANDBOX", ""))
        if isinstance(use_sandbox_raw, str):
            use_sandbox = use_sandbox_raw.lower() in ("1", "true", "yes")
        else:
            use_sandbox = bool(use_sandbox_raw)

        return cls(
            app_key=app_key,
            app_secret=app_secret,
            access_token=overrides.get("access_token", os.getenv("ALIBABA_ACCESS_TOKEN")),
            refresh_token=overrides.get("refresh_token", os.getenv("ALIBABA_REFRESH_TOKEN")),
            use_sandbox=use_sandbox,
            timeout=int(overrides.get("timeout", os.getenv("ALIBABA_TIMEOUT", "30"))),
        )

    @property
    def base_url(self) -> str:
        if self.use_sandbox:
            return "https://openapi-api-sandbox.alibaba.com/rest"
        return "https://openapi-api.alibaba.com/rest"


# Known error code messages from documentation
ERROR_MESSAGES: dict[str, str] = {
    "110001": "Unauthorized: Buyer must use overseas-registered account (not China account)",
    "10010": "Logistics route not found. Check dispatch_location parameter.",
    "130602": "Invalid logistics route. Ensure carrier_code still exists.",
    "130608": "Missing dispatch location. Set dispatch_location = MX for Mexico products.",
    "480006": "Order amount exceeds limit. Maximum is $5000 for BuyNow orders.",
    "10007": "Cannot find SKU cost. Check product MOQ requirements.",
    "410006": "Quantity below minimum. Increase quantity to meet MOQ.",
    "130704": "Promotion unavailable. Contact Alibaba to refresh inventory cache.",
    "130106": "Product invalid. Product is offline, select different product.",
    "130703": "Insufficient inventory. Reduce quantity or select different SKU.",
    "120019": "Product restricted. Product cannot ship to destination country.",
    "800022": "Unable to calculate tariff. Provide complete address details.",
    "10012": "Dispatch location invalid. Match dispatch_location to product's origin.",
    "4015": "Cannot ship to country. Seller doesn't support shipping to destination.",
    "4016": "Freight template service error. Product or shipping configuration invalid.",
    "140004": "Insufficient inventory. Product is out of stock.",
    "10005": "SKU not found. SKU may have been deleted.",
    "400007": "EPR required. Seller needs valid EPR number for DE/FR.",
    "430013": "Order amount too small. Minimum order amount is $0.30.",
}


def get_error_message(code: str, default_message: str | None = None) -> str:
    """Get a helpful error message for an error code.

    Args:
        code: The error code from the API
        default_message: Fallback message if code not found

    Returns:
        Helpful error message
    """
    return ERROR_MESSAGES.get(code, default_message or f"API error code: {code}")
