# API Documentation Differences

This file tracks differences discovered between the [API documentation](alibaba-api-integration-v2.md) and the actual API behavior during implementation and testing.

---

## Format

For each difference found:
- **Date**: When discovered
- **Endpoint**: Which API endpoint
- **Documented Behavior**: What the documentation says
- **Actual Behavior**: What the API actually does
- **Impact**: Severity (Low/Medium/High)
- **Resolution**: How we handled it

---

## Differences Found

### 1. Product List Endpoints Require Additional Parameters ⚠️ IMPORTANT

**Date:** 2026-01-29 (Updated)

**Endpoints Affected:**
- `/eco/buyer/product/check`
- `/eco/buyer/local/product/check`
- `/eco/buyer/crossborder/product/check`

**Documented Behavior:**
API documentation shows pagination via `index` and `size` parameters.

**Actual Behavior:**
`page` and `page_size` are NOT supported. API uses `index` (page number) and `size` (items per page) instead.

**Resolution:**
Use correct pagination parameters:
```python
query_req = json.dumps({
    "scene_id": "906124611",
    "index": 0,        # Page number (0-based)
    "size": 50,        # Items per page
    "product_type": "common"
})
```

For local/cross-border endpoints:
```python
req = json.dumps({
    "index": 0,        # Page number (0-based)
    "size": 50,        # Items per page
    "country": "US"
})
```

**Impact:** HIGH - All product list endpoints fail without these parameters

---

### 2. Product Description Endpoint Requires Country Parameter ✅ RESOLVED

**Date:** 2026-01-29 (Updated)

**Endpoint:** `/eco/buyer/product/description`

**Documented Behavior:**
```python
query_req = json.dumps({"product_id": "1601206892606"})
response = client.get("/eco/buyer/product/description", {"query_req": query_req})
```

**Actual Behavior:**
API requires `country` parameter in the query_req. Without it, returns:
```json
{
  "result": {
    "result_msg": "Parameter format is error!",
    "result_code": "400"
  }
}
```

**Resolution:**
Add `country` parameter to query_req:
```python
query_req = json.dumps({"product_id": "1601206892606", "country": "US"})
response = client.get("/eco/buyer/product/description", {"query_req": query_req})
```

**Status:** ✅ **RESOLVED** - Adding `country` parameter fixes the issue

**Impact:** HIGH - Previously non-functional, now works with country parameter

---

### 3. New Error Code: 4016 (Freight Template Service Error)

**Date:** 2026-01-29

**Endpoint:** `/shipping/freight/calculate`

**Test Case:** Using invalid product_id or certain shipping configurations

**Documented Error:**
Documentation mentions error code `10012` for "Dispatch Location Invalid"

**Actual Error:**
```
[4016] freight template service error
```

**Status:** New error code NOT documented in the original documentation.

**Impact:** MEDIUM - Error handling should account for this code

---

### 4. Order Creation Requires `/order/freight/calculate` for vendor_code ⚠️ IMPORTANT

**Date:** 2026-01-29

**Endpoint:** `/buynow/order/create`

**Issue:** When creating orders, the `carrier_code` (vendor_code) must come from `/order/freight/calculate`, NOT `/shipping/freight/calculate`.

**Documented Behavior:**
The basic `/shipping/freight/calculate` endpoint is shown for freight calculation:
```python
response = client.get("/shipping/freight/calculate", {
    "product_id": "1601494101640",
    "quantity": "1",
    "destination_country": "US",
    "dispatch_location": "CN"
})
```

This returns a `vendor_code` but it may NOT be compatible with order creation.

**Actual Behavior:**
Order creation requires `carrier_code` from the **advanced** `/order/freight/calculate` endpoint:
```python
# First get eCompanyId from product description
product_data = client.get("/eco/buyer/product/description", ...)
e_company_id = product_data["result"]["result_data"]["eCompanyId"]

# Use advanced freight calculation for order-compatible vendor_code
freight_response = client.get("/order/freight/calculate", {
    "e_company_id": e_company_id,
    "destination_country": "US",
    "dispatch_location": "CN",
    "address": json.dumps({
        "zip": "10012",
        "country": {"code": "US", "name": "United States"},
        "province": {"code": "NY", "name": "New York"},
        "city": {"code": "", "name": "New York"},
        "address": "123 Main Street"
    }),
    "logistics_product_list": json.dumps([{
        "product_id": "1601494101640",
        "sku_id": "107089731477",
        "quantity": "1",
        "country_code": "US"
    }])
})

# Use returned vendor_code as carrier_code in order creation
carrier_code = freight_response["value"][0]["vendor_code"]  # e.g., "seller_oversea_distributor_usps"
```

**Error Code 4028:** Using incorrect `vendor_code` from basic endpoint results in:
```
[4028] order vendor code not match
```

**Resolution:** Always use `/order/freight/calculate` when preparing for order creation. This endpoint requires:
- `e_company_id` (from product description)
- Full `address` object with country/province/city as nested objects
- `logistics_product_list` array with product_id, sku_id, quantity, country_code

**Request Shape:**
```python
# GET /order/freight/calculate
{
    "e_company_id": "cVmhg7/xG8q3UQgcH/5Fag==",  # from product.eCompanyId
    "destination_country": "US",
    "dispatch_location": "CN",  # or "US", "MX"
    "address": json.dumps({
        "zip": "10012",
        "country": {"code": "US", "name": "United States"},
        "province": {"code": "NY", "name": "New York"},
        "city": {"code": "", "name": "New York"},
        "address": "123 Main Street"
    }),
    "logistics_product_list": json.dumps([{
        "product_id": "1601494101640",
        "sku_id": "107089731477",
        "quantity": "1",
        "country_code": "US"
    }])
}
```

