from repo_memory_mcp.storage import Storage
from repo_memory_mcp.models import Memory
def test_storage_roundtrip(tmp_path):
    s=Storage(tmp_path/'m.db'); now=Memory.now(); m=Memory(id='1',repository_id='r',repository_path=str(tmp_path),memory_type='rule',topic='x',content='y',created_at=now,updated_at=now); s.add(m); assert s.get('1','r').content=='y'; assert len(s.list('r'))==1
