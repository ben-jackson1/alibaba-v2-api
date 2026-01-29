# Product Requirements Document: Alibaba API CLI & Integration Test Suite

## Executive Summary

This document defines requirements for a Python CLI tool that implements all Alibaba.com Open Platform API v2 endpoints for documentation validation. The tool will make real API calls and compare responses against documented examples to identify discrepancies, missing fields, incorrect types, and undocumented behaviors.

**Project Status**: Requirements Definition
**Version**: 1.0
**Date**: 2026-01-29

---

## Problem Statement

The Alibaba.com Open Platform API v2 documentation exists at `/docs/alibaba-api-integration-v2.md` but has not been validated against the live API. This presents significant risks for developers implementing dropshipping integrations:

1. **Incorrect Documentation** - Field names, data types, or structures may be wrong
2. **Undocumented Behaviors** - API may behave differently than documentation suggests
3. **Missing Error Cases** - Error codes and conditions may not be fully documented
4. **API Drift** - The live API may have changed since documentation was written

Without validation, developers risk:
- Wasted development time implementing against incorrect specs
- Production issues when real API responses don't match expectations
- Delayed integrations while debugging undocumented behaviors

## Goals & Success Metrics

### Primary Goals

1. **API Endpoint Coverage** - Implement all 17 documented endpoints as CLI commands
2. **Request Validation** - Verify request signing, parameters, and endpoints work as documented
3. **Response Validation** - Compare actual API responses against documented examples
4. **Error Handling** - Verify all documented error codes are returned correctly

### Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Endpoint Coverage | 100% | All 17 endpoints implemented and tested |
| Documentation Accuracy | 100% | All documented fields verified present in actual responses |
| Test Pass Rate | 100% | All integration tests pass with valid credentials |
| Response Time | < 5 seconds per call | CLI commands return within 5 seconds |

---

## User Personas

### Primary: API Integration Developer

**Profile**: Developer building dropshipping integration with Alibaba.com

**Goals**:
- Verify API documentation before starting implementation
- Test API calls with real data
- Understand actual response structures
- Identify any discrepancies between docs and reality

**Pain Points**:
- Uncertain if documentation is accurate
- Risk of building on incorrect assumptions
- Time wasted debugging undocumented behaviors

### Secondary: QA Engineer

**Profile**: Quality assurance validating API compatibility

**Goals**:
- Regression test API changes
- Verify new API versions
- Document any breaking changes

---

## Functional Requirements

### FR1: CLI Command Structure

**Description**: The tool must provide a command-line interface with subcommands for each API endpoint.

**User Story**: As a developer, I want to run API calls from the CLI so that I can quickly test endpoints without writing code.

**Priority**: P0

**Acceptance Criteria**:
- [ ] CLI entry point is `alibaba-cli`
- [ ] Each API endpoint has a corresponding subcommand
- [ ] Global flags for credentials: `--app-key`, `--app-secret`, `--access-token`, `--refresh-token`
- [ ] Environment variable support for all credentials
- [ ] `--sandbox` flag to toggle between sandbox and production
- [ ] `--json` flag for formatted output (default), `--raw` for exact API response
- [ ] `--help` flag shows usage for all commands

### FR2: OAuth Token Management

**Description**: Implement OAuth token creation and refresh endpoints.

**User Story**: As a developer, I want to exchange OAuth codes for access tokens so that I can authenticate API calls.

**Priority**: P0

**Acceptance Criteria**:
- [ ] `auth token create` command exchanges OAuth code for access token
- [ ] `auth token refresh` command refreshes using refresh token
- [ ] Token response includes: access_token, refresh_token, expires_in, refresh_expires_in, user_info
- [ ] Commands accept `--code` or `--refresh-token` parameter
- [ ] Token endpoints do NOT require access_token (they are unauthenticated)

### FR3: Product Discovery Endpoints

**Description**: Implement all product listing and detail endpoints.

**User Story**: As a developer, I want to search and retrieve product information so that I can validate product-related API behavior.

**Priority**: P0

