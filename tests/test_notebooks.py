"""Tests for notebook tools."""

from unittest.mock import MagicMock, patch

import pytest

from joplin_mcp.errors import ValidationError
from joplin_mcp.tools.notebooks import (
    create_notebook,
    get_notebook,
    get_notebook_tree,
    list_notebooks,
    update_notebook,
)


@pytest.fixture
def mock_client():
    """Create a mock client for testing."""
    with patch("joplin_mcp.tools.notebooks.get_client") as mock_get_client:
        mock = MagicMock()
        mock_get_client.return_value = mock
        yield mock


class TestListNotebooks:
    """Tests for list_notebooks function."""

    def test_list_notebooks_basic(self, mock_client: MagicMock) -> None:
        """Test basic notebook listing."""
        mock_client.get_notebooks.return_value = [
            {
                "id": "nb1",
                "title": "Notebook 1",
                "parent_id": "",
                "created_time": 1704067200000,
                "updated_time": 1704153600000,
            },
            {
                "id": "nb2",
                "title": "Notebook 2",
                "parent_id": "nb1",
                "created_time": 1704067200000,
                "updated_time": 1704153600000,
            },
        ]

        result = list_notebooks()

        assert len(result) == 2
        assert result[0].id == "nb1"
        assert result[1].parent_id == "nb1"

    def test_list_notebooks_with_parent_id(self, mock_client: MagicMock) -> None:
        """Test that parent_id is correctly populated."""
        mock_client.get_notebooks.return_value = [
            {
                "id": "child",
                "title": "Child",
                "parent_id": "parent",
                "created_time": 1704067200000,
                "updated_time": 1704153600000,
            },
        ]

        result = list_notebooks()

        assert result[0].parent_id == "parent"

    def test_list_notebooks_limit_enforced(self, mock_client: MagicMock) -> None:
        """Test that limit is capped at 100."""
        mock_client.get_notebooks.return_value = []

        list_notebooks(limit=200)

        call_kwargs = mock_client.get_notebooks.call_args.kwargs
        assert call_kwargs["limit"] == 100

    def test_list_notebooks_invalid_limit(self, mock_client: MagicMock) -> None:
        """Test that invalid limit raises ValidationError."""
        with pytest.raises(ValidationError):
            list_notebooks(limit=0)


class TestGetNotebook:
    """Tests for get_notebook function."""

    def test_get_notebook(self, mock_client: MagicMock) -> None:
        """Test getting a notebook by ID."""
        mock_client.get_notebook.return_value = {
            "id": "nb1",
            "title": "Test Notebook",
            "parent_id": "",
            "created_time": 1704067200000,
            "updated_time": 1704153600000,
        }

        result = get_notebook("nb1")

        assert result.id == "nb1"
        assert result.title == "Test Notebook"


class TestCreateNotebook:
    """Tests for create_notebook function."""

    def test_create_notebook_minimal(self, mock_client: MagicMock) -> None:
        """Test creating a notebook with just title."""
        mock_client.create_notebook.return_value = {
            "id": "new_nb",
            "title": "New Notebook",
            "parent_id": "",
            "created_time": 1704067200000,
            "updated_time": 1704153600000,
        }

        result = create_notebook(title="New Notebook")

        assert result.id == "new_nb"
        assert result.title == "New Notebook"

    def test_create_notebook_nested(self, mock_client: MagicMock) -> None:
        """Test creating a nested notebook."""
        mock_client.create_notebook.return_value = {
            "id": "child_nb",
            "title": "Child",
            "parent_id": "parent_nb",
            "created_time": 1704067200000,
            "updated_time": 1704153600000,
        }

        create_notebook(title="Child", parent_id="parent_nb")

        call_kwargs = mock_client.create_notebook.call_args.kwargs
        assert call_kwargs["parent_id"] == "parent_nb"


class TestUpdateNotebook:
    """Tests for update_notebook function."""

    def test_update_notebook_title(self, mock_client: MagicMock) -> None:
        """Test updating notebook title."""
        mock_client.get_notebook.return_value = {
            "id": "nb1",
            "title": "Updated Title",
            "parent_id": "",
            "created_time": 1704067200000,
            "updated_time": 1704153600000,
        }

        update_notebook("nb1", title="Updated Title")

        call_kwargs = mock_client.update_notebook.call_args.kwargs
        assert call_kwargs["title"] == "Updated Title"

    def test_update_notebook_no_changes(self, mock_client: MagicMock) -> None:
        """Test update with no changes."""
        mock_client.get_notebook.return_value = {
            "id": "nb1",
            "title": "Test",
            "parent_id": "",
            "created_time": 1704067200000,
            "updated_time": 1704153600000,
        }

        update_notebook("nb1")

        mock_client.update_notebook.assert_not_called()


class TestGetNotebookTree:
    """Tests for get_notebook_tree function."""

    def test_get_notebook_tree_flat(self, mock_client: MagicMock) -> None:
        """Test tree with all root-level notebooks."""
        mock_client.get_notebooks.return_value = [
            {"id": "nb1", "title": "A", "parent_id": ""},
            {"id": "nb2", "title": "B", "parent_id": ""},
        ]

        result = get_notebook_tree()

        assert len(result) == 2
        assert result[0].children == []
        assert result[1].children == []

    def test_get_notebook_tree_nested(self, mock_client: MagicMock) -> None:
        """Test tree with nested notebooks."""
        mock_client.get_notebooks.return_value = [
            {"id": "root", "title": "Root", "parent_id": ""},
            {"id": "child1", "title": "Child 1", "parent_id": "root"},
            {"id": "child2", "title": "Child 2", "parent_id": "root"},
            {"id": "grandchild", "title": "Grandchild", "parent_id": "child1"},
        ]

        result = get_notebook_tree()

        assert len(result) == 1  # Only root at top level
        assert result[0].id == "root"
        assert len(result[0].children) == 2  # Two children

        # Find child1 and verify grandchild
        child1 = next(c for c in result[0].children if c.id == "child1")
        assert len(child1.children) == 1
        assert child1.children[0].id == "grandchild"

    def test_get_notebook_tree_orphan(self, mock_client: MagicMock) -> None:
        """Test that notebooks with missing parents are treated as root."""
        mock_client.get_notebooks.return_value = [
            {"id": "nb1", "title": "Root", "parent_id": ""},
            {"id": "orphan", "title": "Orphan", "parent_id": "missing_parent"},
        ]

        result = get_notebook_tree()

        # Orphan should be at root level since parent doesn't exist
        assert len(result) == 2
        root_ids = [n.id for n in result]
        assert "orphan" in root_ids
