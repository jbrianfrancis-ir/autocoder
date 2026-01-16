---
phase: 6-structured-logging
plan: 02
type: execute
wave: 2
depends_on: ["6-01"]
files_modified:
  - agent.py
  - client.py
  - progress.py
  - prompts.py
autonomous: true

must_haves:
  truths:
    - "agent.py uses logger instead of print() for operational messages"
    - "client.py uses logger instead of print() for operational messages"
    - "progress.py uses logger instead of print() for operational messages"
    - "prompts.py uses logger instead of print() for warnings"
  artifacts:
    - path: "agent.py"
      provides: "Agent session logic with structured logging"
      contains: "logger = logging.getLogger(__name__)"
    - path: "client.py"
      provides: "Client configuration with structured logging"
      contains: "logger = logging.getLogger(__name__)"
    - path: "progress.py"
      provides: "Progress tracking with structured logging"
      contains: "logger = logging.getLogger(__name__)"
    - path: "prompts.py"
      provides: "Prompt loading with structured logging"
      contains: "logger = logging.getLogger(__name__)"
  key_links:
    - from: "agent.py"
      to: "logging_config.py"
      via: "logger uses configuration from dictConfig"
      pattern: "logging\\.getLogger\\(__name__\\)"
---

<objective>
Convert core agent modules from print() statements to structured logging.

Purpose: Implements LOG-01 by ensuring agent.py, client.py, progress.py, and prompts.py use consistent log format with timestamp, level, module, and message.

Output: Four core modules updated to use logging.getLogger(__name__) with appropriate log levels.
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
@agent.py
@client.py
@progress.py
@prompts.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Convert agent.py and client.py to structured logging</name>
  <files>agent.py, client.py</files>
  <action>
**agent.py changes:**

1. Add logging import and logger at module level (after existing imports):
   ```python
   import logging
   logger = logging.getLogger(__name__)
   ```

2. Convert print() statements to appropriate log levels:

   | Current print() | New logger call | Rationale |
   |-----------------|-----------------|-----------|
   | `print("Sending prompt...")` | `logger.info("Sending prompt to Claude Agent SDK")` | Normal operation |
   | `print(block.text, ...)` | Keep as print() | User-visible agent output |
   | `print(f"[Tool: {name}]")` | Keep as print() | User-visible agent output |
   | `print("   [BLOCKED]...")` | Keep as print() | User-visible agent output |
   | `print("   [Error]...")` | Keep as print() | User-visible agent output |
   | `print("   [Done]")` | Keep as print() | User-visible agent output |
   | `print("-" * 70)` | Keep as print() | User-visible formatting |
   | `print(f"Error during agent session: {e}")` | `logger.error("Error during agent session: %s", e)` | Error logging |
   | `print("=" * 70)` headers | Keep as print() | User-visible formatting |
   | `print(f"Project directory: {project_dir}")` | `logger.info("Project directory: %s", project_dir)` | Info |
   | `print(f"Model: {model}")` | `logger.info("Model: %s", model)` | Info |
   | `print("Mode: YOLO...")` | `logger.info("Mode: %s", "YOLO" if yolo_mode else "Standard")` | Info |
   | `print(f"Max iterations: {n}")` | `logger.info("Max iterations: %s", max_iterations or "Unlimited")` | Info |
   | `print("Fresh start...")` | `logger.info("Fresh start - will use initializer agent")` | Info |
   | `print("Continuing existing project")` | `logger.info("Continuing existing project")` | Info |
   | `print(f"Reached max iterations ({n})")` | `logger.info("Reached max iterations: %d", max_iterations)` | Info |
   | `print("Session encountered an error")` | `logger.warning("Session encountered an error, will retry")` | Warning |
   | `print("Preparing next session...")` | `logger.debug("Preparing next session")` | Debug |

3. Keep ALL user-visible output as print():
   - Agent text output (block.text)
   - Tool use indicators ([Tool: name], [Done], [Error], [BLOCKED])
   - Session banners (=== and --- lines)
   - Final instructions for running the app

**client.py changes:**

1. Add logging import and logger at module level:
   ```python
   import logging
   logger = logging.getLogger(__name__)
   ```

2. Convert all print() statements:
   | Current print() | New logger call |
   |-----------------|-----------------|
   | `print(f"Created security settings at {settings_file}")` | `logger.info("Created security settings at %s", settings_file)` |
   | `print("   - Sandbox enabled...")` | `logger.debug("Sandbox enabled (OS-level bash isolation)")` |
   | `print(f"   - Filesystem restricted to: {path}")` | `logger.debug("Filesystem restricted to: %s", project_dir.resolve())` |
   | `print("   - Bash commands restricted...")` | `logger.debug("Bash commands restricted to allowlist")` |
   | `print("   - MCP servers: ...")` | `logger.debug("MCP servers: %s", "features only (YOLO)" if yolo_mode else "playwright, features")` |
   | `print("   - Project settings enabled...")` | `logger.debug("Project settings enabled (skills, commands, CLAUDE.md)")` |
   | `print(f"   - Using system CLI: {cli}")` | `logger.info("Using system CLI: %s", system_cli)` |
   | `print("   - Warning: System Claude CLI not found...")` | `logger.warning("System Claude CLI not found, using bundled CLI")` |

