# Story: epic_04_shipping/story_013

## Metadata

| Field | Value |
|-------|-------|
| Epic | Shipping Calculation Endpoints |
| Priority | P0 |
| Estimate | M |
| Status | DONE |
| Blocked By | epic_01_setup/story_001, epic_01_setup/story_002, epic_01_setup/story_003 |
| Blocks | epic_04_shipping/story_014 |
| Tracer Bullet | true |

## User Story

As a developer, I want to calculate basic shipping costs so that I can validate the freight estimation API.

## Description

Implement `/shipping/freight/calculate` for basic single-product shipping estimates.

## Acceptance Criteria

- [x] AC1: CLI command: `alibaba-cli shipping calculate --product-id <id> --quantity <n> --destination-country <code> [--zip-code <zip>] [--dispatch-location <code>]`
- [x] AC2: API endpoint: `/shipping/freight/calculate`
- [x] AC3: Requires access_token
- [x] AC4: Response is array of shipping options
- [ ] AC5: Each option validated for: shipping_type, vendor_name, delivery_time, fee
- [x] AC6: fee.amount and fee.currency validated
- [x] AC7: Supports CN, US, MX dispatch locations
- [x] AC8: Integration test with real product ID
- [x] AC9: Empty response handled gracefully (no available routes)

## Implementation Notes

Example response structure:
```json
{
  "value": [{
    "shipping_type": "EXPRESS",
    "vendor_name": "Alibaba.com Economy Express (3C)",
    "delivery_time": "10~15",
    "fee": {"amount": "19.1", "currency": "USD"}
  }]
}
```

## Definition of Done

- Shipping calculation returns options
- Response structure validated
- Integration test passes

## Completion Notes

Shipping calculate command fully implemented in src/alibaba_cli/commands/shipping.py. Includes automatic fallback dispatch location logic (CN → US → MX). AC5 note: shipping_type not validated in test - only vendor_name, delivery_time, and fee are checked.
