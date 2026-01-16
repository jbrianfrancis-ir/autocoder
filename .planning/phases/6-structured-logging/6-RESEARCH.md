# Phase 6: Structured Logging - Research

**Researched:** 2026-01-16
**Domain:** Python logging, stdlib configuration, FastAPI/Uvicorn integration
**Confidence:** HIGH

## Summary

This research addresses how to implement consistent, configurable logging across all Python modules in the autocoder project. The project currently has a mix of:
- 13 files using `logging.getLogger(__name__)` (server modules)
- 25+ files using `print()` statements (CLI tools, agent modules)
- No centralized configuration
- No environment variable support for log levels

The standard approach is to use Python's built-in `logging` module with `dictConfig` for centralized configuration. This is sufficient for the project's needs and avoids adding new dependencies.

**Primary recommendation:** Use Python stdlib `logging` with a centralized `dictConfig` configuration module. No external libraries needed.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| logging | stdlib | Core logging facility | Built-in, universally supported, no dependencies |
| logging.config | stdlib | dictConfig, fileConfig | Standard way to configure logging hierarchies |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| structlog | 25.x | Structured JSON logging | If machine-parseable logs needed (v2 feature, not v1.1) |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| stdlib logging | structlog | More features, but adds dependency and complexity |
| stdlib logging | loguru | Simpler API, but less control over hierarchy |
| dictConfig | basicConfig | basicConfig is simpler but less flexible for per-module config |

**Installation:**
```bash
# No new dependencies needed - use stdlib logging
# Already in Python standard library
```

## Architecture Patterns

### Recommended Project Structure
```
autocoder/
├── logging_config.py        # NEW: Centralized logging configuration
├── agent.py                 # Update: import logging_config, use logger
├── client.py                # Update: use logger instead of print
├── progress.py              # Update: use logger instead of print
├── prompts.py               # Update: use logger instead of print
├── registry.py              # Already uses logging
├── server/
│   ├── __init__.py
│   ├── main.py              # Update: configure logging on startup
│   ├── websocket.py         # Already uses logging
│   └── services/            # Already uses logging
└── mcp_server/
    └── feature_mcp.py       # Update: add logging
```

### Pattern 1: Centralized Configuration Module
**What:** Single module that configures all logging behavior
**When to use:** Always - this is the entry point for logging setup
**Example:**
```python
# logging_config.py
# Source: https://docs.python.org/3/howto/logging.html

import logging
import logging.config
import os
import sys

# Environment variable for global log level (default: INFO)
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

# Per-module overrides via environment variables
# Format: LOG_LEVEL_<MODULE> where <MODULE> is uppercase module name
# Example: LOG_LEVEL_AGENT=DEBUG

def get_module_level(module_name: str) -> str:
    """Get log level for a specific module from environment."""
    env_key = f"LOG_LEVEL_{module_name.upper().replace('.', '_')}"
    return os.environ.get(env_key, LOG_LEVEL).upper()

# Standard log format: timestamp, level, module, message
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def get_logging_config() -> dict:
    """Build logging configuration dictionary."""
    return {
        "version": 1,
        "disable_existing_loggers": False,  # Important: preserve existing loggers
        "formatters": {
            "standard": {
                "format": LOG_FORMAT,
                "datefmt": DATE_FORMAT,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",  # Handler accepts all; logger filters
                "formatter": "standard",
                "stream": "ext://sys.stderr",
            },
        },
        "root": {
            "level": LOG_LEVEL,
            "handlers": ["console"],
        },
        "loggers": {
            # Per-module configuration
            "agent": {"level": get_module_level("agent")},
            "client": {"level": get_module_level("client")},
            "progress": {"level": get_module_level("progress")},
            "registry": {"level": get_module_level("registry")},
            "server": {"level": get_module_level("server")},
            "mcp_server": {"level": get_module_level("mcp_server")},
            # Third-party noise reduction
            "uvicorn": {"level": "WARNING"},
            "uvicorn.access": {"level": "WARNING"},
        },
    }


def configure_logging() -> None:
    """Configure logging for the application. Call once at startup."""
    config = get_logging_config()
    logging.config.dictConfig(config)
```

