# Story: epic_04_shipping/story_014

## Metadata

| Field | Value |
|-------|-------|
| Epic | Shipping Calculation Endpoints |
| Priority | P0 |
| Estimate | L |
| Status | DONE |
| Blocked By | epic_04_shipping/story_013 |
| Blocks | None |
| Tracer Bullet | false |

## User Story

As a developer, I want to calculate shipping for multiple products so that I can validate the advanced freight API used before order creation.

## Description

Implement `/order/freight/calculate` for multi-product shipping calculations with full address details.

## Acceptance Criteria

- [x] AC1: CLI command: `alibaba-cli shipping calculate-advanced --e-company-id <id> --destination-country <code> --address <json> --logistics-product-list <json> [--dispatch-location <code>]`
- [x] AC2: API endpoint: `/order/freight/calculate`
- [x] AC3: Requires access_token
- [x] AC4: Address JSON includes: zip, country, province, city, address
- [x] AC5: logistics_product_list is JSON array of {product_id, sku_id, quantity}
- [x] AC6: Response: array of shipping options with vendor_code, vendor_name, shipping_type, delivery_time, fee
- [x] AC7: Integration test with real product and address
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

## Completion Notes

Advanced shipping calculate command fully implemented in src/alibaba_cli/commands/shipping.py. AC8 note: JSON file input via @filename syntax not implemented - command accepts JSON string directly only.
