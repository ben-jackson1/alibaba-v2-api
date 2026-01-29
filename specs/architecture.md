# System Architecture: Alibaba API CLI

## Overview

This document describes the architecture of the Alibaba API CLI, a Python command-line tool for validating Alibaba.com Open Platform API v2 documentation.

---

## Architecture Principles

1. **Simplicity Over Cleverness** - Straightforward code is easier to validate
2. **Explicit Over Implicit** - Clear parameter passing, no magic
3. **Testable by Design** - Every component can be unit tested
4. **Documentation-Driven** - Code structure mirrors API documentation

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User                                    │
│  (developer validating API documentation)                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ CLI commands
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CLI Layer (Click)                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │ auth        │ │ product     │ │ shipping    │               │
│  │ commands    │ │ commands    │ │ commands    │               │
│  └─────────────┘ └─────────────┘ └─────────────┘               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │ order       │ │ test flow   │ │ status      │               │
│  │ commands    │ │ commands    │ │ commands    │               │
│  └─────────────┘ └─────────────┘ └─────────────┘               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ API calls
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Client Layer                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ AlibabaClient                                             │  │
│  │  - _request() method with signing                        │  │
│  │  - Environment/credential loading                        │  │
│  │  - Response parsing and error handling                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Signature Calculator                                      │  │
│  │  - Parameter sorting                                     │  │
│  │  - HMAC-SHA256 signing                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP requests
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    HTTP Layer (httpx)                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ HTTP Client                                               │  │
│  │  - GET/POST requests                                     │  │
│  │  - Timeout handling                                      │  │
│  │  - Response parsing                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTPS
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              Alibaba.com Open Platform API                      │
│  https://openapi-api.alibaba.com/rest                           │
│  https://openapi-api-sandbox.alibaba.com/rest                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Design

### 1. CLI Layer

**Purpose**: User-facing command interface

**Components**:
```
src/alibaba_cli/
├── __init__.py
├── cli.py              # Main entry point, global options
├── commands/
│   ├── __init__.py
│   ├── auth.py         # auth token create/refresh/status
│   ├── product.py      # product list/get/inventory
│   ├── shipping.py     # shipping calculate
│   └── order.py        # order create/pay/list/get
└── output.py           # Response formatting (JSON/raw)
```

**Responsibilities**:
- Parse command-line arguments
- Load credentials from env vars
- Invoke appropriate client methods
- Format and display responses
- Handle user-facing errors

### 2. Client Layer

**Purpose**: API communication abstraction

**Components**:
```
src/alibaba_cli/
├── client.py           # AlibabaClient class
├── signing.py          # calculate_signature function
├── config.py           # Configuration loading
├── exceptions.py       # Custom exception classes
└── models/
    ├── __init__.py
    ├── auth.py         # Token response models
    ├── product.py      # Product response models
    ├── shipping.py     # Shipping response models
    └── order.py        # Order response models
```

**Responsibilities**:
- Construct signed requests
- Execute HTTP calls
- Parse responses
- Handle API errors
- Validate response structure

### 3. Test Layer

**Purpose**: Automated documentation validation

**Components**:
```
tests/
├── conftest.py          # Pytest fixtures
├── unit/
│   ├── test_signing.py
│   ├── test_client.py
│   └── test_models.py
└── integration/
    ├── test_auth.py
    ├── test_products.py
    ├── test_shipping.py
    └── test_orders.py
```

**Responsibilities**:
- Validate response structures
- Check required fields present
- Verify field types match documentation
- Test error handling

---

## Data Flow

### Request Flow

```
1. User executes CLI command
   ↓
2. CLI parses arguments and loads credentials
   ↓
3. Command handler creates AlibabaClient instance
   ↓
4. Client builds request with business params
   ↓
5. Client adds system params (app_key, timestamp, sign_method)
   ↓
6. Client calculates signature using all params
   ↓
7. Client adds signature to params
   ↓
8. Client sends HTTP request via httpx
   ↓
9. Client receives and parses response
   ↓
10. Client validates response structure
    ↓
11. Client returns parsed data or raises exception
    ↓
12. CLI formats and outputs response
```

