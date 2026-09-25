from repo_memory_mcp.models import Memory
def test_tags_normalize():
    m=Memory(id='1',repository_id='r',repository_path='/',memory_type='rule',topic='x',content='y',tags=[' Python ','python'],created_at=Memory.now(),updated_at=Memory.now()); assert m.tags==['python']
