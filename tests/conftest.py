"""Pytest configuration and fixtures."""

import os
from collections.abc import Generator
from typing import Any

import pytest


@pytest.fixture
def test_credentials() -> dict[str, str]:
    """Test credentials from environment variables.

    Returns empty dict if credentials not set - tests should skip in this case.
    """
    return {
        "app_key": os.getenv("ALIBABA_APP_KEY", ""),
        "app_secret": os.getenv("ALIBABA_APP_SECRET", ""),
        "access_token": os.getenv("ALIBABA_ACCESS_TOKEN", ""),
        "refresh_token": os.getenv("ALIBABA_REFRESH_TOKEN", ""),
        "auth_code": os.getenv("ALIBABA_TEST_AUTH_CODE", ""),
        "use_sandbox": os.getenv("ALIBABA_USE_SANDBOX", ""),
    }


@pytest.fixture
def test_product_ids() -> dict[str, str]:
    """Test product IDs from environment variables."""
    return {
        "product_id": os.getenv("ALIBABA_TEST_PRODUCT_ID", "1601206892606"),
        "sku_id": os.getenv("ALIBABA_TEST_SKU_ID", ""),
    }


@pytest.fixture
def test_trade_ids() -> dict[str, str]:
    """Test order/trade IDs from environment variables."""
    return {
        "trade_id": os.getenv("ALIBABA_TEST_TRADE_ID", ""),
    }


@pytest.fixture
def mock_alibaba_response() -> dict[str, Any]:
    """Mock successful API response structure."""
    return {
        "code": "0",
        "request_id": "0ba2887315178178017221014",
        "result": {
            "result_code": "200",
            "result_msg": "request success",
        },
    }


def pytest_configure(config: pytest.Config) -> None:
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests requiring real credentials",
    )
    config.addinivalue_line(
        "markers",
        "unit: marks tests as unit tests (no external calls)",
    )
