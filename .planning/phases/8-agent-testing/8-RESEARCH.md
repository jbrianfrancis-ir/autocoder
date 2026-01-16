# Phase 8: Agent Testing - Research

**Researched:** 2026-01-16
**Domain:** Python async testing with pytest, mocking Claude Agent SDK
**Confidence:** HIGH

## Summary

Testing `agent.py` requires mocking the Claude Agent SDK client and its async methods. The codebase uses async functions (`run_agent_session`, `run_autonomous_agent`) that rely on:
1. `ClaudeSDKClient` with async context manager protocol
2. Async generator methods (`receive_response`)
3. Dependencies on `progress.py` and `prompts.py`

The standard approach uses `pytest` (already in requirements.txt at v8.0+) with `pytest-asyncio` for async test support and Python's built-in `unittest.mock.AsyncMock` (available since Python 3.8) for mocking async operations.

**Primary recommendation:** Use pytest-asyncio with auto mode, structure tests in `tests/test_agent.py`, mock ClaudeSDKClient with AsyncMock for the async context manager and response streaming.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pytest | 8.0+ | Test framework | Already in requirements.txt, standard Python testing |
| pytest-asyncio | 0.24+ | Async test support | Official pytest async extension |
| unittest.mock | stdlib | Mocking | Built-in, AsyncMock supports async mocking since 3.8 |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest-cov | 5.0+ | Coverage reporting | Optional, for measuring test coverage |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| pytest-asyncio | asyncio.run in each test | More boilerplate, pytest-asyncio is simpler |
| unittest.mock | asynctest | asynctest is unmaintained, stdlib AsyncMock is sufficient |

**Installation:**
```bash
pip install pytest-asyncio
```

## Architecture Patterns

### Recommended Test Structure
```
tests/
├── __init__.py
├── conftest.py           # Shared fixtures for mock SDK client
└── test_agent.py         # Tests for agent.py functions
```

### Pattern 1: Async Test Function with pytest-asyncio
**What:** Mark async test functions to be run by pytest
**When to use:** All tests of async functions
**Example:**
```python
# Source: pytest-asyncio documentation
import pytest

@pytest.mark.asyncio
async def test_run_agent_session_success():
    # Test body with await calls
    pass
```

### Pattern 2: Mock Async Context Manager
**What:** Mock ClaudeSDKClient's `__aenter__` and `__aexit__`
**When to use:** Testing `run_autonomous_agent` which uses `async with client:`
**Example:**
```python
# Source: Python unittest.mock docs + best practices
from unittest.mock import AsyncMock, MagicMock

def create_mock_client():
    """Create a mock ClaudeSDKClient with async context manager support."""
    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.query = AsyncMock()
    mock_client.receive_response = mock_async_generator
    return mock_client
```

### Pattern 3: Mock Async Generator
**What:** Mock `receive_response()` which returns `AsyncIterator`
**When to use:** Testing response processing in `run_agent_session`
**Example:**
```python
# Source: Python async iteration patterns
from unittest.mock import MagicMock

async def mock_response_generator(messages):
    """Create an async generator that yields mock messages."""
    for msg in messages:
        yield msg

# Create mock message objects
mock_text_block = MagicMock()
mock_text_block.__class__.__name__ = "TextBlock"
mock_text_block.text = "Hello from agent"

mock_assistant_msg = MagicMock()
mock_assistant_msg.__class__.__name__ = "AssistantMessage"
mock_assistant_msg.content = [mock_text_block]
```

### Pattern 4: Fixture for Mock Client
**What:** Pytest fixture that creates configured mock client
**When to use:** Shared across multiple test functions
**Example:**
```python
# Source: pytest fixture patterns
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.fixture
def mock_sdk_client():
    """Fixture providing a mock ClaudeSDKClient."""
    with patch('agent.create_client') as mock_create:
        client = MagicMock()
        client.__aenter__ = AsyncMock(return_value=client)
        client.__aexit__ = AsyncMock(return_value=None)
        client.query = AsyncMock()
        mock_create.return_value = client
        yield client
```

