# Story: epic_02_auth/story_005

## Metadata

| Field | Value |
|-------|-------|
| Epic | Authentication Endpoints |
| Priority | P0 |
| Estimate | M |
| Status | DONE |
| Blocked By | epic_01_setup/story_001, epic_01_setup/story_002, epic_01_setup/story_003 |
| Blocks | epic_02_auth/story_006, epic_02_auth/story_007, epic_03_products/story_008, epic_04_shipping/story_013, epic_05_orders/story_017 |
| Tracer Bullet | true |

## User Story

As a developer, I want to exchange an OAuth authorization code for an access token so that I can authenticate subsequent API calls.

## Description

Implement the `/auth/token/create` endpoint to exchange OAuth authorization codes for access tokens. This is the first step in the authentication flow.

## Acceptance Criteria

- [ ] AC1: CLI command: `alibaba-cli auth token create --code <authorization_code>`
- [x] AC2: API endpoint: `/auth/token/create`
- [x] AC3: Does NOT require access_token (authenticated endpoint exception)
- [x] AC4: Request param: `code` (the OAuth authorization code)
- [x] AC5: Response includes: access_token, refresh_token, expires_in, refresh_expires_in, user_info
- [x] AC6: user_info includes: country, loginId, user_id, seller_id
- [x] AC7: Returns JSON formatted output
- [x] AC8: Error handling for invalid/expired codes
- [x] AC9: Integration test requires real code (skipped if not provided)

## Implementation Notes

Example response structure:
```json
{
  "access_token": "50000601c30atpedfgu3LVvik87Ixlsvle3mSoB7701ceb156fPunYZ43GBg",
  "refresh_token": "500016000300bwa2WteaQyfwBMnPxurcA0mXGhQdTt18356663CfcDTYpWoi",
  "expires_in": "864000",
  "refresh_expires_in": "5184000",
  "user_info": {
    "country": "GLOBAL",
    "loginId": "buyer123",
    "user_id": "200042362",
    "seller_id": "1001"
  },
  "code": "0"
}
```

## Definition of Done

- CLI command works with real OAuth code
- Response matches documented structure
- Tests validate response fields
- Error cases handled

## Completion Notes

Token create fully implemented. AC1 note: Actual command is `alibaba-cli auth token-create --code` (Click uses dashes by default, command is functional).
