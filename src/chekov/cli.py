from __future__ import annotations

import argparse
import sys

from . import __version__
from .config import host_identity, paths
from .discovery import discover
from .status import render
from .store import Store


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(prog="chekov", description="Local situational awareness for agentic work")
    result.add_argument("--sources", action="store_true", help="show provenance for displayed assertions")
    result.add_argument("--active-minutes", type=int, default=2, help="activity window (default: 2)")
    result.add_argument("--recent-hours", type=int, default=24, help="recent-session window (default: 24)")
    result.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.active_minutes < 0 or args.recent_hours < 0:
        print("chekov: time windows must be non-negative", file=sys.stderr)
        return 2
    location = paths()
    host_id, hostname = host_identity(location)
    workspaces, sessions, git_observations = discover(
        active_minutes=args.active_minutes, recent_hours=args.recent_hours
    )
    store = Store(location.database)
    try:
        store.record(host_id, hostname, workspaces, sessions, git_observations)
    finally:
        store.close()
    print(render(workspaces, sessions, git_observations, show_sources=args.sources))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
