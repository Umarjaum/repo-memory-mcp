from __future__ import annotations
import json, uuid
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from .models import Memory
from .repository import detect_repository
from .security import assert_safe
from .storage import Storage
from .search import SearchEngine

mcp = FastMCP("repo-memory-mcp")
def service(workspace=None):
    info=detect_repository(workspace); return info, Storage(info.path/".repo-memory"/"memory.db")
def add(kind, topic, content, context_file="general", tags=None, importance="normal", workspace=None):
    assert_safe(f"{topic} {content} {context_file} {' '.join(tags or [])}"); info,store=service(workspace); now=Memory.now(); mem=Memory(id=uuid.uuid4().hex,repository_id=info.repository_id,repository_path=str(info.path),memory_type=kind,topic=topic,content=content,context_file=context_file,tags=tags or [],importance=importance,created_at=now,updated_at=now); store.add(mem); return {"ok":True,"memory_id":mem.id,"message":f"Stored {kind} memory for this repository."}

@mcp.tool(description="Store a correction or lesson learned during development. Use for durable guidance that should prevent repeated mistakes; do not store credentials, secrets, or transient chat context.")
def remember_correction(topic: str, lesson: str, context_file: str="general", tags: list[str]|None=None, importance: str="normal"):
    return add("correction",topic,lesson,context_file,tags,importance)
@mcp.tool(description="Store a durable repository-specific rule or convention. Use when the agent should follow a project constraint in future sessions.")
def remember_rule(rule: str, context_file: str="general", tags: list[str]|None=None, importance: str="normal"):
    return add("rule",rule,rule,context_file,tags,importance)
@mcp.tool(description="Store an architectural or implementation decision together with its rationale.")
def remember_decision(decision: str, rationale: str, context_file: str="general", tags: list[str]|None=None):
    return add("decision",decision,rationale,context_file,tags,"high")
@mcp.tool(description="Search active repository memories using deterministic local relevance scoring across topic, content, tags, context, and type.")
def recall_memory(query: str, limit: int=8):
    info,store=service(); return SearchEngine().rank(store.list(info.repository_id),query,max(1,min(limit,50)))
@mcp.tool(description="Return a concise startup context prioritizing critical and high-importance rules, conventions, decisions, and recent corrections.")
def get_startup_context(limit: int=12):
    info,store=service(); items=store.list(info.repository_id,limit=max(1,min(limit,50))); groups={"IMPORTANT RULES":[],"ARCHITECTURE & DECISIONS":[],"RECENT CORRECTIONS":[],"OTHER MEMORY":[]}
    for m in items:
        key="IMPORTANT RULES" if m.memory_type in ("rule","constraint","convention") else "ARCHITECTURE & DECISIONS" if m.memory_type in ("architecture","decision") else "RECENT CORRECTIONS" if m.memory_type in ("correction","bugfix") else "OTHER MEMORY"; groups[key].append(f"- {m.content} [{m.context_file}]")
    return "Repository Memory\n\n"+"\n\n".join(f"{k}:\n"+"\n".join(v) for k,v in groups.items() if v)
@mcp.tool(description="List all active durable project rules for the current repository.")
def list_project_rules():
    info,store=service(); return [m.model_dump(mode="json") for m in store.list(info.repository_id,memory_type="rule")]
@mcp.tool(description="List repository memories with optional type and status filters.")
def list_memories(memory_type: str|None=None, status: str="active", limit: int=50):
    info,store=service(); return [m.model_dump(mode="json") for m in store.list(info.repository_id,memory_type,status,limit)]
@mcp.tool(description="Update an existing memory by ID. This changes the existing record and timestamp; it never silently creates a replacement.")
def update_memory(memory_id: str, topic: str|None=None, content: str|None=None, context_file: str|None=None, tags: list[str]|None=None, importance: str|None=None, status: str|None=None):
    assert_safe(" ".join(x for x in [topic,content,context_file] if x)); info,store=service(); return store.update(memory_id,info.repository_id,{"topic":topic,"content":content,"context_file":context_file,"tags":tags,"importance":importance,"status":status}).model_dump(mode="json")
@mcp.tool(description="Archive a memory so it is retained for auditability but excluded from normal recall and startup context.")
def forget_memory(memory_id: str):
    info,store=service(); return store.update(memory_id,info.repository_id,{"status":"archived"}).model_dump(mode="json")
@mcp.tool(description="Export active and archived memories as portable JSON to a user-specified path.")
def export_memory(output_path: str):
    info,store=service(); data=[m.model_dump(mode="json") for m in store.list(info.repository_id,status=None,limit=500)]; Path(output_path).expanduser().write_text(json.dumps(data,indent=2),encoding="utf-8"); return {"ok":True,"count":len(data),"output_path":str(Path(output_path).expanduser())}
@mcp.tool(description="Import a JSON export without overwriting existing memories; malformed records are rejected.")
def import_memory(input_path: str):
    info,store=service(); raw=json.loads(Path(input_path).expanduser().read_text(encoding="utf-8")); count=0
    for item in raw:
        mem=Memory.model_validate(item)
        if mem.repository_id != info.repository_id: raise ValueError("Import belongs to a different repository.")
        try: store.add(mem); count += 1
        except Exception: pass
    return {"ok":True,"imported":count}
def main():
    mcp.run()
