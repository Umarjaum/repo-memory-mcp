from __future__ import annotations
import hashlib, subprocess
from pathlib import Path
from .exceptions import RepositoryDetectionError

class RepositoryInfo:
    def __init__(self, path: Path, repository_id: str):
        self.path, self.repository_id = path, repository_id

def detect_repository(workspace: str | Path | None = None) -> RepositoryInfo:
    start = Path(workspace or Path.cwd()).expanduser().resolve()
    if not start.exists():
        raise RepositoryDetectionError(f"Workspace does not exist: {start}")
    try:
        result = subprocess.run(["git", "-C", str(start), "rev-parse", "--show-toplevel"], capture_output=True, text=True, timeout=3)
        root = Path(result.stdout.strip()).resolve() if result.returncode == 0 and result.stdout.strip() else start
    except (OSError, subprocess.SubprocessError):
        root = start
    stable = hashlib.sha256(str(root).encode("utf-8")).hexdigest()[:24]
    return RepositoryInfo(root, stable)
