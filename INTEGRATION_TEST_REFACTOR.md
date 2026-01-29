# Integration Test Refactor: High-Level API Coverage

## Goal

Update integration tests to use high-level wrapper methods while retaining low-level smoke tests for API baseline verification.

## Problem Statement

Current integration tests use low-level `client.get(path, params)` directly. The new high-level wrapper methods (`get_product()`, `list_orders()`, etc.) are untested, so bugs in the wrapper layer would go undetected.

## Solution: Hybrid Approach

```
tests/integration/
├── test_low_level.py      # NEW: 2-3 smoke tests for core API
├── test_products.py       # UPDATED: Use high-level methods
├── test_orders.py         # UPDATED: Use high-level methods
├── test_shipping.py       # UPDATED: Use high-level methods
└── test_auth.py           # UPDATED: Use high-level methods
```

**Why hybrid?**
- Low-level smoke tests confirm the API works at all
- High-level tests verify wrappers work correctly
- If high-level fails but low-level passes → wrapper bug
- If both fail → API problem

---

## Implementation Plan

### Phase 1: Create Low-Level Smoke Tests ✅
**File:** `tests/integration/test_low_level.py`

| Test | Purpose |
|------|---------|
| `test_get_endpoint_works` | Verify GET requests, signing, response parsing |
| `test_post_endpoint_works` | Verify POST requests work |
| `test_error_handling_works` | Verify API errors are properly raised |
| `test_signing_headers_present` | Verify request signing is applied |

### Phase 2: Update Product Tests ✅
**File:** `tests/integration/test_products.py`

| Current | Updated To |
|---------|------------|
| `client.get("/eco/buyer/product/check", ...)` | `client.list_products(scene_id=...)` |
| `client.get("/eco/buyer/product/description", ...)` | `client.get_product(product_id=...)` |
| `client.get("/eco/buyer/product/inventory", ...)` | `client.get_product_inventory(...)` |
| `client.get("/eco/buyer/local/product/check", ...)` | `client.get_local_products(...)` |
| `client.get("/eco/buyer/crossborder/product/check", ...)` | `client.get_crossborder_products(...)` |

### Phase 3: Update Order Tests ✅
**File:** `tests/integration/test_orders.py`

| Current | Updated To |
|---------|------------|
| `client.get("/alibaba/order/list", ...)` | `client.list_orders(...)` |
| `client.get("/alibaba/order/get", ...)` | `client.get_order(trade_id=...)` |
| `client.post("/buynow/order/create", ...)` | `client.create_order(...)` |
| `client.post("/alibaba/dropshipping/order/pay", ...)` | `client.pay_orders(...)` |
| `client.get("/order/logistics/query", ...)` | `client.get_order_logistics(...)` |
| `client.get("/order/logistics/tracking/get", ...)` | `client.get_order_tracking(...)` |
| `client.get("/alibaba/order/fund/query", ...)` | `client.get_order_funds(...)` |

### Phase 4: Update Shipping Tests ✅
**File:** `tests/integration/test_shipping.py`

| Current | Updated To |
|---------|------------|
| `client.get("/shipping/freight/calculate", ...)` | `client.calculate_freight(...)` |
| `client.get("/order/freight/calculate", ...)` | `client.calculate_freight_advanced(...)` |

### Phase 5: Update Auth Tests ✅
**File:** `tests/integration/test_auth.py`

| Current | Updated To |
|---------|------------|
| `client.get("/auth/token/create", ...)` | `client.create_token(code=...)` |
| `client.get("/auth/token/refresh", ...)` | `client.refresh_token(...)` |

---

## Acceptance Criteria

### Must Have ✅
- [x] `tests/integration/test_low_level.py` exists with 2-3 smoke tests
- [x] All product tests use `client.list_products()`, `client.get_product()`, etc.
- [x] All order tests use `client.list_orders()`, `client.get_order()`, etc.
- [x] All shipping tests use `client.calculate_freight()`, etc.
- [x] All auth tests use `client.create_token()`, `client.refresh_token()`
- [x] No hardcoded endpoint paths in updated test files
- [x] All integration tests still pass with real API credentials
- [x] `uv run pytest tests/integration/ -v` succeeds
- [x] `uv run ruff check tests/integration/` passes

### Should Have ✅
- [x] Tests assert on meaningful response data (not just `_raw`)
- [x] Test comments/docstrings show high-level usage
- [x] Parameter names in tests match high-level method signatures

### Nice to Have ✅
- [x] Add a test demonstrating the `search_products()` convenience method
- [x] Add a test for `auth_status` property
- [ ] Update README examples to match test patterns

---

## Test Conversion Example

### Before
```python
def test_get_product_description(client, product_id):
    response = client.get(
        "/eco/buyer/product/description",
        {"query_req": json.dumps({
            "product_id": int(product_id),
            "country": "US"
        })}
    )
    assert "result" in response
    result_data = response.get("result", {}).get("result_data", {})
    assert result_data.get("subject") is not None
```

### After
```python
def test_get_product(client, product_id):
    """Test getting product details using high-level API."""
    product = client.get_product(product_id=product_id, country="US")

    # Assert on meaningful data, not wrapper internals
    assert product.get("subject") is not None
    assert product.get("productId") == product_id
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Wrapper has bug, test fails | Low-level smoke test still passes → isolates to wrapper |
| API changes break tests | Same risk as before; wrappers don't increase exposure |
| Loss of low-level coverage | Keep dedicated smoke test file |
| Tests take longer | Same number of API calls, just different entry point |

---

## Success Metrics ✅

- **Coverage:** All high-level methods have at least one integration test
- **Reliability:** Tests pass consistently with valid credentials
- **Usability:** Test code demonstrates intended library usage
- **Debuggability:** Failures clearly indicate wrapper vs API issues

---

## Estimated Effort

| Phase | Time | Actual |
|-------|------|--------|
| Phase 1: Smoke tests | 30 min | ✅ |
| Phase 2: Product tests | 1 hour | ✅ |
| Phase 3: Order tests | 1 hour | ✅ |
| Phase 4: Shipping tests | 30 min | ✅ |
| Phase 5: Auth tests | 30 min | ✅ |
| Verification & cleanup | 30 min | ✅ |

**Total: ~4 hours** ✅ COMPLETED
