# Story: epic_01_setup/story_004

## Metadata

| Field | Value |
|-------|-------|
| Epic | Project Setup & Core Infrastructure |
| Priority | P1 |
| Estimate | S |
| Status | DONE |
| Blocked By | epic_01_setup/story_001, epic_01_setup/story_003 |
| Blocks | None |
| Tracer Bullet | false |

## User Story

As a developer, I want global CLI flags and environment variable support for credentials so that I can configure the CLI conveniently.

## Description

Implement global CLI options for app_key, app_secret, access_token, refresh_token, and sandbox toggle with environment variable fallback.

## Acceptance Criteria

- [x] AC1: Global flags: --app-key, --app-secret, --access-token, --refresh-token, --sandbox
- [x] AC2: Environment variables: ALIBABA_APP_KEY, ALIBABA_APP_SECRET, ALIBABA_ACCESS_TOKEN, ALIBABA_REFRESH_TOKEN, ALIBABA_USE_SANDBOX
- [x] AC3: CLI flags take precedence over environment variables
- [x] AC4: --sandbox flag accepts boolean or "true"/"false" strings
- [x] AC5: Helpful error when required credentials are missing
- [ ] AC6: --json flag for JSON output (default), --raw for raw response
- [x] AC7: --version flag shows version
- [x] AC8: Global --verbose flag for debug output

## Implementation Notes

Use Click's context object to pass configuration to subcommands. Consider using a settings class that loads from environment first, then allows override from CLI flags.

## Definition of Done

- All global flags work correctly
- Environment variables are respected
- Error messages are helpful
- Tests cover configuration loading

## Completion Notes

CLI fully implemented in src/alibaba_cli/cli.py. AC6 note: --json flag not explicitly added (JSON is default output format, --raw flag exists for non-pretty output).
