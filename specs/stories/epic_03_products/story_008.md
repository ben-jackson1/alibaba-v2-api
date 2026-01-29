# Story: epic_03_products/story_008

## Metadata

| Field | Value |
|-------|-------|
| Epic | Product Discovery Endpoints |
| Priority | P0 |
| Estimate | M |
| Status | DONE |
| Blocked By | epic_01_setup/story_001, epic_01_setup/story_002, epic_01_setup/story_003, epic_02_auth/story_005 |
| Blocks | epic_03_products/story_009, epic_03_products/story_010, epic_03_products/story_011, epic_03_products/story_012 |
| Tracer Bullet | true |

## User Story

As a developer, I want to retrieve product lists from different scene IDs so that I can discover available products.

## Description

Implement the general product list endpoint `/eco/buyer/product/check` which returns products based on scene ID (curated dropshipping lists).

## Acceptance Criteria

- [x] AC1: CLI command: `alibaba-cli product list --scene-id <id> [--page <n>] [--page-size <n>]`
- [x] AC2: API endpoint: `/eco/buyer/product/check`
- [x] AC3: Requires access_token
- [x] AC4: Request param: `query_req` as JSON string with scene_id, page, page_size
- [x] AC5: Response: result.result_data is array of product IDs
- [x] AC6: Response: result.result_total shows total available
- [x] AC7: Default page=0, page_size=50, max page_size=100
- [x] AC8: Integration test with real scene ID (e.g., 906124611)
- [x] AC9: Validated response structure matches documentation

## Implementation Notes

Available scene IDs from documentation:
- 906124611: Standard US-based fulfillment
- 906168847: Cross-border fulfillment (China to US)
- 907135637: Fast fulfillment from US (within 48 hours)
- 907732810: Dropshipping-eligible products from Mexico
- 907180667: Top-selling products from the US
- 907180664: Top-selling products from Mexico

## Definition of Done

- CLI returns list of product IDs
- Response structure validated
- Integration test passes

## Completion Notes

Product list endpoint fully implemented. API requires additional undocumented parameters (size, index, product_type) which have been added. Integration test passes.
