"""
HMAC-SHA256 request signing for Alibaba API.

Reference: https://openapi.alibaba.com/doc/api.htm
"""

import hashlib
import hmac


def calculate_signature(api_path: str, params: dict[str, str], app_secret: str) -> str:
    """
    Generate HMAC-SHA256 signature for Alibaba API requests.

    The signature algorithm:
    1. Sort parameters alphabetically by key (ASCII order)
    2. Concatenate key-value pairs (no separators): key1value1key2value2...
    3. Prepend API path: message = api_path + concat_string
    4. Generate HMAC-SHA256 signature using app_secret
    5. Return uppercase hex string

    Args:
        api_path: The API endpoint path (e.g., "/auth/token/create")
        params: Dictionary of all request parameters (excluding 'sign')
        app_secret: Your application's secret key

    Returns:
        Uppercase hex string of the HMAC-SHA256 signature

    Examples:
        >>> calculate_signature(
        ...     "/auth/token/create",
        ...     {"app_key": "12345", "code": "test", "timestamp": "1234567890"},
        ...     "secret"
        ... )
        'A1B2C3D4E5F6...'
    """
    # 1. Sort parameters alphabetically by key (ASCII order)
    sorted_params = dict(sorted(params.items()))

    # 2. Concatenate key-value pairs without separators
    concat_string = "".join(f"{k}{v}" for k, v in sorted_params.items())

    # 3. Prepend API path
    message = f"{api_path}{concat_string}"

    # 4. Generate HMAC-SHA256 signature
    signature = hmac.new(
        app_secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    # 5. Return uppercase hex string
    return signature.upper()


def build_signed_params(
    api_path: str,
    params: dict[str, str],
    app_key: str,
    app_secret: str,
    access_token: str | None = None,
) -> dict[str, str]:
    """
    Build complete parameter set with signature for an API request.

    Args:
        api_path: The API endpoint path
        params: Business parameters for the API
        app_key: Your application key
        app_secret: Your application secret
        access_token: User's access token (optional)

    Returns:
        Complete parameter dictionary including system params and signature
    """
    import time

    # Build system parameters
    system_params: dict[str, str] = {
        "app_key": app_key,
        "sign_method": "sha256",
        "timestamp": str(int(time.time() * 1000)),  # Milliseconds
    }

    # Add access_token if provided
    if access_token:
        system_params["access_token"] = access_token

    # Merge with business parameters
    all_params = {**system_params, **params}

    # Generate and add signature
    all_params["sign"] = calculate_signature(api_path, all_params, app_secret)

    return all_params
