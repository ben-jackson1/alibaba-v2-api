# Story: epic_04_shipping/story_015

## Metadata

| Field | Value |
|-------|-------|
| Epic | Shipping Calculation Endpoints |
| Priority | P2 |
| Estimate | S |
| Status | PENDING |
| Blocked By | epic_04_shipping/story_013 |
| Blocks | None |
| Tracer Bullet | false |

## User Story

As a developer, I want automatic dispatch location fallback so that shipping calculations work even when the primary location fails.

## Description

Implement fallback logic to try alternative dispatch locations (CN → US → MX) when shipping calculation returns no results.

## Acceptance Criteria

- [ ] AC1: When shipping calculation returns empty, automatically retry with next dispatch location
- [ ] AC2: Fallback order: CN → US → MX
- [ ] AC3: Shows which dispatch location succeeded in output
- [ ] AC4: Optional flag --no-fallback to disable this behavior
- [ ] AC5: Integration test demonstrates fallback working

## Definition of Done

- Fallback logic works as expected
- Output indicates which location was used
- Tests cover fallback scenarios
