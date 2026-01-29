# Technology Stack: Alibaba API CLI

## Overview

This document specifies the technology choices for the Alibaba API CLI & Integration Test Suite, designed for documentation validation rather than production use.

---

## Core Language

**Python 3.12+**

### Rationale
- User specified Python 3.12+ explicitly
- Modern type hints and syntax improve code quality
- Excellent ecosystem for CLI tools and HTTP clients
- Native support for asynchronous operations (if needed later)

### Key Features Used
- Type hints (`dict[str, str]`, etc.)
- Match statements (for error code handling)
- `functools.cache` for response memoization
- `pathlib` for path operations

---

## CLI Framework

**Click 8.x**

### Rationale
| Factor | Click | Typer | Argparse |
|--------|-------|-------|----------|
| Maturity | Mature | Newer | Built-in, verbose |
| Decorator syntax | Yes | Yes | No |
| Subcommands | Easy | Easy | Manual |
| Documentation | Excellent | Growing | Sparse |
| Adoption | Proven | Growing | N/A |

### Alternatives Considered

**Typer** (rejected):
- Pros: Modern, uses type hints
- Cons: Less mature, smaller ecosystem
- Decision: Click is more proven for CLI tools

**Argparse** (rejected):
- Pros: Built-in, no dependency
- Cons: Verbose, manual subcommand handling
- Decision: Developer experience matters more

---

## HTTP Client

**httpx 0.27+**

### Rationale
| Factor | httpx | requests |
|--------|-------|----------|
| Async support | Yes | Limited (via aiohttp) |
| HTTP/2 | Yes | No |
| Type hints | Full | Partial |
| API compatibility | requests-like | N/A |
| Maintenance | Active | Minimal |

### Usage Pattern
```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.get(url, params=params, timeout=30)
    return response.json()
```

### Alternatives Considered

**requests** (rejected):
- Pros: Familiar, stable
- Cons: No native async, no HTTP/2
- Decision: httpx is future-proof

---

## Data Validation

**Pydantic 2.x**

### Rationale
- Validate API responses against documented schemas
- Type coercion for string → int conversions
- JSON serialization/deserialization
- Excellent error messages

### Usage Pattern
```python
from pydantic import BaseModel, Field

class AlibabaResponse(BaseModel):
    code: str
    request_id: str
    value: dict | None = None
```

---

## Testing Framework

**pytest 8.x + pytest-asyncio**

### Rationale
- De facto standard for Python testing
- Fixture system for credential management
- Markers for integration tests
- Async support for httpx testing

### Required Plugins
- `pytest-asyncio`: Async test support
- `pytest-mock`: Mocking utilities
- `pytest-cov`: Coverage reporting

---

## Code Quality

**ruff 0.6+**

### Rationale
- Fast (written in Rust)
- Replaces flake8, black, isort
- Single config file
- IDE integration

### Configuration
```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]
```

---

## Type Checking

**mypy 1.11+**

### Rationale
- Static type checking
- Catches bugs before runtime
- Better IDE autocomplete

### Strict Mode
- `strict = True` for core modules
- Slightly relaxed for test modules

---

## Development Tools

| Tool | Purpose | Version |
|------|---------|---------|
| `hatch` | Project/build management | 1.11+ |
| `pre-commit` | Git hooks automation | 3.8+ |
| `coverage` | Code coverage reporting | 7.6+ |

---

## Packaging

**pyproject.toml** (PEP 621)

### Build System
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "alibaba-cli"
version = "0.1.0"
requires-python = ">=3.12"
```

### Entry Point
```toml
[project.scripts]
alibaba-cli = "alibaba_cli.cli:main"
```

---

## Dependencies Summary

### Production
```
click>=8.1.0
httpx>=0.27.0
pydantic>=2.9.0
```

### Development
```
pytest>=8.3.0
pytest-asyncio>=0.24.0
pytest-mock>=3.14.0
pytest-cov>=5.0.0
ruff>=0.6.0
mypy>=1.11.0
pre-commit>=3.8.0
```

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-29 | 1.0 | Initial tech stack selection |
