# Joplin MCP Server

[![Tests](https://github.com/rpakishore/joplin-mcp-server/actions/workflows/tests.yml/badge.svg)](https://github.com/rpakishore/joplin-mcp-server/actions/workflows/tests.yml)

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that provides AI assistants with access to your [Joplin](https://joplinapp.org/) notes, notebooks, and tags.

## Features

- **Read & Write Notes**: Search, view, create, and update notes with full Markdown support
- **Organize with Notebooks**: List, create, and manage notebook hierarchy
- **Tag Management**: Create tags and organize notes with tagging
- **Todo Support**: Create and manage todo items with completion tracking
- **Resource Visibility**: View metadata for attachments on notes

**Design Philosophy**: Read + Create/Update only (no delete operations) for productivity without destruction risk.

## Installation

### MCP Client Configuration

Add to your MCP client configuration (e.g., Claude Desktop, Cursor):

```json
{
  "mcpServers": {
    "joplin": {
      "command": "uv",
      "args": [
        "run",
        "--with", "joppy",
        "--with", "mcp",
        "--with", "git+https://github.com/rpakishore/joplin-mcp-server",
        "joplin-mcp"
      ],
      "env": {
        "JOPLIN_API_TOKEN": "your-token-here"
      }
    }
  }
}
```

### Getting Your Joplin API Token

1. Open Joplin desktop application
2. Go to **Tools → Options → Web Clipper**
3. Enable the Web Clipper service
4. Copy the **Authorization token**

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `JOPLIN_API_TOKEN` | Yes | - | Your Joplin API authorization token |
| `JOPLIN_HOST` | No | `localhost` | Joplin API host |
| `JOPLIN_PORT` | No | `41184` | Joplin API port |

## Available Tools

### Notes (4 tools)

| Tool | Description |
|------|-------------|
| `search_notes` | Search notes with filters (query, notebook, tag, todo status) |
| `get_note` | Get full note content with attached tags |
| `create_note` | Create a new note with optional tags and todo status |
| `update_note` | Update note fields (partial update - only specified fields change) |

### Notebooks (5 tools)

| Tool | Description |
|------|-------------|
| `list_notebooks` | List all notebooks (flat list with parent_id) |
| `get_notebook` | Get notebook details |
| `create_notebook` | Create a new notebook (optionally nested) |
| `update_notebook` | Update notebook title or parent |
| `get_notebook_tree` | Get hierarchical notebook structure |

### Tags (5 tools)

| Tool | Description |
|------|-------------|
| `list_tags` | List all tags |
| `get_tag` | Get tag details |
| `create_tag` | Create a new tag |
| `add_tag_to_note` | Attach a tag to a note |
| `remove_tag_from_note` | Remove a tag from a note |

### Resources (1 tool)

| Tool | Description |
|------|-------------|
| `get_note_resources` | List attachments on a note (metadata only) |

## Usage Examples

### Search for Notes

```
Search for notes containing "meeting" in notebook "Work":
→ search_notes(query="meeting", notebook_id="abc123")

Find incomplete todos:
→ search_notes(is_todo=true, is_completed=false)

Advanced search with raw Joplin query:
→ search_notes(raw_query="title:report created:20240101")
```

### Create a Note

```
Create a simple note:
→ create_note(title="Meeting Notes", body="# Agenda\n- Item 1\n- Item 2", notebook_id="abc123")

Create a todo:
→ create_note(title="Review PR", body="Check the new feature branch", is_todo=true)

Create with tags:
→ create_note(title="Project Ideas", body="...", tags=["tag-id-1", "tag-id-2"])
```

### Update a Note

```
Update only the title (body unchanged):
→ update_note(note_id="xyz789", title="New Title")

Mark todo as complete:
→ update_note(note_id="xyz789", todo_completed=true)
```

### Organize with Tags

```
Create a tag and apply it:
→ create_tag(title="important")
→ add_tag_to_note(tag_id="new-tag-id", note_id="note-id")
```

## Search Parameters

The `search_notes` tool supports these filters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | string | Text search in title and body |
| `notebook_id` | string | Filter by notebook |
| `tag_id` | string | Filter by tag |
| `is_todo` | boolean | Filter to only todos |
| `is_completed` | boolean | Filter by completion status |
| `limit` | integer | Max results (default: 50, max: 100) |
| `raw_query` | string | Raw Joplin search query (advanced) |

## Error Handling

The server returns structured errors with categories:

| Category | Description |
|----------|-------------|
| `auth_error` | Invalid or missing API token |
| `connection_error` | Cannot connect to Joplin |
| `not_found` | Note/notebook/tag doesn't exist |
| `validation_error` | Invalid parameters |
| `joplin_error` | Other Joplin API errors |

Each error includes a friendly `message` and optional `detail` field with technical information.

## Development

```bash
# Clone the repository
git clone https://github.com/rpakishore/joplin-mcp-server
cd joplin-mcp-server

# Install dependencies
uv sync

# Run tests
uv run pytest

# Lint and format
uv run ruff check src/
uv run ruff format src/

# Type check
uv run mypy src/

# Run server locally
JOPLIN_API_TOKEN=your-token uv run joplin-mcp
```

## Requirements

- Python 3.11+
- Joplin desktop with Web Clipper enabled
- `uv` package manager

## License

MIT

## Credits

- [joppy](https://github.com/marph91/joppy) - Python interface to Joplin API
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) - Model Context Protocol implementation
