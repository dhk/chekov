from __future__ import annotations

import json
import os
import socket
import uuid
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Paths:
    data_dir: Path
    config_file: Path
    database: Path


def paths() -> Paths:
    root = Path(os.environ.get("CHEKOV_HOME", Path.home() / ".local" / "share" / "chekov"))
    return Paths(root, root / "config.json", root / "chekov.db")


def host_identity(location: Paths | None = None) -> tuple[str, str]:
    location = location or paths()
    location.data_dir.mkdir(parents=True, exist_ok=True)
    if location.config_file.exists():
        try:
            data = json.loads(location.config_file.read_text())
            if data.get("host_id"):
                return str(data["host_id"]), str(data.get("hostname") or socket.gethostname())
        except (OSError, ValueError, TypeError):
            pass
    data = {"host_id": str(uuid.uuid4()), "hostname": socket.gethostname()}
    location.config_file.write_text(json.dumps(data, indent=2) + "\n")
    return data["host_id"], data["hostname"]

