# Story: epic_01_setup/story_003

## Metadata

| Field | Value |
|-------|-------|
| Epic | Project Setup & Core Infrastructure |
| Priority | P0 |
| Estimate | M |
| Status | PENDING |
| Blocked By | epic_01_setup/story_002 |
| Blocks | epic_02_auth/story_005, epic_03_products/story_008, epic_04_shipping/story_013, epic_05_orders/story_017 |
| Tracer Bullet | false |

## User Story

As a developer, I want a base API client that handles signing and HTTP requests so that I don't repeat code for each endpoint.

## Description

Create a base API client class that encapsulates request signing, HTTP calls, and common response handling.

## Acceptance Criteria

- [ ] AC1: `AlibabaClient` class with app_key, app_secret, access_token optional params
- [ ] AC2: `use_sandbox` param to toggle base URL
- [ ] AC3: `_request()` method that handles signing, HTTP call, and response parsing
- [ ] AC4: System params (app_key, sign_method, timestamp) added automatically
- [ ] AC5: access_token added to params when provided
- [ ] AC6: Supports both GET and POST methods
- [ ] AC7: Returns parsed JSON response or raises exception on error
- [ ] AC8: Unit tests with mocked HTTP responses
- [ ] AC9: Error response format: code, message, request_id extracted

## Implementation Notes

Base URLs:
- Production: `https://openapi-api.alibaba.com/rest`
- Sandbox: `https://openapi-api-sandbox.alibaba.com/rest`

System params:
- `app_key`: From client init
- `sign_method`: Always "sha256"
- `timestamp`: Milliseconds since epoch
- `sign`: Calculated signature
- `access_token`: When provided

## Definition of Done

- Client makes properly signed requests
- Error responses are parsed correctly
- Tests cover both success and error cases
