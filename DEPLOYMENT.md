# DEPLOYMENT.md - Operations Guide

## Environment Setup

### Prerequisites

1. **Python 3.11+** installed
2. **uv** package manager installed:
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Windows (PowerShell)
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```
3. **Joplin Desktop** running with Web Clipper enabled

### Joplin Configuration

1. Open Joplin desktop application
2. Navigate to **Tools → Options → Web Clipper**
3. Toggle **Enable Web Clipper Service** to ON
4. Note the port (default: `41184`)
5. Copy the **Authorization token**

## Running the Server

### Via MCP Client (Recommended)

Add to your MCP client configuration file:

**Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):
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

**Cursor/Other MCP Clients**: Check your client's documentation for config file location.

### Local Development

```bash
# Clone and install
git clone https://github.com/rpakishore/joplin-mcp-server
cd joplin-mcp-server
uv sync

# Set environment variables
export JOPLIN_API_TOKEN="your-token-here"
export JOPLIN_HOST="localhost"  # optional
export JOPLIN_PORT="41184"      # optional

# Run server
uv run joplin-mcp
```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `JOPLIN_API_TOKEN` | **Yes** | - | Joplin Web Clipper authorization token |
| `JOPLIN_HOST` | No | `localhost` | Joplin API hostname |
| `JOPLIN_PORT` | No | `41184` | Joplin API port |

## CI/CD

### GitHub Actions Workflow

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          version: "latest"

      - name: Set up Python
        run: uv python install 3.11

      - name: Install dependencies
        run: uv sync --all-extras

      - name: Lint
        run: uv run ruff check src/ tests/

      - name: Type check
        run: uv run mypy src/

      - name: Run tests
        run: uv run pytest --tb=short

  format-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          version: "latest"

      - name: Check formatting
        run: |
          uv sync
          uv run ruff format --check src/ tests/
```

### Release Process

1. Update version in `pyproject.toml`
2. Create git tag: `git tag v0.1.0`
3. Push tag: `git push origin v0.1.0`
4. GitHub release will make the package available via `git+https://github.com/...`

## Troubleshooting

### Connection Errors

**Error**: `connection_error: Cannot connect to Joplin`

**Solutions**:
1. Verify Joplin desktop is running
2. Check Web Clipper is enabled: **Tools → Options → Web Clipper**
3. Verify port matches: default is `41184`
4. Check firewall isn't blocking localhost connections

```bash
# Test Joplin API directly
curl http://localhost:41184/ping
# Should return: "JoplinClipperServer"
```

### Authentication Errors

**Error**: `auth_error: Invalid API token`

**Solutions**:
1. Regenerate token in Joplin: **Tools → Options → Web Clipper → Copy token**
2. Verify no extra whitespace in token
3. Check environment variable is set correctly:
   ```bash
   echo $JOPLIN_API_TOKEN
   ```

### Token Not Set

**Error**: `ValueError: JOPLIN_API_TOKEN environment variable is required`

**Solutions**:
1. Set the environment variable in your shell:
   ```bash
   export JOPLIN_API_TOKEN="your-token"
   ```
2. Or add to MCP config's `env` block

### Server Not Starting

**Error**: `ModuleNotFoundError: No module named 'joplin_mcp'`

**Solutions**:
1. Ensure using `uv run` with all dependencies:
   ```bash
   uv run --with joppy --with mcp --with git+https://github.com/rpakishore/joplin-mcp-server joplin-mcp
   ```
2. For local dev, ensure `uv sync` completed successfully

### MCP Client Not Detecting Server

**Solutions**:
1. Restart the MCP client (Claude Desktop, Cursor, etc.)
2. Verify JSON config syntax is valid
3. Check client logs for error messages
4. Test server manually first:
   ```bash
   JOPLIN_API_TOKEN=your-token uv run joplin-mcp
   ```

## Monitoring

### Logs

The MCP server logs to stderr. In MCP clients, check the client's log output.

For local debugging:
```bash
JOPLIN_API_TOKEN=your-token uv run joplin-mcp 2>&1 | tee server.log
```

### Health Check

Test Joplin connectivity before starting:
```bash
curl -s "http://localhost:41184/ping" && echo " - Joplin OK"
```

## Security Considerations

1. **Token Security**: The `JOPLIN_API_TOKEN` provides full access to your Joplin data. Never commit it to version control.

2. **Local Only**: By default, Joplin's Web Clipper only listens on localhost. This server is designed for local use only.

3. **No Delete Operations**: This MCP server intentionally omits delete operations to prevent accidental data loss.

4. **Read + Write Scope**: The server can read all notes/notebooks/tags and create/update them. Consider this when granting access to AI assistants.
