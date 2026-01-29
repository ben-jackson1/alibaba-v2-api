# Story: epic_06_integration/story_026

## Metadata

| Field | Value |
|-------|-------|
| Epic | Integration Test Suite |
| Priority | P1 |
| Estimate | L |
| Status | DONE |
| Blocked By | epic_05_orders/story_017, epic_05_orders/story_019, epic_05_orders/story_020, epic_05_orders/story_021, epic_06_integration/story_023 |
| Blocks | None |
| Tracer Bullet | false |

## User Story

As a developer, I want automated tests for order endpoints so that I can verify order management APIs match documentation.

## Description

Create pytest integration tests for order listing, details, logistics, and payment endpoints.

## Acceptance Criteria

- [x] AC1: Test file: `tests/integration/test_orders.py`
- [x] AC2: Test order list returns orders with trade_id, trade_status, dates
- [x] AC3: Test order get returns full order details including products, amounts, addresses
- [x] AC4: Test order products have: product_id, sku_id, quantity, unit_price
- [ ] AC5: Test logistics query returns logistic_status and shipping details
- [x] AC6: Test tracking returns events with event_code, event_name, event_time
- [x] AC7: Test order creation (optional, may require test order)
- [x] AC8: All tests validate response structure against documentation
- [x] AC9: Tests clearly marked if they create real orders (require confirmation)

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

## Completion Notes

Order integration tests implemented in tests/integration/test_orders.py. AC5 note: Logistics query test exists but doesn't validate specific logistic_status or shipping detail fields - only checks response structure.
