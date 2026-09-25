from __future__ import annotations
import json, sqlite3
from pathlib import Path
from .models import Memory
from .exceptions import DuplicateMemoryError, MemoryNotFoundError

class Storage:
    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()
    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA journal_mode=WAL")
        return conn
    def _init_schema(self):
        with self.connect() as c:
            c.executescript("""CREATE TABLE IF NOT EXISTS memories (id TEXT PRIMARY KEY, repository_id TEXT NOT NULL, repository_path TEXT NOT NULL, memory_type TEXT NOT NULL, topic TEXT NOT NULL, content TEXT NOT NULL, context_file TEXT NOT NULL, tags TEXT NOT NULL, importance TEXT NOT NULL, status TEXT NOT NULL, source TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, UNIQUE(repository_id, topic, content)); CREATE INDEX IF NOT EXISTS idx_mem_repo_status ON memories(repository_id,status); CREATE INDEX IF NOT EXISTS idx_mem_type ON memories(memory_type);""")
    def add(self, memory: Memory) -> Memory:
        try:
            with self.connect() as c:
                c.execute("INSERT INTO memories VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", (memory.id,memory.repository_id,memory.repository_path,memory.memory_type,memory.topic,memory.content,memory.context_file,json.dumps(memory.tags),memory.importance,memory.status,memory.source,memory.created_at.isoformat(),memory.updated_at.isoformat()))
        except sqlite3.IntegrityError as e:
            raise DuplicateMemoryError("An identical memory already exists in this repository.") from e
        return memory
    def _row(self, row):
        if not row: raise MemoryNotFoundError("Memory was not found in this repository.")
        d = dict(row); d["tags"] = json.loads(d["tags"]); return Memory.model_validate(d)
    def get(self, memory_id, repository_id):
        with self.connect() as c: return self._row(c.execute("SELECT * FROM memories WHERE id=? AND repository_id=?", (memory_id,repository_id)).fetchone())
    def list(self, repository_id, memory_type=None, status="active", limit=50):
        q="SELECT * FROM memories WHERE repository_id=?"; args=[repository_id]
        if memory_type: q += " AND memory_type=?"; args.append(memory_type)
        if status: q += " AND status=?"; args.append(status)
        q += " ORDER BY CASE importance WHEN 'critical' THEN 4 WHEN 'high' THEN 3 WHEN 'normal' THEN 2 ELSE 1 END DESC, updated_at DESC LIMIT ?"; args.append(max(1,min(limit,500)))
        with self.connect() as c: return [self._row(r) for r in c.execute(q,args).fetchall()]
    def update(self, memory_id, repository_id, fields):
        current=self.get(memory_id, repository_id); data=current.model_dump(); data.update({k:v for k,v in fields.items() if v is not None}); updated=Memory.model_validate(data)
        with self.connect() as c: c.execute("UPDATE memories SET topic=?,content=?,context_file=?,tags=?,importance=?,status=?,updated_at=? WHERE id=? AND repository_id=?", (updated.topic,updated.content,updated.context_file,json.dumps(updated.tags),updated.importance,updated.status,updated.updated_at.isoformat(),memory_id,repository_id))
        return updated
