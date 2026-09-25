from repo_memory_mcp.repository import detect_repository
def test_fallback(tmp_path):
    info=detect_repository(tmp_path); assert info.path==tmp_path.resolve(); assert len(info.repository_id)==24
