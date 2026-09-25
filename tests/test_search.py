from repo_memory_mcp.search import SearchEngine
from repo_memory_mcp.models import Memory
def test_search():
    now=Memory.now(); m=Memory(id='1',repository_id='r',repository_path='/',memory_type='rule',topic='Pydantic',content='Use v2',tags=['python'],created_at=now,updated_at=now); assert SearchEngine().rank([m],'Pydantic')[0]['memory_id']=='1'
