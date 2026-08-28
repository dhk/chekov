from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from urllib.parse import urlsplit

from .models import Source, Workspace


def _git(path: Path, *args: str) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(path), *args], capture_output=True, text=True, timeout=3, check=False
    )
    return result.stdout.strip() if result.returncode == 0 else None


def normalize_remote(value: str) -> str:
    value = value.strip().removesuffix(".git").removesuffix("/")
    if value.startswith("git@") and ":" in value:
        host, repo = value[4:].split(":", 1)
        return f"{host.lower()}/{repo.lower()}"
    parts = urlsplit(value)
    if parts.hostname:
        return f"{parts.hostname.lower()}/{parts.path.strip('/').lower()}"
    return value.lower()


def workspace_for(path: Path) -> Workspace:
    path = path.expanduser().resolve()
    root_text = _git(path, "rev-parse", "--show-toplevel")
    root = Path(root_text).resolve() if root_text else path
    marker = root / ".chekov" / "workspace.json"
    identity_kind = "directory"
    identity_value = str(root)
    source = Source("filesystem", str(root))
    if marker.is_file():
        try:
            explicit = json.loads(marker.read_text()).get("id")
            if explicit:
                identity_kind, identity_value = "explicit", str(explicit)
                source = Source("chekov-workspace-marker", str(marker))
        except (OSError, ValueError, TypeError):
            pass
    if identity_kind == "directory" and root_text:
        remote = _git(root, "remote", "get-url", "origin")
        if remote:
            identity_kind, identity_value = "git-remote", normalize_remote(remote)
            source = Source("git-config", f"{root}/.git/config")
        else:
            common = _git(root, "rev-parse", "--git-common-dir") or str(root / ".git")
            identity_kind, identity_value = "git-common-dir", str((root / common).resolve())
            source = Source("git", str(root))
    digest = hashlib.sha256(f"{identity_kind}\0{identity_value}".encode()).hexdigest()[:20]
    return Workspace(digest, root.name, root, identity_kind, identity_value, source)

