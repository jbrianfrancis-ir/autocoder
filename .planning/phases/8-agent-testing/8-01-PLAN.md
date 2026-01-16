---
phase: 8-agent-testing
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - tests/__init__.py
  - tests/conftest.py
  - tests/test_agent.py
  - pyproject.toml
autonomous: true

must_haves:
  truths:
    - "pytest tests/ passes with no errors"
    - "run_agent_session normal flow returns ('continue', response_text)"
    - "run_agent_session exception returns ('error', error_message)"
    - "TextBlock content is accumulated in response"
    - "ToolUseBlock and ToolResultBlock are handled without crashing"
  artifacts:
    - path: "tests/__init__.py"
      provides: "Package marker"
    - path: "tests/conftest.py"
      provides: "Shared pytest fixtures for mocking ClaudeSDKClient"
      exports: ["mock_text_block", "mock_assistant_message", "mock_sdk_client"]
    - path: "tests/test_agent.py"
      provides: "Unit tests for run_agent_session"
      min_lines: 80
    - path: "pyproject.toml"
      provides: "pytest-asyncio configuration"
      contains: "asyncio_mode"
  key_links:
    - from: "tests/test_agent.py"
      to: "agent.py"
      via: "from agent import run_agent_session"
      pattern: "from agent import"
    - from: "tests/conftest.py"
      to: "tests/test_agent.py"
      via: "pytest fixture injection"
      pattern: "@pytest.fixture"
---

<objective>
Create test infrastructure and unit tests for agent.py's run_agent_session function.

Purpose: Establish test foundation and verify core session loop handles normal flow and all message types correctly. This covers TEST-01 (core session loop) partially and TEST-02 (error handling) fully for run_agent_session.

Output: Working pytest setup with passing tests for run_agent_session
</objective>

<execution_context>
@~/.claude/get-shit-done/workflows/execute-plan.md
@~/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/phases/8-agent-testing/8-RESEARCH.md
@agent.py
@pyproject.toml
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create test infrastructure</name>
  <files>
    tests/__init__.py
    tests/conftest.py
    pyproject.toml
  </files>
  <action>
    1. Create tests/ directory with __init__.py (empty file)

    2. Create tests/conftest.py with shared fixtures:
       - mock_text_block: MagicMock with __class__.__name__ = "TextBlock", .text attribute
       - mock_tool_use_block: MagicMock with __class__.__name__ = "ToolUseBlock", .name and .input attributes
       - mock_tool_result_block: MagicMock with __class__.__name__ = "ToolResultBlock", .content and .is_error attributes
       - mock_assistant_message(mock_text_block): MagicMock with __class__.__name__ = "AssistantMessage", .content = [mock_text_block]
       - mock_user_message(mock_tool_result_block): MagicMock with __class__.__name__ = "UserMessage", .content = [mock_tool_result_block]
       - mock_sdk_client: MagicMock with __aenter__/___aexit__ as AsyncMock, .query as AsyncMock, .receive_response as async generator

       IMPORTANT: Use type() trick for __class__.__name__:
       ```python
       block = MagicMock()
       block.__class__ = type('TextBlock', (), {'__name__': 'TextBlock'})()
       ```

    3. Add pytest-asyncio configuration to pyproject.toml:
       ```toml
       [tool.pytest.ini_options]
       asyncio_mode = "auto"
       asyncio_default_fixture_loop_scope = "function"
       ```
  </action>
  <verify>
    pytest --collect-only tests/ shows fixtures are discoverable
  </verify>
  <done>
    tests/ directory exists with conftest.py containing all fixtures, pyproject.toml has pytest-asyncio config
  </done>
</task>

<task type="auto">
  <name>Task 2: Test run_agent_session normal flow and message types</name>
  <files>
    tests/test_agent.py
  </files>
  <action>
    Create tests/test_agent.py with these test cases:

    1. test_run_agent_session_returns_continue_on_success:
       - Mock client with single AssistantMessage containing TextBlock
       - Call run_agent_session
       - Assert returns ("continue", text_content)
       - Assert client.query was called with the prompt

    2. test_run_agent_session_accumulates_text_blocks:
       - Mock client with AssistantMessage containing multiple TextBlocks
       - Assert response_text contains all text concatenated

    3. test_run_agent_session_handles_tool_use_block:
       - Mock client with AssistantMessage containing ToolUseBlock
       - Assert no exception raised
       - Assert returns "continue" status

    4. test_run_agent_session_handles_tool_result_block:
       - Mock client with UserMessage containing ToolResultBlock
       - Test variants: is_error=False, is_error=True, "blocked" in content
       - Assert no exception raised

    5. test_run_agent_session_returns_error_on_exception:
       - Mock client.query to raise Exception("Connection failed")
       - Assert returns ("error", "Connection failed")

    Use patch('builtins.print') to suppress output in all tests.
    Use Path from pathlib for project_dir (can use tmp_path fixture).
  </action>
  <verify>
    pytest tests/test_agent.py -v shows all tests pass
  </verify>
  <done>
    5+ tests pass covering normal flow, message type handling, and error path for run_agent_session
  </done>
</task>

</tasks>

<verification>
Run full test suite:
```bash
pip install pytest-asyncio  # If not already installed
pytest tests/ -v
```

Expected: All tests pass, no warnings about coroutines not awaited.
</verification>

<success_criteria>
1. pytest tests/ runs without errors
2. Tests cover: normal flow, multiple text blocks, tool use blocks, tool results, exceptions
3. test_run_agent_session_returns_error_on_exception verifies error handling
4. No hardcoded paths or real filesystem dependencies
</success_criteria>

<output>
After completion, create `.planning/phases/8-agent-testing/8-01-SUMMARY.md`
</output>
