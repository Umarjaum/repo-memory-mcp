from __future__ import annotations

import json
import os
import tempfile
import uuid
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import ValidationError

from .exceptions import DuplicateMemoryError, InvalidImportError
from .models import Memory
from .repository import detect_repository
from .search import SearchEngine
from .security import assert_safe
from .storage import Storage


mcp = FastMCP("repo-memory-mcp")
_VALID_STATUSES = {"active", "archived"}
_MAX_CONTEXT_CHARS = 12000


def service(workspace: str | Path | None = None) -> tuple[Any, Storage]:
    info = detect_repository(workspace)
    return info, Storage(info.path / ".repo-memory" / "memory.db")


def _limit(value: int, default: int, maximum: int = 50) -> int:
    try:
        return max(1, min(int(value), maximum))
    except (TypeError, ValueError) as error:
        raise ValueError(f"limit must be an integer between 1 and {maximum}") from error


def _add_memory(
    kind: str,
    topic: str,
    content: str,
    context_file: str = "general",
    tags: list[str] | None = None,
    importance: str = "normal",
    workspace: str | Path | None = None,
) -> dict[str, Any]:
    assert_safe(f"{topic} {content} {context_file} {' '.join(tags or [])}")
    info, store = service(workspace)
    now = Memory.now()
    memory = Memory(
        id=uuid.uuid4().hex,
        repository_id=info.repository_id,
        repository_path=str(info.path),
        memory_type=kind,
        topic=topic,
        content=content,
        context_file=context_file,
        tags=tags or [],
        importance=importance,
        created_at=now,
        updated_at=now,
    )
    store.add(memory)
    return {
        "ok": True,
        "memory_id": memory.id,
        "message": f"Stored {kind} memory for this repository.",
    }


@mcp.tool(description="Store a correction or lesson learned during development. Use for durable guidance that should prevent repeated mistakes; do not store credentials, secrets, or transient chat context.")
def remember_correction(
    topic: str,
    lesson: str,
    context_file: str = "general",
    tags: list[str] | None = None,
    importance: str = "normal",
) -> dict[str, Any]:
    return _add_memory("correction", topic, lesson, context_file, tags, importance)


@mcp.tool(description="Store a durable repository-specific rule or convention. Use when the agent should follow a project constraint in future sessions.")
def remember_rule(
    rule: str,
    context_file: str = "general",
    tags: list[str] | None = None,
    importance: str = "normal",
) -> dict[str, Any]:
    return _add_memory("rule", rule, rule, context_file, tags, importance)


@mcp.tool(description="Store an architectural or implementation decision together with its rationale.")
def remember_decision(
    decision: str,
    rationale: str,
    context_file: str = "general",
    tags: list[str] | None = None,
) -> dict[str, Any]:
    return _add_memory("decision", decision, rationale, context_file, tags, "high")


@mcp.tool(description="Search active repository memories using deterministic local relevance scoring across topic, content, tags, context, and type.")
def recall_memory(query: str, limit: int = 8) -> list[dict[str, Any]]:
    if not query or not query.strip():
        return []
    info, store = service()
    return SearchEngine().rank(store.list(info.repository_id), query, _limit(limit, 8))


@mcp.tool(description="Return a concise startup context prioritizing critical and high-importance rules, conventions, decisions, and recent corrections.")
def get_startup_context(limit: int = 12) -> str:
    info, store = service()
    items = store.list(info.repository_id, limit=_limit(limit, 12))
    groups: dict[str, list[str]] = {
        "IMPORTANT RULES": [],
        "ARCHITECTURE & DECISIONS": [],
        "RECENT CORRECTIONS": [],
        "OTHER MEMORY": [],
    }
    for memory in items:
        key = (
            "IMPORTANT RULES"
            if memory.memory_type in ("rule", "constraint", "convention")
            else "ARCHITECTURE & DECISIONS"
            if memory.memory_type in ("architecture", "decision")
            else "RECENT CORRECTIONS"
            if memory.memory_type in ("correction", "bugfix")
            else "OTHER MEMORY"
        )
        groups[key].append(f"- {memory.content} [{memory.context_file}]")
    output = "Repository Memory\n\n" + "\n\n".join(
        f"{key}:\n" + "\n".join(values)
        for key, values in groups.items()
        if values
    )
    return output[:_MAX_CONTEXT_CHARS]