### Anti-Patterns to Avoid
- **Mixing sync and async assertions:** Always use `await` for async calls in tests
- **Not mocking filesystem operations:** Tests should not depend on real project directories
- **Forgetting to mock `print()`:** agent.py uses print extensively; capture or mock stdout
- **Testing SDK internals:** Focus on agent.py behavior, not claude_agent_sdk implementation

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Async test runner | Custom event loop management | pytest-asyncio | Handles loop lifecycle, cleanup |
| Mock async methods | Future objects manually | AsyncMock | Built-in, handles await properly |
| Capture stdout | Manual sys.stdout redirect | pytest's capsys fixture | Cleaner, automatic cleanup |
| Temporary directories | Manual tempfile cleanup | pytest's tmp_path fixture | Automatic cleanup, isolation |

**Key insight:** Python's stdlib `unittest.mock.AsyncMock` handles async mocking correctly. No need for third-party async mocking libraries.

## Common Pitfalls

### Pitfall 1: Not Configuring pytest-asyncio Mode
**What goes wrong:** Tests fail with "coroutine was never awaited" warnings
**Why it happens:** pytest-asyncio requires explicit configuration
**How to avoid:** Add to pyproject.toml:
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```
**Warning signs:** Warnings about coroutines not being awaited

### Pitfall 2: Mocking `type().__name__` Instead of `__class__.__name__`
**What goes wrong:** `msg_type = type(msg).__name__` returns "MagicMock" not the intended type
**Why it happens:** MagicMock's type is always MagicMock
**How to avoid:** Configure mock's spec or set `__class__`:
```python
mock_msg = MagicMock()
mock_msg.__class__ = MagicMock(__name__="AssistantMessage")
# OR use spec=
mock_msg = MagicMock(spec=AssistantMessage)
```
**Warning signs:** Type checks in agent.py fail to match message types

### Pitfall 3: Infinite Loop in `run_autonomous_agent`
**What goes wrong:** Tests hang because the while True loop never exits
**Why it happens:** `run_autonomous_agent` loops until max_iterations
**How to avoid:** Always pass `max_iterations=1` in tests:
```python
await run_autonomous_agent(project_dir, model="test", max_iterations=1)
```
**Warning signs:** Test timeout, pytest hangs

### Pitfall 4: Real Filesystem Access
**What goes wrong:** Tests create files in actual directories, flaky across environments
**Why it happens:** `agent.py` calls `project_dir.mkdir()`, progress functions
**How to avoid:** Use pytest's `tmp_path` fixture and mock filesystem-touching functions:
```python
@pytest.fixture
def mock_project_dir(tmp_path):
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    return project_dir
```
**Warning signs:** Tests pass locally but fail in CI

### Pitfall 5: Not Mocking print() Output
**What goes wrong:** Test output cluttered with agent banners and messages
**Why it happens:** agent.py has many print() statements for user output
**How to avoid:** Use `capsys` fixture or mock print:
```python
def test_session(capsys, mock_sdk_client):
    # Run test
    captured = capsys.readouterr()
    # Can assert on captured.out if needed
```
**Warning signs:** Noisy test output

### Pitfall 6: Forgetting asyncio.sleep Mock
**What goes wrong:** Tests slow due to real sleep calls
**Why it happens:** `run_autonomous_agent` has `asyncio.sleep(AUTO_CONTINUE_DELAY_SECONDS)`
**How to avoid:** Mock asyncio.sleep:
```python
@pytest.fixture
def mock_sleep(monkeypatch):
    monkeypatch.setattr('asyncio.sleep', AsyncMock())
```
**Warning signs:** Tests take 3+ seconds unexpectedly

## Code Examples

Verified patterns for testing agent.py:

### Test run_agent_session Normal Flow
```python
# Source: Patterns from pytest-asyncio and unittest.mock docs
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

