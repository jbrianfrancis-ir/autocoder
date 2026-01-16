---
phase: 6-structured-logging
plan: 03
type: execute
wave: 2
depends_on: ["6-01"]
files_modified:
  - mcp_server/feature_mcp.py
  - autonomous_agent_demo.py
autonomous: true

must_haves:
  truths:
    - "MCP server has structured logging for database operations"
    - "autonomous_agent_demo.py uses logger for operational messages"
    - "Logging works correctly when MCP server runs as subprocess"
  artifacts:
    - path: "mcp_server/feature_mcp.py"
      provides: "MCP server with structured logging"
      contains: "logger = logging.getLogger(__name__)"
    - path: "autonomous_agent_demo.py"
      provides: "Entry point with logging configuration"
      contains: "configure_logging"
  key_links:
    - from: "mcp_server/feature_mcp.py"
      to: "logging_config.py"
      via: "Independent logging configuration for subprocess"
      pattern: "from logging_config import configure_logging"
    - from: "autonomous_agent_demo.py"
      to: "logging_config.py"
      via: "Configures logging before agent runs"
      pattern: "from logging_config import configure_logging"
---

<objective>
Add structured logging to MCP server and autonomous_agent_demo entry point.

Purpose: Completes LOG-01 coverage by adding logging to the MCP server (runs as subprocess) and the main CLI entry point. Ensures logging is configured correctly for both server and CLI contexts.

Output: mcp_server/feature_mcp.py with logging, autonomous_agent_demo.py with logging configuration.
</objective>

<execution_context>
@~/.claude/get-shit-done/workflows/execute-plan.md
@~/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/phases/6-structured-logging/6-RESEARCH.md
@.planning/phases/6-structured-logging/6-01-SUMMARY.md
@mcp_server/feature_mcp.py
@autonomous_agent_demo.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add logging to MCP server</name>
  <files>mcp_server/feature_mcp.py</files>
  <action>
The MCP server runs as a subprocess spawned by the Claude SDK. It needs its own logging configuration since it has a separate Python process.

1. Add imports at the top of the file (after existing imports):
   ```python
   import logging

   # Configure logging for subprocess context
   # MCP server runs as separate process, needs own configuration
   import sys
   sys.path.insert(0, str(Path(__file__).parent.parent))  # Already exists
   from logging_config import configure_logging
   configure_logging()

   logger = logging.getLogger(__name__)
   ```

2. Add logging to key operations:

   In `server_lifespan`:
   - `logger.info("Initializing MCP server for project: %s", PROJECT_DIR)`
   - `logger.debug("Database initialized at %s", PROJECT_DIR / "features.db")`
   - `logger.info("Loaded %d features from specs directory", len(specs))` (when loading from specs)
   - `logger.info("MCP server shutdown, database connection closed")`

   In `get_session`:
   - `logger.error("Database not initialized")` (before raising RuntimeError)

   In tool functions (add debug logging for operations):
   - `feature_get_stats`: `logger.debug("Getting feature stats")`
   - `feature_get_next`: `logger.debug("Getting next feature to implement")`
   - `feature_get_for_regression`: `logger.debug("Getting %d random passing features for regression", limit)`
   - `feature_mark_passing`: `logger.info("Feature %d marked as passing", feature_id)`
   - `feature_skip`: `logger.info("Feature %d skipped, moved to priority %d", feature_id, new_priority)`
   - `feature_mark_in_progress`: `logger.debug("Feature %d marked in-progress", feature_id)`
   - `feature_clear_in_progress`: `logger.debug("Feature %d in-progress cleared", feature_id)`
   - `feature_create_bulk`: `logger.info("Created %d features in bulk", created_count)`
   - `feature_sync_from_specs`: `logger.info("Synced specs: added=%d, updated=%d, unchanged=%d", added, updated, unchanged)`

   In exception handlers:
   - `feature_create_bulk` catch block: `logger.error("Bulk create failed: %s", e)`
   - `feature_sync_from_specs` catch block: `logger.error("Sync from specs failed: %s", e)`

3. Use % style formatting for all logger calls.

Note: The MCP server configures logging independently because it runs as a subprocess. The parent process (agent) and child process (MCP server) each call configure_logging() in their own process space.
  </action>
  <verify>
Run: `python -c "import mcp_server.feature_mcp; print('MCP server imports OK')"`
Should print "MCP server imports OK" without errors.

Run: `LOG_LEVEL=DEBUG python -c "import logging; from mcp_server.feature_mcp import mcp; print('MCP instance:', mcp.name)"`
Should show the MCP server name ("features").
  </verify>
  <done>
mcp_server/feature_mcp.py has structured logging with configure_logging() called at module load time and appropriate log levels for all operations.
  </done>
</task>

<task type="auto">
  <name>Task 2: Add logging to autonomous_agent_demo entry point</name>
  <files>autonomous_agent_demo.py</files>
  <action>
First, read the current content of autonomous_agent_demo.py to understand its structure.

Then update it:

1. Add logging configuration at the very top (after shebang/docstring, before other imports):
   ```python
   from logging_config import configure_logging
   configure_logging()

   import logging
   logger = logging.getLogger(__name__)
   ```

2. Convert operational print() statements to logger:
   - Startup messages -> logger.info()
   - Error messages -> logger.error()
   - Warning messages -> logger.warning()

3. Keep user-facing output as print():
   - Usage/help messages
   - Interactive prompts
   - Final status output

4. Log the entry point execution:
   ```python
   if __name__ == "__main__":
       logger.info("Starting autonomous agent demo")
       # ... existing argparse code ...
       logger.info("Configuration: project=%s, model=%s, yolo=%s", project_dir, model, yolo_mode)
   ```

The exact changes depend on what print() statements exist in the file. The principle is:
- Operational/diagnostic messages -> logger
- User-facing output/prompts -> print()
  </action>
  <verify>
Run: `python autonomous_agent_demo.py --help`
Should print help text (user-facing) without logging configuration errors.

Run: `LOG_LEVEL=DEBUG python -c "from logging_config import configure_logging; configure_logging(); import autonomous_agent_demo; print('Demo module imports OK')"`
Should print "Demo module imports OK" without errors.
  </verify>
  <done>
autonomous_agent_demo.py configures logging at startup and uses logger for operational messages while keeping user-facing output as print().
  </done>
</task>

</tasks>

<verification>
1. MCP server can be imported and has logging:
   ```bash
   LOG_LEVEL=DEBUG python -c "
   from logging_config import configure_logging
   configure_logging()
   import logging
   lgr = logging.getLogger('mcp_server.feature_mcp')
   lgr.debug('Test debug message')
   lgr.info('Test info message')
   print('MCP logging OK')
   "
   ```

2. autonomous_agent_demo can be imported:
   ```bash
   python -c "import autonomous_agent_demo; print('Demo OK')"
   ```

3. Full integration test (brief run):
   ```bash
   # This tests that logging doesn't break the agent startup
   timeout 5 python autonomous_agent_demo.py --help || true
   # Should show help text and exit cleanly
   ```
</verification>

<success_criteria>
- mcp_server/feature_mcp.py calls configure_logging() at module load
- mcp_server/feature_mcp.py has logger = logging.getLogger(__name__)
- MCP server logs database initialization, feature operations, and errors
- autonomous_agent_demo.py calls configure_logging() before other imports
- autonomous_agent_demo.py logs configuration and startup info
- All modules can be imported without errors
- LOG_LEVEL environment variable controls log output
</success_criteria>

<output>
After completion, create `.planning/phases/6-structured-logging/6-03-SUMMARY.md`
</output>
