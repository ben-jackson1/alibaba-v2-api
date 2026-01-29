# Story: epic_01_setup/story_002

## Metadata

| Field | Value |
|-------|-------|
| Epic | Project Setup & Core Infrastructure |
| Priority | P0 |
| Estimate | M |
| Status | PENDING |
| Blocked By | epic_01_setup/story_001 |
| Blocks | epic_02_auth/story_005, epic_03_products/story_008, epic_04_shipping/story_013, epic_05_orders/story_017 |
| Tracer Bullet | false |

## User Story

As a developer, I want the request signing implemented correctly so that Alibaba API accepts my requests.

## Description

Implement HMAC-SHA256 request signing according to Alibaba specification. This is the core authentication mechanism for all API calls.

## Acceptance Criteria

- [ ] AC1: Function `calculate_signature(api_path: str, params: dict, app_secret: str) -> str`
- [ ] AC2: Parameters are sorted alphabetically (ASCII order) before concatenation
- [ ] AC3: Concatenation format: key1value1key2value2... (no separators)
- [ ] AC4: Message = api_path + concatenated_params
- [ ] AC5: HMAC-SHA256 signature generated using app_secret
- [ ] AC6: Signature returned as uppercase hex string
- [ ] AC7: Unit tests verify signature matches documented examples
- [ ] AC8: Edge case: empty params dict handled correctly
- [ ] AC9: Edge case: special characters in values handled correctly

## Implementation Notes

Reference the algorithm in docs/alibaba-api-integration-v2.md:

```python
def calculate_signature(api_path: str, params: dict, app_secret: str) -> str:
    sorted_params = dict(sorted(params.items()))
    concat_string = ''.join(f"{k}{v}" for k, v in sorted_params.items())
    message = f"{api_path}{concat_string}"
    signature = hmac.new(
        app_secret.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest().upper()
    return signature
```

## Definition of Done

- All unit tests pass
- Signature matches test vectors (if available) or matches documentation
- Code is typed and documented
