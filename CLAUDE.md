# CLAUDE.md

## Project Overview

**uv workspace** with two Python packages (Python 3.12+):
- **tde** - Runs `dotnet format`, outputs diagnostics in TOON format
- **tda** - AI agent using claude-agent-sdk, wraps tde tools for conversational analysis

Structure:
```
src/tde/src/tde/
  ├── runner.py    # Executes dotnet format, manages temp JSON
  ├── parser.py    # JSON → list[Diagnostic]
  ├── formatter.py # Diagnostic → TOON string
  └── cli.py       # Click CLI: 'style' and 'analyzers' commands
src/tda/src/tda/
  ├── tools.py     # @tool functions wrapping tde
  ├── agent.py     # MCP server creation
  ├── cli.py       # Agent CLI (anyio-based)
  └── system_prompt.prompty  # Agent instructions
```

## Key Configuration

**TDA Agent (src/tda/src/tda/cli.py):**
- System prompt: `system_prompt.prompty` (Prompty format) loaded at runtime
- Uses `SystemPromptPreset` with `append` (base Claude Code behavior preserved)
- **CRITICAL**: `append` field doesn't support multiline strings → collapsed to single line
- Permission mode: `bypassPermissions` (auto-approves all tools)
- Available tools: `Read`, `Write`, `Edit`, `Glob`, `Grep`, `WebFetch`, MCP diagnostics tools
- MCP tools support file filtering via `include` parameter (glob patterns)
- Interactive mode: `-i` flag maintains conversation context, shows spinner while waiting
- Default severity: `warn` (unless explicitly requested otherwise)
- Documentation lookup: WebFetch for CA*/IDE* codes from Microsoft Learn
- Context7 ref: `/anthropics/claude-agent-sdk-python`

**TDE Commands:**
- `--no-restore` always used (performance)
- dotnet format flags: `--verify-no-changes`, `--verbosity quiet`, `--report <temp>`
- Supports `--diagnostics` (filter IDs) and `--severity` (error/hidden/info/warn)

**TOON Format:**
- Token reduction: 30-60% vs JSON
- Grouping: `group_by="error"` (by rule ID) or `"file"` (by file path)
- Summary mode: `summary=True`

## Important Rules

1. **Terminology**: Always use "diagnostic" (never "violation", "error", or "issue")
2. **Workspace deps**: Add to package `pyproject.toml`, use `workspace = true` for cross-package deps, run `uv lock`
3. **Adding agent tools**:
   - Add to tde package → Create `@tool` in `tda/tools.py` → Register in `tda/agent.py` → Add to `allowed_tools` in `tda/cli.py`
   - Naming: `extract_<type>_diagnostics`

## Commands

```bash
uv sync  # Install workspace
uv run --package tde tde style /path --severity warn --summary
uv run --package tda tda "query" --cwd /path -i  # Interactive mode
```
