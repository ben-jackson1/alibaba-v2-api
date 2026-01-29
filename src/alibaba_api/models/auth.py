"""Pydantic models for authentication endpoints."""

from pydantic import BaseModel, Field


class UserInfo(BaseModel):
    """User information from token response."""

    country: str
    login_id: str = Field(alias="loginId")
    user_id: str = Field(alias="user_id")
    seller_id: str | None = Field(default=None, alias="seller_id")


class TokenResponse(BaseModel):
    """Response from /auth/token/create and /auth/token/refresh."""

    access_token: str = Field(alias="access_token")
    refresh_token: str = Field(alias="refresh_token")
    expires_in: str = Field(alias="expires_in")
    refresh_expires_in: str = Field(alias="refresh_expires_in")
    account_id: str | None = Field(default=None, alias="account_id")
    account: str | None = Field(default=None, alias="account")
    account_platform: str | None = Field(default=None, alias="account_platform")
    country: str | None = Field(default=None)
    user_info: UserInfo | None = Field(default=None, alias="user_info")
    code: str = Field(default="0")
    request_id: str | None = Field(default=None, alias="request_id")


class TokenResponseWrapper(BaseModel):
    """Wrapper for token endpoint responses."""

    code: str = Field(default="0")
    request_id: str | None = Field(default=None, alias="request_id")
    access_token: str | None = Field(default=None, alias="access_token")
    refresh_token: str | None = Field(default=None, alias="refresh_token")
    expires_in: str | None = Field(default=None, alias="expires_in")
    refresh_expires_in: str | None = Field(default=None, alias="refresh_expires_in")
    account_id: str | None = Field(default=None, alias="account_id")
    account: str | None = Field(default=None, alias="account")
    account_platform: str | None = Field(default=None, alias="account_platform")
    country: str | None = Field(default=None)
    user_info: UserInfo | None = Field(default=None, alias="user_info")
