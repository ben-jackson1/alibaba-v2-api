# Story: epic_05_orders/story_017

## Metadata

| Field | Value |
|-------|-------|
| Epic | Order Management Endpoints |
| Priority | P0 |
| Estimate | L |
| Status | PENDING |
| Blocked By | epic_01_setup/story_001, epic_01_setup/story_002, epic_01_setup/story_003, epic_02_auth/story_005 |
| Blocks | epic_05_orders/story_018, epic_05_orders/story_019, epic_05_orders/story_020, epic_05_orders/story_021, epic_05_orders/story_022 |
| Tracer Bullet | true |

## User Story

As a developer, I want to create a BuyNow order so that I can validate the complete order creation flow.

## Description

Implement `/buynow/order/create` for creating dropshipping orders with full logistics details.

## Acceptance Criteria

- [ ] AC1: CLI command: `alibaba-cli order create --channel-refer-id <id> --product-list <json> --logistics-detail <json> [--remark <text>] [--properties <json>]`
- [ ] AC2: API endpoint: `/buynow/order/create`
- [ ] AC3: Requires access_token
- [ ] AC4: product_list: JSON array of {product_id, sku_id, quantity}
- [ ] AC5: logistics_detail: JSON with shipment_address (full address object), dispatch_location, carrier_code
- [ ] AC6: Response: trade_id and pay_url
- [ ] AC7: Integration test with real product data (may create test order)
- [ ] AC8: Supports @filename for JSON input
- [ ] AC9: Response structure validated against documentation

## Implementation Notes

logistics_detail structure:
```json
{
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
}
```

## Definition of Done

- Order creation returns trade_id
- Full address structure handled
- Integration test passes
