"""MCP Server for Joplin."""

from mcp.server.fastmcp import FastMCP

from joplin_mcp.errors import JoplinMCPError
from joplin_mcp.models import (
    ErrorResponse,
    Note,
    Notebook,
    NotebookTreeNode,
    NoteSnippet,
    Resource,
    Tag,
)
from joplin_mcp.tools import notebooks, notes, resources, tags

mcp = FastMCP("joplin")


def _handle_error(e: JoplinMCPError) -> ErrorResponse:
    """Convert a JoplinMCPError to ErrorResponse."""
    return ErrorResponse(
        category=e.category,
        message=e.message,
        detail=e.detail,
    )


# Note tools
@mcp.tool()
def search_notes(
    query: str | None = None,
    notebook_id: str | None = None,
    tag_id: str | None = None,
    is_todo: bool | None = None,
    is_completed: bool | None = None,
    limit: int = 50,
    raw_query: str | None = None,
) -> list[NoteSnippet] | ErrorResponse:
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
    try:
        return notes.search_notes(
            query=query,
            notebook_id=notebook_id,
            tag_id=tag_id,
            is_todo=is_todo,
            is_completed=is_completed,
            limit=limit,
            raw_query=raw_query,
        )
    except JoplinMCPError as e:
        return _handle_error(e)


@mcp.tool()
def get_note(note_id: str) -> Note | ErrorResponse:
    """Get a note by ID with full content.

    Args:
        note_id: The note ID.

    Returns:
        Full note with body and attached tags.
    """
    try:
        return notes.get_note(note_id)
    except JoplinMCPError as e:
        return _handle_error(e)


@mcp.tool()
def create_note(
    title: str,
    body: str,
    notebook_id: str | None = None,
    is_todo: bool = False,
    tags: list[str] | None = None,
) -> Note | ErrorResponse:
    """Create a new note.

    Args:
        title: Note title.
        body: Note body content (markdown supported).
        notebook_id: ID of the notebook to create the note in.
        is_todo: Whether this is a todo item.
        tags: List of tag IDs to attach to the note.

    Returns:
        The created note.
    """
    try:
        return notes.create_note(
            title=title,
            body=body,
            notebook_id=notebook_id,
            is_todo=is_todo,
            tags=tags,
        )
    except JoplinMCPError as e:
        return _handle_error(e)


@mcp.tool()
def update_note(
    note_id: str,
    title: str | None = None,
    body: str | None = None,
    notebook_id: str | None = None,
    is_todo: bool | None = None,
    todo_completed: bool | None = None,
) -> Note | ErrorResponse:
    """Update an existing note. Omit fields to keep current values.

    Args:
        note_id: The note ID to update.
        title: New title (or omit to keep current).
        body: New body content (or omit to keep current).
        notebook_id: New notebook ID (or omit to keep current).
        is_todo: Whether this is a todo item (or omit to keep current).
        todo_completed: Whether the todo is completed (or omit to keep current).

    Returns:
        The updated note.
    """
    try:
        return notes.update_note(
            note_id=note_id,
            title=title,
            body=body,
            notebook_id=notebook_id,
            is_todo=is_todo,
            todo_completed=todo_completed,
        )
    except JoplinMCPError as e:
        return _handle_error(e)


# Notebook tools
@mcp.tool()
def list_notebooks(limit: int = 50) -> list[Notebook] | ErrorResponse:
    """List all notebooks as a flat list.

    Args:
        limit: Maximum number of notebooks to return (default 50, max 100).

    Returns:
        Flat list of notebooks with parent_id field for hierarchy.
    """
    try:
        return notebooks.list_notebooks(limit=limit)
    except JoplinMCPError as e:
        return _handle_error(e)


@mcp.tool()
def get_notebook(notebook_id: str) -> Notebook | ErrorResponse:
    """Get a notebook by ID.

    Args:
        notebook_id: The notebook ID.

    Returns:
        The notebook.
    """
    try:
        return notebooks.get_notebook(notebook_id)
    except JoplinMCPError as e:
        return _handle_error(e)


@mcp.tool()
def create_notebook(
    title: str,
    parent_id: str | None = None,
) -> Notebook | ErrorResponse:
    """Create a new notebook.

    Args:
        title: Notebook title.
        parent_id: ID of parent notebook (for nested notebooks).

    Returns:
        The created notebook.
    """
    try:
        return notebooks.create_notebook(title=title, parent_id=parent_id)
    except JoplinMCPError as e:
        return _handle_error(e)


@mcp.tool()
def update_notebook(
    notebook_id: str,
    title: str | None = None,
    parent_id: str | None = None,
) -> Notebook | ErrorResponse:
    """Update an existing notebook. Omit fields to keep current values.

    Args:
        notebook_id: The notebook ID to update.
        title: New title (or omit to keep current).
        parent_id: New parent ID (or omit to keep current).

    Returns:
        The updated notebook.
    """
    try:
        return notebooks.update_notebook(
            notebook_id=notebook_id,
            title=title,
            parent_id=parent_id,
        )
    except JoplinMCPError as e:
        return _handle_error(e)


@mcp.tool()
def get_notebook_tree() -> list[NotebookTreeNode] | ErrorResponse:
    """Get the notebook hierarchy as a tree.

    Returns:
        List of root-level notebook nodes with nested children.
    """
    try:
        return notebooks.get_notebook_tree()
    except JoplinMCPError as e:
        return _handle_error(e)


# Tag tools
@mcp.tool()
def list_tags(limit: int = 50) -> list[Tag] | ErrorResponse:
    """List all tags.

    Args:
        limit: Maximum number of tags to return (default 50, max 100).

    Returns:
        List of tags.
    """
    try:
        return tags.list_tags(limit=limit)
    except JoplinMCPError as e:
        return _handle_error(e)


@mcp.tool()
def get_tag(tag_id: str) -> Tag | ErrorResponse:
    """Get a tag by ID.

    Args:
        tag_id: The tag ID.

    Returns:
        The tag.
    """
    try:
        return tags.get_tag(tag_id)
    except JoplinMCPError as e:
        return _handle_error(e)


@mcp.tool()
def create_tag(title: str) -> Tag | ErrorResponse:
    """Create a new tag.

    Args:
        title: Tag title.

    Returns:
        The created tag.
    """
    try:
        return tags.create_tag(title=title)
    except JoplinMCPError as e:
        return _handle_error(e)


@mcp.tool()
def add_tag_to_note(tag_id: str, note_id: str) -> dict[str, str] | ErrorResponse:
    """Add a tag to a note.

    Args:
        tag_id: The tag ID.
        note_id: The note ID.

    Returns:
        Success message.
    """
    try:
        return tags.add_tag_to_note(tag_id=tag_id, note_id=note_id)
    except JoplinMCPError as e:
        return _handle_error(e)


@mcp.tool()
def remove_tag_from_note(tag_id: str, note_id: str) -> dict[str, str] | ErrorResponse:
    """Remove a tag from a note.

    Args:
        tag_id: The tag ID.
        note_id: The note ID.

    Returns:
        Success message.
    """
    try:
        return tags.remove_tag_from_note(tag_id=tag_id, note_id=note_id)
    except JoplinMCPError as e:
        return _handle_error(e)


# Resource tools
@mcp.tool()
def get_note_resources(note_id: str) -> list[Resource] | ErrorResponse:
    """Get resources (attachments) for a note.

    Args:
        note_id: The note ID.

    Returns:
        List of resource metadata (no binary content).
    """
    try:
        return resources.get_note_resources(note_id)
    except JoplinMCPError as e:
        return _handle_error(e)


def main() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
