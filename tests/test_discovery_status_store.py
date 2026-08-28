from __future__ import annotations

import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from chekov.discovery import classify
from chekov.models import GitObservation, Session, Source, Workspace
from chekov.status import render
from chekov.store import Store


NOW = datetime(2026, 8, 26, 12, tzinfo=timezone.utc)


def session(age_minutes: int, waiting: bool = False) -> Session:
    return Session("codex", "s1", Path("/tmp/work"), NOW - timedelta(hours=1),
                   NOW - timedelta(minutes=age_minutes), waiting, Source("fixture", "session.jsonl"))


def test_state_classification() -> None:
    assert classify(session(1), NOW, timedelta(minutes=2), timedelta(hours=24)) == "active"
    assert classify(session(10), NOW, timedelta(minutes=2), timedelta(hours=24)) == "recent"
    assert classify(session(10, True), NOW, timedelta(minutes=2), timedelta(hours=24)) == "waiting"
    assert classify(session(1500), NOW, timedelta(minutes=2), timedelta(hours=24)) == "idle"


def test_status_is_compact_and_can_show_provenance(tmp_path: Path) -> None:
    workspace = Workspace("w1", "sample", tmp_path, "explicit", "sample", Source("marker", "marker.json"))
    current = session(1)
    current.workspace_id = "w1"
    current.state = "active"
    git = GitObservation("w1", 2, Source("git-status", str(tmp_path)))
    text = render([workspace], [current], [git], now=NOW, show_sources=True)
    assert "1 workspaces · 1 active/recent sessions" in text
    assert "SAMPLE" in text
    assert "uncommitted 2 files" in text
    assert "source: fixture session.jsonl" in text
    assert "workspace: explicit sample" in text


def test_store_persists_normalized_state_and_provenance(tmp_path: Path) -> None:
    database = tmp_path / "chekov.db"
    workspace = Workspace("w1", "sample", tmp_path, "explicit", "sample", Source("marker", "marker.json"))
    current = session(1)
    current.workspace_id = "w1"
    current.state = "active"
    git = GitObservation("w1", 2, Source("git-status", str(tmp_path)))
    store = Store(database)
    store.record("host", "machine", [workspace], [current], [git])
    store.close()
    connection = sqlite3.connect(database)
    assert connection.execute("SELECT state, source_kind FROM sessions").fetchone() == ("active", "fixture")
    assert connection.execute("SELECT COUNT(*) FROM observations").fetchone()[0] == 2


def load_tests(loader, tests, pattern):  # noqa: ARG001
    suite = unittest.TestSuite()
    for name, function in sorted(globals().items()):
        if name.startswith("test_") and callable(function):
            def run(function=function):
                if function.__code__.co_argcount:
                    with tempfile.TemporaryDirectory() as directory:
                        function(Path(directory))
                else:
                    function()
            suite.addTest(unittest.FunctionTestCase(run, description=name))
    return suite
