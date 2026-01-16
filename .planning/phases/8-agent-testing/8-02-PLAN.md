---
phase: 8-agent-testing
plan: 02
type: execute
wave: 2
depends_on: ["8-01"]
files_modified:
  - tests/test_agent.py
autonomous: true

must_haves:
  truths:
    - "run_autonomous_agent completes with max_iterations=1"
    - "First run uses initializer prompt, subsequent runs use coding prompt"
    - "YOLO mode uses yolo prompt instead of standard coding prompt"
    - "Error status triggers retry with delay"
    - "All tests pass with pytest"
  artifacts:
    - path: "tests/test_agent.py"
      provides: "Complete test coverage for agent.py"
      min_lines: 150
      contains: "test_run_autonomous_agent"
  key_links:
    - from: "tests/test_agent.py"
      to: "agent.py"
      via: "from agent import run_autonomous_agent"
      pattern: "run_autonomous_agent"
    - from: "tests/test_agent.py"
      to: "agent dependencies"
      via: "monkeypatch.setattr"
      pattern: "monkeypatch.setattr.*agent\\."
---

<objective>
Add unit tests for agent.py's run_autonomous_agent function with comprehensive dependency mocking.

Purpose: Complete TEST-01 coverage by testing the autonomous agent loop including prompt selection, iteration control, and status handling. Verifies the orchestration logic works correctly.

Output: Full test coverage for agent.py with all tests passing
</objective>

<execution_context>
@~/.claude/get-shit-done/workflows/execute-plan.md
@~/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/phases/8-agent-testing/8-RESEARCH.md
@.planning/phases/8-agent-testing/8-01-SUMMARY.md
@agent.py
@tests/conftest.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create fixture for run_autonomous_agent dependencies</name>
  <files>
    tests/conftest.py
  </files>
  <action>
    Add a comprehensive fixture to tests/conftest.py for mocking all run_autonomous_agent dependencies:

    ```python
    @pytest.fixture
    def mock_autonomous_agent_deps(monkeypatch, tmp_path, mock_sdk_client):
        """Mock all external dependencies for run_autonomous_agent."""
        # Mock create_client to return the mock_sdk_client
        monkeypatch.setattr('agent.create_client', lambda *args, **kwargs: mock_sdk_client)

        # Mock progress functions
        monkeypatch.setattr('agent.has_features', lambda _: True)  # Default to continuation
        monkeypatch.setattr('agent.print_progress_summary', lambda _: None)
        monkeypatch.setattr('agent.print_session_header', lambda *args: None)

        # Mock prompts
        monkeypatch.setattr('agent.get_coding_prompt', lambda _: "coding prompt")
        monkeypatch.setattr('agent.get_initializer_prompt', lambda _: "init prompt")
        monkeypatch.setattr('agent.get_coding_prompt_yolo', lambda _: "yolo prompt")
        monkeypatch.setattr('agent.copy_spec_to_project', lambda _: None)

        # Mock asyncio.sleep to avoid delays
        monkeypatch.setattr('asyncio.sleep', AsyncMock())

        # Create test project directory
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()

        return {
            'client': mock_sdk_client,
            'project_dir': project_dir,
            'monkeypatch': monkeypatch,
        }
    ```

    This fixture:
    - Uses the existing mock_sdk_client fixture
    - Mocks all imported functions from progress.py and prompts.py
    - Mocks asyncio.sleep to avoid test delays
    - Provides a temporary project directory
  </action>
  <verify>
    pytest --collect-only tests/ shows mock_autonomous_agent_deps fixture
  </verify>
  <done>
    mock_autonomous_agent_deps fixture exists and provides all mocked dependencies
  </done>
</task>

<task type="auto">
  <name>Task 2: Test run_autonomous_agent scenarios</name>
  <files>
    tests/test_agent.py
  </files>
  <action>
    Add tests for run_autonomous_agent to tests/test_agent.py:

    1. test_run_autonomous_agent_single_iteration:
       - Use mock_autonomous_agent_deps fixture
       - Call run_autonomous_agent with max_iterations=1
       - Assert completes without error
       - Assert client.query was called

    2. test_run_autonomous_agent_first_run_uses_initializer:
       - Set has_features to return False (first run)
       - Run with max_iterations=1
       - Capture what prompt was passed to client.query
       - Assert "init prompt" was used

    3. test_run_autonomous_agent_continuation_uses_coding_prompt:
       - Set has_features to return True (continuation)
       - Run with max_iterations=1
       - Assert "coding prompt" was used

    4. test_run_autonomous_agent_yolo_mode_uses_yolo_prompt:
       - Set has_features to return True
       - Run with max_iterations=1, yolo_mode=True
       - Assert "yolo prompt" was used

    5. test_run_autonomous_agent_error_retries:
       - Make run_agent_session return ("error", "test error") first time
       - Then return ("continue", "ok") second time
       - Run with max_iterations=2
       - Assert asyncio.sleep was called (retry delay)

    For prompt verification, capture the argument to client.query using mock's call_args.

    Use patch('builtins.print') to suppress banner/header output.
  </action>
  <verify>
    pytest tests/test_agent.py -v shows all run_autonomous_agent tests pass
  </verify>
  <done>
    5 tests for run_autonomous_agent pass, covering iteration control, prompt selection, and error handling
  </done>
</task>

<task type="auto">
  <name>Task 3: Final verification and cleanup</name>
  <files>
    tests/test_agent.py
  </files>
  <action>
    1. Run full test suite to ensure all tests pass:
       ```bash
       pytest tests/ -v
       ```

    2. Verify test count covers requirements:
       - TEST-01 (core session loop): run_agent_session tests + run_autonomous_agent tests
       - TEST-02 (error handling): error return test + retry test

    3. Run with any warnings visible:
       ```bash
       pytest tests/ -v -W default
       ```

    4. Fix any warnings about:
       - Coroutines never awaited
       - Deprecation warnings
       - Fixture scope issues
  </action>
  <verify>
    pytest tests/ -v shows 10+ tests passing with no warnings
  </verify>
  <done>
    All tests pass, no warnings, TEST-01 and TEST-02 requirements satisfied
  </done>
</task>

</tasks>

<verification>
Run complete test suite:
```bash
pytest tests/ -v --tb=short
```

Expected output:
- 10+ tests collected
- All tests pass
- No warnings about coroutines

Coverage check (optional):
```bash
pip install pytest-cov
pytest tests/ --cov=agent --cov-report=term-missing
```
</verification>

<success_criteria>
1. All tests pass (pytest exits with code 0)
2. run_autonomous_agent tested with: single iteration, first run, continuation, yolo mode, error retry
3. No real filesystem operations (uses tmp_path)
4. No real network calls (all SDK calls mocked)
5. No test delays (asyncio.sleep mocked)
</success_criteria>

<output>
After completion, create `.planning/phases/8-agent-testing/8-02-SUMMARY.md`
</output>
