# Story: epic_06_integration/story_026

## Metadata

| Field | Value |
|-------|-------|
| Epic | Integration Test Suite |
| Priority | P1 |
| Estimate | L |
| Status | PENDING |
| Blocked By | epic_05_orders/story_017, epic_05_orders/story_019, epic_05_orders/story_020, epic_05_orders/story_021, epic_06_integration/story_023 |
| Blocks | None |
| Tracer Bullet | false |

## User Story

As a developer, I want automated tests for order endpoints so that I can verify order management APIs match documentation.

## Description

Create pytest integration tests for order listing, details, logistics, and payment endpoints.

## Acceptance Criteria

- [ ] AC1: Test file: `tests/integration/test_orders.py`
- [ ] AC2: Test order list returns orders with trade_id, trade_status, dates
- [ ] AC3: Test order get returns full order details including products, amounts, addresses
- [ ] AC4: Test order products have: product_id, sku_id, quantity, unit_price
- [ ] AC5: Test logistics query returns logistic_status and shipping details
- [ ] AC6: Test tracking returns events with event_code, event_name, event_time
- [ ] AC7: Test order creation (optional, may require test order)
- [ ] AC8: All tests validate response structure against documentation
- [ ] AC9: Tests clearly marked if they create real orders (require confirmation)

## Implementation Notes

Order creation tests should:
- Use a special test product/flag
- Create minimal orders
- Clearly indicate they will charge money
- Be skipped by default, run only with explicit flag

## Definition of Done

- Order endpoint tests implemented
- Response structures validated
- Order creation test safely implemented
- Tests pass with real data
