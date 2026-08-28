from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from ..models import Session, Source
from .common import existing_directory, json_lines, parse_time


class CodexAdapter:
    runtime = "codex"

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / ".codex" / "sessions"

    def discover(self) -> list[Session]:
        sessions: list[Session] = []
        if not self.root.is_dir():
            return sessions
        for path in self.root.glob("**/*.jsonl"):
            stat_time = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
            started = None
            last = stat_time
            workspace = None
            session_id = path.stem
            waiting = False
            for item in json_lines(path):
                timestamp = parse_time(item.get("timestamp"), stat_time)
                started = timestamp if started is None or timestamp < started else started
                last = max(last, timestamp)
                payload = item.get("payload") if isinstance(item.get("payload"), dict) else {}
                workspace = existing_directory(payload.get("cwd")) or existing_directory(item.get("cwd")) or workspace
                session_id = str(payload.get("id") or item.get("session_id") or session_id)
                event_type = str(payload.get("type") or item.get("type") or "")
                if event_type in {"task_complete", "agent_message", "turn.completed"}:
                    waiting = True
                elif event_type in {"task_started", "user_message", "turn.started", "function_call"}:
                    waiting = False
            if workspace is None:
                continue
            sessions.append(Session(self.runtime, session_id, workspace, started, last, waiting,
                                    Source("codex-session-store", str(path))))
        return sessions

