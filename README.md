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
)

with AlibabaClient(config) as client:
    # List products by scene
    products = client.list_products(scene_id="906124611", page_size=10)

    # Get product details
    product = client.get_product(product_id="1601494101640", country="US")

    # Calculate shipping cost
    freight = client.calculate_freight(
        product_id="1601494101640",
        quantity=1,
        destination_country="US",
        dispatch_location="US"
    )

    # List orders
    orders = client.list_orders(role="buyer", page_size=10)

    # Get order details
    order = client.get_order(trade_id="290711862501027597")

    # Create an order
    order = client.create_order(
        channel_refer_id="ORDER-001",
        product_list=[{"product_id": "1601494101640", "sku_id": "107089731477", "quantity": "1"}],
        logistics_detail={
            "shipment_address": {
                "zip": "10012",
                "country": "United States of America",
                "country_code": "US",
                "province": "New York",
                "province_code": "NY",
                "city": "New York",
                "address": "123 Main Street",
            },
            "dispatch_location": "US",
            "carrier_code": "seller_oversea_distributor_usps"
        }
    )
```

## High-Level API Methods

### Products

| Method | Description |
|--------|-------------|
| `list_products(scene_id, page, page_size)` | List products by scene ID |
| `get_product(product_id, country)` | Get product details |
| `get_product_inventory(product_id, sku_id)` | Check product inventory |
| `get_local_products(country, page)` | Get products from local warehouse |
| `get_crossborder_products(page)` | Get cross-border products from China |
| `search_products(scene_id, limit)` | Search products and get full details |

### Orders

| Method | Description |
|--------|-------------|
| `list_orders(role, status, page_size)` | List orders with optional filters |
| `get_order(trade_id, language)` | Get detailed order information |
| `create_order(channel_refer_id, product_list, logistics_detail)` | Create a new order |
| `pay_orders(order_id_list, payment_method)` | Pay for one or more orders |
| `get_order_logistics(trade_id)` | Get order logistics status |
| `get_order_tracking(trade_id)` | Get tracking events for an order |
| `get_order_funds(trade_id)` | Get payment and fund details |

### Shipping

| Method | Description |
|--------|-------------|
| `calculate_freight(product_id, quantity, destination_country, ...)` | Calculate basic shipping cost |
| `calculate_freight_advanced(e_company_id, destination_country, address, ...)` | Calculate shipping for multiple products with full address |

### Auth

| Method | Description |
|--------|-------------|
| `create_token(code)` | Exchange authorization code for access token |
| `refresh_token(refresh_token)` | Refresh an expired access token |

## Low-Level API

For endpoints not covered by high-level methods, use `get()` or `post()` directly:

```python
with AlibabaClient(config) as client:
    # Raw GET request
    response = client.get("/eco/buyer/product/description", {
        "query_req": '{"product_id": "1601206892606", "country": "US"}'
    })

    # Raw POST request
    response = client.post("/alibaba/order/list", {
        "role": "buyer",
        "start_page": "0",
        "page_size": "10",
    })
```

## OAuth Flow

### Step 1: Get Authorization Code

Visit the authorization URL in your browser:

```
https://openapi-auth.alibaba.com/oauth/authorize?response_type=code&client_id={YOUR_APP_KEY}&redirect_uri={YOUR_REGISTERED_CALLBACK_URL}
```

The `redirect_uri` must match the callback URL registered in your Alibaba app settings. After authorizing, copy the authorization code from the response. **Note:** Authorization codes are single-use and expire in ~30 minutes.

### Step 2: Exchange Code for Tokens

```python
from alibaba_api import AlibabaClient, Config

config = Config(
    app_key="your_app_key",
    app_secret="your_app_secret",
)

with AlibabaClient(config) as client:
    # Exchange authorization code for tokens
    tokens = client.create_token(code="your_authorization_code")

    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
```

### Step 3: Refresh Access Token

```python
# When access token expires, use the refresh token
with AlibabaClient(config) as client:
    new_tokens = client.create_token(refresh_token=refresh_token)
    access_token = new_tokens["access_token"]
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

### Setting Up `.env` File

Create a `.env` file in the project root:

```bash
# Required credentials
export ALIBABA_APP_KEY="your_app_key"
export ALIBABA_APP_SECRET="your_app_secret"
export ALIBABA_ACCESS_TOKEN="your_access_token"
export ALIBABA_REFRESH_TOKEN="your_refresh_token"

# Optional: Test data for integration tests
export ALIBABA_TEST_PRODUCT_ID="1601494101640"
export ALIBABA_TEST_SKU_ID="107089731477"
export ALIBABA_TEST_TRADE_ID="your_order_id"
export ALIBABA_TEST_AUTH_CODE="fresh_authorization_code"  # For token creation test only

# Optional: Use sandbox environment
export ALIBABA_USE_SANDBOX="false"
```

Then source it before running tests:
```bash
source .env
pytest tests/integration/ -v
```

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
# Unit tests only (no credentials required)
pytest tests/unit/ -v

# Integration tests (requires credentials)
source .env
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
