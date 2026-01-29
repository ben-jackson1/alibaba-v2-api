# Story: epic_03_products/story_010

## Metadata

| Field | Value |
|-------|-------|
| Epic | Product Discovery Endpoints |
| Priority | P0 |
| Estimate | M |
| Status | PENDING |
| Blocked By | epic_03_products/story_008 |
| Blocks | None |
| Tracer Bullet | false |

## User Story

As a developer, I want to query local warehouse products (US/MX) so that I can validate fast-shipping product discovery.

## Description

Implement local warehouse product endpoints: `/eco/buyer/local/product/check` for US/MX warehouse inventory.

## Acceptance Criteria

- [ ] AC1: CLI command: `alibaba-cli product local --country <code> [--page <n>] [--page-size <n>]`
- [ ] AC2: API endpoint: `/eco/buyer/local/product/check`
- [ ] AC3: Requires access_token
- [ ] AC4: Request param: `req` as JSON with country, page, page_size
- [ ] AC5: Response: array of product IDs from local warehouses
- [ ] AC6: Also implement: `product local-regular` for `/eco/buyer/localregular/product/check`
- [ ] AC7: Also implement: `product crossborder` for `/eco/buyer/crossborder/product/check`
- [ ] AC8: Integration test for each endpoint variant

## Implementation Notes

Three local/cross-border product endpoints:
1. `/eco/buyer/local/product/check` - Local warehouses (US/MX)
2. `/eco/buyer/localregular/product/check` - Regular local fulfillment
3. `/eco/buyer/crossborder/product/check` - Cross-border from China

## Definition of Done

- All three product list variants implemented
- Each returns product IDs
- Integration tests pass
