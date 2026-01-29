# Project Brief: Alibaba API CLI & Integration Test Suite

## Overview

A Python CLI tool and integration test suite for validating the Alibaba.com Open Platform API v2 documentation. The tool will implement all documented API endpoints to verify that real API responses match the documented examples.

## Problem Statement

The Alibaba.com Open Platform API v2 documentation exists but has not been verified against the actual API. This creates risk for anyone implementing dropshipping integration:

1. **Uncorrected documentation errors** - Field names, types, or structures may be incorrect
2. **Undocumented behaviors** - Real API may behave differently than docs suggest
3. **Missing error codes** - Error conditions may exist that aren't documented
4. **Endpoint changes** - API may have drifted from documentation

## Target User

**Primary**: Developer validating API documentation before building production dropshipping integration.

**Secondary**: QA/engineering team needing to verify API compatibility after updates.

## Success Metrics

1. **All 14+ endpoints return successful responses** when called with documented parameters
2. **Response structure matches documentation** - all documented fields are present and types are correct
3. **Error handling works** - documented error codes are returned for invalid inputs
4. **Test suite passes** - can be run reproducibly with credentials

## Core Features (MVP)

### 1. CLI Command Structure
```
alibaba-cli <endpoint> [options]

Examples:
alibaba-cli auth token create --code xxx
alibaba-cli product list --scene-id 906124611
alibaba-cli product get --product-id 1601206892606
alibaba-cli order create --channel-ref ORDER-001 --product-list '[...]'
alibaba-cli order get --trade-id 234193410001028893
```

### 2. Authentication Commands
- `auth token create` - Exchange OAuth code for access token
- `auth token refresh` - Refresh using refresh token

### 3. Product Discovery Commands
- `product list` - General product list by scene ID
- `product local` - Local warehouse products (US/MX)
- `product local-regular` - Regular local fulfillment
- `product crossborder` - Cross-border products from China
- `product get` - Get product description
- `product inventory` - Check inventory levels

### 4. Shipping Commands
- `shipping calculate` - Basic freight estimation
- `shipping calculate-advanced` - Multi-product freight calculation

### 5. Order Commands
- `order create` - Create BuyNow order
- `order pay` - Pay for order
- `order list` - List orders with filters
- `order get` - Get order details
- `order logistics` - Get logistics status
- `order tracking` - Get tracking events
- `order fund` - Get payment details

### 6. Request Signing
- HMAC-SHA256 signature calculation per documentation
- Timestamp in milliseconds
- Alphabetical parameter sorting

### 7. Environment Configuration
- Support sandbox/production toggle
- Credentials via env vars or CLI flags:
  - `ALIBABA_APP_KEY` / `--app-key`
  - `ALIBABA_APP_SECRET` / `--app-secret`
  - `ALIBABA_ACCESS_TOKEN` / `--access-token`
  - `ALIBABA_REFRESH_TOKEN` / `--refresh-token`
  - `ALIBABA_USE_SANDBOX=true` / `--sandbox`

### 8. Output Format
- JSON output for all commands (easy to compare/validate)
- Pretty-print option for human reading
- Raw output option for exact API response

## Out of Scope

1. **Persistent token storage** - No credential caching, all auth via flags/env vars
2. **Interactive OAuth flow** - No web server for OAuth, code provided manually
3. **Production features** - No retry logic, rate limiting, or advanced error recovery
4. **Webhook handling** - Not implementing webhook receiver for push notifications
5. **Database** - No data persistence
6. **Multi-user support** - Single credential set at a time

## Technical Constraints

| Constraint | Detail |
|------------|--------|
| Language | Python 3.12+ |
| CLi Framework | `click` or `typer` |
| HTTP Client | `httpx` (async support) or `requests` |
| Testing | `pytest` for integration tests |
| Output | JSON formatted responses |
| Configuration | Environment variables + CLI flags |
| Error Handling | Must handle all documented error codes |

## API Endpoints to Implement

| # | Endpoint | Purpose | Requires Access Token |
|---|----------|---------|----------------------|
| 1 | `/auth/token/create` | OAuth token exchange | No |
| 2 | `/auth/token/refresh` | Refresh token | No |
| 3 | `/eco/buyer/product/check` | Product list by scene | Yes |
| 4 | `/eco/buyer/local/product/check` | Local warehouse products | Yes |
| 5 | `/eco/buyer/localregular/product/check` | Regular local products | Yes |
| 6 | `/eco/buyer/crossborder/product/check` | Cross-border products | Yes |
| 7 | `/eco/buyer/product/description` | Product details | Yes |
| 8 | `/eco/buyer/product/inventory` | Inventory check | Yes |
| 9 | `/shipping/freight/calculate` | Basic shipping | Yes |
| 10 | `/order/freight/calculate` | Advanced shipping | Yes |
| 11 | `/buynow/order/create` | Create order | Yes |
| 12 | `/alibaba/dropshipping/order/pay` | Pay order | Yes |
| 13 | `/alibaba/order/list` | List orders | Yes |
| 14 | `/alibaba/order/get` | Order details | Yes |
| 15 | `/order/logistics/query` | Logistics status | Yes |
| 16 | `/order/logistics/tracking/get` | Tracking events | Yes |
| 17 | `/alibaba/order/fund/query` | Payment details | Yes |

## Timeline

- **Phase 1**: Project setup, request signing, auth endpoints (1 day)
- **Phase 2**: Product discovery endpoints (1 day)
- **Phase 3**: Shipping calculation endpoints (1 day)
- **Phase 4**: Order management endpoints (1-2 days)
- **Phase 5**: Integration tests and documentation validation (1 day)

## Open Questions

1. **Do you have valid test credentials?** (app_key, app_secret, OAuth code or access_token)
2. **Do you have test product IDs and trade IDs?** For validating product/order endpoints
3. **Sandbox availability?** Is the sandbox environment (`openapi-api-sandbox.alibaba.com`) accessible?
4. **Webhook verification?** Should we also implement a webhook signature verifier test?

## Dependencies

- Alibaba.com Open Platform account with API credentials
- Valid OAuth authorization code (or existing access_token)
- Test data: product IDs, trade IDs for validation
- Internet access to `openapi-api.alibaba.com`
