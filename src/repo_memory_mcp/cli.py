import argparse, json
from .server import service
from .repository import detect_repository

def main():
    p=argparse.ArgumentParser(prog="repo-memory"); sub=p.add_subparsers(dest="cmd",required=True)
    sub.add_parser("init"); sub.add_parser("list"); sub.add_parser("rules"); sub.add_parser("doctor")
    s=sub.add_parser("search"); s.add_argument("query")
    e=sub.add_parser("export"); e.add_argument("output_path")
    i=sub.add_parser("import"); i.add_argument("input_path")
    a=p.parse_args(); info,store=service()
    if a.cmd=="init": print(f"Initialized {info.path/'.repo-memory/memory.db'}")
    elif a.cmd in ("list","rules"): print(json.dumps([m.model_dump(mode="json") for m in store.list(info.repository_id,memory_type="rule" if a.cmd=="rules" else None)],indent=2))
    elif a.cmd=="search":
        from .search import SearchEngine; print(json.dumps(SearchEngine().rank(store.list(info.repository_id),a.query),indent=2))
    elif a.cmd=="export":
        from .server import export_memory; print(export_memory(a.output_path))
    elif a.cmd=="import":
        from .server import import_memory; print(import_memory(a.input_path))
    elif a.cmd=="doctor": print(json.dumps({"python":__import__('sys').version.split()[0],"repository":str(info.path),"repository_id":info.repository_id,"storage":str(store.db_path),"status":"ok"},indent=2))
