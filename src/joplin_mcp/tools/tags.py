"""Tag tools for Joplin MCP Server."""

from datetime import datetime
from typing import Any

from joplin_mcp.client import get_client
from joplin_mcp.errors import ValidationError
from joplin_mcp.models import Tag


def _ensure_datetime(value: datetime | int | None) -> datetime:
    """Ensure the value is a datetime, converting from timestamp if needed."""
    if value is None:
        return datetime.now()
    if isinstance(value, datetime):
        return value
    # Legacy: convert from milliseconds timestamp
    return datetime.fromtimestamp(value / 1000)


def _tag_from_dict(data: dict[str, Any]) -> Tag:
    """Convert a tag dict to Tag model."""
    return Tag(
        id=data["id"],
        title=data["title"],
        created_time=_ensure_datetime(data.get("created_time")),
        updated_time=_ensure_datetime(data.get("updated_time")),
    )


def list_tags(limit: int = 50) -> list[Tag]:
    """List all tags.

    Args:
        limit: Maximum number of tags to return (default 50, max 100).

    Returns:
        List of tags.
    """
    if limit < 1:
        raise ValidationError("limit must be at least 1")
    if limit > 100:
        limit = 100

    client = get_client()
    tags_data = client.get_tags(
        fields="id,title,created_time,updated_time",
        limit=limit,
    )

    return [_tag_from_dict(t) for t in tags_data]


def get_tag(tag_id: str) -> Tag:
    """Get a tag by ID.

    Args:
        tag_id: The tag ID.

    Returns:
        The tag.
    """
    client = get_client()
    data = client.get_tag(tag_id)
    return _tag_from_dict(data)


def create_tag(title: str) -> Tag:
    """Create a new tag.

    Args:
        title: Tag title.

    Returns:
        The created tag.
    """
    client = get_client()
    created = client.create_tag(title=title)
    return _tag_from_dict(created)


def add_tag_to_note(tag_id: str, note_id: str) -> dict[str, str]:
    """Add a tag to a note.

    Args:
        tag_id: The tag ID.
        note_id: The note ID.

    Returns:
        Success message.
    """
    client = get_client()
    client.add_tag_to_note(tag_id=tag_id, note_id=note_id)
    return {"message": f"Tag {tag_id} added to note {note_id}"}


def remove_tag_from_note(tag_id: str, note_id: str) -> dict[str, str]:
    """Remove a tag from a note.

    Args:
        tag_id: The tag ID.
        note_id: The note ID.

    Returns:
        Success message.
    """
    client = get_client()
    client.remove_tag_from_note(tag_id=tag_id, note_id=note_id)
    return {"message": f"Tag {tag_id} removed from note {note_id}"}
