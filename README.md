# Alibaba API CLI

CLI tool and integration test suite for validating the [Alibaba.com Open Platform API v2](https://openapi.alibaba.com/doc/api.htm) documentation.

## Purpose

This tool exists to validate that the Alibaba API documentation at `/docs/alibaba-api-integration-v2.md` accurately reflects the actual API behavior. It implements all documented endpoints as CLI commands and includes an integration test suite.

## Installation

```bash
# Clone repository
git clone <repo-url>
cd alibaba-v2-api

# Install in development mode
pip install -e ".[dev]"

# Verify installation
alibaba-cli --version
```

## Quick Start

### 1. Set Credentials

```bash
export ALIBABA_APP_KEY="your_app_key"
export ALIBABA_APP_SECRET="your_app_secret"
```

### 2. Get OAuth Token

First, visit the authorization URL in your browser:

```
https://openapi-auth.alibaba.com/oauth/authorize?response_type=code&client_id={app_key}&redirect_uri={callback_url}
```

Then exchange the code for a token:

```bash
alibaba-cli auth token create --code "your_oauth_code"
```

Save the `access_token` and `refresh_token` for subsequent calls:

```bash
export ALIBABA_ACCESS_TOKEN="your_access_token"
export ALIBABA_REFRESH_TOKEN="your_refresh_token"
```

### 3. Make API Calls

```bash
# List products
alibaba-cli product list --scene-id 906124611 --page 0 --page-size 10

# Get product details
alibaba-cli product get --product-id 1601206892606

# Calculate shipping
alibaba-cli shipping calculate \
  --product-id 1601206892606 \
  --quantity 10 \
  --destination-country US
```

## CLI Commands

### Authentication

| Command | Description |
|---------|-------------|
| `auth token create --code <code>` | Exchange OAuth code for access token |
| `auth token refresh --refresh-token <token>` | Refresh access token |
| `auth status` | Check credential configuration |

### Products

| Command | Description |
|---------|-------------|
| `product list --scene-id <id>` | Get product list by scene ID |
| `product local --country <code>` | Get local warehouse products |
| `product crossborder` | Get cross-border products |
| `product get --product-id <id>` | Get product details |
| `product inventory --product-id <id>` | Check inventory |

### Shipping

| Command | Description |
|---------|-------------|
| `shipping calculate` | Basic freight estimation |
| `shipping calculate-advanced` | Multi-product freight calculation |

### Orders

| Command | Description |
|---------|-------------|
| `order create` | Create BuyNow order |
| `order pay` | Pay for order |
| `order list` | List orders |
| `order get --trade-id <id>` | Get order details |
| `order logistics --trade-id <id>` | Get logistics status |
| `order tracking --trade-id <id>` | Get tracking events |

## Global Options

| Flag | Environment Variable | Description |
|------|---------------------|-------------|
| `--app-key` | `ALIBABA_APP_KEY` | Application key |
| `--app-secret` | `ALIBABA_APP_SECRET` | Application secret |
| `--access-token` | `ALIBABA_ACCESS_TOKEN` | OAuth access token |
| `--refresh-token` | `ALIBABA_REFRESH_TOKEN` | OAuth refresh token |
| `--sandbox` | `ALIBABA_USE_SANDBOX` | Use sandbox environment |
| `--json` | - | Formatted JSON output (default) |
| `--raw` | - | Raw API response |
| `--verbose` | - | Debug output |

## Running Integration Tests

```bash
# Set credentials
export ALIBABA_APP_KEY="test_key"
export ALIBABA_APP_SECRET="test_secret"
export ALIBABA_ACCESS_TOKEN="test_token"

# Run all integration tests
pytest tests/integration/ -v -m integration

# Run specific test file
pytest tests/integration/test_auth.py -v
```

## Development

```bash
# Run linting
ruff check src/
ruff format src/

# Run type checking
mypy src/

# Run unit tests
pytest tests/ -v
```

## Project Structure

```
alibaba-v2-api/
├── src/alibaba_cli/
│   ├── __init__.py
│   ├── cli.py              # Main entry point
│   ├── client.py           # API client
│   ├── signing.py          # Request signing
│   ├── config.py           # Configuration
│   ├── exceptions.py       # Exceptions
│   ├── models/             # Pydantic models
│   └── commands/           # CLI commands
├── tests/
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
├── docs/
│   └── alibaba-api-integration-v2.md
├── specs/                  # PRD and stories
└── pyproject.toml
```

## API Endpoints Implemented

| # | Endpoint | CLI Command |
|---|----------|-------------|
| 1 | `/auth/token/create` | `auth token create` |
| 2 | `/auth/token/refresh` | `auth token refresh` |
| 3 | `/eco/buyer/product/check` | `product list` |
| 4 | `/eco/buyer/local/product/check` | `product local` |
| 5 | `/eco/buyer/localregular/product/check` | `product local-regular` |
| 6 | `/eco/buyer/crossborder/product/check` | `product crossborder` |
| 7 | `/eco/buyer/product/description` | `product get` |
| 8 | `/eco/buyer/product/inventory` | `product inventory` |
| 9 | `/shipping/freight/calculate` | `shipping calculate` |
| 10 | `/order/freight/calculate` | `shipping calculate-advanced` |
| 11 | `/buynow/order/create` | `order create` |
| 12 | `/alibaba/dropshipping/order/pay` | `order pay` |
| 13 | `/alibaba/order/list` | `order list` |
| 14 | `/alibaba/order/get` | `order get` |
| 15 | `/order/logistics/query` | `order logistics` |
| 16 | `/order/logistics/tracking/get` | `order tracking` |
| 17 | `/alibaba/order/fund/query` | `order fund` |

## License

MIT
