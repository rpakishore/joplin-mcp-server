"""Resource tools for Joplin MCP Server."""

from datetime import datetime
from typing import Any

from joplin_mcp.client import get_client
from joplin_mcp.models import Resource


def _ensure_datetime(value: datetime | int | None) -> datetime:
    """Ensure the value is a datetime, converting from timestamp if needed."""
    if value is None:
        return datetime.now()
    if isinstance(value, datetime):
        return value
    # Legacy: convert from milliseconds timestamp
    return datetime.fromtimestamp(value / 1000)


def _resource_from_dict(data: dict[str, Any]) -> Resource:
    """Convert a resource dict to Resource model."""
    return Resource(
        id=data["id"],
        title=data.get("title", "") or "",
        filename=data.get("filename", "") or "",
        mime=data.get("mime", "application/octet-stream") or "application/octet-stream",
        size=data.get("size", 0) or 0,
        created_time=_ensure_datetime(data.get("created_time")),
        updated_time=_ensure_datetime(data.get("updated_time")),
    )


def get_note_resources(note_id: str) -> list[Resource]:
    """Get resources (attachments) for a note.

    Args:
        note_id: The note ID.

    Returns:
        List of resource metadata (no binary content).
    """
    client = get_client()
    resources_data = client.get_note_resources(note_id)

    return [_resource_from_dict(r) for r in resources_data]
