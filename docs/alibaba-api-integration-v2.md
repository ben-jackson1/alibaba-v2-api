# Alibaba API Integration Guide V2

This document provides a comprehensive guide for implementing the new Alibaba.com Open Platform API integration for dropshipping operations.

> **Migration Note:** This document covers the new Alibaba.com Open Platform APIs which replace the legacy Taobao Open Platform (TOP) integration. See [Endpoint Mapping](#endpoint-mapping) for migration guidance.

---

## Table of Contents

1. [Overview](#overview)
2. [Base URLs](#base-urls)
3. [API Credentials](#api-credentials)
4. [Authentication](#authentication)
5. [Request Signing](#request-signing)
6. [API Endpoints](#api-endpoints)
   - [Token Management](#1-generate-access-token)
   - [Product APIs](#3-product-list)
   - [Shipping APIs](#6-basic-freight-cost-estimation)
   - [Order APIs](#8-create-buynow-order)
   - [Logistics APIs](#12-logistics-tracking)
7. [Error Handling](#error-handling)
8. [Push Notifications (Webhooks)](#push-notifications-webhooks)
9. [Endpoint Mapping](#endpoint-mapping)

---

## Overview

The new Alibaba.com Open Platform enables:
- **Product Discovery**: Search and retrieve product listings from dropshipping-eligible catalogs
- **Product Details**: Fetch product details, variants, pricing, and images
- **Inventory Check**: Verify product availability and stock levels
- **Shipping Calculation**: Get shipping costs and delivery estimates
- **Order Creation**: Place dropshipping orders on Alibaba.com
- **Order Payment**: Process payments for orders
- **Order Management**: Query order details and status
- **Order Tracking**: Get logistics and tracking information
- **Real-time Notifications**: Receive order and product updates via webhooks

### Official Documentation

| Portal | URL | Description |
|--------|-----|-------------|
| Alibaba Open Platform | https://openapi.alibaba.com/doc/doc.htm | Main documentation portal |
| API Reference | https://openapi.alibaba.com/doc/api.htm | Complete API documentation |
| Dropshipping Guide | https://openapi.alibaba.com/doc/doc.htm#/?docId=125 | Dropshipping partner integration guide |
| Order Status/FAQ | https://openapi.alibaba.com/doc/doc.htm#/?docId=131 | Order API error codes and FAQ |

---

## Base URLs

| Environment | URL | Usage |
|-------------|-----|-------|
| **Production API** | `https://openapi-api.alibaba.com/rest` | All production API calls |
| **Sandbox API** | `https://openapi-api-sandbox.alibaba.com/rest` | Testing environment |
| **OAuth Authorization** | `https://openapi-auth.alibaba.com/oauth/authorize` | User authorization page |

### URL Construction

API calls are constructed as:
```
https://openapi-api.alibaba.com/rest{api_path}?{query_parameters}
```

Example:
```
https://openapi-api.alibaba.com/rest/auth/token/create?app_key=12345678&code=xxx&timestamp=1517820392000&sign_method=sha256&sign=XXX
```

---

## API Credentials

### Required Settings

```python
# Application credentials (shared across all users)
ALIBABA_APP_KEY = "your_app_key"
ALIBABA_APP_SECRET = "your_app_secret"

# Optional: Toggle between sandbox and production
ALIBABA_USE_SANDBOX = False  # Set to True for sandbox testing
```

### User-Specific Tokens

Store these per user in your database:

```python
class AlibabaAccount(Model):
    user = ForeignKey(User)
    access_token = TextField()             # OAuth access token
    refresh_token = TextField()            # For refreshing access token
    access_token_expires_at = DateTimeField()   # Access token expiration
    refresh_token_expires_at = DateTimeField()  # Refresh token expiration
    alibaba_user_id = CharField()          # Alibaba user ID (user_id from token)
    havana_id = CharField()                # Havana ID (for migrated users)
    account_platform = CharField()         # e.g., "buyApp"
```

---

## Authentication

### Token Types

| Token Type | Scope | Expiration | Notes |
|------------|-------|------------|-------|
| `access_token` | Per-user API calls | ~10 days (configurable) | Required for most API calls |
| `refresh_token` | Token refresh only | ~60 days | Used to get new access_token |

### OAuth Flow

```
┌─────────────┐      ┌──────────────────────────┐      ┌─────────────────┐
│   Buyer     │      │   Your Application       │      │   Alibaba.com   │
└──────┬──────┘      └────────────┬─────────────┘      └────────┬────────┘
       │                          │                             │
       │  1. Click "Connect"      │                             │
       │─────────────────────────>│                             │
       │                          │                             │
       │  2. Redirect to Alibaba  │                             │
       │<─────────────────────────│                             │
       │                          │                             │
       │  3. User logs in & authorizes                          │
       │─────────────────────────────────────────────────────────>
       │                          │                             │
       │  4. Redirect with code   │                             │
       │<─────────────────────────────────────────────────────────
       │                          │                             │
       │                          │  5. Exchange code for token │
       │                          │────────────────────────────>│
       │                          │                             │
       │                          │  6. Return access_token     │
       │                          │<────────────────────────────│
       │                          │                             │
       │  7. Connection complete  │                             │
       │<─────────────────────────│                             │
```

**Step 1-2: Authorization URL**

```
https://openapi-auth.alibaba.com/oauth/authorize?response_type=code&redirect_uri={callback_url}&client_id={app_key}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `response_type` | Yes | Must be `code` |
| `client_id` | Yes | Your application's App Key |
| `redirect_uri` | Yes | URL-encoded callback URL registered with your app |

> **Important:** The authorization code returned expires within 30 minutes. Exchange it for an access token promptly.

---

## Request Signing

All API requests must be signed using HMAC-SHA256.

### Signature Algorithm

```python
import hmac
import hashlib
import time
import urllib.parse

def calculate_signature(api_path: str, params: dict, app_secret: str) -> str:
    """
    Generate HMAC-SHA256 signature for Alibaba API requests.
    
    Args:
        api_path: The API endpoint path (e.g., "/auth/token/create")
        params: Dictionary of all request parameters (excluding 'sign')
        app_secret: Your application's secret key
    
    Returns:
        Uppercase hex string of the signature
    """
    # 1. Sort parameters alphabetically by key (ASCII order)
    sorted_params = dict(sorted(params.items()))
    
    # 2. Concatenate key-value pairs
    concat_string = ''.join(f"{k}{v}" for k, v in sorted_params.items())
    
    # 3. Prepend API path
    message = f"{api_path}{concat_string}"
    
    # 4. Generate HMAC-SHA256 signature
    signature = hmac.new(
        app_secret.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest().upper()
    
    return signature


def make_api_request(
    api_path: str,
    params: dict,
    app_key: str,
    app_secret: str,
    access_token: str = None,
    method: str = "GET"
) -> dict:
    """
    Make a signed request to the Alibaba API.
    
    Args:
        api_path: The API endpoint path (e.g., "/eco/buyer/product/description")
        params: Business parameters for the API
        app_key: Your application key
        app_secret: Your application secret
        access_token: User's access token (required for most APIs)
        method: HTTP method (GET or POST)
    
    Returns:
        JSON response from the API
    """
    import requests
    
    # Build system parameters
    system_params = {
        'app_key': app_key,
        'sign_method': 'sha256',
        'timestamp': str(int(time.time() * 1000)),  # Milliseconds
    }
    
    if access_token:
        system_params['access_token'] = access_token
    
    # Merge with business parameters
    all_params = {**system_params, **params}
    
    # Generate signature
    all_params['sign'] = calculate_signature(api_path, all_params, app_secret)
    
    # Build URL
    base_url = "https://openapi-api.alibaba.com/rest"
    url = f"{base_url}{api_path}"
    
    # Make request
    if method.upper() == "GET":
        response = requests.get(url, params=all_params, timeout=30)
    else:
        response = requests.post(url, data=all_params, timeout=30)
    
    return response.json()
```

### System Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `app_key` | Yes | Your application's App Key |
| `sign_method` | Yes | Must be `sha256` |
| `timestamp` | Yes | Current timestamp in milliseconds |
| `access_token` | Conditional | Required for APIs that need user authorization |
| `sign` | Yes | HMAC-SHA256 signature (uppercase hex) |

---

## API Endpoints

### 1. Generate Access Token

**Endpoint:** `GET/POST /auth/token/create`

**Purpose:** Exchange OAuth authorization code for access token.

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `code` | String | Yes | Authorization code from OAuth redirect |
| `uuid` | String | No | Optional unique identifier |

**Example Request:**
```python
response = make_api_request(
    api_path="/auth/token/create",
    params={"code": "3_500102_JxZ05Ux3cnnSSUm6dCxYg6Q26"},
    app_key=APP_KEY,
    app_secret=APP_SECRET,
    access_token=None  # Not needed for token creation
)
```

**Example Response:**
```json
{
  "access_token": "50000601c30atpedfgu3LVvik87Ixlsvle3mSoB7701ceb156fPunYZ43GBg",
  "refresh_token": "500016000300bwa2WteaQyfwBMnPxurcA0mXGhQdTt18356663CfcDTYpWoi",
  "expires_in": "864000",
  "refresh_expires_in": "5184000",
  "account_id": "7063844",
  "account": "buyer@example.com",
  "account_platform": "buyApp",
  "country": "sg",
  "user_info": {
    "country": "GLOBAL",
    "loginId": "buyer123",
    "user_id": "200042362",
    "seller_id": "1001"
  },
  "code": "0",
  "request_id": "0ba2887315178178017221014"
}
```

**Response Fields:**

| Field | Description |
|-------|-------------|
| `access_token` | Token for API calls |
| `refresh_token` | Token for refreshing access_token |
| `expires_in` | Access token lifetime in seconds |
| `refresh_expires_in` | Refresh token lifetime in seconds |
| `user_info.user_id` | User's Alibaba ID |
| `account_platform` | Account type (e.g., "buyApp" for buyers) |

> **Note:** For ISVs migrated from the original platform, `user_id` in the old platform corresponds to `havana_id` in the new system.

---

### 2. Refresh Access Token

**Endpoint:** `GET/POST /auth/token/refresh`

**Purpose:** Get a new access token using the refresh token.

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `refresh_token` | String | Yes | The refresh token from previous token response |

**Example Request:**
```python
response = make_api_request(
    api_path="/auth/token/refresh",
    params={"refresh_token": "500016000300bwa2WteaQyfwBMnPxurcA0mXGhQdTt..."},
    app_key=APP_KEY,
    app_secret=APP_SECRET,
    access_token=None
)
```

**Example Response:**
```json
{
  "access_token": "50000601c30atpedfgu3LVvik87Ixlsvle3mSoB7701ceb156fPunYZ43GBg",
  "refresh_token": "500016000300bwa2WteaQyfwBMnPxurcA0mXGhQdTt18356663CfcDTYpWoi",
  "expires_in": "864000",
  "refresh_expires_in": "5184000",
  "code": "0",
  "request_id": "0ba2887315178178017221014"
}
```

**Usage Notes:**
- If `refresh_expires_in` = 0, the token cannot be refreshed
- Recommended to refresh 30 minutes before expiration
- After refresh token expires, buyer must re-authorize

---

### 3. Product List (General)

**Endpoint:** `GET /eco/buyer/product/check`

**Purpose:** Retrieve a list of product IDs curated for dropshipping. This is the general endpoint that can return products from different fulfillment types based on scene ID.

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query_req` | Object (JSON string) | Yes | Query parameters |

**Query Request Object:**

| Field | Type | Description |
|-------|------|-------------|
| `scene_id` | String | Product list scene ID (see below) |
| `page` | Integer | Page number (starting from 0) |
| `page_size` | Integer | Items per page (max 100) |

**Available Scene IDs:**

| Scene ID | Description |
|----------|-------------|
| `906124611` | Standard US-based fulfillment |
| `906168847` | Cross-border fulfillment (China to US) |
| `907135637` | Fast fulfillment from US (within 48 hours) |
| `907732810` | Dropshipping-eligible products from Mexico |
| `907180667` | Top-selling products from the US |
| `907180664` | Top-selling products from Mexico |

**Example Request:**
```python
query_req = json.dumps({
    "scene_id": "906124611",
    "page": 0,
    "page_size": 50
})

response = make_api_request(
    api_path="/eco/buyer/product/check",
    params={"query_req": query_req},
    app_key=APP_KEY,
    app_secret=APP_SECRET,
    access_token=ACCESS_TOKEN
)
```

**Example Response:**
```json
{
  "result": {
    "result_msg": "request success",
    "result_data": [1284823, 28743823, 1600124642247],
    "result_code": "200",
    "result_total": "100000"
  },
  "code": "0",
  "request_id": "0ba2887315178178017221014"
}
```

---

### 3a. Local Product List (US/Mexico Warehouse)

**Endpoint:** `GET /eco/buyer/local/product/check`

**Purpose:** Retrieve products specifically from overseas (local) warehouse inventory - products stocked in US or Mexico warehouses for faster domestic delivery.

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `req` | Object (JSON string) | Yes | Query parameters |

**Request Object:**

| Field | Type | Description |
|-------|------|-------------|
| `page` | Integer | Page number (starting from 0) |
| `page_size` | Integer | Items per page |
| `country` | String | Warehouse country code (e.g., "US", "MX") |

**Example Request:**
```python
req = json.dumps({
    "page": 0,
    "page_size": 50,
    "country": "US"
})

response = make_api_request(
    api_path="/eco/buyer/local/product/check",
    params={"req": req},
    app_key=APP_KEY,
    app_secret=APP_SECRET,
    access_token=ACCESS_TOKEN
)
```

**Example Response:**
```json
{
  "result": {
    "result_msg": "request success",
    "result_data": [1284823, 28743823],
    "result_code": "200"
  },
  "code": "0",
  "request_id": "0ba2887315178178017221014"
}
```

**Use Case:** Fast shipping (1-5 days) for US/Mexico customers since products ship from local warehouses.

---

### 3b. Local Product List - Regular Fulfillment

**Endpoint:** `GET /eco/buyer/localregular/product/check`

**Purpose:** Retrieve products from overseas inventory with regular (non-expedited) fulfillment options.

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `req` | Object (JSON string) | Yes | Query parameters |

**Example Request:**
```python
req = json.dumps({
    "page": 0,
    "page_size": 50
})

response = make_api_request(
    api_path="/eco/buyer/localregular/product/check",
    params={"req": req},
    app_key=APP_KEY,
    app_secret=APP_SECRET,
    access_token=ACCESS_TOKEN
)
```

---

### 3c. Cross-Border Product List

**Endpoint:** `GET /eco/buyer/crossborder/product/check`

**Purpose:** Retrieve products that ship from China (cross-border) to international destinations.

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `param0` | Object (JSON string) | Yes | Query parameters |

**Example Request:**
```python
param0 = json.dumps({
    "page": 0,
    "page_size": 50
})

response = make_api_request(
    api_path="/eco/buyer/crossborder/product/check",
    params={"param0": param0},
    app_key=APP_KEY,
    app_secret=APP_SECRET,
    access_token=ACCESS_TOKEN
)
```

**Use Case:** Larger product selection, typically 10-20 day shipping, lower per-unit costs.

---

### Product Discovery Summary

| Endpoint | Warehouse Location | Typical Shipping | Best For |
|----------|-------------------|------------------|----------|
| `/eco/buyer/local/product/check` | US/Mexico | 1-5 days | Fast domestic delivery |
| `/eco/buyer/localregular/product/check` | Overseas (regular) | 3-9 days | Standard local fulfillment |
| `/eco/buyer/crossborder/product/check` | China | 10-20 days | Widest selection, lower cost |
| `/eco/buyer/product/check` | Various (by scene_id) | Varies | Curated dropshipping lists |

> **Tip:** When displaying products, use the inventory API (`/eco/buyer/product/inventory`) to check `shipping_from` field which indicates the warehouse location (CN, US, MX).

---

### 4. Get Product Description

**Endpoint:** `GET /eco/buyer/product/description`

**Purpose:** Get detailed product information including variants, pricing, and images.

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query_req` | Object (JSON string) | Yes | Query containing product_id |

**Query Request Object:**

| Field | Type | Description |
|-------|------|-------------|
| `product_id` | String | The Alibaba product ID |

**Example Request:**
```python
query_req = json.dumps({"product_id": "1601206892606"})

response = make_api_request(
    api_path="/eco/buyer/product/description",
    params={"query_req": query_req},
    app_key=APP_KEY,
    app_secret=APP_SECRET,
    access_token=ACCESS_TOKEN
)
```

**Example Response:**
```json
{
  "result": {
    "result_msg": "request success",
    "result_data": {
      "product_id": "1601206892606",
      "title": "Sublimation Mug 40oz Tumbler Stainless Steel Double Wall",
      "description": "<html>Product description HTML</html>",
      "detail_url": "https://www.alibaba.com/product-detail/1601206892606.html",
      "main_image": "https://sc04.alicdn.com/kf/H223c0dee279948d3bbfeb813ab8fb58co.jpg",
      "images": [
        "https://sc04.alicdn.com/kf/image1.jpg",
        "https://sc04.alicdn.com/kf/image2.jpg"
      ],
      "category_id": "100003291",
      "category": "Vacuum Flasks & Thermoses",
      "supplier": "Company Name",
      "eCompanyId": "xxxxxxxxx",
      "currency": "USD",
      "min_order_quantity": "50",
      "status": "PRODUCT_ONLINE",
      "mode_id": "AV.YW.DEP.103.L",
      "wholesale_trade": {
        "min_order_quantity": "12",
        "unit_type": "Piece",
        "handling_time": "3",
        "price": "12.34",
        "deliver_periods": [
          {"quantity": "50", "process_period": "3"}
        ]
      },
      "skus": [
        {
          "sku_id": "105613018158",
          "product_id": "1601206892606",
          "seller_sku_id": "1601206892606_107152354495",
          "status": "NORMAL",
          "unit": "Piece",
          "image": "https://sc04.alicdn.com/kf/sku_image.jpg",
          "sku_attr_list": [
            {
              "attr_name_id": "1111",
              "attr_name_desc": "Color",
              "attr_value_id": "-11",
              "attr_value_desc": "40oz solid color tumbler 1.0",
              "attr_value_image": "https://sc04.alicdn.com/kf/attr_image.jpg"
            }
          ],
          "ladder_price": [
            {
              "min_quantity": "50",
              "max_quantity": "499",
              "price": "3.69",
              "currency": "USD"
            }
          ]
        }
      ]
    },
    "result_code": "200"
  },
  "code": "0",
  "request_id": "0ba2887315178178017221014"
}
```

**Key Fields:**

| Field | Description |
|-------|-------------|
| `eCompanyId` | Supplier ID (needed for shipping calculation) |
| `skus[].sku_id` | Variant ID (needed for order creation) |
| `skus[].ladder_price` | Volume-based pricing tiers |

---

### 5. Get Item Inventory

**Endpoint:** `GET /eco/buyer/product/inventory`

**Purpose:** Check inventory levels and availability for specific products.

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `inv_req` | Object (JSON string) | Yes | Inventory query parameters |

**Inventory Request Object:**

| Field | Type | Description |
|-------|------|-------------|
| `product_id` | String | The Alibaba product ID |
| `sku_id` | String | Optional: specific SKU ID |
| `shipping_from` | String | Optional: origin country code (CN, US, MX) |

**Example Request:**
```python
inv_req = json.dumps({
    "product_id": "1600927952535",
    "shipping_from": "CN"
})

response = make_api_request(
    api_path="/eco/buyer/product/inventory",
    params={"inv_req": inv_req},
    app_key=APP_KEY,
    app_secret=APP_SECRET,
    access_token=ACCESS_TOKEN
)
```

**Example Response:**
```json
{
  "result": {
    "result_msg": "request success",
    "result_data": [
      {
        "shipping_from": "CN",
        "inventory_list": [
          {
            "product_id": "1600927952535",
            "sku_id": "104536974925",
            "inventory_count": "1196",
            "inventory_unit": "Piece"
          }
        ]
      }
    ],
    "result_code": "200"
  },
  "code": "0",
  "request_id": "0ba2887315178178017221014"
}
```

---

### 6. Basic Freight Cost Estimation

**Endpoint:** `GET/POST /shipping/freight/calculate`

**Purpose:** Get estimated shipping costs for a single product (use during product browsing).

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `product_id` | String | Yes | Alibaba product ID |
| `quantity` | Integer | Yes | Number of items |
| `destination_country` | String | Yes | ISO country code (e.g., "US") |
| `zip_code` | String | No | Destination ZIP code |
| `dispatch_location` | String | No | Origin location (CN, US, MX). Default: CN |
| `enable_distribution_waybill` | Boolean | No | Enable distribution waybill options |

**Example Request:**
```python
response = make_api_request(
    api_path="/shipping/freight/calculate",
    params={
        "product_id": "1600124642247",
        "quantity": "5",
        "destination_country": "US",
        "zip_code": "90001",
        "dispatch_location": "CN"
    },
    app_key=APP_KEY,
    app_secret=APP_SECRET,
    access_token=ACCESS_TOKEN
)
```

**Example Response:**
```json
{
  "code": "0",
  "value": [
    {
      "shipping_type": "EXPRESS",
      "vendor_code": "EX_ASP_Economy_Express_3C",
      "vendor_name": "Alibaba.com Economy Express (3C)",
      "trade_term": "DAP",
      "dispatch_country": "CN",
      "destination_country": "US",
      "delivery_time": "10~15",
      "solution_biz_type": "distributionWaybill",
      "fee": {
        "amount": "19.1",
        "currency": "USD"
      }
    }
  ],
  "request_id": "0ba2887315178178017221014"
}
```

---

### 7. Advanced Freight Cost Calculation

**Endpoint:** `GET/POST /order/freight/calculate`

**Purpose:** Get accurate shipping costs for multiple products (use before order creation).

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `e_company_id` | String | Yes | Supplier's company ID (from product description) |
| `destination_country` | String | Yes | ISO country code |
| `dispatch_location` | String | No | Origin (CN, US, MX). Default: CN |
| `address` | Object (JSON string) | Yes | Shipping address details |
| `logistics_product_list` | Array (JSON string) | Yes | List of products |
| `enable_distribution_waybill` | Boolean | No | Enable distribution waybill |

**Address Object:**

```json
{
  "zip": "35022",
  "country": {"code": "US", "name": "United States"},
  "province": {"code": "AL", "name": "Alabama"},
  "city": {"code": "", "name": "Bessemer"},
  "address": "4595 Clubview Drive"
}
```

**Logistics Product List:**

```json
[
  {"product_id": "1600191825486", "sku_id": "12321", "quantity": "1"}
]
```

**Example Request:**
```python
address = json.dumps({
    "zip": "35022",
    "country": {"code": "US", "name": "United States"},
    "province": {"code": "AL", "name": "Alabama"},
    "city": {"code": "", "name": "Bessemer"},
    "address": "4595 Clubview Drive"
})

logistics_product_list = json.dumps([
    {"product_id": "1600191825486", "sku_id": "12321", "quantity": "1"}
])

response = make_api_request(
    api_path="/order/freight/calculate",
    params={
        "e_company_id": "cVmhg7/xG8q3UQgcH/5Fag==",
        "destination_country": "US",
        "dispatch_location": "CN",
        "address": address,
        "logistics_product_list": logistics_product_list
    },
    app_key=APP_KEY,
    app_secret=APP_SECRET,
    access_token=ACCESS_TOKEN
)
```

**Example Response:**
```json
{
  "code": "0",
  "value": [
    {
      "vendor_code": "seller_oversea_distributor_sellers_shipping_method_1",
      "vendor_name": "Seller's Shipping Method 1",
      "shipping_type": "EXPRESS/MULTIMODAL_TRANSPORT",
      "trade_term": "DAP",
      "dispatch_country": "US",
      "destination_country": "US",
      "delivery_time": "3-9",
      "solution_biz_type": "distributionWaybill",
      "store_type": "CERTIFIED",
      "fee": {
        "amount": "3.0",
        "currency": "USD"
      }
    }
  ],
  "request_id": "0ba2887315178178017221014"
}
```

---

### 8. Create BuyNow Order

**Endpoint:** `GET/POST /buynow/order/create`

**Purpose:** Create a dropshipping order.

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `channel_refer_id` | String | Yes | Your internal order reference ID |
| `product_list` | Array (JSON string) | Yes | Products to order |
| `logistics_detail` | Object (JSON string) | Yes | Shipping details |
| `properties` | Object (JSON string) | No | Custom properties (platform, orderId) |
| `remark` | String | No | Order notes |
| `attachments` | Array (JSON string) | No | Waybill attachments |
| `enable_distribution_waybill` | Boolean | No | Enable distribution waybill |
| `clearance_detail` | Object (JSON string) | No | For orders requiring customs clearance |

**Product List:**

```json
[
  {"product_id": "100001", "sku_id": "200001", "quantity": "10"}
]
```

**Logistics Detail:**

```json
{
  "shipment_address": {
    "zip": "10012",
    "country": "United States of America",
    "country_code": "US",
    "province": "New York",
    "province_code": "NY",
    "city": "New York",
    "city_code": "NYC",
    "address": "123 Main Street",
    "alternate_address": "Apt 4B",
    "contact_person": "John Doe",
    "telephone": {
      "country": "+1",
      "area": "",
      "number": "5551234567"
    }
  },
  "dispatch_location": "CN",
  "carrier_code": "EX_ASP_JYC_FEDEX"
}
```

**Example Request:**
```python
product_list = json.dumps([
    {"product_id": "100001", "sku_id": "200001", "quantity": "10"}
])

logistics_detail = json.dumps({
    "shipment_address": {
        "zip": "10012",
        "country": "United States of America",
        "country_code": "US",
        "province": "New York",
        "province_code": "NY",
        "city": "New York",
        "address": "123 Main Street",
        "contact_person": "John Doe",
        "telephone": {"country": "+1", "number": "5551234567"}
    },
    "dispatch_location": "CN",
    "carrier_code": "EX_ASP_JYC_FEDEX"
})

properties = json.dumps({
    "platform": "Shopify",
    "orderId": "SH12345678"
})

response = make_api_request(
    api_path="/buynow/order/create",
    params={
        "channel_refer_id": "ORDER-2026-001",
        "product_list": product_list,
        "logistics_detail": logistics_detail,
        "properties": properties,
        "remark": "Please handle with care"
    },
    app_key=APP_KEY,
    app_secret=APP_SECRET,
    access_token=ACCESS_TOKEN
)
```

**Example Response:**
```json
{
  "code": "0",
  "value": {
    "trade_id": "234193410001028893",
    "pay_url": "https://biz.alibaba.com/ta/detail.htm?orderId=234193410001028893"
  },
  "request_id": "0ba2887315178178017221014"
}
```

**Important Fields:**

| Field | Description |
|-------|-------------|
| `trade_id` | Alibaba order ID - store this for all subsequent operations |
| `pay_url` | URL for manual payment if automated payment fails |

---

### 9. Pay for Order

**Endpoint:** `GET/POST /alibaba/dropshipping/order/pay`

**Purpose:** Process payment for dropshipping orders.

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `param_order_pay_request` | Object (JSON string) | Yes | Payment request details |

**Payment Request Object:**

```json
{
  "order_id_list": ["1234", "2234"],
  "payment_method": "CREDIT_CARD",
  "user_ip": "10.11.102.11",
  "user_agent": "Mozilla/5.0...",
  "accept_language": "en-US,en;q=0.9",
  "screen_resolution": "1920*1080",
  "is_pc": true,
  "isv_drop_shipper_registration_time": 1616595118627
}
```

**Example Request:**
```python
param_order_pay_request = json.dumps({
    "order_id_list": ["234193410001028893"],
    "payment_method": "CREDIT_CARD",
    "user_ip": "192.168.1.1",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "accept_language": "en-US,en;q=0.9",
    "screen_resolution": "1920*1080",
    "is_pc": True,
    "isv_drop_shipper_registration_time": 1616595118627
})

response = make_api_request(
    api_path="/alibaba/dropshipping/order/pay",
    params={"param_order_pay_request": param_order_pay_request},
    app_key=APP_KEY,
    app_secret=APP_SECRET,
    access_token=ACCESS_TOKEN
)
```

**Example Response (Success):**
```json
{
  "code": "0",
  "value": {
    "status": "PAY_SUCCESS"
  },
  "request_id": "0ba2887315178178017221014"
}
```

**Example Response (Requires Manual Payment):**
```json
{
  "code": "0",
  "value": {
    "status": "PAY_FAILED",
    "reason_code": "NEVER_PAY_SUCCESS_IN_DROPSHIPER",
    "reason_message": "The buyer has never paid for a successful dropshipping order and needs to visit payUrl to pay.",
    "pay_url": "https://biz.alibaba.com/..."
  },
  "request_id": "0ba2887315178178017221014"
}
```

---

### 10. Get Order List

**Endpoint:** `GET/POST /alibaba/order/list`

**Purpose:** Retrieve a list of orders with optional filters.

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `role` | String | Yes | "buyer" or "seller" |
| `start_page` | Integer | No | Page number (starts at 0) |
| `page_size` | Integer | No | Items per page (default 10) |
| `status` | String | No | Filter by order status |
| `create_date_start` | Object (JSON string) | No | Order creation date range start |
| `create_date_end` | Object (JSON string) | No | Order creation date range end |
| `modified_date_start` | Object (JSON string) | No | Order modification date range start |
| `modified_date_end` | Object (JSON string) | No | Order modification date range end |

**Date Object:**
```json
{"date_timestamp": "1733821832000", "date_str": "2025-12-10 00:00:00"}
```

**Example Request:**
```python
response = make_api_request(
    api_path="/alibaba/order/list",
    params={
        "role": "buyer",
        "start_page": "0",
        "page_size": "20",
        "status": "unpay"
    },
    app_key=APP_KEY,
    app_secret=APP_SECRET,
    access_token=ACCESS_TOKEN
)
```

**Example Response:**
```json
{
  "code": "0",
  "value": {
    "total_count": "264930",
    "order_list": [
      {
        "trade_id": "271207727001028893",
        "trade_status": "unpay",
        "create_date": {
          "format_date": "Jul. 31, 2025, 21:09:36 PDT.",
          "timestamp": "1754021376000"
        },
        "modify_date": {
          "format_date": "Jul. 31, 2025, 21:09:37 PDT.",
          "timestamp": "1754021377000"
        }
      }
    ]
  },
  "request_id": "0ba2887315178178017221014"
}
```

---

### 11. Get Order Details

**Endpoint:** `GET/POST /alibaba/order/get`

**Purpose:** Get comprehensive details for a specific order.

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `e_trade_id` | String | Yes | Alibaba order ID (trade_id) |
| `data_select` | String | No | Optional data to include (e.g., "draft_role") |
| `language` | String | No | Response language (e.g., "en_US") |

**Example Request:**
```python
response = make_api_request(
    api_path="/alibaba/order/get",
    params={
        "e_trade_id": "234193410001028893",
        "language": "en_US"
    },
    app_key=APP_KEY,
    app_secret=APP_SECRET,
    access_token=ACCESS_TOKEN
)
```

**Example Response:**
```json
{
  "code": "0",
  "value": {
    "trade_id": "234193410001028893",
    "trade_status": "unpay",
    "pay_step": "ADVANCE",
    "fulfillment_channel": "TAD",
    "dropshipping": "true",
    "create_date": {
      "format_date": "Dec. 10, 2025, 10:30:32 PST.",
      "timestamp": "1733821832000"
    },
    "shipping_address": {
      "zip": "10012",
      "country": "United States of America",
      "country_code": "US",
      "province": "New York",
      "city": "New york",
      "address": "123 Main Street",
      "contact_person": "John Doe",
      "mobile": {"country": "+1", "number": "5551234567"}
    },
    "order_products": [
      {
        "product_id": "1601314875038",
        "sku_id": "106117950042",
        "name": "Product Name",
        "quantity": "2.0000",
        "unit": "Pieces",
        "unit_price": {"amount": "0.1000", "currency": "USD"},
        "product_image": "https://sc04.alicdn.com/kf/product.jpg",
        "sku_attributes": [
          {"key": "Color", "value": "Red"}
        ]
      }
    ],
    "product_total_amount": {"amount": "0.20", "currency": "USD"},
    "shipment_fee": {"amount": "4.67", "currency": "USD"},
    "total_amount": {"amount": "4.87", "currency": "USD"},
    "carrier": {
      "code": "SEMI_MANAGED_CARRIER_CODE_CHEAPEST",
      "name": "Standard"
    },
    "buyer": {
      "immutable_eid": "8s0vvDIbRvbS9hSAK4bUtw==",
      "full_name": "Buyer Name"
    },
    "seller": {
      "immutable_eid": "kx++Dlfuw+osaJiw08no/A==",
      "full_name": "Seller Name"
    }
  },
  "request_id": "0ba2887315178178017221014"
}
```

---

### 12. Logistics Tracking

**Endpoint:** `GET/POST /order/logistics/tracking/get`

**Purpose:** Get tracking events and shipment updates for an order.

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `trade_id` | String | Yes | Alibaba order ID |

**Example Request:**
```python
response = make_api_request(
    api_path="/order/logistics/tracking/get",
    params={"trade_id": "234193410001028893"},
    app_key=APP_KEY,
    app_secret=APP_SECRET,
    access_token=ACCESS_TOKEN
)
```

**Example Response:**
```json
{
  "code": "0",
  "tracking_list": [
    {
      "carrier": "FEDEX",
      "tracking_number": "776705370628",
      "current_event_code": "DELIVERED",
      "tracking_url": "https://sale.alibaba.com/...",
      "event_list": [
        {
          "event_code": "DELIVERED",
          "event_name": "Delivered",
          "event_location": "US, TN, HENDERSONVILLE",
          "event_time": "2024-06-11 15:53:00"
        },
        {
          "event_code": "IN_TRANSIT",
          "event_name": "In Transit",
          "event_location": "US, TN, NASHVILLE",
          "event_time": "2024-06-10 08:23:00"
        }
      ]
    }
  ],
  "request_id": "0ba2887315178178017221014"
}
```

---

### 13. Order Logistics Query

**Endpoint:** `GET/POST /order/logistics/query`

**Purpose:** Get shipping status and tracking number for an order.

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `trade_id` | String | Yes | Alibaba order ID |
| `data_select` | String | No | Set to "logistic_order" for tracking details |

**Example Request:**
```python
response = make_api_request(
    api_path="/order/logistics/query",
    params={
        "trade_id": "234193410001028893",
        "data_select": "logistic_order"
    },
    app_key=APP_KEY,
    app_secret=APP_SECRET,
    access_token=ACCESS_TOKEN
)
```

**Example Response:**
```json
{
  "code": "0",
  "value": {
    "logistic_status": "CONFIRM_RECEIPT",
    "shipment_date": {
      "format_date": "Jun. 11, 2024, 20:10:13 PDT.",
      "timestamp": "1718161813000"
    },
    "shipping_order_list": [
      {
        "voucher": {
          "tracking_number": "123432",
          "service_provider": "EX_ASP_OCEAN_EXPRESS",
          "logistics_type": "EXPRESS"
        }
      }
    ]
  },
  "request_id": "0ba2887315178178017221014"
}
```

---

### 14. Order Fund Query

**Endpoint:** `GET/POST /alibaba/order/fund/query`

**Purpose:** Get payment records and financial details for an order.

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `e_trade_id` | String | Yes | Alibaba order ID |
| `data_select` | String | No | Data type (e.g., "fund_transaction_fee") |

**Example Request:**
```python
response = make_api_request(
    api_path="/alibaba/order/fund/query",
    params={
        "e_trade_id": "234193410001028893",
        "data_select": "fund_transaction_fee"
    },
    app_key=APP_KEY,
    app_secret=APP_SECRET,
    access_token=ACCESS_TOKEN
)
```

**Example Response:**
```json
{
  "code": "0",
  "value": {
    "payment_transaction_fee": {
      "amount": "11",
      "currency": "USD"
    }
  },
  "request_id": "0ba2887315178178017221014"
}
```

---

## Error Handling

### Common Error Codes

| Error Code | Sub Code | Meaning | Solution |
|------------|----------|---------|----------|
| `110001` | - | Unauthorized Buyer | Buyer must use overseas-registered account (not China account) |
| `10010` | - | Logistics Route Not Found | Check `dispatch_location` parameter |
| `130602` | - | Invalid Logistics Route | Ensure `carrier_code` still exists |
| `130608` | - | Missing Dispatch Location | Set `dispatch_location = MX` for Mexico products |
| `480006` | - | Order Amount Exceeds Limit | Order must be under $5000 for BuyNow orders |
| `10007` | - | Cannot Find SKU Cost | Check product MOQ requirements |
| `410006` | - | Quantity Below Minimum | Increase quantity to meet MOQ |
| `130704` | - | Promotion Unavailable | Contact Alibaba to refresh inventory cache |
| `130106` | - | Product Invalid | Product is offline, select different product |
| `130703` | - | Insufficient Inventory | Reduce quantity or select different SKU |
| `120019` | - | Product Restricted | Product cannot ship to destination country |
| `800022` | - | Unable to Calculate Tariff | Provide complete address details |
| `10012` | - | Dispatch Location Invalid | Match `dispatch_location` to product's origin |
| `4015` | - | Cannot Ship to Country | Seller doesn't support shipping to destination |
| `140004` | - | Insufficient Inventory | Product is out of stock |
| `10005` | - | SKU Not Found | SKU may have been deleted |
| `400007` | - | EPR Required | Seller needs valid EPR number for DE/FR |
| `430013` | - | Order Amount Too Small | Minimum order amount is $0.30 |

### Order Status Codes

| Status | Description |
|--------|-------------|
| `to_be_audited` | Waiting for audit |
| `unpay` | Waiting for advance payment |
| `paying` | Payment verification in progress |
| `paid` | Payment successful |
| `captured` | Payment completed, funds transferred |
| `undeliver` | Waiting for seller to ship |
| `delivering` | In delivery (seller shipping) |
| `wait_confirm_receipt` | Waiting for buyer to confirm receipt |
| `trade_close` | Order closed/canceled |
| `trade_success` | Order completed |
| `frozen` | Order frozen (refund in progress) |
| `charge_back` | Credit card chargeback |

### Dispatch Location Fallback

Some products may fail with one dispatch location but work with another:

```python
def calculate_shipping_with_fallback(product_id, quantity, destination_country, zip_code):
    # Try China first (cross-border)
    response = make_api_request(
        api_path="/shipping/freight/calculate",
        params={
            "product_id": product_id,
            "quantity": quantity,
            "destination_country": destination_country,
            "zip_code": zip_code,
            "dispatch_location": "CN"
        },
        app_key=APP_KEY,
        app_secret=APP_SECRET,
        access_token=ACCESS_TOKEN
    )
    
    if response.get("code") != "0" or not response.get("value"):
        # Fallback to US warehouse
        response = make_api_request(
            api_path="/shipping/freight/calculate",
            params={
                "product_id": product_id,
                "quantity": quantity,
                "destination_country": destination_country,
                "zip_code": zip_code,
                "dispatch_location": "US"
            },
            app_key=APP_KEY,
            app_secret=APP_SECRET,
            access_token=ACCESS_TOKEN
        )
    
    return response
```

### Country Code Mapping

```python
# UK is not a valid ISO code for Alibaba
def normalize_country_code(country_code):
    if country_code == 'UK':
        return 'GB'
    return country_code
```

---

## Push Notifications (Webhooks)

Alibaba.com supports webhook-based push notifications for real-time updates on orders and products.

### Supported Message Types

| Message Title | Message Tag | Description |
|---------------|-------------|-------------|
| `ECOLOGY PRODUCT OPTION MSG` | `PRODUCT_OPTION_TAG` | Product add/delete (meets or no longer meets listing requirements) |
| `ECOLOGY PRODUCT CHANGE MSG` | `PRODUCT_CHANGE_TAG` | Product pricing changes |
| `ICBU ORDER SYNC MESSAGE` | - | Order status changes (created, paid, shipped, etc.) |

### Onboarding Process

1. **Prepare Callback HTTPS Service**
   - Your callback URL must support HTTPS
   - Certificate must be CA-issued (OV or EV certificates only, DV not supported)
   - Self-signed certificates are not allowed

2. **Configure in App Console**
   - Navigate to your app settings in the Alibaba.com App Console
   - Configure message subscription for the message types you need
   - Set your callback URL

3. **Test the Callback**
   - Use the App Console testing feature to verify your endpoint works
   - Ensure you return HTTP 200 within 500ms

4. **Handle Retries**
   - Return `200 OK` HTTP status to acknowledge receipt
   - If no `200 OK` within 500ms, message will be retried
   - Up to 12 retry attempts over ~6 hours
   - If failure rate exceeds 50%, platform will stop pushing to your callback

### Webhook Payload Structure

**HTTP Request:**
```http
POST /your/callback/endpoint HTTP/1.1
Host: www.example.com
Content-Type: application/json
Authorization: 34f7b258df045d4ed9341850ca85b866f34828fd7d51862f11137216294a894c
```

**Order Status Change Message:**
```json
{
  "havana_id": "17379911544",
  "seller_id": "200042360",
  "message_type": 3,
  "data": {
    "status": "trade_close",
    "trade_id_str": "255201166001024316",
    "order_status": "PLACE_ORDER_SUCCESS",
    "trade_order_id": "30160843",
    "status_update_time": "2025-04-19 23:18:56"
  },
  "timestamp": 1650435537,
  "site": "icbu_global"
}
```

**Product Add/Delete Message:**
```json
{
  "seller_id": "BROADCAST",
  "message_type": 1,
  "data": {
    "productId": "123456789",
    "option": "ADD"
  },
  "timestamp": 1650435537
}
```

**Product Price Change Message:**
```json
{
  "seller_id": "BROADCAST",
  "message_type": 1,
  "data": {
    "productId": "123456789",
    "skuId": "123456789",
    "option": "PRICE_CHANGE",
    "value": "11.00",
    "timestamp": "1650435537"
  },
  "timestamp": 1650435537
}
```

### Payload Fields

| Field | Description |
|-------|-------------|
| `Authorization` (header) | HMAC-SHA256 signature for verification |
| `havana_id` | Corresponds to original TOP platform `userId` |
| `seller_id` | Account ID of the user (buyer ID for order messages) |
| `message_type` | Message type identifier (determines `data` structure) |
| `data` | Core payload with event details |
| `timestamp` | Unix timestamp of the message |
| `site` | Platform identifier (e.g., "icbu_global") |

### Signature Verification

The `Authorization` header contains an HMAC-SHA256 signature. **Verification is strongly recommended** to prevent malicious push attempts.

**Signature Algorithm:**
```
Base = {AppKey} + {raw_message_body}
Signature = HEX_ENCODE(HMAC-SHA256(Base, AppSecret))
```

**Python Implementation:**
```python
import hmac
import hashlib

def verify_webhook_signature(
    authorization_header: str,
    raw_body: str,
    app_key: str,
    app_secret: str
) -> bool:
    """
    Verify the webhook signature from Alibaba.
    
    Args:
        authorization_header: The Authorization header value
        raw_body: The raw JSON body as a string (do not parse/serialize)
        app_key: Your application key
        app_secret: Your application secret
    
    Returns:
        True if signature is valid, False otherwise
    """
    # Build the base string: AppKey + raw message body
    base = app_key + raw_body
    
    # Generate HMAC-SHA256 signature
    signature = hmac.new(
        app_secret.encode('utf-8'),
        base.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # Compare with the Authorization header (case-insensitive)
    return signature.lower() == authorization_header.lower()
```

**Important Notes:**
- Use the **raw request body string** - do not parse and re-serialize the JSON
- Different JSON libraries may reorder fields, causing signature mismatch
- Keep signature verification separate from business logic

### Webhook Handler Example

```python
from flask import Flask, request, jsonify
import json

app = Flask(__name__)

APP_KEY = "your_app_key"
APP_SECRET = "your_app_secret"

@app.route('/webhook/alibaba', methods=['POST'])
def alibaba_webhook():
    # Get raw body for signature verification
    raw_body = request.get_data(as_text=True)
    
    # Verify signature
    authorization = request.headers.get('Authorization')
    if authorization:
        if not verify_webhook_signature(authorization, raw_body, APP_KEY, APP_SECRET):
            return 'Invalid signature', 401
    
    # Parse the message
    try:
        message = json.loads(raw_body)
    except json.JSONDecodeError:
        return 'Invalid JSON', 400
    
    message_type = message.get('message_type')
    data = message.get('data', {})
    
    # Queue for async processing (recommended for <500ms response)
    queue_message_for_processing(message)
    
    # Return 200 OK immediately
    return 'OK', 200

def queue_message_for_processing(message):
    """
    Queue message for async processing.
    Use a message queue (Redis, RabbitMQ, Celery) to handle
    messages asynchronously and avoid timeout issues.
    """
    message_type = message.get('message_type')
    data = message.get('data', {})
    
    if message_type == 3:  # Order status change
        # Handle order update
        trade_id = data.get('trade_id_str')
        status = data.get('status')
        # Queue: update_order_status.delay(trade_id, status)
    
    elif message_type == 1:  # Product change
        product_id = data.get('productId')
        option = data.get('option')
        if option == 'ADD':
            # Queue: add_product.delay(product_id)
            pass
        elif option == 'DELETE':
            # Queue: remove_product.delay(product_id)
            pass
        elif option == 'PRICE_CHANGE':
            # Queue: update_product_price.delay(product_id)
            pass
```

### Best Practices

1. **Respond within 500ms**: Queue messages for async processing
2. **Implement idempotency**: Duplicate messages may occur due to retries
3. **Use `trade_id` to fetch full order details**: Message data is summary only
4. **Don't rely solely on webhooks**: Implement periodic polling as fallback

### Fallback Polling Pattern

If webhooks fail or as a backup verification:

```python
def poll_order_updates():
    """Poll for order updates as a fallback to webhooks."""
    import time
    
    last_poll_time = int(time.time() * 1000) - 86400000  # 24 hours ago
    
    while True:
        start_time = time.time()
        
        try:
            response = make_api_request(
                api_path="/alibaba/order/list",
                params={
                    "role": "buyer",
                    "modified_date_start": json.dumps({
                        "date_timestamp": str(last_poll_time)
                    }),
                    "page_size": "100"
                },
                app_key=APP_KEY,
                app_secret=APP_SECRET,
                access_token=ACCESS_TOKEN
            )
            
            if response.get("code") == "0":
                orders = response.get("value", {}).get("order_list", [])
                for order in orders:
                    process_order_update(order)
                
                last_poll_time = int(time.time() * 1000)
        
        except Exception as e:
            log_exception(e)
        
        # Poll every 15 seconds
        elapsed = time.time() - start_time
        sleep_time = max(0, 15 - elapsed)
        time.sleep(sleep_time)
```

> **Note:** Alibaba recommends "push first, pull as fallback" - webhook success rate is 99.8% on first attempt and 100% within 3 attempts for mainstream cloud servers.

---

## Endpoint Mapping

### V1 to V2 Migration

| V1 Endpoint (Legacy) | V2 Endpoint (New) | Notes |
|---------------------|-------------------|-------|
| `taobao.top.auth.token.create` | `/auth/token/create` | Different response structure |
| `alibaba.dropshipping.token.create` | N/A | Ecology token no longer needed |
| `alibaba.dropshipping.product.get` | `/eco/buyer/product/description` | Use with `/eco/buyer/product/check` for discovery |
| `alibaba.shipping.freight.calculate` | `/shipping/freight/calculate` | Simpler parameter format |
| `alibaba.order.freight.calculate` | `/order/freight/calculate` | Similar functionality |
| `alibaba.buynow.order.create` | `/buynow/order/create` | Simplified parameters |
| `alibaba.dropshipping.order.pay` | `/alibaba/dropshipping/order/pay` | Same endpoint, simplified params |
| `alibaba.seller.order.fund.get` | `/alibaba/order/fund/query` | New endpoint path |
| `alibaba.seller.order.logistics.get` | `/order/logistics/query` | New endpoint path |
| `alibaba.order.logistics.tracking.get` | `/order/logistics/tracking/get` | Same functionality |
| `taobao.tmc.user.permit` | Webhook configuration | Configure in App Console |
| `taobao.tmc.messages.consume` | Webhook endpoint | Push-based instead of polling |
| `taobao.tmc.messages.confirm` | HTTP 200 response | Acknowledge via HTTP status |

### Key Differences

| Feature | V1 (Legacy) | V2 (New) |
|---------|-------------|----------|
| Base URL | `eco.taobao.com` | `openapi-api.alibaba.com/rest` |
| Auth URL | `crosstrade.alibaba.com` | `openapi-auth.alibaba.com` |
| Ecology Token | Required | Not required |
| Response Wrapper | API-specific keys | Consistent `value` key |
| Notifications | TMC polling | Webhooks |
| Signature | Same algorithm | Same algorithm |

---

## Quick Reference

### Endpoint Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/auth/token/create` | GET/POST | OAuth token exchange |
| `/auth/token/refresh` | GET/POST | Refresh access token |
| `/eco/buyer/product/check` | GET | Get product ID list by scene (curated lists) |
| `/eco/buyer/local/product/check` | GET | Get products from local warehouses (US/MX) |
| `/eco/buyer/localregular/product/check` | GET | Get products with regular local fulfillment |
| `/eco/buyer/crossborder/product/check` | GET | Get cross-border products (from China) |
| `/eco/buyer/product/description` | GET | Get product details |
| `/eco/buyer/product/inventory` | GET | Check product inventory |
| `/shipping/freight/calculate` | GET/POST | Basic shipping estimate |
| `/order/freight/calculate` | GET/POST | Detailed shipping calculation |
| `/buynow/order/create` | GET/POST | Create order |
| `/alibaba/dropshipping/order/pay` | GET/POST | Pay for order |
| `/alibaba/order/list` | GET/POST | List orders |
| `/alibaba/order/get` | GET/POST | Get order details |
| `/alibaba/order/fund/query` | GET/POST | Get payment details |
| `/order/logistics/query` | GET/POST | Get shipping status |
| `/order/logistics/tracking/get` | GET/POST | Get tracking events |

---

## Implementation Checklist

- [ ] Register application on Alibaba.com Open Platform
- [ ] Obtain `APP_KEY` and `APP_SECRET`
- [ ] Configure OAuth callback URL
- [ ] Implement OAuth flow for buyer authorization
- [ ] Store user tokens securely with expiration tracking
- [ ] Implement request signing (HMAC-SHA256)
- [ ] Implement token refresh before expiration
- [ ] Handle dispatch location fallback for shipping
- [ ] Normalize country codes (UK → GB)
- [ ] Set up webhook endpoint for notifications (or implement polling)
- [ ] Implement error handling for all known error codes
- [ ] Cache product and shipping data appropriately
- [ ] Test with sandbox environment before production

---

## Issues and Unknowns

### Documentation Gaps

1. **Rate Limiting**: The new API documentation doesn't specify rate limits. Monitor for error code 7 ("App call limited") and implement appropriate backoff.

2. **Order Cancellation**: The `/alibaba/order/cancel` endpoint exists but parameters are not fully documented. Test thoroughly in sandbox.

3. **Product Events API**: The `/eco/buyer/product/events` endpoint for sending product status updates is referenced but parameter details are limited.

4. **Message Type Mapping**: The `message_type` field values and their meanings are not fully enumerated. Known values:
   - `1` = Product change / Order creation
   - `3` = Order status change
   - `15` = Product status update

### Known Limitations

1. **BuyNow Order Limit**: Maximum order amount is $5,000 for BuyNow (TAD) orders
2. **Minimum Order**: Orders must be at least $0.30
3. **China Accounts**: Buyers must use overseas-registered accounts (not CNFM accounts)
4. **EPR Compliance**: Orders to Germany/France require valid EPR numbers from sellers

### Migration Considerations

1. The `ecology_token` is no longer required - remove token refresh logic for this
2. Response structures have changed - update parsing logic
3. The `user_id` field mapping has changed for migrated accounts (now `havana_id`)
4. TMC message polling is replaced with webhooks - implement new notification handling