**Acceptance Criteria**:
- [ ] `product list` --scene-id <id> --page <n> --page-size <n>
- [ ] `product local` --country <code> --page <n> --page-size <n>
- [ ] `product local-regular` --page <n> --page-size <n>
- [ ] `product crossborder` --page <n> --page-size <n>
- [ ] `product get` --product-id <id>
- [ ] `product inventory` --product-id <id> [--sku-id <id>] [--shipping-from <code>]
- [ ] All endpoints require valid access_token
- [ ] Product list commands return array of product IDs
- [ ] Product detail returns full product info including SKUs, images, pricing

### FR4: Shipping Calculation Endpoints

**Description**: Implement basic and advanced freight calculation endpoints.

**User Story**: As a developer, I want to calculate shipping costs so that I can validate shipping API behavior and response structures.

**Priority**: P0

**Acceptance Criteria**:
- [ ] `shipping calculate` --product-id <id> --quantity <n> --destination-country <code> [--zip-code <zip>] [--dispatch-location <code>]
- [ ] `shipping calculate-advanced` --e-company-id <id> --address <json> --logistics-product-list <json> --destination-country <code>
- [ ] Basic calculation returns: shipping_type, vendor_name, delivery_time, fee (amount, currency)
- [ ] Advanced calculation accepts multiple products and full address
- [ ] Support for CN, US, MX dispatch locations
- [ ] Handle empty results when route unavailable

### FR5: Order Management Endpoints

**Description**: Implement order creation, payment, listing, and detail endpoints.

**User Story**: As a developer, I want to create and query orders so that I can validate the complete order flow API behavior.

**Priority**: P0

**Acceptance Criteria**:
- [ ] `order create` --channel-refer-id <id> --product-list <json> --logistics-detail <json> [--remark <text>]
- [ ] `order pay` --order-id-list <json> --payment-method <method> --user-ip <ip> --user-agent <ua>
- [ ] `order list` --role <buyer|seller> [--status <status>] [--start-page <n>] [--page-size <n>]
- [ ] `order get` --trade-id <id> [--language <code>]
- [ ] `order logistics` --trade-id <id> [--data-select <select>]
- [ ] `order tracking` --trade-id <id>
- [ ] `order fund` --trade-id <id> [--data-select <select>]
- [ ] Order create returns trade_id and pay_url
- [ ] Order pay returns status (PAY_SUCCESS or PAY_FAILED with pay_url)
- [ ] Order get returns full order details including products, amounts, addresses

### FR6: Request Signing

**Description**: Implement HMAC-SHA256 request signing per Alibaba specification.

**User Story**: As a developer, I want requests to be properly signed so that the API accepts them.

**Priority**: P0

**Acceptance Criteria**:
- [ ] All requests include app_key, sign_method=sha256, timestamp (milliseconds)
- [ ] Parameters sorted alphabetically before concatenation
- [ ] Message = api_path + concat_string
- [ ] HMAC-SHA256 signature using app_secret
- [ ] Signature converted to uppercase hex
- [ ] access_token included in signed params when required

### FR7: Error Handling

**Description**: Handle all documented error codes with helpful messages.

**User Story**: As a developer, I want clear error messages when API calls fail so that I can understand what went wrong.

**Priority**: P1

**Acceptance Criteria**:
- [ ] Parse error code and sub_code from API responses
- [ ] Display error message from API
- [ ] Map known error codes to helpful descriptions
- [ ] Include request_id in error output for debugging
- [ ] Handle network errors gracefully
- [ ] Non-zero exit code on API errors

### FR8: Integration Test Suite

**Description**: Automated tests that call all endpoints and validate responses against documentation.

**User Story**: As a developer, I want to run automated tests so that I can verify all documentation is accurate without manual CLI usage.

**Priority**: P0

**Acceptance Criteria**:
- [ ] pytest test suite with fixtures for credentials
- [ ] Test for each endpoint group (auth, products, shipping, orders)
- [ ] Tests validate response structure matches documentation
- [ ] Tests validate required fields are present
- [ ] Tests validate field types where documented
- [ ] Tests are marked as integration tests (require real credentials)
- [ ] Test results show which endpoints passed/failed validation

