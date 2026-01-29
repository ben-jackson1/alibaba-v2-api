# Story: epic_03_products/story_011

## Metadata

| Field | Value |
|-------|-------|
| Epic | Product Discovery Endpoints |
| Priority | P1 |
| Estimate | S |
| Status | PENDING |
| Blocked By | epic_03_products/story_008 |
| Blocks | None |
| Tracer Bullet | false |

## User Story

As a developer, I want to check product inventory so that I can validate stock levels before ordering.

## Description

Implement `/eco/buyer/product/inventory` to check inventory levels for products and SKUs.

## Acceptance Criteria

- [ ] AC1: CLI command: `alibaba-cli product inventory --product-id <id> [--sku-id <id>] [--shipping-from <code>]`
- [ ] AC2: API endpoint: `/eco/buyer/product/inventory`
- [ ] AC3: Requires access_token
- [ ] AC4: Request param: `inv_req` as JSON with product_id, optional sku_id, shipping_from
- [ ] AC5: Response: inventory_count and inventory_unit per SKU
- [ ] AC6: Response includes shipping_from country code
- [ ] AC7: Integration test with real product ID
- [ ] AC8: Error handling when product/SKU not found

## Definition of Done

- Inventory query returns stock levels
- Response structure validated
- Tests pass
