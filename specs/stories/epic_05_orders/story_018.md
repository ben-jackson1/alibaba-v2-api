# Story: epic_05_orders/story_018

## Metadata

| Field | Value |
|-------|-------|
| Epic | Order Management Endpoints |
| Priority | P0 |
| Estimate | L |
| Status | PENDING |
| Blocked By | epic_05_orders/story_017 |
| Blocks | None |
| Tracer Bullet | false |

## User Story

As a developer, I want to pay for orders so that I can complete the order flow.

## Description

Implement `/alibaba/dropshipping/order/pay` for processing order payments.

## Acceptance Criteria

- [ ] AC1: CLI command: `alibaba-cli order pay --order-id-list <json> --payment-method <method> --user-ip <ip> --user-agent <ua> [--accept-language <lang>] [--screen-resolution <res>]`
- [ ] AC2: API endpoint: `/alibaba/dropshipping/order/pay`
- [ ] AC3: Requires access_token
- [ ] AC4: param_order_pay_request JSON with order_id_list, payment_method, user_ip, user_agent
- [ ] AC5: Response: status (PAY_SUCCESS or PAY_FAILED)
- [ ] AC6: PAY_FAILED includes: reason_code, reason_message, pay_url
- [ ] AC7: Integration test (may require real payment method)
- [ ] AC8: Dry-run mode for testing without actual payment

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
