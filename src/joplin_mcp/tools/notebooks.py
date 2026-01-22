"""Notebook tools for Joplin MCP Server."""

from datetime import datetime
from typing import Any

from joplin_mcp.client import get_client
from joplin_mcp.errors import ValidationError
from joplin_mcp.models import Notebook, NotebookTreeNode


def _ensure_datetime(value: datetime | int | None) -> datetime:
    """Ensure the value is a datetime, converting from timestamp if needed."""
    if value is None:
        return datetime.now()
    if isinstance(value, datetime):
        return value
    # Legacy: convert from milliseconds timestamp
    return datetime.fromtimestamp(value / 1000)


def _notebook_from_dict(data: dict[str, Any]) -> Notebook:
    """Convert a notebook dict to Notebook model."""
    return Notebook(
        id=data["id"],
        title=data["title"],
        parent_id=data.get("parent_id") or None,
        created_time=_ensure_datetime(data.get("created_time")),
        updated_time=_ensure_datetime(data.get("updated_time")),
    )


def list_notebooks(limit: int = 50) -> list[Notebook]:
    """List all notebooks as a flat list.

    Args:
        limit: Maximum number of notebooks to return (default 50, max 100).

    Returns:
        Flat list of notebooks with parent_id field.
    """
    if limit < 1:
        raise ValidationError("limit must be at least 1")
    if limit > 100:
        limit = 100

    client = get_client()
    notebooks_data = client.get_notebooks(
        fields="id,title,parent_id,created_time,updated_time",
        limit=limit,
    )

    return [_notebook_from_dict(nb) for nb in notebooks_data]


def get_notebook(notebook_id: str) -> Notebook:
    """Get a notebook by ID.

    Args:
        notebook_id: The notebook ID.

    Returns:
        The notebook.
    """
    client = get_client()
    data = client.get_notebook(notebook_id)
    return _notebook_from_dict(data)


def create_notebook(title: str, parent_id: str | None = None) -> Notebook:
    """Create a new notebook.

    Args:
        title: Notebook title.
        parent_id: ID of parent notebook (for nested notebooks).

    Returns:
        The created notebook.
    """
    client = get_client()

    kwargs: dict[str, Any] = {"title": title}
    if parent_id:
        kwargs["parent_id"] = parent_id

    created = client.create_notebook(**kwargs)
    return _notebook_from_dict(created)


def update_notebook(
    notebook_id: str,
    title: str | None = None,
    parent_id: str | None = None,
) -> Notebook:
    """Update an existing notebook. None values mean 'don't change'.

    Args:
        notebook_id: The notebook ID to update.
        title: New title (or None to keep current).
        parent_id: New parent ID (or None to keep current).

    Returns:
        The updated notebook.
    """
    client = get_client()

    kwargs: dict[str, Any] = {}
    if title is not None:
        kwargs["title"] = title
    if parent_id is not None:
        kwargs["parent_id"] = parent_id

    if kwargs:
        client.update_notebook(notebook_id, **kwargs)

    return get_notebook(notebook_id)


def get_notebook_tree() -> list[NotebookTreeNode]:
    """Get the notebook hierarchy as a tree.

    Returns:
        List of root-level notebook nodes with nested children.
    """
    client = get_client()
    notebooks_data = client.get_notebooks(
        fields="id,title,parent_id",
        limit=100,
    )

    # Build a map of id -> notebook data
    notebook_map: dict[str, dict[str, Any]] = {nb["id"]: nb for nb in notebooks_data}

    # Build children map
    children_map: dict[str, list[str]] = {}
    root_ids: list[str] = []

    for nb in notebooks_data:
        parent_id = nb.get("parent_id")
        if parent_id and parent_id in notebook_map:
            if parent_id not in children_map:
                children_map[parent_id] = []
            children_map[parent_id].append(nb["id"])
        else:
            root_ids.append(nb["id"])

    def build_tree(node_id: str) -> NotebookTreeNode:
        """Recursively build a tree node."""
        nb = notebook_map[node_id]
        child_ids = children_map.get(node_id, [])
        children = [build_tree(child_id) for child_id in child_ids]
        return NotebookTreeNode(
            id=nb["id"],
            title=nb["title"],
            children=children,
        )

    return [build_tree(root_id) for root_id in root_ids]