---

## Non-Functional Requirements

### NFR1: Performance

| Requirement | Target |
|-------------|--------|
| CLI startup time | < 100ms |
| API response handling | < 5 seconds per call |
| Test suite execution | < 60 seconds for all tests |

### NFR2: Security

| Requirement | Specification |
|-------------|---------------|
| Credential handling | Read-only, never log credentials |
| Token storage | No persistent storage (design choice) |
| HTTPS only | All API calls over HTTPS |
| Error messages | Never expose secrets in error output |

### NFR3: Compatibility

| Requirement | Specification |
|-------------|---------------|
| Python version | 3.12+ |
| Operating systems | Linux, macOS, Windows (via WSL or native) |
| Dependencies | Minimal, well-maintained packages |

### NFR4: Maintainability

| Requirement | Specification |
|-------------|---------------|
| Test coverage | > 80% for non-API code |
| Documentation | README with usage examples |
| Code style | Follow PEP 8, use ruff for linting |
| Type hints | Required on all public functions |

---

## Epic Breakdown

### Epic 1: Project Setup & Core Infrastructure
**Goal**: Establish project structure, dependencies, and request signing foundation
**FRs Included**: FR1, FR6
**Stories**: 4 stories
**Estimate**: M

### Epic 2: Authentication Endpoints
**Goal**: Implement OAuth token creation and refresh
**FRs Included**: FR2
**Stories**: 3 stories
**Estimate**: M
**Blocked By**: Epic 1

### Epic 3: Product Discovery Endpoints
**Goal**: Implement all product listing and detail endpoints
**FRs Included**: FR3
**Stories**: 5 stories
**Estimate**: L
**Blocked By**: Epic 1, Epic 2

### Epic 4: Shipping Calculation Endpoints
**Goal**: Implement basic and advanced freight calculation
**FRs Included**: FR4
**Stories**: 3 stories
**Estimate**: M
**Blocked By**: Epic 1

### Epic 5: Order Management Endpoints
**Goal**: Implement order creation, payment, and query endpoints
**FRs Included**: FR5
**Stories**: 6 stories
**Estimate**: L
**Blocked By**: Epic 1, Epic 2

### Epic 6: Integration Test Suite
**Goal**: Automated tests validating all endpoints against documentation
**FRs Included**: FR7, FR8
**Stories**: 4 stories
**Estimate**: M
**Blocked By**: Epic 2, Epic 3, Epic 4, Epic 5

**Total**: 25 stories across 6 epics

---

## User Flows

### Flow 1: First-Time Setup

```bash
# 1. Set credentials as environment variables
export ALIBABA_APP_KEY="your_app_key"
export ALIBABA_APP_SECRET="your_app_secret"

# 2. Get OAuth code (manual browser flow)
# User visits: https://openapi-auth.alibaba.com/oauth/authorize?...

# 3. Exchange code for access token
alibaba-cli auth token create --code "3_500102_JxZ05Ux3cnnSSUm6dCxYg6Q26"

# 4. Save access_token and refresh_token for subsequent calls
export ALIBABA_ACCESS_TOKEN="..."
export ALIBABA_REFRESH_TOKEN="..."
```

### Flow 2: Product Discovery Validation

```bash
# 1. Get product list from a scene
alibaba-cli product list --scene-id 906124611 --page 0 --page-size 10

# 2. Get details for a specific product
alibaba-cli product get --product-id 1601206892606

# 3. Check inventory
alibaba-cli product inventory --product-id 1601206892606 --shipping-from CN

# 4. Calculate shipping
alibaba-cli shipping calculate \
  --product-id 1601206892606 \
  --quantity 10 \
  --destination-country US \
  --zip-code 90001 \
  --dispatch-location CN
```

### Flow 3: Order Flow Validation

