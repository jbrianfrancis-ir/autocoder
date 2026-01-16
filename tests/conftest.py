"""
Shared pytest fixtures for agent testing.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def mock_text_block():
    """Create a mock TextBlock with text attribute."""
    block = MagicMock()
    # Use type() trick for __class__.__name__ matching in agent.py
    block.__class__ = type('TextBlock', (), {'__name__': 'TextBlock'})
    block.text = "Test response text"
    return block


@pytest.fixture
def mock_tool_use_block():
    """Create a mock ToolUseBlock with name and input attributes."""
    block = MagicMock()
    block.__class__ = type('ToolUseBlock', (), {'__name__': 'ToolUseBlock'})
    block.name = "test_tool"
    block.input = {"arg": "value"}
    return block


@pytest.fixture
def mock_tool_result_block():
    """Create a mock ToolResultBlock with content and is_error attributes."""
    block = MagicMock()
    block.__class__ = type('ToolResultBlock', (), {'__name__': 'ToolResultBlock'})
    block.content = "Tool execution result"
    block.is_error = False
    return block


@pytest.fixture
def mock_assistant_message(mock_text_block):
    """Create a mock AssistantMessage containing a TextBlock."""
    msg = MagicMock()
    msg.__class__ = type('AssistantMessage', (), {'__name__': 'AssistantMessage'})
    msg.content = [mock_text_block]
    return msg


@pytest.fixture
def mock_user_message(mock_tool_result_block):
    """Create a mock UserMessage containing a ToolResultBlock."""
    msg = MagicMock()
    msg.__class__ = type('UserMessage', (), {'__name__': 'UserMessage'})
    msg.content = [mock_tool_result_block]
    return msg


@pytest.fixture
def mock_sdk_client():
    """
    Create a mock ClaudeSDKClient with async context manager support.

    The client supports:
    - async with client: (context manager)
    - await client.query(message)
    - async for msg in client.receive_response()
    """
    client = MagicMock()

    # Async context manager support
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)

    # query is async
    client.query = AsyncMock()

    # receive_response returns an async generator
    # Default: yields nothing (override in tests)
    async def empty_generator():
        return
        yield  # Make it a generator

    client.receive_response = MagicMock(return_value=empty_generator())

    return client


@pytest.fixture
def mock_autonomous_agent_deps(monkeypatch, tmp_path, mock_sdk_client):
    """
    Mock all external dependencies for run_autonomous_agent.

    Provides comprehensive mocking for:
    - create_client (returns mock_sdk_client)
    - Progress functions (has_features, print_progress_summary, print_session_header)
    - Prompt functions (get_coding_prompt, get_initializer_prompt, get_coding_prompt_yolo)
    - asyncio.sleep (to avoid test delays)
    - Temporary project directory

    Usage:
        async def test_something(mock_autonomous_agent_deps):
            deps = mock_autonomous_agent_deps
            await run_autonomous_agent(deps['project_dir'], 'model', max_iterations=1)
    """
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

    # Track asyncio.sleep calls
    sleep_mock = AsyncMock()
    monkeypatch.setattr('asyncio.sleep', sleep_mock)

    # Create test project directory
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()

    return {
        'client': mock_sdk_client,
        'project_dir': project_dir,
        'monkeypatch': monkeypatch,
        'sleep_mock': sleep_mock,
    }
