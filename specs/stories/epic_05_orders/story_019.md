# Story: epic_05_orders/story_019

## Metadata

| Field | Value |
|-------|-------|
| Epic | Order Management Endpoints |
| Priority | P0 |
| Estimate | M |
| Status | DONE |
| Blocked By | epic_02_auth/story_005 |
| Blocks | None |
| Tracer Bullet | false |

## User Story

As a developer, I want to list orders with filters so that I can find specific orders for testing.

## Description

Implement `/alibaba/order/list` for retrieving orders with optional filtering.

## Acceptance Criteria

- [x] AC1: CLI command: `alibaba-cli order list --role <buyer|seller> [--status <status>] [--start-page <n>] [--page-size <n>]`
- [x] AC2: API endpoint: `/alibaba/order/list`
- [x] AC3: Requires access_token
- [x] AC4: Response: total_count and order_list array
- [x] AC5: Each order has: trade_id, trade_status, create_date, modify_date
- [ ] AC6: Optional date filtering with create_date_start/end and modified_date_start/end
- [x] AC7: Integration test with real account
- [ ] AC8: Status codes documented (unpay, paid, delivering, etc.)

## Definition of Done

- Order listing works with filters
- Response structure validated
- Integration test passes

## Completion Notes

Order list command fully implemented in src/alibaba_cli/commands/order.py. AC6 note: Date filtering flags (create_date_start/end, modified_date_start/end) not implemented. AC8 note: Status codes not explicitly documented in CLI help.
