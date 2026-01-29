# Story: epic_02_auth/story_006

## Metadata

| Field | Value |
|-------|-------|
| Epic | Authentication Endpoints |
| Priority | P0 |
| Estimate | S |
| Status | PENDING |
| Blocked By | epic_02_auth/story_005 |
| Blocks | None |
| Tracer Bullet | false |

## User Story

As a developer, I want to refresh my access token using a refresh token so that I don't need to re-authorize.

## Description

Implement the `/auth/token/refresh` endpoint to get a new access token using a refresh token.

## Acceptance Criteria

- [ ] AC1: CLI command: `alibaba-cli auth token refresh --refresh-token <token>`
- [ ] AC2: API endpoint: `/auth/token/refresh`
- [ ] AC3: Does NOT require access_token
- [ ] AC4: Request param: `refresh_token`
- [ ] AC5: Response includes: access_token, refresh_token, expires_in, refresh_expires_in
- [ ] AC6: Returns JSON formatted output
- [ ] AC7: Error handling for invalid/expired refresh tokens
- [ ] AC8: Integration test with real refresh token

## Implementation Notes

Note: If `refresh_expires_in` = 0, the token cannot be refreshed and user must re-authorize.

## Definition of Done

- CLI command works with real refresh token
- Response structure matches documentation
- Error cases handled appropriately
