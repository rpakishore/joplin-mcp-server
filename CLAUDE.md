# CLAUDE.md - Agent Quick Reference

## Commands
```bash
uv run pytest                    # Run all tests
uv run pytest tests/test_X.py    # Run specific test file
uv run ruff check src/           # Lint
uv run ruff format src/          # Format
uv run mypy src/                 # Type check
uv run joplin-mcp                # Run MCP server locally
```

## Project Structure
```
src/joplin_mcp/
├── __init__.py          # Package init, exports version
├── __main__.py          # Entry point: `python -m joplin_mcp`
├── server.py            # FastMCP server setup, tool registration
├── config.py            # Environment config (JOPLIN_API_TOKEN, JOPLIN_HOST)
├── client.py            # Joppy client wrapper with connection management
├── errors.py            # Error categories: AuthError, ConnectionError, NotFoundError, ValidationError, JoplinError
├── tools/
│   ├── __init__.py
│   ├── notes.py         # search_notes, get_note, create_note, update_note
│   ├── notebooks.py     # list_notebooks, get_notebook, create_notebook, update_notebook, get_notebook_tree
│   ├── tags.py          # list_tags, get_tag, create_tag, add_tag_to_note, remove_tag_from_note
│   └── resources.py     # get_note_resources
└── models.py            # Pydantic models for requests/responses
tests/
├── conftest.py          # Fixtures: mock joppy client
└── test_*.py            # One test file per tool module
```

## Code Style
- Type hints required on ALL functions (public and private)
- Docstrings: Google style, required on public functions only
- Use Pydantic models for tool inputs/outputs
- Errors: Raise custom exceptions from `errors.py`, never raw exceptions
- Update semantics: `None` means "don't change" for Optional fields

## Architecture Rules
- All Joplin API calls go through `client.py` (never import joppy directly in tools)
- Config loaded once via `config.py` at startup
- Tools return Pydantic models, FastMCP handles serialization
- Search results: metadata + 500-char snippet, use `get_note` for full content
- Pagination: `limit` param (default 50, max 100), no cursor

## Error Handling Pattern
```python
from joplin_mcp.errors import NotFoundError, JoplinError

try:
    result = client.get_note(note_id)
except SomeJoppyException as e:
    raise NotFoundError("Note not found", detail=str(e))
```
