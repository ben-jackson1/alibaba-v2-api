# Story: epic_06_integration/story_025

## Metadata

| Field | Value |
|-------|-------|
| Epic | Integration Test Suite |
| Priority | P0 |
| Estimate | M |
| Status | PENDING |
| Blocked By | epic_04_shipping/story_013, epic_04_shipping/story_014, epic_06_integration/story_023 |
| Blocks | None |
| Tracer Bullet | false |

## User Story

As a developer, I want automated tests for shipping endpoints so that I can verify freight calculation APIs match documentation.

## Description

Create pytest integration tests for basic and advanced shipping calculation endpoints.

## Acceptance Criteria

- [ ] AC1: Test file: `tests/integration/test_shipping.py`
- [ ] AC2: Test basic freight calculation returns shipping options
- [ ] AC3: Test each shipping option has: shipping_type, vendor_name, delivery_time, fee
- [ ] AC4: Test fee has amount and currency
- [ ] AC5: Test advanced calculation with multiple products
- [ ] AC6: Test with different dispatch locations (CN, US, MX)
- [ ] AC7: Test empty results when route unavailable
- [ ] AC8: Validate response structure against documentation

## Definition of Done

- All shipping endpoint tests implemented
- Response structures validated
- Tests pass with real data
