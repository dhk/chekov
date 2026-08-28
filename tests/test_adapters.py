from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from chekov.adapters.claude import ClaudeAdapter
from chekov.adapters.codex import CodexAdapter


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True)
    path.write_text("".join(json.dumps(record) + "\n" for record in records))


def test_claude_discovers_metadata_without_storing_content(tmp_path: Path) -> None:
    workspace = tmp_path / "work"
    workspace.mkdir()
    session = tmp_path / "claude" / "project" / "session.jsonl"
    write_jsonl(session, [
        {"type": "user", "sessionId": "abc", "cwd": str(workspace), "timestamp": "2026-08-26T10:00:00Z", "message": {"content": "secret prompt"}},
        {"type": "assistant", "sessionId": "abc", "cwd": str(workspace), "timestamp": "2026-08-26T10:01:00Z", "message": {"content": [{"type": "text", "text": "secret answer"}]}},
    ])

    found = ClaudeAdapter(tmp_path / "claude").discover()

    assert len(found) == 1
    assert found[0].source_session_id == "abc"
    assert found[0].workspace_path == workspace.resolve()
    assert found[0].waiting is True
    assert "secret" not in repr(found[0])


def test_codex_discovers_rollout_session(tmp_path: Path) -> None:
    workspace = tmp_path / "work"
    workspace.mkdir()
    session = tmp_path / "codex" / "2026" / "rollout.jsonl"
    write_jsonl(session, [
        {"timestamp": "2026-08-26T10:00:00Z", "type": "session_meta", "payload": {"id": "xyz", "cwd": str(workspace)}},
        {"timestamp": "2026-08-26T10:03:00Z", "type": "event_msg", "payload": {"type": "task_complete"}},
    ])

    found = CodexAdapter(tmp_path / "codex").discover()

    assert len(found) == 1
    assert found[0].source_session_id == "xyz"
    assert found[0].workspace_path == workspace.resolve()
    assert found[0].waiting is True


def test_malformed_records_do_not_hide_valid_session(tmp_path: Path) -> None:
    workspace = tmp_path / "work"
    workspace.mkdir()
    session = tmp_path / "codex" / "rollout.jsonl"
    session.parent.mkdir(parents=True)
    session.write_text("not-json\n" + json.dumps({"cwd": str(workspace), "session_id": "ok"}) + "\n")
    assert CodexAdapter(tmp_path / "codex").discover()[0].source_session_id == "ok"


def load_tests(loader, tests, pattern):  # noqa: ARG001
    suite = unittest.TestSuite()
    for name, function in sorted(globals().items()):
        if name.startswith("test_") and callable(function):
            def run(function=function):
                with tempfile.TemporaryDirectory() as directory:
                    function(Path(directory))
            suite.addTest(unittest.FunctionTestCase(run, description=name))
    return suite