@pytest.mark.asyncio
async def test_run_agent_session_returns_continue_on_success():
    """Test that successful session returns ('continue', response_text)."""
    # Create mock client
    mock_client = MagicMock()
    mock_client.query = AsyncMock()

    # Create mock response messages
    mock_text_block = MagicMock()
    mock_text_block.__class__ = type('TextBlock', (), {'__name__': 'TextBlock'})()
    mock_text_block.text = "Agent response"

    mock_msg = MagicMock()
    mock_msg.__class__ = type('AssistantMessage', (), {'__name__': 'AssistantMessage'})()
    mock_msg.content = [mock_text_block]

    async def mock_receive():
        yield mock_msg

    mock_client.receive_response = mock_receive

    # Import and test
    from agent import run_agent_session

    with patch('builtins.print'):  # Suppress output
        status, response = await run_agent_session(
            mock_client, "test prompt", Path("/tmp/test")
        )

    assert status == "continue"
    assert "Agent response" in response
    mock_client.query.assert_called_once_with("test prompt")
```

### Test run_agent_session Error Handling
```python
@pytest.mark.asyncio
async def test_run_agent_session_returns_error_on_exception():
    """Test that exceptions return ('error', error_message)."""
    mock_client = MagicMock()
    mock_client.query = AsyncMock(side_effect=Exception("Connection failed"))

    from agent import run_agent_session

    status, response = await run_agent_session(
        mock_client, "test prompt", Path("/tmp/test")
    )

    assert status == "error"
    assert "Connection failed" in response
```

### Test run_autonomous_agent with Mocked Dependencies
```python
@pytest.fixture
def mock_agent_dependencies(monkeypatch, tmp_path):
    """Mock all external dependencies for run_autonomous_agent."""
    # Mock create_client
    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.query = AsyncMock()

    async def mock_receive():
        mock_text = MagicMock()
        mock_text.__class__ = type('TextBlock', (), {'__name__': 'TextBlock'})()
        mock_text.text = "Done"
        mock_msg = MagicMock()
        mock_msg.__class__ = type('AssistantMessage', (), {'__name__': 'AssistantMessage'})()
        mock_msg.content = [mock_text]
        yield mock_msg

    mock_client.receive_response = mock_receive
    monkeypatch.setattr('agent.create_client', lambda *args, **kwargs: mock_client)

    # Mock progress functions
    monkeypatch.setattr('agent.has_features', lambda _: True)
    monkeypatch.setattr('agent.print_progress_summary', lambda _: None)
    monkeypatch.setattr('agent.print_session_header', lambda *args: None)

    # Mock prompts
    monkeypatch.setattr('agent.get_coding_prompt', lambda _: "coding prompt")
    monkeypatch.setattr('agent.get_initializer_prompt', lambda _: "init prompt")
    monkeypatch.setattr('agent.copy_spec_to_project', lambda _: None)

    # Mock sleep to avoid delays
    monkeypatch.setattr('asyncio.sleep', AsyncMock())

    return mock_client, tmp_path

@pytest.mark.asyncio
async def test_run_autonomous_agent_single_iteration(mock_agent_dependencies):
    """Test that run_autonomous_agent completes with max_iterations=1."""
    mock_client, tmp_path = mock_agent_dependencies
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    from agent import run_autonomous_agent

    with patch('builtins.print'):
        await run_autonomous_agent(
            project_dir=project_dir,
            model="test-model",
            max_iterations=1,
            yolo_mode=False,
        )

    # Verify client was used
    mock_client.query.assert_called_once()
```

### conftest.py Shared Fixtures
```python
# tests/conftest.py
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def mock_text_block():
    """Create a mock TextBlock."""
    block = MagicMock()
    block.__class__ = type('TextBlock', (), {'__name__': 'TextBlock'})()
    block.text = "Test response"
    return block