**Response Shape:**
```json
{
  "code": "0",
  "value": [
    {
      "destination_country": "US",
      "vendor_code": "seller_oversea_distributor_sellers_shipping_method_1",
      "fee": {"amount": "3.0", "currency": "USD"},
      "shipping_type": "EXPRESS/MULTIMODAL_TRANSPORT",
      "dispatch_country": "US",
      "vendor_name": "Seller's Shipping Method 1",
      "solution_biz_type": "distributionWaybill",
      "trade_term": "DAP",
      "delivery_time": "3-9",
      "store_type": "CERTIFIED"
    }
  ],
  "request_id": "0ba2887315178178017221014"
}
```

**Key:** Use `vendor_code` as `carrier_code` in `/buynow/order/create`

**Impact:** HIGH - Order creation will fail with Error 4028 if using wrong freight endpoint

---

### 5. New Error Codes Discovered

**Date:** 2026-01-29

**Error Code 4027:** "find sku cost error"
- **Cause:** Quantity below minimum order quantity (MOQ) from ladder_price
- **Resolution:** Use quantity from the first ladder_price tier

**Error Code 4028:** "order vendor code not match"
- **Cause:** Using `vendor_code` from `/shipping/freight/calculate` instead of `/order/freight/calculate`
- **Resolution:** Use advanced freight endpoint for order creation (see #4 above)

**Error Code 130106:** "The product has expired. Please select again."
- **Cause:** Product is no longer active on Alibaba.com
- **Resolution:** Use a different active product ID

---

## Summary Statistics

| Endpoint | Status | Notes |
|----------|--------|-------|
| /auth/token/create | ✅ Works | As documented |
| /auth/token/refresh | ✅ Works | As documented |
| /eco/buyer/product/check | ⚠️ DIFFERS | Missing "size", "index", "product_type" params in docs |
| /eco/buyer/product/description | ⚠️ DIFFERS | Missing "country" param in docs |
| /eco/buyer/product/inventory | ✅ Works | As documented |
| /eco/buyer/local/product/check | ⚠️ DIFFERS | Missing "size", "index" params |
| /eco/buyer/crossborder/product/check | ⚠️ DIFFERS | Missing "size", "index" params |
| /shipping/freight/calculate | ✅ Works | Basic freight estimates, but NOT for order creation |
| /order/freight/calculate | ⚠️ CRITICAL | MUST use this endpoint for order creation vendor_code |
| /alibaba/order/list | ✅ Works | As documented |
| /alibaba/order/get | ✅ Works | As documented |
| /order/logistics/query | ✅ Works | As documented |
| /order/logistics/tracking/get | ✅ Works | As documented |
| /buynow/order/create | ⚠️ RESTRICTED | Test account limitations |

---

## Test Results Summary

**Date:** 2026-01-29 (Final)

**Unit Tests:** 29/29 PASSED ✅

**Integration Tests:** 14 passed, 4 skipped

**Passed:**
- ✅ Token refresh
- ✅ Invalid code error handling
- ✅ Order list
- ✅ Order get
- ✅ Order logistics query
- ✅ Order tracking
- ✅ Product list by scene (with added params)
- ✅ Product description (with country param)
- ✅ Product inventory
- ✅ Local product list (with added params)
- ✅ Cross-border product list (with added params)
- ✅ Basic freight calculation
- ✅ Advanced freight calculation
- ✅ Empty response handling

**Skipped (Expected):**
- ⏭️ Token create with code (no auth_code)
- ⏭️ Order pay (requires real payment)
- ⏭️ Order fund query (requires additional permissions)
- ⏭️ Order create (test account restriction)

---

## Action Items

1. ✅ **Update implementation** to add `size` and `index` parameters to all product endpoints
2. ✅ **Update implementation** to add `product_type` to `/eco/buyer/product/check`
3. ✅ **Update error codes** list with newly discovered 4016, 4027, 4028, 130106
4. ✅ **Update implementation** to add `country` parameter to product description
5. ✅ **Document test account limitation** for order creation
6. ✅ **Use `/order/freight/calculate`** for order creation (not `/shipping/freight/calculate`)

---

## Raw Response Captures

### Product Description Success Example

With `country` parameter included:
```json
{
  "result": {
    "result_msg": "request success",
    "result_data": {
      "product_id": "1601206892606",
      "title": "Sublimation Mug 40oz Stainless Steel Vacuum Insulated Tumbler...",
      "skus": [...]
    },
    "result_code": "200"
  },
  "code": "0"
}
```

### Test Account Limitation Error

Order creation with test accounts returns:
```json
{
  "code": "300000",
  "message": "The internal seller test account can only place orders to the buyer's test account..."
}
```

This is expected behavior for sandbox/test accounts.

### Order Freight Calculation Success Example

Using `/order/freight/calculate` for order creation:
```json
{
  "code": "0",
  "value": [
    {
      "destination_country": "US",
      "vendor_code": "seller_oversea_distributor_sellers_shipping_method_1",
      "fee": {
        "amount": "3.0",
        "currency": "USD"
      },
      "shipping_type": "EXPRESS/MULTIMODAL_TRANSPORT",
      "dispatch_country": "US",
      "vendor_name": "Seller's Shipping Method 1",
      "solution_biz_type": "distributionWaybill",
      "trade_term": "DAP",
      "delivery_time": "3-9",
      "store_type": "CERTIFIED"
    }
  ],
  "request_id": "0ba2887315178178017221014"
}
```

Use `vendor_code` as `carrier_code` in `/buynow/order/create` request.
