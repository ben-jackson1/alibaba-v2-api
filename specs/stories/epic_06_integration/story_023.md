# Story: epic_06_integration/story_023

## Metadata

| Field | Value |
|-------|-------|
| Epic | Integration Test Suite |
| Priority | P0 |
| Estimate | M |
| Status | PENDING |
| Blocked By | epic_02_auth/story_005 |
| Blocks | epic_06_integration/story_024, epic_06_integration/story_025, epic_06_integration/story_026 |
| Tracer Bullet | true |

## User Story

As a developer, I want automated tests for authentication endpoints so that I can verify the auth APIs match documentation.

## Description

Create pytest integration tests for OAuth token creation and refresh endpoints.

## Acceptance Criteria

- [ ] AC1: Test file: `tests/integration/test_auth.py`
- [ ] AC2: Fixture for test credentials (app_key, app_secret, OAuth code)
- [ ] AC3: Test token_create returns expected fields: access_token, refresh_token, expires_in, user_info
- [ ] AC4: Test user_info has: country, loginId, user_id, seller_id
- [ ] AC5: Test token_refresh with valid refresh_token
- [ ] AC6: Test error handling for invalid code
- [ ] AC7: Tests marked with pytest.mark.integration
- [ ] AC8: Tests skipped if credentials not provided
- [ ] AC9: Tests validate response structure matches documentation

## Implementation Notes

Use pytest fixtures with environment variable checks:

```python
@pytest.fixture
def creds():
    return {
        "app_key": os.getenv("ALIBABA_APP_KEY"),
        "app_secret": os.getenv("ALIBABA_APP_SECRET"),
        "code": os.getenv("ALIBABA_TEST_AUTH_CODE")
    }

@pytest.mark.skipif(not creds()["app_key"], reason="No credentials")
def test_token_create(creds):
    ...
```

## Definition of Done

- Auth tests pass with real credentials
- Response fields validated
- Skips gracefully when no credentials