### Pattern 2: Module-Level Logger Setup
**What:** Each module gets its own logger using `__name__`
**When to use:** In every Python module that needs logging
**Example:**
```python
# In any module (e.g., agent.py)
# Source: https://docs.python.org/3/howto/logging.html

import logging

logger = logging.getLogger(__name__)

def my_function():
    logger.debug("Debug details")
    logger.info("Normal operation")
    logger.warning("Something unexpected")
    logger.error("Operation failed")
```

### Pattern 3: Startup Configuration
**What:** Configure logging before any other imports that might log
**When to use:** In main entry points (server, CLI)
**Example:**
```python
# server/main.py - configure before other imports
# Source: https://docs.python.org/3/howto/logging.html

from logging_config import configure_logging
configure_logging()  # Must be first

# Now import everything else
from fastapi import FastAPI
# ... rest of imports
```

### Anti-Patterns to Avoid
- **Using print() for operational messages:** Use logger.info() instead
- **Using root logger directly:** Always use `logging.getLogger(__name__)`
- **Configuring logging in library modules:** Only configure in entry points
- **Setting handlers on individual loggers:** Use centralized configuration
- **Using disable_existing_loggers=True:** Breaks third-party library logging

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Log formatting | Custom format strings | logging.Formatter with standard format | Handles edge cases, timestamps correctly |
| Log level parsing | Manual string checking | getattr(logging, level) | Handles all levels including custom ones |
| Per-module config | Manual if/else chains | dictConfig loggers section | Hierarchical, inherits correctly |
| Environment config | Custom parser | os.environ.get with default | Standard, well-understood |
| Timestamp formatting | strftime in format string | logging datefmt parameter | Consistent, tested |

**Key insight:** Python's logging module is complex under the hood (handlers, formatters, filters, propagation) but dictConfig abstracts this cleanly. Attempting to manually configure logging usually misses edge cases.

## Common Pitfalls

### Pitfall 1: Configuring Logging Too Late
**What goes wrong:** Log messages emitted before configuration are lost or use defaults
**Why it happens:** Imports trigger code that logs before configure_logging() is called
**How to avoid:** Configure logging as the very first action in entry points
**Warning signs:** Missing log messages at startup, uvicorn/fastapi logs but not application logs

### Pitfall 2: disable_existing_loggers=True (Default)
**What goes wrong:** Loggers created before dictConfig become silent
**Why it happens:** dictConfig defaults to True for this setting
**How to avoid:** Always set `"disable_existing_loggers": False` in config
**Warning signs:** Some modules log, others are silent; depends on import order

### Pitfall 3: Uvicorn Overwriting Configuration
**What goes wrong:** Uvicorn applies its own logging config, overwriting yours
**Why it happens:** uvicorn.run() calls dictConfig internally
**How to avoid:** Pass log_config=None to uvicorn.run() or configure after startup
**Warning signs:** Log format reverts to uvicorn default, custom levels ignored

### Pitfall 4: Logging Sensitive Data
**What goes wrong:** API keys, passwords appear in logs
**Why it happens:** Logging full request/response objects, exception args
**How to avoid:** Sanitize before logging, use existing redaction patterns
**Warning signs:** Security audit finds credentials in log files

### Pitfall 5: Using f-strings for Log Messages
**What goes wrong:** String interpolation happens even if log level filters message
**Why it happens:** f-strings evaluate immediately, not lazily
**How to avoid:** Use % formatting: `logger.debug("Processing %s", item)`
**Warning signs:** Performance issues in debug logging, complex objects stringified unnecessarily

## Code Examples

Verified patterns from official sources:

### Environment Variable Configuration
```python
# Source: https://gist.github.com/juanpabloaj/3e6a41f683c1767c17824811db01165b
import os
import logging

LOGLEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(level=LOGLEVEL, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
```

### dictConfig with Per-Module Levels
```python
# Source: https://docs.python.org/3/library/logging.config.html
import logging.config

config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "stream": "ext://sys.stderr"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"]
    },
    "loggers": {
        "myapp.database": {"level": "DEBUG"},
        "myapp.api": {"level": "WARNING"},
    }
}

logging.config.dictConfig(config)
```

