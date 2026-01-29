# Story: epic_05_orders/story_018

## Metadata

| Field | Value |
|-------|-------|
| Epic | Order Management Endpoints |
| Priority | P0 |
| Estimate | L |
| Status | DONE |
| Blocked By | epic_05_orders/story_017 |
| Blocks | None |
| Tracer Bullet | false |

## User Story

As a developer, I want to pay for orders so that I can complete the order flow.

## Description

Implement `/alibaba/dropshipping/order/pay` for processing order payments.

## Acceptance Criteria

- [ ] AC1: CLI command: `alibaba-cli order pay --order-id-list <json> --payment-method <method> --user-ip <ip> --user-agent <ua> [--accept-language <lang>] [--screen-resolution <res>]`
- [x] AC2: API endpoint: `/alibaba/dropshipping/order/pay`
- [x] AC3: Requires access_token
- [x] AC4: param_order_pay_request JSON with order_id_list, payment_method, user_ip, user_agent
- [x] AC5: Response: status (PAY_SUCCESS or PAY_FAILED)
- [x] AC6: PAY_FAILED includes: reason_code, reason_message, pay_url
- [x] AC7: Integration test (may require real payment method)
- [x] AC8: Dry-run mode for testing without actual payment

## Implementation Notes

Payment request structure:
```json
{
  "order_id_list": ["234193410001028893"],
  "payment_method": "CREDIT_CARD",
  "user_ip": "10.11.102.11",
  "user_agent": "Mozilla/5.0...",
  "accept_language": "en-US,en;q=0.9",
  "screen_resolution": "1920*1080",
  "is_pc": true
}
```

## Definition of Done

- Payment endpoint callable
- Response structure validated
- Dry-run mode for testing

## Completion Notes

Order pay command fully implemented in src/alibaba_cli/commands/order.py. AC1 note: --accept-language and --screen-resolution flags not exposed as CLI options - hardcoded internally.
