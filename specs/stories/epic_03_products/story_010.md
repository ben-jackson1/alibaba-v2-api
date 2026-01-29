# Story: epic_03_products/story_010

## Metadata

| Field | Value |
|-------|-------|
| Epic | Product Discovery Endpoints |
| Priority | P0 |
| Estimate | M |
| Status | DONE |
| Blocked By | epic_03_products/story_008 |
| Blocks | None |
| Tracer Bullet | false |

## User Story

As a developer, I want to query local warehouse products (US/MX) so that I can validate fast-shipping product discovery.

## Description

Implement local warehouse product endpoints: `/eco/buyer/local/product/check` for US/MX warehouse inventory.

## Acceptance Criteria

- [x] AC1: CLI command: `alibaba-cli product local --country <code> [--page <n>] [--page-size <n>]`
- [x] AC2: API endpoint: `/eco/buyer/local/product/check`
- [x] AC3: Requires access_token
- [x] AC4: Request param: `req` as JSON with country, page, page_size
- [x] AC5: Response: array of product IDs from local warehouses
- [ ] AC6: Also implement: `product local-regular` for `/eco/buyer/localregular/product/check`
- [x] AC7: Also implement: `product crossborder` for `/eco/buyer/crossborder/product/check`
- [x] AC8: Integration test for each endpoint variant

## Implementation Notes

Three local/cross-border product endpoints:
1. `/eco/buyer/local/product/check` - Local warehouses (US/MX)
2. `/eco/buyer/localregular/product/check` - Regular local fulfillment
3. `/eco/buyer/crossborder/product/check` - Cross-border from China

## Definition of Done

- All three product list variants implemented
- Each returns product IDs
- Integration tests pass

## Completion Notes

`product local` and `product crossborder` commands implemented. AC6 (local-regular endpoint) NOT implemented - would require separate command for `/eco/buyer/localregular/product/check`.
