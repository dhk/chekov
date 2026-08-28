from __future__ import annotations

from datetime import datetime, timedelta, timezone

from .adapters import ClaudeAdapter, CodexAdapter
from .identity import workspace_for
from .models import GitObservation, Session, Workspace
from .git import observe_git


def classify(session: Session, now: datetime, active: timedelta, recent: timedelta) -> str:
    age = now - session.last_activity_at.astimezone(timezone.utc)
    if session.waiting and age <= recent:
        return "waiting"
    if age <= active:
        return "active"
    if age <= recent:
        return "recent"
    return "idle"


def discover(adapters: list | None = None, *, now: datetime | None = None,
             active_minutes: int = 2, recent_hours: int = 24) -> tuple[list[Workspace], list[Session], list[GitObservation]]:
    now = now or datetime.now(timezone.utc)
    sessions = [session for adapter in (adapters or [ClaudeAdapter(), CodexAdapter()]) for session in adapter.discover()]
    workspaces: dict[str, Workspace] = {}
    for session in sessions:
        workspace = workspace_for(session.workspace_path)  # type: ignore[arg-type]
        session.workspace_id = workspace.id
        session.state = classify(session, now, timedelta(minutes=active_minutes), timedelta(hours=recent_hours))
        workspaces[workspace.id] = workspace
    git_observations = [item for workspace in workspaces.values() if (item := observe_git(workspace)) is not None]
    return sorted(workspaces.values(), key=lambda item: item.name.lower()), sessions, git_observations
