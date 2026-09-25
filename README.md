# repo-memory-mcp

mcp-name: io.github.Umarjaum/repo-memory-mcp

## Persistent memory for AI coding agents

AI coding agents are powerful, but they forget repository-specific corrections, conventions, and architectural decisions. **repo-memory-mcp** gives an MCP-compatible coding agent a persistent, local, repository-aware memory layer.

> Teach your coding agent once. Let your repository remember.

### Why it exists

MCP hosts decide when tools are called; MCP does not automatically intercept every conversation. This project therefore exposes explicit tools for startup context, searching, storing corrections and decisions, updating stale guidance, and archiving obsolete memories.

### Features

- Repository-scoped SQLite storage in `.repo-memory/`
- FastMCP tools for corrections, rules, decisions, search, and startup context
- Deterministic local relevance scoring; no pretend semantic search
- Local-first, API-key-free, cloud-free, telemetry-free operation
- Conservative secret detection for explicitly submitted content
- Import/export and audit-friendly archiving
- Python 3.10+, Pydantic v2, pytest, standard-library-first design

### Install

For local development:

```bash
pip install -e .[dev]
repo-memory doctor
```

After publishing the package to PyPI:

```bash
pip install repo-memory-mcp
uvx repo-memory-mcp
```

The published-package commands should only be used once the package is publicly available.

### Configure an MCP client

The examples in [`examples/`](examples/) use the common stdio configuration shape. Clients can differ; follow the client’s documented MCP configuration format.

### Tool workflow

1. New session: call `get_startup_context()`.
2. Developer correction: call `remember_correction(topic, lesson)`.
3. Relevant work: call `recall_memory(query)`.
4. Obsolete guidance: call `forget_memory(memory_id)`.

Your memories stay on your machine. The implementation does not require API keys, cloud accounts, remote databases, external embeddings, or telemetry. The claims apply to this codebase as shipped; your operating system, package manager, backups, or MCP host may have separate behavior.

### Development

```bash
pytest
repo-memory init
repo-memory list
repo-memory search "pydantic models"
```

### Roadmap

Future work may improve ranking, add confidence feedback, provide optional local embeddings, generate project context, and add a memory inspection UI. Team/shared memory remains explicitly opt-in.

### License

MIT. See [`LICENSE`](LICENSE).
