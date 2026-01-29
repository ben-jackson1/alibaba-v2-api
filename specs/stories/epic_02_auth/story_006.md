# Story: epic_02_auth/story_006

## Metadata

| Field | Value |
|-------|-------|
| Epic | Authentication Endpoints |
| Priority | P0 |
| Estimate | S |
| Status | DONE |
| Blocked By | epic_02_auth/story_005 |
| Blocks | None |
| Tracer Bullet | false |

## User Story

As a developer, I want to refresh my access token using a refresh token so that I don't need to re-authorize.

## Description

Implement the `/auth/token/refresh` endpoint to get a new access token using a refresh token.

## Acceptance Criteria

- [ ] AC1: CLI command: `alibaba-cli auth token refresh --refresh-token <token>`
- [x] AC2: API endpoint: `/auth/token/refresh`
- [x] AC3: Does NOT require access_token
- [x] AC4: Request param: `refresh_token`
- [x] AC5: Response includes: access_token, refresh_token, expires_in, refresh_expires_in
- [x] AC6: Returns JSON formatted output
- [x] AC7: Error handling for invalid/expired refresh tokens
- [x] AC8: Integration test with real refresh token

## Implementation Notes

Note: If `refresh_expires_in` = 0, the token cannot be refreshed and user must re-authorize.

## Definition of Done

- CLI command works with real refresh token
- Response structure matches documentation
- Error cases handled appropriately

## Completion Notes

Token refresh fully implemented. AC1 note: Actual command is `alibaba-cli auth token-refresh --refresh-token` (Click uses dashes by default).
