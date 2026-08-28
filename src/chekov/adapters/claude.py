from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from ..models import Session, Source
from .common import existing_directory, json_lines, parse_time


class ClaudeAdapter:
    runtime = "claude"

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / ".claude" / "projects"

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
                workspace = existing_directory(item.get("cwd")) or workspace
                session_id = str(item.get("sessionId") or item.get("session_id") or session_id)
                kind = item.get("type")
                message = item.get("message") if isinstance(item.get("message"), dict) else {}
                content = message.get("content")
                has_tool_use = isinstance(content, list) and any(
                    isinstance(block, dict) and block.get("type") == "tool_use" for block in content
                )
                if kind in {"assistant", "result"}:
                    waiting = not has_tool_use
                elif kind in {"user", "tool_result", "progress"}:
                    waiting = False
            if workspace is None:
                continue
            sessions.append(Session(self.runtime, session_id, workspace, started, last, waiting,
                                    Source("claude-session-store", str(path))))
        return sessions