### Replacing print() with logger
```python
# Before (current state in agent.py)
print(f"Project directory: {project_dir}")
print(f"Error during agent session: {e}")

# After
logger = logging.getLogger(__name__)
logger.info("Project directory: %s", project_dir)
logger.error("Error during agent session: %s", e)
```

### FastAPI/Uvicorn Integration
```python
# Source: https://pawamoy.github.io/posts/unify-logging-for-a-gunicorn-uvicorn-app/
# In server/main.py

from logging_config import configure_logging
configure_logging()  # Configure BEFORE uvicorn starts

# When running uvicorn programmatically:
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server.main:app",
        host="127.0.0.1",
        port=8888,
        log_config=None,  # Prevent uvicorn from overwriting our config
    )
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| basicConfig | dictConfig | Python 2.7+ (2010) | More flexible, hierarchical |
| INI config files | YAML/JSON with dictConfig | Python 2.7+ | Programmatic control |
| Print statements | logging module | Always was best practice | Structured, configurable |

**Deprecated/outdated:**
- `logging.warn()`: Use `logging.warning()` instead (warn is deprecated)
- `fileConfig()`: Use `dictConfig()` for new code (more flexible)

## Open Questions

Things that couldn't be fully resolved:

1. **CLI vs Server Log Destination**
   - What we know: Server should log to stderr; CLI should output to stdout for user
   - What's unclear: Should CLI keep print() for user-facing output or use logging with stdout handler?
   - Recommendation: Keep print() for intentional user output (progress bars, prompts), use logging for operational messages

2. **MCP Server Logging**
   - What we know: MCP servers run as subprocesses with their own logging context
   - What's unclear: Whether they should configure logging independently or inherit from parent
   - Recommendation: Configure independently in feature_mcp.py since it runs as separate process

## Sources

### Primary (HIGH confidence)
- [Python logging HOWTO](https://docs.python.org/3/howto/logging.html) - Core patterns, dictConfig, format strings
- [Python logging.config documentation](https://docs.python.org/3/library/logging.config.html) - dictConfig schema, configuration options

### Secondary (MEDIUM confidence)
- [Unified logging for Gunicorn/Uvicorn](https://pawamoy.github.io/posts/unify-logging-for-a-gunicorn-uvicorn-app/) - FastAPI integration patterns
- [Better Stack Python Logging Best Practices](https://betterstack.com/community/guides/logging/python/python-logging-best-practices/) - Environment variable patterns
- [Environment variable log level gist](https://gist.github.com/juanpabloaj/3e6a41f683c1767c17824811db01165b) - Simple env var pattern

### Tertiary (LOW confidence)
- [structlog documentation](https://www.structlog.org/en/stable/standard-library.html) - Reference for v2 features (JSON output)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Python stdlib is well-documented and stable
- Architecture: HIGH - dictConfig patterns are established best practice
- Pitfalls: HIGH - Well-documented in official guides and community

**Research date:** 2026-01-16
**Valid until:** Indefinite (stdlib logging is stable, patterns don't change)

## Current State Analysis

### Files Using logging.getLogger(__name__) (13 files)
Already following best practice, need centralized configuration:
- server/websocket.py
- server/services/assistant_chat_session.py
- server/services/spec_chat_session.py
- server/services/assistant_database.py
- server/services/process_manager.py
- server/routers/features.py
- server/routers/assistant_chat.py
- server/routers/filesystem.py
- server/routers/spec_creation.py
- registry.py

### Files Using print() (need conversion)
High priority (core modules):
- agent.py (28 print statements - mix of user output and logging)
- client.py (10 print statements)
- progress.py (8 print statements)
- prompts.py (5 print statements)

Medium priority (CLI tools):
- start.py (31 print statements - mostly user prompts, keep as print)
- start_ui.py (22 print statements - mostly user prompts, keep as print)
- autonomous_agent_demo.py (7 print statements)

Low priority (dev tools):
- test_security.py (31 print statements - test output, can stay as print)
- api/migration.py (8 print statements)

### Files with No Logging (need addition)
- mcp_server/feature_mcp.py
- spec_parser.py

---
*Research complete: 2026-01-16*
