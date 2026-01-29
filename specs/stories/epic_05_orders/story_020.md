# Story: epic_05_orders/story_020

## Metadata

| Field | Value |
|-------|-------|
| Epic | Order Management Endpoints |
| Priority | P0 |
| Estimate | M |
| Status | PENDING |
| Blocked By | epic_05_orders/story_019 |
| Blocks | None |
| Tracer Bullet | false |

## User Story

As a developer, I want to get detailed order information so that I can validate the complete order response structure.

## Description

Implement `/alibaba/order/get` for retrieving comprehensive order details.

## Acceptance Criteria

- [ ] AC1: CLI command: `alibaba-cli order get --trade-id <id> [--language <code>]`
- [ ] AC2: API endpoint: `/alibaba/order/get`
- [ ] AC3: Requires access_token
- [ ] AC4: Response validated for: trade_id, trade_status, create_date, shipping_address
- [ ] AC5: order_products array validated for: product_id, sku_id, quantity, unit_price
- [ ] AC6: Amounts validated: product_total_amount, shipment_fee, total_amount
- [ ] AC7: Integration test with real trade_id
- [ ] AC8: Full response output with --raw flag

## Definition of Done

- Order details retrieved completely
- All documented fields validated
- Integration test passes
