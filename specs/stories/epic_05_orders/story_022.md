# Story: epic_05_orders/story_022

## Metadata

| Field | Value |
|-------|-------|
| Epic | Order Management Endpoints |
| Priority | P2 |
| Estimate | M |
| Status | PENDING |
| Blocked By | epic_05_orders/story_017, epic_05_orders/story_020 |
| Blocks | None |
| Tracer Bullet | false |

## User Story

As a developer, I want a complete order flow test command so that I can validate the full order lifecycle.

## Description

Create a convenience command that performs a test order flow: calculate shipping → create order → get order details → (optionally) pay → check status.

## Acceptance Criteria

- [ ] AC1: CLI command: `alibaba-cli order test-flow --product-id <id> --sku-id <id> --quantity <n> --address <json>`
- [ ] AC2: Executes: shipping calc → order create → order get
- [ ] AC3: Optional --pay flag to attempt payment
- [ ] AC4: Shows each step with results
- [ ] AC5: Saves trade_id for subsequent queries
- [ ] AC6: Error at any step stops the flow and shows details
- [ ] AC7: Integration test demonstrating full flow

## Definition of Done

- Test flow command works end-to-end
- Each step validated
- Useful for testing
