from __future__ import annotations

import subprocess

from .models import GitObservation, Source, Workspace


def observe_git(workspace: Workspace) -> GitObservation | None:
    result = subprocess.run(
        ["git", "-C", str(workspace.path), "status", "--porcelain=v1", "-z"],
        capture_output=True, timeout=5, check=False,
    )
    if result.returncode != 0:
        return None
    entries = [entry for entry in result.stdout.split(b"\0") if entry]
    count = 0
    index = 0
    while index < len(entries):
        status = entries[index][:2]
        count += 1
        index += 2 if b"R" in status or b"C" in status else 1
    return GitObservation(workspace.id, count, Source("git-status", str(workspace.path)))
