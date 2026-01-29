# Story: epic_03_products/story_009

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

As a developer, I want to get detailed product information so that I can validate the complete product response structure.

## Description

Implement `/eco/buyer/product/description` to retrieve full product details including variants, pricing, and images.

## Acceptance Criteria

- [ ] AC1: CLI command: `alibaba-cli product get --product-id <id>`
- [ ] AC2: API endpoint: `/eco/buyer/product/description`
- [ ] AC3: Requires access_token
- [ ] AC4: Request param: `query_req` as JSON with product_id
- [ ] AC5: Response validated for: product_id, title, images, skus[], currency, min_order_quantity
- [ ] AC6: Each SKU validated for: sku_id, ladder_price[], sku_attr_list[]
- [ ] AC7: Integration test with real product ID
- [ ] AC8: Large response pretty-printed for readability

## Implementation Notes

Key response fields to validate:
- `eCompanyId`: Supplier ID (needed for shipping)
- `skus[].sku_id`: Variant ID (needed for orders)
- `skus[].ladder_price`: Volume pricing tiers
- `images`: Array of image URLs

## Definition of Done

- Full product details retrieved
- All documented fields present in response
- Integration test passes
