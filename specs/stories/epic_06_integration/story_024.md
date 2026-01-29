# Story: epic_06_integration/story_024

## Metadata

| Field | Value |
|-------|-------|
| Epic | Integration Test Suite |
| Priority | P0 |
| Estimate | L |
| Status | PENDING |
| Blocked By | epic_03_products/story_008, epic_03_products/story_009, epic_06_integration/story_023 |
| Blocks | None |
| Tracer Bullet | false |

## User Story

As a developer, I want automated tests for product endpoints so that I can verify product APIs match documentation.

## Description

Create pytest integration tests for all product discovery endpoints.

## Acceptance Criteria

- [ ] AC1: Test file: `tests/integration/test_products.py`
- [ ] AC2: Test product list with scene ID returns product IDs
- [ ] AC3: Test product get returns full product details with all documented fields
- [ ] AC4: Test product inventory returns inventory counts
- [ ] AC5: Test local product list by country
- [ ] AC6: Test cross-border product list
- [ ] AC7: Validate SKUs have: sku_id, ladder_price, sku_attr_list
- [ ] AC8: Validate images array is present
- [ ] AC9: Tests validate response structure against documentation

## Implementation Notes

Key validation points:
- Product has `eCompanyId` (supplier ID)
- Each SKU has `ladder_price` array with min_quantity, max_quantity, price, currency
- `sku_attr_list` has attr_name_id, attr_name_desc, attr_value_id, attr_value_desc

## Definition of Done

- All product endpoint tests implemented
- Response structures validated
- Tests pass with real data
