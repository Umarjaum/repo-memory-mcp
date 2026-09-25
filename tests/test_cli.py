def test_cli_importable():
    from repo_memory_mcp.cli import main
    assert callable(main)
