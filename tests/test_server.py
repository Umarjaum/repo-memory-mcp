from __future__ import annotations

import json

import pytest

from repo_memory_mcp import server
from repo_memory_mcp.exceptions import InvalidImportError
from repo_memory_mcp.models import Memory
from repo_memory_mcp.repository import RepositoryInfo
from repo_memory_mcp.storage import Storage


def test_export_and_duplicate_aware_import(tmp_path, monkeypatch):
    info = RepositoryInfo(tmp_path, "repo-id")
    storage = Storage(tmp_path / "memory.db")
    now = Memory.now()
    storage.add(
        Memory(
            id="one",
            repository_id="repo-id",
            repository_path=str(tmp_path),
            memory_type="rule",
            topic="style",
            content="Use typed models",
            created_at=now,
            updated_at=now,
        )
    )
    monkeypatch.setattr(server, "service", lambda workspace=None: (info, storage))
    output = tmp_path / "exports" / "memory.json"
    result = server.export_memory(str(output))
    assert result["count"] == 1
    assert json.loads(output.read_text())[0]["id"] == "one"
    imported = server.import_memory(str(output))
    assert imported["imported"] == 0
    assert imported["duplicates"] == ["one"]


def test_import_rejects_malformed_records(tmp_path, monkeypatch):
    info = RepositoryInfo(tmp_path, "repo-id")
    storage = Storage(tmp_path / "memory.db")
    monkeypatch.setattr(server, "service", lambda workspace=None: (info, storage))
    source = tmp_path / "bad.json"
    source.write_text(json.dumps([{"id": "bad", "content": "missing fields"}]))
    with pytest.raises(InvalidImportError, match="index 0"):
        server.import_memory(str(source))


def test_empty_search_is_safe(tmp_path, monkeypatch):
    info = RepositoryInfo(tmp_path, "repo-id")
    storage = Storage(tmp_path / "memory.db")
    monkeypatch.setattr(server, "service", lambda workspace=None: (info, storage))
    assert server.recall_memory("   ") == []
