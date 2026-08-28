from __future__ import annotations

from datetime import datetime, timezone

from .models import GitObservation, Session, Workspace


def _age(value: datetime, now: datetime) -> str:
    minutes = max(0, int((now - value.astimezone(timezone.utc)).total_seconds() // 60))
    if minutes < 1:
        return "now"
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    return f"{hours}h" if hours < 48 else f"{hours // 24}d"


def render(workspaces: list[Workspace], sessions: list[Session], git_observations: list[GitObservation],
           *, now: datetime | None = None, show_sources: bool = False) -> str:
    now = now or datetime.now(timezone.utc)
    visible = [session for session in sessions if session.state != "idle"]
    visible_workspace_ids = {session.workspace_id for session in visible}
    visible_workspace_count = sum(workspace.id in visible_workspace_ids for workspace in workspaces)
    lines = [f"{visible_workspace_count} workspaces · {len(visible)} active/recent sessions"]
    git_by_workspace = {item.workspace_id: item for item in git_observations}
    for workspace in workspaces:
        relevant = sorted((s for s in visible if s.workspace_id == workspace.id), key=lambda s: s.last_activity_at, reverse=True)
        if not relevant:
            continue
        lines.extend(["", workspace.name.upper()])
        for session in relevant:
            state = session.state if session.state in {"active", "waiting"} else _age(session.last_activity_at, now)
            lines.append(f"  {session.runtime:<10} {state:<10} {_age(session.last_activity_at, now)} ago")
            if show_sources:
                lines.append(f"    source: {session.source.kind} {session.source.reference}")
        git = git_by_workspace.get(workspace.id)
        if git and git.changed_files:
            lines.append(f"  uncommitted {git.changed_files} file{'s' if git.changed_files != 1 else ''}")
            if show_sources:
                lines.append(f"    source: {git.source.kind} {git.source.reference}")
        if show_sources:
            lines.append(f"    workspace: {workspace.identity_kind} {workspace.identity_value}")
    if not visible:
        lines.extend(["", "No active or recent Claude Code or Codex sessions found."])
    return "\n".join(lines)
