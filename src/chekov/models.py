from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class Source:
    kind: str
    reference: str


@dataclass
class Session:
    runtime: str
    source_session_id: str
    workspace_path: Path | None
    started_at: datetime | None
    last_activity_at: datetime
    waiting: bool
    source: Source
    state: str = "recent"
    workspace_id: str | None = None
    evidence: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Workspace:
    id: str
    name: str
    path: Path
    identity_kind: str
    identity_value: str
    source: Source


@dataclass(frozen=True)
class GitObservation:
    workspace_id: str
    changed_files: int
    source: Source

