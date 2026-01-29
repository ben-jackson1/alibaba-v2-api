"""Custom exceptions for Alibaba API."""


class AlibabaError(Exception):
    """Base exception for all Alibaba API errors."""

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        request_id: str | None = None,
    ) -> None:
        self.message = message
        self.code = code
        self.request_id = request_id
        super().__init__(message)


class AlibabaAPIError(AlibabaError):
    """Exception raised when the API returns an error response."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        request_id: str | None = None,
        sub_code: str | None = None,
    ) -> None:
        self.sub_code = sub_code
        super().__init__(message, code=code, request_id=request_id)

    def __str__(self) -> str:
        if self.sub_code:
            return f"[{self.code}:{self.sub_code}] {self.message}"
        return f"[{self.code}] {self.message}"


class AlibabaAuthError(AlibabaError):
    """Exception raised for authentication/authorization failures."""


class AlibabaValidationError(AlibabaError):
    """Exception raised for request validation failures."""


class AlibabaSignatureError(AlibabaError):
    """Exception raised for signature calculation errors."""


class AlibabaNetworkError(AlibabaError):
    """Exception raised for network/HTTP errors."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        request_id: str | None = None,
    ) -> None:
        self.status_code = status_code
        super().__init__(message, request_id=request_id)
