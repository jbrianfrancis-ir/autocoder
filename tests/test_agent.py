"""
Unit tests for agent.py run_agent_session function.

Tests cover:
- Normal flow returns ('continue', response_text)
- Text block accumulation
- Tool use block handling
- Tool result block handling (success, error, blocked)
- Exception handling returns ('error', message)
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# Lightweight fake classes that match type(obj).__name__ patterns in agent.py
# Using actual classes so type(instance).__name__ returns the correct name
class TextBlock:
    """Fake TextBlock for testing."""
    def __init__(self, text: str):
        self.text = text


class ToolUseBlock:
    """Fake ToolUseBlock for testing."""
    def __init__(self, name: str, input_data: dict | None = None):
        self.name = name
        self.input = input_data or {}


class ToolResultBlock:
    """Fake ToolResultBlock for testing."""
    def __init__(self, content: str, is_error: bool = False):
        self.content = content
        self.is_error = is_error


class AssistantMessage:
    """Fake AssistantMessage for testing."""
    def __init__(self, content: list):
        self.content = content


class UserMessage:
    """Fake UserMessage for testing."""
    def __init__(self, content: list):
        self.content = content


# Factory functions for convenience
def make_text_block(text: str) -> TextBlock:
    """Create a TextBlock."""
    return TextBlock(text)


def make_tool_use_block(name: str, input_data: dict | None = None) -> ToolUseBlock:
    """Create a ToolUseBlock."""
    return ToolUseBlock(name, input_data)


def make_tool_result_block(content: str, is_error: bool = False) -> ToolResultBlock:
    """Create a ToolResultBlock."""
    return ToolResultBlock(content, is_error)


def make_assistant_message(blocks: list) -> AssistantMessage:
    """Create an AssistantMessage containing blocks."""
    return AssistantMessage(blocks)


def make_user_message(blocks: list) -> UserMessage:
    """Create a UserMessage containing blocks."""
    return UserMessage(blocks)


def make_mock_client(messages: list):
    """
    Create a mock ClaudeSDKClient that yields the given messages.

    Args:
        messages: List of message mocks to yield from receive_response
    """
    client = MagicMock()
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)
    client.query = AsyncMock()

    async def mock_generator():
        for msg in messages:
            yield msg

    client.receive_response = MagicMock(return_value=mock_generator())
    return client


class TestRunAgentSessionNormalFlow:
    """Tests for run_agent_session normal flow."""

    @patch('builtins.print')
    async def test_returns_continue_on_success(self, mock_print, tmp_path):
        """run_agent_session returns ('continue', text) on success."""
        # Import here to avoid import-time side effects
        from agent import run_agent_session

        # Setup: client yields AssistantMessage with TextBlock
        text_block = make_text_block("Hello from Claude")
        assistant_msg = make_assistant_message([text_block])
        client = make_mock_client([assistant_msg])

        # Execute
        status, response = await run_agent_session(client, "Test prompt", tmp_path)

        # Verify
        assert status == "continue"
        assert response == "Hello from Claude"
        client.query.assert_called_once_with("Test prompt")

    @patch('builtins.print')
    async def test_accumulates_text_blocks(self, mock_print, tmp_path):
        """run_agent_session accumulates text from multiple TextBlocks."""
        from agent import run_agent_session

        # Setup: AssistantMessage with multiple TextBlocks
        text_block1 = make_text_block("First ")
        text_block2 = make_text_block("Second ")
        text_block3 = make_text_block("Third")
        assistant_msg = make_assistant_message([text_block1, text_block2, text_block3])
        client = make_mock_client([assistant_msg])

        # Execute
        status, response = await run_agent_session(client, "Test prompt", tmp_path)

        # Verify
        assert status == "continue"
        assert response == "First Second Third"


class TestRunAgentSessionToolHandling:
    """Tests for run_agent_session tool block handling."""

    @patch('builtins.print')
    async def test_handles_tool_use_block(self, mock_print, tmp_path):
        """run_agent_session handles ToolUseBlock without crashing."""
        from agent import run_agent_session

        # Setup: AssistantMessage with ToolUseBlock
        tool_block = make_tool_use_block("bash", {"command": "ls"})
        assistant_msg = make_assistant_message([tool_block])
        client = make_mock_client([assistant_msg])

        # Execute - should not raise
        status, response = await run_agent_session(client, "Test prompt", tmp_path)

        # Verify
        assert status == "continue"
        # Response text is empty (no TextBlocks)
        assert response == ""

    @patch('builtins.print')
    async def test_handles_tool_result_success(self, mock_print, tmp_path):
        """run_agent_session handles successful ToolResultBlock."""
        from agent import run_agent_session

        # Setup: UserMessage with successful tool result
        result_block = make_tool_result_block("Command output", is_error=False)
        user_msg = make_user_message([result_block])
        client = make_mock_client([user_msg])

        # Execute - should not raise
        status, response = await run_agent_session(client, "Test prompt", tmp_path)

        # Verify
        assert status == "continue"

    @patch('builtins.print')
    async def test_handles_tool_result_error(self, mock_print, tmp_path):
        """run_agent_session handles error ToolResultBlock."""
        from agent import run_agent_session

        # Setup: UserMessage with error tool result
        result_block = make_tool_result_block("Error: command failed", is_error=True)
        user_msg = make_user_message([result_block])
        client = make_mock_client([user_msg])

        # Execute - should not raise
        status, response = await run_agent_session(client, "Test prompt", tmp_path)

        # Verify
        assert status == "continue"

    @patch('builtins.print')
    async def test_handles_tool_result_blocked(self, mock_print, tmp_path):
        """run_agent_session handles blocked command in ToolResultBlock."""
        from agent import run_agent_session

        # Setup: UserMessage with blocked tool result
        result_block = make_tool_result_block("Command blocked by security hook", is_error=False)
        user_msg = make_user_message([result_block])
        client = make_mock_client([user_msg])

        # Execute - should not raise
        status, response = await run_agent_session(client, "Test prompt", tmp_path)

        # Verify
        assert status == "continue"


class TestRunAgentSessionErrorHandling:
    """Tests for run_agent_session error handling."""

    @patch('builtins.print')
    async def test_returns_error_on_exception(self, mock_print, tmp_path):
        """run_agent_session returns ('error', message) on exception."""
        from agent import run_agent_session

        # Setup: client.query raises exception
        client = MagicMock()
        client.__aenter__ = AsyncMock(return_value=client)
        client.__aexit__ = AsyncMock(return_value=None)
        client.query = AsyncMock(side_effect=Exception("Connection failed"))

        # Execute
        status, response = await run_agent_session(client, "Test prompt", tmp_path)

        # Verify
        assert status == "error"
        assert response == "Connection failed"


class TestRunAgentSessionMixedMessages:
    """Tests for run_agent_session with mixed message types."""

    @patch('builtins.print')
    async def test_handles_full_conversation_flow(self, mock_print, tmp_path):
        """run_agent_session handles a realistic conversation flow."""
        from agent import run_agent_session

        # Setup: Realistic flow with text, tool use, tool result, more text
        messages = [
            make_assistant_message([
                make_text_block("Let me check the files. "),
                make_tool_use_block("bash", {"command": "ls"}),
            ]),
            make_user_message([
                make_tool_result_block("file1.py\nfile2.py"),
            ]),
            make_assistant_message([
                make_text_block("Found 2 files."),
            ]),
        ]
        client = make_mock_client(messages)

        # Execute
        status, response = await run_agent_session(client, "List files", tmp_path)

        # Verify
        assert status == "continue"
        # Text from both AssistantMessages accumulated
        assert response == "Let me check the files. Found 2 files."
