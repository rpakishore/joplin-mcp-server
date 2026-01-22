---
name: upgrade-joppy
description: Analyze joppy library updates and implement necessary changes to this repo
allowed-tools: Read, Grep, Glob, WebFetch, WebSearch, Bash, Edit, Write, TodoWrite
---

# Joppy Upgrade Analysis

Analyze updates to the joppy library and implement necessary changes to this repository.

## Context

This is a Joplin MCP Server that wraps the joppy library. All joppy interactions go through `src/joplin_mcp/client.py`.

**Arguments**: $ARGUMENTS (optional: specific version to target, or leave empty for latest)

## Step 1: Gather Current State

Read these files to understand current joppy usage:

1. Read `JOPPY_UPGRADE.md` for the API mapping table and constraints
2. Read `src/joplin_mcp/client.py` to see current wrapper implementation
3. Read `pyproject.toml` to check current version constraints

## Step 2: Fetch Joppy Updates

1. Fetch the latest joppy releases from: https://github.com/marph91/joppy/releases
2. Search for any joppy changelog, breaking changes, or migration guides
3. If a specific version was requested via $ARGUMENTS, focus on changes up to that version

## Step 3: Analyze Impact

Compare the release notes against our API usage. For each change, categorize as:

### Must Fix (Breaking Changes)
Changes that will break our current implementation:
- Method signature changes for methods we use
- Removed methods or parameters
- Changed return types

### Should Update (Deprecations)
Things we should address soon:
- Deprecated methods we use
- Recommended migration paths
- Security fixes

### Nice to Have (New Features)
New capabilities that could enhance this project:
- New API methods that align with our tools
- Performance improvements
- New data fields we could expose

**Remember**: Only consider features that align with our core ideology (read + create/update, no deletes).

## Step 4: Generate Report

Create a clear summary:

```
## Joppy Upgrade Report

**Current version**: [from pyproject.toml or "unversioned"]
**Latest version**: [from releases]

### Breaking Changes
- [list any breaking changes]

### Deprecations
- [list deprecations affecting us]

### New Features Worth Adding
- [list features that align with our ideology]

### Recommended Actions
1. [specific action items]
```

## Step 5: Implement Changes (with approval)

If changes are needed, ask for approval before implementing. Then:

1. Update `src/joplin_mcp/client.py` wrapper methods
2. Update error handling if needed
3. Add new tool functions if new features warrant them (in `tools/` modules)
4. Update Pydantic models in `models.py` if data structures changed
5. Update or add tests in `tests/`

## Step 6: Validate

Run the validation suite:
```bash
uv run pytest
uv run ruff check src/
uv run mypy src/
```

## Step 7: Update Documentation

1. Update `JOPPY_UPGRADE.md` with:
   - Any API mapping changes
   - New entry in Version History table
2. Update `README.md` if new tools were added

## Core Ideology Reminder

When evaluating new features or changes, remember:

1. **No delete operations** - Never expose delete functionality (except tag removal from notes)
2. **client.py is the gateway** - All joppy imports stay in client.py
3. **Error translation** - All joppy exceptions must be translated to our error types
4. **Pydantic models** - All tool I/O uses Pydantic models
5. **Update semantics** - `None` means "don't change" for Optional fields
