# repo-memory-mcp

mcp-name: io.github.Umarjaum/repo-memory-mcp

## Persistent memory for AI coding agents

AI coding agents are powerful, but they forget repository-specific corrections, conventions, constraints, and architectural decisions. **repo-memory-mcp** gives MCP-compatible coding agents a persistent, local, repository-aware memory layer.

> **Teach your coding agent once. Let your repository remember.**

[![Tests](https://github.com/Umarjaum/repo-memory-mcp/actions/workflows/test.yml/badge.svg)](https://github.com/Umarjaum/repo-memory-mcp/actions/workflows/test.yml) [![PyPI](https://img.shields.io/pypi/v/repo-memory-mcp-ai.svg)](https://pypi.org/project/repo-memory-mcp-ai/) [![License](https://img.shields.io/github/license/Umarjaum/repo-memory-mcp.svg)](LICENSE)

## What it does

MCP hosts decide when tools are called; MCP does **not** automatically intercept every conversation. This project exposes explicit tools that let an agent load important context at session startup, search relevant memories, store corrections and decisions, update stale guidance, and archive obsolete memories.

The memory database lives in `.repo-memory/memory.db` inside the detected repository. It uses SQLite, deterministic local ranking, and no cloud service.

## Why developers use it

- **Persistent project memory:** corrections, rules, conventions, constraints, decisions, and bug-fix lessons survive sessions.
- **Repository-aware isolation:** unrelated repositories do not share memory.
- **Local-first privacy:** no API keys, remote database, external embeddings, telemetry, or background upload.
- **Explicit MCP workflow:** the agent chooses when to remember and recall; there is no claim of automatic conversation interception.
- **Fast and inspectable:** SQLite storage, JSON export, CLI diagnostics, and human-readable records.
- **Security-minded:** likely API keys, bearer tokens, passwords, cloud credentials, and private keys are rejected by default.

## Install and use in two minutes

The public PyPI distribution is named `repo-memory-mcp-ai` because the shorter `repo-memory-mcp` name is already owned by another project. The MCP server and GitHub project identity remain `repo-memory-mcp`.

```bash
pip install repo-memory-mcp-ai
repo-memory doctor
```

Start the MCP server directly:

```bash
repo-memory-mcp
```

Or run it without a permanent installation:

```bash
uvx --from repo-memory-mcp-ai repo-memory-mcp
```

The server is local and communicates over stdio. It does not need an API key.

## Configure an MCP client

The common stdio configuration is:

```json
{
  "mcpServers": {
    "repo-memory": {
      "command": "uvx",
      "args": ["--from", "repo-memory-mcp-ai", "repo-memory-mcp"]
    }
  }
}
```

Use the client-specific configuration location and format documented by your MCP host. Ready-to-copy examples are in [`examples/`](examples/):

- [`claude-desktop.json`](examples/claude-desktop.json)
- [`cursor.json`](examples/cursor.json)
- [`workflow.md`](examples/workflow.md)

The project is vendor-neutral and is intended for Claude Code, Cursor, Cline, Windsurf, and other MCP-compatible coding agents. Compatibility depends on the host’s MCP support and configuration format.

## Recommended agent workflow

At the beginning of a coding session, call `get_startup_context()`. When the developer corrects a repeated mistake, call `remember_correction(topic, lesson)`. When a relevant question arises, call `recall_memory(query)`. When guidance becomes stale, call `update_memory()` or archive it with `forget_memory()`.

Example instruction to an agent:

```text
At the start of this session, call get_startup_context. If I correct a repeated mistake or establish a durable project rule, store it with the appropriate repo-memory tool. Do not store credentials or transient chat context.
```

## Available MCP tools

| Tool | Use it for |
|---|---|
| `get_startup_context` | Load concise, high-value repository guidance at session start |
| `remember_correction` | Store a lesson learned from a correction or bug fix |
| `remember_rule` | Store a durable project rule or convention |
| `remember_decision` | Store an architectural decision and rationale |
| `recall_memory` | Search active memory with deterministic local scoring |
| `list_project_rules` | List active project rules |
| `list_memories` | Filter memories by type or status |
| `update_memory` | Correct an existing memory without creating a replacement |
| `forget_memory` | Archive obsolete memory for audit-friendly retention |
| `export_memory` / `import_memory` | Move validated memory between safe copies of the same repository |

## CLI

```bash
repo-memory init
repo-memory list
repo-memory rules
repo-memory search "database migrations"
repo-memory export ./memory-backup.json
repo-memory import ./memory-backup.json
repo-memory doctor
```

## Privacy and security boundaries

Memories stay on the machine running the server. This implementation does not require API keys, cloud accounts, remote databases, external embeddings, or telemetry. It only inspects text explicitly submitted to memory tools. Your operating system, package manager, backups, and MCP host may have separate behavior.

Likely secrets are rejected by default. Do not submit passwords, tokens, private keys, or credentials to memory tools. The `.repo-memory/` directory is ignored by Git so private memory is not accidentally committed.

## Development

```bash
git clone https://github.com/Umarjaum/repo-memory-mcp.git
cd repo-memory-mcp
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
pytest
```

## Discovery and publishing

- Project site: [repo-memory-mcp.pages.dev](https://repo-memory-mcp.pages.dev/)
- Documentation: [quickstart and tools](https://repo-memory-mcp.pages.dev/docs.html)
- Client guides: [Claude, Cursor, VS Code, Cline, and Windsurf](https://repo-memory-mcp.pages.dev/clients.html)
- Extensions: [VS Code and Bing-compatible browser companion](https://repo-memory-mcp.pages.dev/extensions.html)
- Contributions: [open-source contribution guide](https://repo-memory-mcp.pages.dev/contribute.html)
- Source: [GitHub](https://github.com/Umarjaum/repo-memory-mcp)
- Package: [PyPI](https://pypi.org/project/repo-memory-mcp-ai/)
- Registry metadata: [`server.json`](server.json)
- Publishing guide: [`PUBLISHING.md`](PUBLISHING.md)

## Roadmap

Future work may improve ranking, add confidence feedback, provide optional local embeddings, generate project context, add a memory inspection UI, and publish the companion extensions to official marketplaces. Team/shared memory remains explicitly opt-in.

## Companion extensions

- [`extensions/vscode`](extensions/vscode/) provides local setup commands for VS Code.
- [`extensions/bing`](extensions/bing/) provides a privacy-safe Manifest V3 context-menu helper for turning selected Bing research into a repo-memory prompt.

The browser companion intentionally does not invoke the local stdio MCP process. Direct browser-to-MCP integration would require a separately reviewed native-messaging bridge.

## License

MIT. See [`LICENSE`](LICENSE).
