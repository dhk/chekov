from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .models import GitObservation, Session, Workspace


SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS hosts (
  id TEXT PRIMARY KEY, hostname TEXT NOT NULL, last_seen TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS workspaces (
  id TEXT PRIMARY KEY, name TEXT NOT NULL, path TEXT NOT NULL,
  identity_kind TEXT NOT NULL, identity_value TEXT NOT NULL,
  source_kind TEXT NOT NULL, source_reference TEXT NOT NULL, last_seen TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sessions (
  runtime TEXT NOT NULL, source_session_id TEXT NOT NULL, host_id TEXT NOT NULL,
  workspace_id TEXT NOT NULL, started_at TEXT, last_activity_at TEXT NOT NULL,
  state TEXT NOT NULL, source_kind TEXT NOT NULL, source_reference TEXT NOT NULL,
  PRIMARY KEY(runtime, source_session_id, host_id),
  FOREIGN KEY(host_id) REFERENCES hosts(id), FOREIGN KEY(workspace_id) REFERENCES workspaces(id)
);
CREATE TABLE IF NOT EXISTS observations (
  id INTEGER PRIMARY KEY AUTOINCREMENT, observed_at TEXT NOT NULL, type TEXT NOT NULL,
  host_id TEXT NOT NULL, workspace_id TEXT, session_id TEXT, value TEXT NOT NULL,
  source_kind TEXT NOT NULL, source_reference TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS observations_workspace ON observations(workspace_id, observed_at);
"""


class Store:
    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(path)
        self.connection.row_factory = sqlite3.Row
        self.connection.executescript(SCHEMA)

    def close(self) -> None:
        self.connection.close()

    def record(self, host_id: str, hostname: str, workspaces: list[Workspace], sessions: list[Session],
               git_observations: list[GitObservation]) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self.connection:
            self.connection.execute(
                "INSERT INTO hosts VALUES (?, ?, ?) ON CONFLICT(id) DO UPDATE SET hostname=excluded.hostname,last_seen=excluded.last_seen",
                (host_id, hostname, now),
            )
            for workspace in workspaces:
                self.connection.execute(
                    "INSERT INTO workspaces VALUES (?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET name=excluded.name,path=excluded.path,last_seen=excluded.last_seen",
                    (workspace.id, workspace.name, str(workspace.path), workspace.identity_kind,
                     workspace.identity_value, workspace.source.kind, workspace.source.reference, now),
                )
            for session in sessions:
                self.connection.execute(
                    "INSERT INTO sessions VALUES (?,?,?,?,?,?,?,?,?) ON CONFLICT(runtime,source_session_id,host_id) DO UPDATE SET workspace_id=excluded.workspace_id,last_activity_at=excluded.last_activity_at,state=excluded.state,source_kind=excluded.source_kind,source_reference=excluded.source_reference",
                    (session.runtime, session.source_session_id, host_id, session.workspace_id,
                     session.started_at.isoformat() if session.started_at else None,
                     session.last_activity_at.isoformat(), session.state, session.source.kind, session.source.reference),
                )
                self.connection.execute(
                    "INSERT INTO observations(observed_at,type,host_id,workspace_id,session_id,value,source_kind,source_reference) VALUES(?,?,?,?,?,?,?,?)",
                    (now, "session.state", host_id, session.workspace_id, session.source_session_id,
                     session.state, session.source.kind, session.source.reference),
                )
            for observation in git_observations:
                self.connection.execute(
                    "INSERT INTO observations(observed_at,type,host_id,workspace_id,value,source_kind,source_reference) VALUES(?,?,?,?,?,?,?)",
                    (now, "git.changed_files", host_id, observation.workspace_id,
                     str(observation.changed_files), observation.source.kind, observation.source.reference),
                )
