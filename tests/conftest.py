"""
Shared pytest fixtures for agent testing.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock


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