@mcp.tool(description="List all active durable project rules for the current repository.")
def list_project_rules() -> list[dict[str, Any]]:
    info, store = service()
    return [memory.model_dump(mode="json") for memory in store.list(info.repository_id, memory_type="rule")]


@mcp.tool(description="List repository memories with optional type and status filters.")
def list_memories(
    memory_type: str | None = None,
    status: str = "active",
    limit: int = 50,
) -> list[dict[str, Any]]:
    if status not in _VALID_STATUSES:
        raise ValueError("status must be 'active' or 'archived'")
    info, store = service()
    return [
        memory.model_dump(mode="json")
        for memory in store.list(info.repository_id, memory_type, status, _limit(limit, 50))
    ]


@mcp.tool(description="Update an existing memory by ID. This changes the existing record and timestamp; it never silently creates a replacement.")
def update_memory(
    memory_id: str,
    topic: str | None = None,
    content: str | None = None,
    context_file: str | None = None,
    tags: list[str] | None = None,
    importance: str | None = None,
    status: str | None = None,
) -> dict[str, Any]:
    if not memory_id or not memory_id.strip():
        raise ValueError("memory_id is required")
    if status is not None and status not in _VALID_STATUSES:
        raise ValueError("status must be 'active' or 'archived'")
    assert_safe(" ".join(value for value in (topic, content, context_file) if value))
    info, store = service()
    return store.update(
        memory_id,
        info.repository_id,
        {
            "topic": topic,
            "content": content,
            "context_file": context_file,
            "tags": tags,
            "importance": importance,
            "status": status,
        },
    ).model_dump(mode="json")


@mcp.tool(description="Archive a memory so it is retained for auditability but excluded from normal recall and startup context.")
def forget_memory(memory_id: str) -> dict[str, Any]:
    info, store = service()
    return store.update(memory_id, info.repository_id, {"status": "archived"}).model_dump(mode="json")


@mcp.tool(description="Export all active and archived memories as portable JSON to a user-specified path.")
def export_memory(output_path: str) -> dict[str, Any]:
    info, store = service()
    destination = Path(output_path).expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    data = [memory.model_dump(mode="json") for memory in store.list(info.repository_id, status=None, limit=None)]
    fd, temporary_name = tempfile.mkstemp(prefix="repo-memory-", suffix=".json", dir=destination.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        os.replace(temporary_name, destination)
    except OSError:
        try:
            os.unlink(temporary_name)
        except OSError:
            pass
        raise
    return {"ok": True, "count": len(data), "output_path": str(destination)}


@mcp.tool(description="Import a JSON export without overwriting existing memories; malformed records are rejected and duplicates are reported.")
def import_memory(input_path: str) -> dict[str, Any]:
    info, store = service()
    source = Path(input_path).expanduser().resolve()
    try:
        raw = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise InvalidImportError(f"Could not read a valid JSON import file: {source}") from error
    if not isinstance(raw, list):
        raise InvalidImportError("Import file must contain a JSON array of memory records.")

    imported = 0
    duplicates: list[str] = []
    for index, item in enumerate(raw):
        try:
            memory = Memory.model_validate(item)
        except (ValidationError, TypeError) as error:
            raise InvalidImportError(f"Invalid memory record at index {index}.") from error
        if memory.repository_id != info.repository_id:
            raise InvalidImportError("Import belongs to a different repository.")
        assert_safe(f"{memory.topic} {memory.content} {memory.context_file} {' '.join(memory.tags)}")
        try:
            store.add(memory)
            imported += 1
        except DuplicateMemoryError:
            duplicates.append(memory.id)
    return {"ok": True, "imported": imported, "duplicates": duplicates}


def main() -> None:
    mcp.run()