Use % style formatting (not f-strings) to avoid eager string evaluation.
  </action>
  <verify>
Run: `python -c "import agent; import client; print('Imports OK')"`
Should print "Imports OK" without errors.

Run: `LOG_LEVEL=DEBUG python -c "from logging_config import configure_logging; configure_logging(); import logging; logging.getLogger('agent').debug('test'); logging.getLogger('client').debug('test')"`
Should execute without errors.
  </verify>
  <done>
agent.py and client.py use logger = logging.getLogger(__name__) and appropriate log levels. User-visible output remains as print().
  </done>
</task>

<task type="auto">
  <name>Task 2: Convert progress.py and prompts.py to structured logging</name>
  <files>progress.py, prompts.py</files>
  <action>
**progress.py changes:**

1. Add logging import and logger at module level:
   ```python
   import logging
   logger = logging.getLogger(__name__)
   ```

2. Convert print() statements:
   | Current print() | New logger call |
   |-----------------|-----------------|
   | `print(f"[Database error in count_passing_tests: {e}]")` | `logger.error("Database error in count_passing_tests: %s", e)` |
   | `print(f"[Webhook notification failed: {e}]")` | `logger.warning("Webhook notification failed: %s", e)` |
   | Session header prints (print_session_header) | Keep as print() - user-visible formatting |
   | Progress summary prints (print_progress_summary) | Keep as print() - user-visible output |

Note: print_session_header() and print_progress_summary() are intentionally user-facing output, NOT operational logging. Keep these as print().

**prompts.py changes:**

1. Add logging import and logger at module level:
   ```python
   import logging
   logger = logging.getLogger(__name__)
   ```

2. Convert print() statements:
   | Current print() | New logger call |
   |-----------------|-----------------|
   | `print(f"Warning: Could not read {path}: {e}")` | `logger.warning("Could not read %s: %s", path, e)` |
   | `print(f"  Warning: Could not copy {name}: {e}")` | `logger.warning("Could not copy %s: %s", dest_name, e)` |
   | `print(f"  Created prompt files: {files}")` | `logger.info("Created prompt files: %s", ", ".join(copied_files))` |
   | `print("Copied app_spec.txt to project directory")` | `logger.info("Copied app_spec.txt to project directory")` |
   | `print(f"Warning: Could not copy app_spec.txt: {e}")` | `logger.warning("Could not copy app_spec.txt: %s", e)` |
   | `print("Warning: No app_spec.txt found...")` | `logger.warning("No app_spec.txt found to copy to project directory")` |

All prompts.py output is operational/diagnostic, so all print() statements should become logger calls.

Use % style formatting for all logger calls.
  </action>
  <verify>
Run: `python -c "import progress; import prompts; print('Imports OK')"`
Should print "Imports OK" without errors.

Run: `LOG_LEVEL=DEBUG python -c "from logging_config import configure_logging; configure_logging(); import logging; logging.getLogger('progress').debug('test'); logging.getLogger('prompts').debug('test')"`
Should execute without errors.
  </verify>
  <done>
progress.py and prompts.py use logger = logging.getLogger(__name__) and appropriate log levels. User-visible session/progress output remains as print().
  </done>
</task>

</tasks>

<verification>
1. All four modules import successfully:
   ```bash
   python -c "import agent, client, progress, prompts; print('All modules import OK')"
   ```

2. Loggers are properly configured:
   ```bash
   LOG_LEVEL=DEBUG python -c "
   from logging_config import configure_logging
   configure_logging()
   import logging
   for mod in ['agent', 'client', 'progress', 'prompts']:
       lgr = logging.getLogger(mod)
       print(f'{mod}: {lgr.name}')
   "
   ```

3. No print() statements remain for operational logging (grep check):
   ```bash
   # Should find only user-visible prints (block.text, banners, session headers)
   grep -n "print(" agent.py client.py progress.py prompts.py
   ```
</verification>

<success_criteria>
- agent.py has `logger = logging.getLogger(__name__)` and uses logger for operational messages
- client.py has `logger = logging.getLogger(__name__)` and uses logger for all messages
- progress.py has `logger = logging.getLogger(__name__)` and uses logger for errors/warnings
- prompts.py has `logger = logging.getLogger(__name__)` and uses logger for warnings/info
- User-visible output (agent responses, session banners, progress display) remains as print()
- All logger calls use % style formatting (not f-strings)
</success_criteria>

<output>
After completion, create `.planning/phases/6-structured-logging/6-02-SUMMARY.md`
</output>
