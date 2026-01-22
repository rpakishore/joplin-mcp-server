"""Tests for note tools."""

from unittest.mock import MagicMock, patch

import pytest

from joplin_mcp.errors import ValidationError
from joplin_mcp.tools.notes import create_note, get_note, search_notes, update_note


@pytest.fixture
def mock_client():
    """Create a mock client for testing."""
    with patch("joplin_mcp.tools.notes.get_client") as mock_get_client:
        mock = MagicMock()
        mock_get_client.return_value = mock
        yield mock


class TestSearchNotes:
    """Tests for search_notes function."""

    def test_search_notes_basic(self, mock_client: MagicMock) -> None:
        """Test basic note search."""
        mock_client.search_notes.return_value = [
            {
                "id": "note1",
                "title": "Test Note",
                "parent_id": "nb1",
                "created_time": 1704067200000,
                "updated_time": 1704153600000,
                "is_todo": 0,
                "todo_completed": 0,
                "body": "This is the body",
            }
        ]

        result = search_notes(query="test")

        assert len(result) == 1
        assert result[0].id == "note1"
        assert result[0].title == "Test Note"
        assert result[0].snippet == "This is the body"

    def test_search_notes_with_filters(self, mock_client: MagicMock) -> None:
        """Test search with multiple filters."""
        mock_client.search_notes.return_value = []

        search_notes(
            query="test",
            notebook_id="nb1",
            tag_id="tag1",
            is_todo=True,
            is_completed=False,
        )

        # Verify the query was built correctly
        call_args = mock_client.search_notes.call_args
        query = call_args.kwargs["query"]
        assert "test" in query
        assert "notebook:nb1" in query
        assert "tag:tag1" in query
        assert "type:todo" in query
        assert "iscompleted:0" in query

    def test_search_notes_raw_query(self, mock_client: MagicMock) -> None:
        """Test search with raw query overrides other params."""
        mock_client.search_notes.return_value = []

        search_notes(query="ignored", raw_query="custom:query")

        call_args = mock_client.search_notes.call_args
        assert call_args.kwargs["query"] == "custom:query"

    def test_search_notes_snippet_truncation(self, mock_client: MagicMock) -> None:
        """Test that body is truncated to 500 chars for snippet."""
        long_body = "x" * 1000
        mock_client.search_notes.return_value = [
            {
                "id": "note1",
                "title": "Test",
                "parent_id": "nb1",
                "created_time": 1704067200000,
                "updated_time": 1704153600000,
                "is_todo": 0,
                "todo_completed": 0,
                "body": long_body,
            }
        ]

        result = search_notes()

        assert len(result[0].snippet) == 500

    def test_search_notes_limit_enforced(self, mock_client: MagicMock) -> None:
        """Test that limit is capped at 100."""
        mock_client.search_notes.return_value = []

        search_notes(limit=200)

        call_args = mock_client.search_notes.call_args
        assert call_args.kwargs["limit"] == 100

    def test_search_notes_invalid_limit(self, mock_client: MagicMock) -> None:
        """Test that invalid limit raises ValidationError."""
        with pytest.raises(ValidationError):
            search_notes(limit=0)


class TestGetNote:
    """Tests for get_note function."""

    def test_get_note_with_tags(self, mock_client: MagicMock) -> None:
        """Test getting a note with attached tags."""
        mock_client.get_note.return_value = {
            "id": "note1",
            "title": "Test Note",
            "body": "Full body content",
            "parent_id": "nb1",
            "created_time": 1704067200000,
            "updated_time": 1704153600000,
            "is_todo": 0,
            "todo_completed": 0,
        }
        mock_client.get_note_tags.return_value = [
            {"id": "tag1", "title": "important"},
            {"id": "tag2", "title": "work"},
        ]

        result = get_note("note1")

        assert result.id == "note1"
        assert result.body == "Full body content"
        assert len(result.tags) == 2
        assert result.tags[0].id == "tag1"
        assert result.tags[0].title == "important"

    def test_get_note_no_tags(self, mock_client: MagicMock) -> None:
        """Test getting a note without tags."""
        mock_client.get_note.return_value = {
            "id": "note1",
            "title": "Test",
            "body": "",
            "parent_id": "nb1",
            "created_time": 1704067200000,
            "updated_time": 1704153600000,
            "is_todo": 0,
            "todo_completed": 0,
        }
        mock_client.get_note_tags.return_value = []

        result = get_note("note1")

        assert result.tags == []


