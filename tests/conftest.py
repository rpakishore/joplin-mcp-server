"""Pytest fixtures for Joplin MCP Server tests."""

from datetime import datetime
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_joplin_client(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Create a mock Joplin client."""
    mock_client = MagicMock()
    mock_client._client = MagicMock()

    def get_mock_client() -> MagicMock:
        return mock_client

    monkeypatch.setattr("joplin_mcp.client.get_client", get_mock_client)
    return mock_client


@pytest.fixture
def sample_note() -> dict:
    """Sample note data for testing."""
    return {
        "id": "note123",
        "title": "Test Note",
        "body": "This is the note body content.",
        "parent_id": "notebook456",
        "created_time": datetime(2024, 1, 1, 0, 0, 0),
        "updated_time": datetime(2024, 1, 2, 0, 0, 0),
        "is_todo": False,
        "todo_completed": None,
    }


@pytest.fixture
def sample_notebook() -> dict:
    """Sample notebook data for testing."""
    return {
        "id": "notebook456",
        "title": "Test Notebook",
        "parent_id": "",
        "created_time": datetime(2024, 1, 1, 0, 0, 0),
        "updated_time": datetime(2024, 1, 2, 0, 0, 0),
    }


@pytest.fixture
def sample_tag() -> dict:
    """Sample tag data for testing."""
    return {
        "id": "tag789",
        "title": "test-tag",
        "created_time": datetime(2024, 1, 1, 0, 0, 0),
        "updated_time": datetime(2024, 1, 2, 0, 0, 0),
    }
