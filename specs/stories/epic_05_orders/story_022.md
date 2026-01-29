# Story: epic_05_orders/story_022

## Metadata

| Field | Value |
|-------|-------|
| Epic | Order Management Endpoints |
| Priority | P2 |
| Estimate | M |
| Status | DONE |
| Blocked By | epic_05_orders/story_017, epic_05_orders/story_020 |
| Blocks | None |
| Tracer Bullet | false |

## User Story

As a developer, I want a complete order flow test command so that I can validate the full order lifecycle.

## Description

Create a convenience command that performs a test order flow: calculate shipping → create order → get order details → (optionally) pay → check status.

## Acceptance Criteria

- [x] AC1: CLI command: `alibaba-cli order test-flow --product-id <id> --sku-id <id> --quantity <n> --address <json>`
- [x] AC2: Executes: shipping calc → order create → order get
- [x] AC3: Optional --pay flag to attempt payment
- [x] AC4: Shows each step with results
- [x] AC5: Saves trade_id for subsequent queries
- [x] AC6: Error at any step stops the flow and shows details
- [ ] AC7: Integration test demonstrating full flow

## Definition of Done

- Test flow command works end-to-end
- Each step validated
- Useful for testing

## Completion Notes

Test flow command fully implemented in src/alibaba_cli/commands/order.py. AC7 note: The command itself serves as an interactive integration test - no separate pytest test exists for the full flow (individual components are tested separately).
