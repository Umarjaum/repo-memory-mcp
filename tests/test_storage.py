from __future__ import annotations

import time

import pytest

from repo_memory_mcp.exceptions import DuplicateMemoryError, MemoryNotFoundError
from repo_memory_mcp.models import Memory
from repo_memory_mcp.storage import Storage


def make_memory(tmp_path, memory_id="1", topic="x", content="y", importance="normal"):
    now = Memory.now()
    return Memory(
        id=memory_id,
        repository_id="r",
        repository_path=str(tmp_path),
        memory_type="rule",
        topic=topic,
        content=content,
        importance=importance,
        created_at=now,
        updated_at=now,
    )


def test_storage_roundtrip_and_integrity(tmp_path):
    storage = Storage(tmp_path / "m.db")
    memory = make_memory(tmp_path)
    storage.add(memory)
    assert storage.get("1", "r").content == "y"
    assert len(storage.list("r")) == 1
    assert storage.count("r") == 1
    assert storage.integrity_check() == "ok"


def test_duplicate_memory_is_explicit(tmp_path):
    storage = Storage(tmp_path / "m.db")
    storage.add(make_memory(tmp_path, memory_id="1"))
    with pytest.raises(DuplicateMemoryError):
        storage.add(make_memory(tmp_path, memory_id="2"))


def test_update_refreshes_timestamp_and_preserves_fields(tmp_path):
    storage = Storage(tmp_path / "m.db")
    original = make_memory(tmp_path)
    storage.add(original)
    time.sleep(0.001)
    updated = storage.update("1", "r", {"content": "new lesson", "tags": ["Python"]})
    assert updated.content == "new lesson"
    assert updated.context_file == "general"
    assert updated.tags == ["python"]
    assert updated.updated_at >= original.updated_at


def test_archived_memories_filter_from_active_list(tmp_path):
    storage = Storage(tmp_path / "m.db")
    storage.add(make_memory(tmp_path))
    archived = storage.update("1", "r", {"status": "archived"})
    assert archived.status == "archived"
    assert storage.list("r", status="active") == []
    assert len(storage.list("r", status="archived")) == 1
    assert storage.count("r", status="archived") == 1


def test_missing_memory_is_clear(tmp_path):
    storage = Storage(tmp_path / "m.db")
    with pytest.raises(MemoryNotFoundError):
        storage.get("missing", "r")


def test_unbounded_list_does_not_truncate(tmp_path):
    storage = Storage(tmp_path / "m.db")
    for index in range(6):
        storage.add(make_memory(tmp_path, str(index), f"topic-{index}", f"content-{index}"))
    assert len(storage.list("r", limit=None)) == 6
