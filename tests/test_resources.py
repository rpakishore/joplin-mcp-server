"""Tests for resource tools."""

from unittest.mock import MagicMock, patch

import pytest

from joplin_mcp.tools.resources import get_note_resources


@pytest.fixture
def mock_client():
    """Create a mock client for testing."""
    with patch("joplin_mcp.tools.resources.get_client") as mock_get_client:
        mock = MagicMock()
        mock_get_client.return_value = mock
        yield mock


class TestGetNoteResources:
    """Tests for get_note_resources function."""

    def test_get_note_resources_with_attachments(self, mock_client: MagicMock) -> None:
        """Test getting resources for a note with attachments."""
        mock_client.get_note_resources.return_value = [
            {
                "id": "res1",
                "title": "image.png",
                "filename": "image.png",
                "mime": "image/png",
                "size": 12345,
                "created_time": 1704067200000,
                "updated_time": 1704153600000,
            },
            {
                "id": "res2",
                "title": "document.pdf",
                "filename": "document.pdf",
                "mime": "application/pdf",
                "size": 54321,
                "created_time": 1704067200000,
                "updated_time": 1704153600000,
            },
        ]

        result = get_note_resources("note1")

        assert len(result) == 2
        assert result[0].id == "res1"
        assert result[0].filename == "image.png"
        assert result[0].mime == "image/png"
        assert result[0].size == 12345
        assert result[1].id == "res2"
        assert result[1].mime == "application/pdf"

    def test_get_note_resources_empty(self, mock_client: MagicMock) -> None:
        """Test getting resources for a note without attachments."""
        mock_client.get_note_resources.return_value = []

        result = get_note_resources("note1")

        assert result == []

    def test_get_note_resources_defaults(self, mock_client: MagicMock) -> None:
        """Test that missing fields get default values."""
        mock_client.get_note_resources.return_value = [
            {
                "id": "res1",
                "created_time": 1704067200000,
                "updated_time": 1704153600000,
            }
        ]

        result = get_note_resources("note1")

        assert result[0].title == ""
        assert result[0].filename == ""
        assert result[0].mime == "application/octet-stream"
        assert result[0].size == 0
