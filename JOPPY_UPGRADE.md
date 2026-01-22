# Joppy Upgrade Guide

This document tracks the joppy library API surface used by this project and provides guidance for handling upgrades.

## Current Joppy API Usage

### Imports

```python
from joppy.client_api import ClientApi
from joppy.data_types import NotebookData, NoteData, TagData
```

### ClientApi Initialization

```python
ClientApi(token=api_token, url=f"http://{host}:{port}")
```

### API Method Mapping

| Our Method | Joppy ClientApi Method | Parameters | Returns |
|------------|------------------------|------------|---------|
| **Notes** ||||
| `get_note()` | `client.get_note()` | `id_`, `fields` (comma-separated string) | `NoteData` dataclass |
| `search_notes()` | `client.search()` | `query`, `**kwargs` | Object with `.items` list |
| `create_note()` | `client.add_note()` | `**kwargs` (title, body, parent_id, etc.) | `str` (note ID) |
| `update_note()` | `client.modify_note()` | `id_`, `**kwargs` | `None` |
| `get_note_tags()` | `client.get_tags()` | `note_id=` | Object with `.items` list of `TagData` |
| `get_note_resources()` | `client.get_resources()` | `note_id=` | Object with `.items` list |
| **Notebooks** ||||
| `get_notebooks()` | `client.get_notebooks()` | `**kwargs` | Object with `.items` list of `NotebookData` |
| `get_notebook()` | `client.get_notebook()` | `id_` | `NotebookData` dataclass |
| `create_notebook()` | `client.add_notebook()` | `**kwargs` (title, parent_id) | `str` (notebook ID) |
| `update_notebook()` | `client.modify_notebook()` | `id_`, `**kwargs` | `None` |
| **Tags** ||||
| `get_tags()` | `client.get_tags()` | `**kwargs` | Object with `.items` list of `TagData` |
| `get_tag()` | `client.get_tag()` | `id_` | `TagData` dataclass |
| `create_tag()` | `client.add_tag()` | `title` | `str` (tag ID) |
| `add_tag_to_note()` | `client.add_tag_to_note()` | `tag_id`, `note_id` | `None` |
| `remove_tag_from_note()` | `client.delete_tag()` | `id_`, `note_id=` | `None` |

### Data Types We Depend On

- `NoteData` - fields: id, title, body, parent_id, created_time, updated_time, is_todo, todo_completed
- `NotebookData` - fields: id, title, parent_id, created_time, updated_time
- `TagData` - fields: id, title, created_time, updated_time

### Return Value Patterns

1. **Single item methods** (`get_note`, `get_notebook`, `get_tag`): Return dataclass directly
2. **List methods** (`get_notebooks`, `get_tags`, `search`): Return object with `.items` property
3. **Create methods** (`add_note`, `add_notebook`, `add_tag`): Return string ID of created item
4. **Modify methods** (`modify_note`, `modify_notebook`): Return `None`
5. **Association methods** (`add_tag_to_note`, `delete_tag`): Return `None`

---

## Core Ideology Constraints

When upgrading joppy, changes **must** adhere to these principles:

### 1. No Delete Operations
- **Exception**: `remove_tag_from_note` (removes association, not the tag itself)
- Never expose `delete_note`, `delete_notebook`, or `delete_tag` even if joppy adds them
- Design philosophy: productivity without destruction risk

### 2. client.py Is the Only Joppy Interface
- All joppy imports stay in `client.py`
- Tools in `tools/` only import from `joplin_mcp.client`
- Never import joppy directly in tool modules

### 3. Error Translation Required
All joppy exceptions must be caught and translated to our error types:
- Connection failures → `ConnectionError`
- 401/403 responses → `AuthError`
- 404 responses → `NotFoundError`
- Other errors → `JoplinAPIError`

### 4. Pydantic Models for All I/O
- Tool inputs use Pydantic models from `models.py`
- Tool outputs return Pydantic models (FastMCP handles serialization)
- Raw dicts from joppy are converted to Pydantic models in tools

### 5. Update Semantics
- `None` means "don't change" for Optional fields in update operations
- Only explicitly provided values should be passed to joppy

---

## Upgrade Checklist

Use this checklist when upgrading joppy:

### Analysis Phase
- [ ] Fetch latest joppy release notes from GitHub
- [ ] Check for breaking changes in methods we use (see API Mapping table above)
- [ ] Check for new features that could enhance existing tools
- [ ] Check for deprecations we need to address
- [ ] Check for bug fixes that affect our usage

### Implementation Phase
- [ ] Update `client.py` wrapper methods if API changed
- [ ] Update error handling if new exception types exist
- [ ] Add new wrapper methods for valuable new features
- [ ] Create new tool functions if warranted (following existing patterns)
- [ ] Update Pydantic models if data structures changed

### Validation Phase
- [ ] Run tests: `uv run pytest`
- [ ] Run linter: `uv run ruff check src/`
- [ ] Run type checker: `uv run mypy src/`
- [ ] Manual test with real Joplin instance if possible

### Documentation Phase
- [ ] Update this document with any API changes
- [ ] Update README.md if new tools were added
- [ ] Update CLAUDE.md if patterns changed

---

## Joppy Resources

- **GitHub Repository**: https://github.com/marph91/joppy
- **Releases**: https://github.com/marph91/joppy/releases
- **PyPI**: https://pypi.org/project/joppy/

---

## Version History

| Date | Joppy Version | Changes Made |
|------|---------------|--------------|
| _Initial_ | (unversioned) | Initial implementation |

_Update this table when upgrades are performed._