class TestCreateNote:
    """Tests for create_note function."""

    def test_create_note_minimal(self, mock_client: MagicMock) -> None:
        """Test creating a note with minimal params."""
        mock_client.create_note.return_value = {"id": "new_note"}
        mock_client.get_note.return_value = {
            "id": "new_note",
            "title": "New Note",
            "body": "Content",
            "parent_id": "",
            "created_time": 1704067200000,
            "updated_time": 1704153600000,
            "is_todo": 0,
            "todo_completed": 0,
        }
        mock_client.get_note_tags.return_value = []

        result = create_note(title="New Note", body="Content")

        assert result.id == "new_note"
        mock_client.create_note.assert_called_once()

    def test_create_note_with_tags(self, mock_client: MagicMock) -> None:
        """Test creating a note with tags attached."""
        mock_client.create_note.return_value = {"id": "new_note"}
        mock_client.get_note.return_value = {
            "id": "new_note",
            "title": "New Note",
            "body": "Content",
            "parent_id": "nb1",
            "created_time": 1704067200000,
            "updated_time": 1704153600000,
            "is_todo": 0,
            "todo_completed": 0,
        }
        mock_client.get_note_tags.return_value = [{"id": "tag1", "title": "test"}]

        create_note(
            title="New Note",
            body="Content",
            notebook_id="nb1",
            tags=["tag1", "tag2"],
        )

        # Verify tags were attached
        assert mock_client.add_tag_to_note.call_count == 2

    def test_create_note_as_todo(self, mock_client: MagicMock) -> None:
        """Test creating a todo note."""
        mock_client.create_note.return_value = {"id": "todo_note"}
        mock_client.get_note.return_value = {
            "id": "todo_note",
            "title": "Todo",
            "body": "",
            "parent_id": "",
            "created_time": 1704067200000,
            "updated_time": 1704153600000,
            "is_todo": 1,
            "todo_completed": 0,
        }
        mock_client.get_note_tags.return_value = []

        result = create_note(title="Todo", body="", is_todo=True)

        assert result.is_todo is True
        call_kwargs = mock_client.create_note.call_args.kwargs
        assert call_kwargs["is_todo"] == 1


class TestUpdateNote:
    """Tests for update_note function."""

    def test_update_note_partial(self, mock_client: MagicMock) -> None:
        """Test partial update - only specified fields change."""
        mock_client.get_note.return_value = {
            "id": "note1",
            "title": "Updated Title",
            "body": "Original body",
            "parent_id": "nb1",
            "created_time": 1704067200000,
            "updated_time": 1704153600000,
            "is_todo": 0,
            "todo_completed": 0,
        }
        mock_client.get_note_tags.return_value = []

        update_note("note1", title="Updated Title")

        # Only title should be in the update call
        call_kwargs = mock_client.update_note.call_args.kwargs
        assert "title" in call_kwargs
        assert "body" not in call_kwargs
        assert "parent_id" not in call_kwargs

    def test_update_note_no_changes(self, mock_client: MagicMock) -> None:
        """Test update with no changes still returns note."""
        mock_client.get_note.return_value = {
            "id": "note1",
            "title": "Test",
            "body": "",
            "parent_id": "",
            "created_time": 1704067200000,
            "updated_time": 1704153600000,
            "is_todo": 0,
            "todo_completed": 0,
        }
        mock_client.get_note_tags.return_value = []

        result = update_note("note1")

        assert result.id == "note1"
        mock_client.update_note.assert_not_called()

    def test_update_todo_completed(self, mock_client: MagicMock) -> None:
        """Test marking a todo as completed."""
        mock_client.get_note.return_value = {
            "id": "note1",
            "title": "Todo",
            "body": "",
            "parent_id": "",
            "created_time": 1704067200000,
            "updated_time": 1704153600000,
            "is_todo": 1,
            "todo_completed": 1,
        }
        mock_client.get_note_tags.return_value = []

        update_note("note1", todo_completed=True)

        call_kwargs = mock_client.update_note.call_args.kwargs
        assert call_kwargs["todo_completed"] == 1
