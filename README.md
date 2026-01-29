# Alibaba API

Python library for the [Alibaba.com Open Platform API v2](https://openapi.alibaba.com/doc/api.htm).

## Installation

```bash
# Clone repository
git clone <repo-url>
cd alibaba-v2-api

# Install with uv
uv sync --all-groups

# Or with pip
pip install -e ".[dev]"
```

## Quick Start

```python
from alibaba_api import AlibabaClient, Config

# Configure with credentials
config = Config(
    app_key="your_app_key",
    app_secret="your_app_secret",
    access_token="your_access_token",  # from OAuth flow
    use_sandbox=True,  # or False for production
)

# Make API calls
with AlibabaClient(config) as client:
    # Get product details
    product = client.get("/eco/buyer/product/description", {
        "query_req": '{"product_id": "1601206892606", "country": "US"}'
    })

    # Calculate shipping
    shipping = client.get("/shipping/freight/calculate", {
        "product_id": "1601206892606",
        "quantity": "10",
        "destination_country": "US",
        "zip_code": "90001",
    })

    # List orders
    orders = client.get("/alibaba/order/list", {
        "role": "buyer",
        "start_page": "0",
        "page_size": "10",
    })
```

## OAuth Flow

```python
from alibaba_api import AlibabaClient, Config

config = Config(
    app_key="your_app_key",
    app_secret="your_app_secret",
)

with AlibabaClient(config) as client:
    # Exchange authorization code for tokens
    tokens = client.get("/auth/token/create", {
        "code": "oauth_authorization_code"
    })

    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    # Refresh access token
    new_tokens = client.get("/auth/token/refresh", {
        "refresh_token": refresh_token
    })
```

## Configuration

| Method | Description |
|--------|-------------|
| `Config(app_key, app_secret, ...)` | Create config programmatically |
| `Config.from_env(**overrides)` | Load from environment variables |

### Environment Variables

| Variable | Description |
|----------|-------------|
| `ALIBABA_APP_KEY` | Application key (required) |
| `ALIBABA_APP_SECRET` | Application secret (required) |
| `ALIBABA_ACCESS_TOKEN` | OAuth access token |
| `ALIBABA_REFRESH_TOKEN` | OAuth refresh token |
| `ALIBABA_USE_SANDBOX` | Use sandbox environment (`true`/`false`) |

## Project Structure

```
alibaba-v2-api/
├── src/alibaba_api/
│   ├── __init__.py        # Main exports
│   ├── client.py          # AlibabaClient class
│   ├── config.py          # Configuration
│   ├── signing.py         # HMAC-SHA256 request signing
│   ├── exceptions.py      # Custom exceptions
│   └── models/            # Pydantic models
│       ├── auth.py
│       ├── product.py
│       ├── order.py
│       └── shipping.py
├── tests/
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
└── pyproject.toml
```

## Running Tests

```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests (requires credentials)
export ALIBABA_APP_KEY="your_key"
export ALIBABA_APP_SECRET="your_secret"
export ALIBABA_ACCESS_TOKEN="your_token"
pytest tests/integration/ -v -m integration
```

## Development

```bash
# Lint
uv run ruff check src/
uv run ruff format src/

# Type check
uv run mypy src/

# All tests
uv run pytest -v
```

## API Endpoints Supported

| Category | Endpoints |
|----------|-----------|
| **Auth** | `/auth/token/create`, `/auth/token/refresh` |
| **Products** | `/eco/buyer/product/check`, `/eco/buyer/product/description`, `/eco/buyer/product/inventory`, `/eco/buyer/local/product/check`, `/eco/buyer/crossborder/product/check` |
| **Shipping** | `/shipping/freight/calculate`, `/order/freight/calculate` |
| **Orders** | `/alibaba/order/list`, `/alibaba/order/get`, `/buynow/order/create`, `/alibaba/dropshipping/order/pay`, `/order/logistics/query`, `/order/logistics/tracking/get`, `/alibaba/order/fund/query` |

## License

MIT
