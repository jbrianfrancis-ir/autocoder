---
phase: 6-structured-logging
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - logging_config.py
  - server/main.py
autonomous: true

must_haves:
  truths:
    - "Logging can be configured via LOG_LEVEL environment variable"
    - "Different modules can have different log levels via LOG_LEVEL_<MODULE>"
    - "All log messages include timestamp, level, module name, and message"
  artifacts:
    - path: "logging_config.py"
      provides: "Centralized logging configuration with dictConfig"
      exports: ["configure_logging", "get_logging_config"]
    - path: "server/main.py"
      provides: "Server entry point with logging configured before imports"
      contains: "configure_logging"
  key_links:
    - from: "server/main.py"
      to: "logging_config.py"
      via: "import and call configure_logging()"
      pattern: "from logging_config import configure_logging"
---

<objective>
Create centralized logging configuration module and wire it into the server entry point.

Purpose: Establishes the foundation for consistent, configurable logging across all Python modules. This enables LOG-01 (consistent format) and LOG-02 (configurable levels).

Output: logging_config.py module with dictConfig setup, server/main.py updated to configure logging on startup.
</objective>

<execution_context>
@~/.claude/get-shit-done/workflows/execute-plan.md
@~/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/phases/6-structured-logging/6-RESEARCH.md
@server/main.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create logging_config.py module</name>
  <files>logging_config.py</files>
  <action>
Create a new file `logging_config.py` in the project root with:

1. Environment variable handling:
   - `LOG_LEVEL` env var for global level (default: INFO)
   - `LOG_LEVEL_<MODULE>` pattern for per-module overrides (e.g., LOG_LEVEL_AGENT=DEBUG)
   - Use `os.environ.get()` with `.upper()` for case-insensitivity

2. Log format constants:
   - `LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"`
   - `DATE_FORMAT = "%Y-%m-%d %H:%M:%S"`

3. Helper function `get_module_level(module_name: str) -> str`:
   - Builds env key as `LOG_LEVEL_{module_name.upper().replace('.', '_')}`
   - Returns module-specific level or falls back to global LOG_LEVEL

4. Configuration builder `get_logging_config() -> dict`:
   - Returns dictConfig-compatible dict with:
     - `version: 1`
     - `disable_existing_loggers: False` (critical - preserves third-party loggers)
     - Formatter "standard" using LOG_FORMAT and DATE_FORMAT
     - Handler "console" streaming to stderr
     - Root logger at LOG_LEVEL
     - Per-module loggers for: agent, client, progress, prompts, registry, server, mcp_server
     - Third-party noise reduction: uvicorn and uvicorn.access at WARNING

5. Entry point function `configure_logging() -> None`:
   - Calls `logging.config.dictConfig(get_logging_config())`
   - Should be called once at application startup

Use % style formatting in log messages (not f-strings) to avoid eager evaluation. See research doc Pattern 1 for reference implementation.
  </action>
  <verify>
Run: `python -c "from logging_config import configure_logging, get_logging_config; print(get_logging_config())"`
Should print a valid dict with version, formatters, handlers, root, and loggers keys.
  </verify>
  <done>
logging_config.py exists with configure_logging() and get_logging_config() functions that produce valid dictConfig configuration.
  </done>
</task>

<task type="auto">
  <name>Task 2: Configure logging in server entry point</name>
  <files>server/main.py</files>
  <action>
Update `server/main.py` to configure logging as the first action:

1. Add import at the very top of the file (before other imports):
   ```python
   from logging_config import configure_logging
   configure_logging()  # Must be before other imports that might log
   ```

2. Update the `if __name__ == "__main__":` block to prevent uvicorn from overwriting our config:
   ```python
   if __name__ == "__main__":
       import uvicorn
       uvicorn.run(
           "server.main:app",
           host="127.0.0.1",
           port=8888,
           reload=True,
           log_config=None,  # Prevent uvicorn from overwriting our logging config
       )
   ```

IMPORTANT: The configure_logging() call must be BEFORE the FastAPI import and all other imports. This ensures loggers created during import use our configuration.

Do NOT modify any other functionality in main.py - only add logging configuration.
  </action>
  <verify>
Run: `LOG_LEVEL=DEBUG python -c "from server.main import app; print('Server imports successfully')"`
Should print "Server imports successfully" without errors.

Run: `LOG_LEVEL=WARNING python -c "import logging; from server.main import app; print(logging.getLogger('server').level)"`
Should show the logger exists and configuration was applied.
  </verify>
  <done>
server/main.py configures logging before other imports and passes log_config=None to uvicorn.run().
  </done>
</task>

</tasks>

<verification>
1. Environment variable configuration works:
   ```bash
   LOG_LEVEL=DEBUG python -c "from logging_config import get_logging_config; print(get_logging_config()['root']['level'])"
   # Should print: DEBUG
   ```

2. Per-module override works:
   ```bash
   LOG_LEVEL=INFO LOG_LEVEL_AGENT=DEBUG python -c "from logging_config import get_logging_config; cfg = get_logging_config(); print(cfg['loggers']['agent']['level'])"
   # Should print: DEBUG
   ```

3. Server starts without errors:
   ```bash
   timeout 3 python -m server.main || true
   # Should start server briefly without logging configuration errors
   ```
</verification>

<success_criteria>
- logging_config.py exists with configure_logging() and get_logging_config()
- LOG_LEVEL environment variable controls global log level
- LOG_LEVEL_<MODULE> pattern enables per-module overrides
- server/main.py calls configure_logging() before other imports
- uvicorn.run() receives log_config=None to prevent config override
- Log format includes timestamp, level, module name, and message
</success_criteria>

<output>
After completion, create `.planning/phases/6-structured-logging/6-01-SUMMARY.md`
</output>
