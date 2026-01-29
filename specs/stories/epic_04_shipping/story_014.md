# Story: epic_04_shipping/story_014

## Metadata

| Field | Value |
|-------|-------|
| Epic | Shipping Calculation Endpoints |
| Priority | P0 |
| Estimate | L |
| Status | PENDING |
| Blocked By | epic_04_shipping/story_013 |
| Blocks | None |
| Tracer Bullet | false |

## User Story

As a developer, I want to calculate shipping for multiple products so that I can validate the advanced freight API used before order creation.

## Description

Implement `/order/freight/calculate` for multi-product shipping calculations with full address details.

## Acceptance Criteria

- [ ] AC1: CLI command: `alibaba-cli shipping calculate-advanced --e-company-id <id> --destination-country <code> --address <json> --logistics-product-list <json> [--dispatch-location <code>]`
- [ ] AC2: API endpoint: `/order/freight/calculate`
- [ ] AC3: Requires access_token
- [ ] AC4: Address JSON includes: zip, country, province, city, address
- [ ] AC5: logistics_product_list is JSON array of {product_id, sku_id, quantity}
- [ ] AC6: Response: array of shipping options with vendor_code, vendor_name, shipping_type, delivery_time, fee
- [ ] AC7: Integration test with real product and address
- [ ] AC8: JSON file input support via @filename syntax

## Implementation Notes

Address structure:
```json
{
  "zip": "35022",
  "country": {"code": "US", "name": "United States"},
  "province": {"code": "AL", "name": "Alabama"},
  "city": {"code": "", "name": "Bessemer"},
  "address": "4595 Clubview Drive"
}
```

## Definition of Done

- Multi-product shipping calculation works
- Complex JSON parameters handled correctly
- Integration test passes