```bash
# 1. Calculate shipping for order
alibaba-cli shipping calculate-advanced \
  --e-company-id "cVmhg7/xG8q3UQgcH/5Fag==" \
  --destination-country US \
  --address '{"zip":"10012","country":"United States",...}' \
  --logistics-product-list '[{"product_id":"1600191825486","sku_id":"12321","quantity":"1"}]'

# 2. Create order
alibaba-cli order create \
  --channel-refer-id "TEST-ORDER-001" \
  --product-list '[...]' \
  --logistics-detail '{...}'

# 3. Pay for order
alibaba-cli order pay \
  --order-id-list '["234193410001028893"]' \
  --payment-method CREDIT_CARD \
  --user-ip "192.168.1.1" \
  --user-agent "Mozilla/5.0..."

# 4. Check order status
alibaba-cli order get --trade-id 234193410001028893

# 5. Get tracking
alibaba-cli order tracking --trade-id 234193410001028893
```

### Flow 4: Running Integration Tests

```bash
# 1. Set credentials
export ALIBABA_APP_KEY="test_key"
export ALIBABA_APP_SECRET="test_secret"
export ALIBABA_ACCESS_TOKEN="test_token"

# 2. Run all integration tests
pytest tests/integration/ -v

# 3. Run specific endpoint tests
pytest tests/integration/test_products.py -v

# 4. Run with output showing validation results
pytest tests/integration/ -v --tb=short
```

---

## Risks & Assumptions

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Sandbox environment unavailable | High | Document production-only testing requirements |
| API rate limiting | Medium | Implement delays between test calls |
| OAuth flow complexity | Medium | Provide clear documentation of manual flow |
| API changes during development | Low | Document API version tested |

### Assumptions

| Assumption | Validation |
|------------|------------|
| User has valid Alibaba app credentials | User confirmation required |
| User can complete OAuth flow manually | Document OAuth URL construction |
| Sandbox API mirrors production | Test in both environments |
| Product/order IDs available for testing | Use product list to discover IDs |

---

## Out of Scope

The following features are explicitly **NOT** included in v1:

1. **Persistent credential storage** - No token caching, all auth via flags/env vars
2. **Interactive OAuth flow** - No built-in web server for OAuth callback
3. **Production-ready features**:
   - No automatic retry logic
   - No rate limiting handling
   - No advanced error recovery
4. **Webhook receiver** - Not implementing push notification handler
5. **Database or state management** - Stateless CLI only
6. **Multi-user management** - Single credential set at a time
7. **Batch operations** - One API call per command execution
8. **Configuration file** - Environment variables and flags only

---

## Appendix A: Endpoint Reference

| # | CLI Command | API Endpoint | Access Token Required |
|---|-------------|--------------|----------------------|
| 1 | `auth token create` | `/auth/token/create` | No |
| 2 | `auth token refresh` | `/auth/token/refresh` | No |
| 3 | `product list` | `/eco/buyer/product/check` | Yes |
| 4 | `product local` | `/eco/buyer/local/product/check` | Yes |
| 5 | `product local-regular` | `/eco/buyer/localregular/product/check` | Yes |
| 6 | `product crossborder` | `/eco/buyer/crossborder/product/check` | Yes |
| 7 | `product get` | `/eco/buyer/product/description` | Yes |
| 8 | `product inventory` | `/eco/buyer/product/inventory` | Yes |
| 9 | `shipping calculate` | `/shipping/freight/calculate` | Yes |
| 10 | `shipping calculate-advanced` | `/order/freight/calculate` | Yes |
| 11 | `order create` | `/buynow/order/create` | Yes |
| 12 | `order pay` | `/alibaba/dropshipping/order/pay` | Yes |
| 13 | `order list` | `/alibaba/order/list` | Yes |
| 14 | `order get` | `/alibaba/order/get` | Yes |
| 15 | `order logistics` | `/order/logistics/query` | Yes |
| 16 | `order tracking` | `/order/logistics/tracking/get` | Yes |
| 17 | `order fund` | `/alibaba/order/fund/query` | Yes |

---

## Appendix B: Document History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2026-01-29 | 1.0 | Initial PRD | Claude (BMAD) |
