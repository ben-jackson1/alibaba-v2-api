# Story: epic_03_products/story_012

## Metadata

| Field | Value |
|-------|-------|
| Epic | Product Discovery Endpoints |
| Priority | P2 |
| Estimate | M |
| Status | PENDING |
| Blocked By | epic_03_products/story_008, epic_03_products/story_009 |
| Blocks | None |
| Tracer Bullet | false |

## User Story

As a developer, I want a `product search` convenience command that combines list and detail calls so that I can quickly find products with full details.

## Description

Create a convenience command that fetches product IDs from a list, then retrieves full details for each.

## Acceptance Criteria

- [ ] AC1: CLI command: `alibaba-cli product search --scene-id <id> [--limit <n>]`
- [ ] AC2: Calls product list, then product get for each ID
- [ ] AC3: Limit defaults to 5 products to avoid overwhelming output
- [ ] AC4: Returns array of full product details
- [ ] AC5: Shows progress indicator for multiple API calls
- [ ] AC6: Gracefully handles products that fail to load
- [ ] AC7: Integration test with small limit

## Definition of Done

- Convenience command works as expected
- Output is useful for validation
- Tests cover error cases