@pytest.fixture
def mock_assistant_message(mock_text_block):
    """Create a mock AssistantMessage."""
    msg = MagicMock()
    msg.__class__ = type('AssistantMessage', (), {'__name__': 'AssistantMessage'})()
    msg.content = [mock_text_block]
    return msg

@pytest.fixture
def mock_sdk_client(mock_assistant_message):
    """Create a mock ClaudeSDKClient."""
    client = MagicMock()
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)
    client.query = AsyncMock()

    async def mock_receive():
        yield mock_assistant_message

    client.receive_response = mock_receive
    return client
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| asynctest library | unittest.mock.AsyncMock | Python 3.8 (2019) | No external dependency needed |
| Manual event loop | pytest-asyncio auto mode | pytest-asyncio 0.21+ | Less boilerplate |

**Deprecated/outdated:**
- asynctest: Unmaintained, replaced by stdlib AsyncMock
- pytest.mark.asyncio_cooperative: Removed, use standard asyncio_mode

## Open Questions

Things that couldn't be fully resolved:

1. **Coverage threshold target**
   - What we know: No existing coverage configuration
   - What's unclear: What percentage coverage is acceptable
   - Recommendation: Start with critical paths (error handling), add coverage later

2. **Integration test scope**
   - What we know: Requirements specify unit tests only
   - What's unclear: Whether end-to-end tests with real SDK are desired
   - Recommendation: Stick to unit tests with mocks per requirements

## Sources

### Primary (HIGH confidence)
- pytest-asyncio documentation: https://pytest-asyncio.readthedocs.io/
- Python unittest.mock documentation: https://docs.python.org/3/library/unittest.mock.html

### Secondary (MEDIUM confidence)
- Async test patterns for Pytest: https://tonybaloney.github.io/posts/async-test-patterns-for-pytest-and-unittest.html
- Mastering Async Context Manager Mocking: https://dzone.com/articles/mastering-async-context-manager-mocking-in-python

### Tertiary (LOW confidence)
- WebSearch results for pytest-asyncio best practices 2025

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - pytest and unittest.mock are stdlib/established
- Architecture: HIGH - patterns verified against official docs
- Pitfalls: HIGH - derived from actual agent.py code analysis

**Research date:** 2026-01-16
**Valid until:** 60 days (stable Python testing ecosystem)

## Testable Units in agent.py

Based on code analysis, the testable units are:

### run_agent_session (lines 38-109)
**Inputs:**
- `client: ClaudeSDKClient` - needs mocking
- `message: str` - test input
- `project_dir: Path` - mock path

**Outputs:**
- `tuple[str, str]` - ("continue"|"error", response_text)

**Paths to test:**
1. Normal flow: query succeeds, response received, returns "continue"
2. Exception in query: returns "error" with exception message
3. TextBlock processing: response_text accumulates correctly
4. ToolUseBlock processing: tool name printed
5. ToolResultBlock processing: blocked/error/success cases

### run_autonomous_agent (lines 112-226)
**Inputs:**
- `project_dir: Path` - mock with tmp_path
- `model: str` - test value
- `max_iterations: Optional[int]` - always set to small number in tests
- `yolo_mode: bool` - test both branches

**Dependencies to mock:**
- `create_client` - returns mock client
- `has_features` - return True/False to test branches
- `print_progress_summary` - mock to suppress
- `print_session_header` - mock to suppress
- `get_coding_prompt` / `get_initializer_prompt` / `get_coding_prompt_yolo` - return test strings
- `copy_spec_to_project` - mock to no-op
- `asyncio.sleep` - mock to avoid delays

**Paths to test:**
1. First run (is_first_run=True): uses initializer prompt
2. Continuation (is_first_run=False): uses coding prompt
3. YOLO mode: uses yolo prompt
4. Error status: logs warning, retries
5. Max iterations reached: exits loop
