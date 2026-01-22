"""Tests for tag tools."""

from unittest.mock import MagicMock, patch

import pytest

from joplin_mcp.errors import ValidationError
from joplin_mcp.tools.tags import (
    add_tag_to_note,
    create_tag,
    get_tag,
    list_tags,
    remove_tag_from_note,
)


@pytest.fixture
def mock_client():
    """Create a mock client for testing."""
    with patch("joplin_mcp.tools.tags.get_client") as mock_get_client:
        mock = MagicMock()
        mock_get_client.return_value = mock
        yield mock


class TestListTags:
    """Tests for list_tags function."""

    def test_list_tags_basic(self, mock_client: MagicMock) -> None:
        """Test basic tag listing."""
        mock_client.get_tags.return_value = [
            {
                "id": "tag1",
                "title": "work",
                "created_time": 1704067200000,
                "updated_time": 1704153600000,
            },
            {
                "id": "tag2",
                "title": "personal",
                "created_time": 1704067200000,
                "updated_time": 1704153600000,
            },
        ]

        result = list_tags()

        assert len(result) == 2
        assert result[0].id == "tag1"
        assert result[0].title == "work"

    def test_list_tags_limit_enforced(self, mock_client: MagicMock) -> None:
        """Test that limit is capped at 100."""
        mock_client.get_tags.return_value = []

        list_tags(limit=200)

        call_kwargs = mock_client.get_tags.call_args.kwargs
        assert call_kwargs["limit"] == 100

    def test_list_tags_invalid_limit(self, mock_client: MagicMock) -> None:
        """Test that invalid limit raises ValidationError."""
        with pytest.raises(ValidationError):
            list_tags(limit=0)


class TestGetTag:
    """Tests for get_tag function."""

    def test_get_tag(self, mock_client: MagicMock) -> None:
        """Test getting a tag by ID."""
        mock_client.get_tag.return_value = {
            "id": "tag1",
            "title": "important",
            "created_time": 1704067200000,
            "updated_time": 1704153600000,
        }

        result = get_tag("tag1")

        assert result.id == "tag1"
        assert result.title == "important"


class TestCreateTag:
    """Tests for create_tag function."""

    def test_create_tag(self, mock_client: MagicMock) -> None:
        """Test creating a new tag."""
        mock_client.create_tag.return_value = {
            "id": "new_tag",
            "title": "new-tag",
            "created_time": 1704067200000,
            "updated_time": 1704153600000,
        }

        result = create_tag(title="new-tag")

        assert result.id == "new_tag"
        assert result.title == "new-tag"
        mock_client.create_tag.assert_called_once_with(title="new-tag")


class TestAddTagToNote:
    """Tests for add_tag_to_note function."""

    def test_add_tag_to_note(self, mock_client: MagicMock) -> None:
        """Test adding a tag to a note."""
        mock_client.add_tag_to_note.return_value = {}

        result = add_tag_to_note(tag_id="tag1", note_id="note1")

        assert "message" in result
        assert "tag1" in result["message"]
        assert "note1" in result["message"]
        mock_client.add_tag_to_note.assert_called_once_with(tag_id="tag1", note_id="note1")


class TestRemoveTagFromNote:
    """Tests for remove_tag_from_note function."""

    def test_remove_tag_from_note(self, mock_client: MagicMock) -> None:
        """Test removing a tag from a note."""
        result = remove_tag_from_note(tag_id="tag1", note_id="note1")

        assert "message" in result
        assert "tag1" in result["message"]
        assert "note1" in result["message"]
        mock_client.remove_tag_from_note.assert_called_once_with(tag_id="tag1", note_id="note1")