### Error Handling Flow

```
1. API returns error response
   ↓
2. Client extracts code, message, request_id
   ↓
3. Client maps known error codes to helpful messages
   ↓
4. Client raises AlibabaAPIError with context
   ↓
5. CLI catches exception and displays user-friendly error
   ↓
6. CLI exits with non-zero status code
```

---

## Key Decisions

### ADR-001: Stateless CLI (No Credential Storage)

**Status**: Accepted

**Context**: User specified "No persistence" for credentials.

**Decision**: All credentials passed via CLI flags or environment variables. No token caching, no configuration files.

**Options Considered**:
| Option | Pros | Cons |
|--------|------|------|
| No persistence | Simple, secure, no state management | Must provide credentials each time |
| File storage | Convenient | User explicitly rejected |
| Keyring storage | Secure, convenient | User explicitly rejected |

**Consequences**:
- Simpler codebase
- No state management bugs
- More verbose CLI usage
- Better security (no stored secrets)

**Reversibility**: Easy - could add storage layer later

---

### ADR-002: Pydantic for Response Validation

**Status**: Accepted

**Context**: Need to validate API responses against documentation structure.

**Decision**: Use Pydantic models for all API responses.

**Options Considered**:
| Option | Pros | Cons |
|--------|------|------|
| Pydantic | Type validation, coercions, good errors | Extra dependency |
| Manual validation | No dependency | Verbose, error-prone |
| dataclasses | Built-in | No validation |

**Consequences**:
- Catches response structure mismatches early
- Better type safety
- Clear documentation of expected structure
- Additional dependency

**Reversibility**: Moderate - would need to rewrite validation code

---

### ADR-003: httpx Over requests

**Status**: Accepted

**Context**: HTTP client library choice.

**Decision**: Use httpx for HTTP requests.

**Options Considered**:
| Option | Pros | Cons |
|--------|------|------|
| httpx | Async support, HTTP/2, typed | Slightly less familiar |
| requests | Very familiar, proven | No native async |

**Consequences**:
- Future-proof for async operations
- Better performance potential
- Modern API design
- Learning curve for developers used to requests

**Reversibility**: Easy - API is similar to requests

---

## Implementation Sequence

### Phase 1: Foundation (Tracer Bullets)
1. **story_001**: Project scaffolding - validates toolchain setup
2. **story_002**: Request signing - validates crypto implementation
3. **story_003**: Base client - validates HTTP layer works
4. **story_005**: Auth token - validates end-to-end auth flow

### Phase 2: Core Features
5. **story_008**: Product list - validates product discovery
6. **story_013**: Shipping calculate - validates freight API
7. **story_017**: Order create - validates order management

### Phase 3: Testing
8. **story_023-026**: Integration tests - validate all endpoints

---

## Security Considerations

### Credential Handling
- Credentials read from environment variables only
- Never log credentials or tokens
- Redact sensitive data in error messages

### HTTPS Only
- All API communication over HTTPS
- Certificate validation enabled
- No HTTP fallback

### Signature Security
- HMAC-SHA256 for request signing
- App secret never logged or exposed
- Timestamp in milliseconds prevents replay attacks

---

## Error Handling Strategy

### Exception Hierarchy

```
AlibabaError (base)
├── AlibabaAPIError          # API returned an error response
├── AlibabaAuthError         # Authentication/authorization failed
├── AlibabaValidationError   # Request validation failed
├── AlibabaNetworkError      # Network/HTTP error
└── AlibabaSignatureError    # Signature calculation failed
```

### Error Response Format

```python
class AlibabaAPIError(Exception):
    def __init__(self, code: str, message: str, request_id: str | None = None):
        self.code = code
        self.message = message
        self.request_id = request_id
        super().__init__(f"[{code}] {message}")
```

---

## Performance Considerations

### Timeout Configuration
- Default: 30 seconds per request
- Configurable via `--timeout` flag
- No retry logic (design choice for simplicity)

### Response Sizes
- Large responses (product details) pretty-printed
- Use `--raw` for exact API response
- Streaming not implemented (not needed for validation)

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-29 | 1.0 | Initial architecture |
