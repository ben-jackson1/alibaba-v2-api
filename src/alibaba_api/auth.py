"""Authentication API methods."""

from typing import Any


class AuthMethods:
    """
    Authentication-related API methods.

    This mixin class provides methods for OAuth token management,
    including creating tokens from authorization codes and refreshing tokens.
    """

    def _auth_request(
        self,
        api_path: str,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        return self.get(api_path, params)

    def create_token(
        self,
        code: str,
    ) -> dict[str, Any]:
        """
        Exchange OAuth authorization code for access token.

        First, visit the authorization URL in your browser:
        https://openapi-auth.alibaba.com/oauth/authorize?response_type=code&client_id={app_key}&redirect_uri={callback_url}

        Args:
            code: OAuth authorization code from Alibaba

        Returns:
            Dict with access_token, refresh_token, expires_in,
            refresh_expires_in, user_info, account_platform

        Example:
            tokens = client.create_token(code="3_500102_JxZ05Ux3cnnSSUm6dCxYg6Q26")
        """
        response = self._auth_request("/auth/token/create", {"code": code})

        return {
            "access_token": response.get("access_token"),
            "refresh_token": response.get("refresh_token"),
            "expires_in": response.get("expires_in"),
            "refresh_expires_in": response.get("refresh_expires_in"),
            "user_info": response.get("user_info", {}),
            "account_platform": response.get("account_platform"),
            "_raw": response,
        }

    def refresh_token(
        self,
        refresh_token: str | None = None,
    ) -> dict[str, Any]:
        """
        Refresh access token using refresh token.

        Args:
            refresh_token: OAuth refresh token. If not provided,
                uses the refresh_token from the config

        Returns:
            Dict with access_token, refresh_token, expires_in, refresh_expires_in

        Example:
            tokens = client.refresh_token()
            # or with specific token:
            tokens = client.refresh_token(refresh_token="your_token")
        """
        token = refresh_token or self.config.refresh_token
        if not token:
            raise ValueError(
                "No refresh token available. "
                "Provide refresh_token parameter or set ALIBABA_REFRESH_TOKEN."
            )

        response = self._auth_request("/auth/token/refresh", {"refresh_token": token})

        return {
            "access_token": response.get("access_token"),
            "refresh_token": response.get("refresh_token"),
            "expires_in": response.get("expires_in"),
            "refresh_expires_in": response.get("refresh_expires_in"),
            "_raw": response,
        }

    @property
    def auth_status(self) -> dict[str, Any]:
        """
        Get current authentication status.

        Returns:
            Dict with environment, app_key (masked), has_access_token, has_refresh_token

        Example:
            status = client.auth_status
        """
        return {
            "environment": "sandbox" if self.config.use_sandbox else "production",
            "app_key": (self.config.app_key[:8] + "..." if self.config.app_key else None),
            "has_access_token": bool(self.config.access_token),
            "has_refresh_token": bool(self.config.refresh_token),
        }
