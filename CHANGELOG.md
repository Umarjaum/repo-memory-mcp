# Changelog

## 0.2.0

Robustness release.

- Strict import validation with duplicate reporting instead of silent failures.
- Atomic JSON exports with no arbitrary 500-record truncation.
- Correct update timestamps and duplicate-safe updates.
- SQLite busy timeout, synchronous mode, indexes, counts, and integrity checks.
- Bounded MCP inputs and concise startup context output.
- Broader detection for bearer tokens, GitHub tokens, OpenAI-style keys, AWS keys, and private keys.
- Expanded regression tests for storage, imports, exports, security, and service behavior.

## 0.1.0

Initial release with repository-scoped SQLite memory, FastMCP tools, deterministic local search, startup context, CLI operations, import/export, and conservative secret detection.
