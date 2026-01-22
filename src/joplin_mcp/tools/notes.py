"""Note tools for Joplin MCP Server."""

from datetime import datetime
from typing import Any

from joplin_mcp.client import get_client
from joplin_mcp.errors import ValidationError
from joplin_mcp.models import Note, NoteSnippet, TagRef


def _ensure_datetime(value: datetime | int | None) -> datetime:
    """Ensure the value is a datetime, converting from timestamp if needed."""
    if value is None:
        return datetime.now()
    if isinstance(value, datetime):
        return value
    # Legacy: convert from milliseconds timestamp
    return datetime.fromtimestamp(value / 1000)


def _build_search_query(
    query: str | None = None,
    notebook_id: str | None = None,
    tag_id: str | None = None,
    is_todo: bool | None = None,
    is_completed: bool | None = None,
) -> str:
    """Build a Joplin search query from structured parameters.

    Args:
        query: Free-text search query.
        notebook_id: Filter by notebook ID.
        tag_id: Filter by tag ID.
        is_todo: Filter for todo items.
        is_completed: Filter for completed todos.

    Returns:
        Joplin search query string.
    """
    parts: list[str] = []

    if query:
        parts.append(query)

    if notebook_id:
        parts.append(f"notebook:{notebook_id}")

    if tag_id:
        parts.append(f"tag:{tag_id}")

    if is_todo is True:
        parts.append("type:todo")
    elif is_todo is False:
        parts.append("type:note")

    if is_completed is True:
        parts.append("iscompleted:1")
    elif is_completed is False:
        parts.append("iscompleted:0")

    return " ".join(parts) if parts else "*"


def search_notes(
    query: str | None = None,
    notebook_id: str | None = None,
    tag_id: str | None = None,
    is_todo: bool | None = None,
    is_completed: bool | None = None,
    limit: int = 50,
    raw_query: str | None = None,
) -> list[NoteSnippet]:
    """Search for notes with various filters.

    Args:
        query: Free-text search query.
        notebook_id: Filter by notebook ID.
        tag_id: Filter by tag ID.
        is_todo: Filter for todo items (True) or regular notes (False).
        is_completed: Filter for completed (True) or incomplete (False) todos.
        limit: Maximum number of results (default 50, max 100).
        raw_query: Raw Joplin search query (overrides other params).

    Returns:
        List of matching notes with truncated body snippets.
    """
    if limit < 1:
        raise ValidationError("limit must be at least 1")
    if limit > 100:
        limit = 100

    client = get_client()

    # Use raw_query if provided, otherwise build from params
    search_query = (
        raw_query
        if raw_query
        else _build_search_query(
            query=query,
            notebook_id=notebook_id,
            tag_id=tag_id,
            is_todo=is_todo,
            is_completed=is_completed,
        )
    )

    results = client.search_notes(
        query=search_query,
        limit=limit,
        fields="id,title,parent_id,created_time,updated_time,is_todo,todo_completed,body",
    )

    snippets: list[NoteSnippet] = []
    for note in results:
        body = note.get("body", "") or ""
        snippet = body[:500] if len(body) > 500 else body

        # Handle todo_completed which can be a datetime or bool
        todo_completed = note.get("todo_completed")
        is_completed_bool = bool(todo_completed) if todo_completed else False

        snippets.append(
            NoteSnippet(
                id=note["id"],
                title=note["title"],
                parent_id=note["parent_id"],
                created_time=_ensure_datetime(note.get("created_time")),
                updated_time=_ensure_datetime(note.get("updated_time")),
                is_todo=bool(note.get("is_todo", False)),
                todo_completed=is_completed_bool,
                snippet=snippet,
            )
        )

    return snippets


def get_note(note_id: str) -> Note:
    """Get a note by ID with full content.

    Args:
        note_id: The note ID.

    Returns:
        Full note with body and attached tags.
    """
    client = get_client()

    note = client.get_note(
        note_id,
        fields=[
            "id",
            "title",
            "body",
            "parent_id",
            "created_time",
            "updated_time",
            "is_todo",
            "todo_completed",
        ],
    )

    # Get tags attached to the note
    tags_data = client.get_note_tags(note_id)
    tags = [TagRef(id=t["id"], title=t["title"]) for t in tags_data]

    # Handle todo_completed which can be a datetime or bool
    todo_completed = note.get("todo_completed")
    is_completed_bool = bool(todo_completed) if todo_completed else False

    return Note(
        id=note["id"],
        title=note["title"],
        body=note.get("body", "") or "",
        parent_id=note["parent_id"],
        created_time=_ensure_datetime(note.get("created_time")),
        updated_time=_ensure_datetime(note.get("updated_time")),
        is_todo=bool(note.get("is_todo", False)),
        todo_completed=is_completed_bool,
        tags=tags,
    )


def create_note(
    title: str,
    body: str,
    notebook_id: str | None = None,
    is_todo: bool = False,
    tags: list[str] | None = None,
) -> Note:
    """Create a new note.

    Args:
        title: Note title.
        body: Note body content.
        notebook_id: ID of the notebook to create the note in.
        is_todo: Whether this is a todo item.
        tags: List of tag IDs to attach to the note.

    Returns:
        The created note.
    """
    client = get_client()

    kwargs: dict[str, Any] = {
        "title": title,
        "body": body,
        "is_todo": 1 if is_todo else 0,
    }

    if notebook_id:
        kwargs["parent_id"] = notebook_id

    created = client.create_note(**kwargs)

    # Attach tags if provided
    if tags:
        for tag_id in tags:
            client.add_tag_to_note(tag_id=tag_id, note_id=created["id"])

    # Return the full note with tags
    return get_note(created["id"])


def update_note(
    note_id: str,
    title: str | None = None,
    body: str | None = None,
    notebook_id: str | None = None,
    is_todo: bool | None = None,
    todo_completed: bool | None = None,
) -> Note:
    """Update an existing note. None values mean 'don't change'.

    Args:
        note_id: The note ID to update.
        title: New title (or None to keep current).
        body: New body content (or None to keep current).
        notebook_id: New notebook ID (or None to keep current).
        is_todo: Whether this is a todo item (or None to keep current).
        todo_completed: Whether the todo is completed (or None to keep current).

    Returns:
        The updated note.
    """
    client = get_client()

    kwargs: dict[str, Any] = {}

    if title is not None:
        kwargs["title"] = title
    if body is not None:
        kwargs["body"] = body
    if notebook_id is not None:
        kwargs["parent_id"] = notebook_id
    if is_todo is not None:
        kwargs["is_todo"] = 1 if is_todo else 0
    if todo_completed is not None:
        kwargs["todo_completed"] = 1 if todo_completed else 0

    if kwargs:
        client.update_note(note_id, **kwargs)

    return get_note(note_id)
