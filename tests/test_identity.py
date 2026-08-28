from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from chekov.identity import normalize_remote, workspace_for
from chekov.git import observe_git


def test_remote_normalization() -> None:
    assert normalize_remote("git@GitHub.com:DHk/Chekov.git") == "github.com/dhk/chekov"
    assert normalize_remote("https://github.com/DHK/chekov.git") == "github.com/dhk/chekov"


def test_workspace_uses_remote_not_absolute_path(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", str(repo)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "remote", "add", "origin", "git@github.com:dhk/chekov.git"], check=True)
    workspace = workspace_for(repo)
    assert workspace.identity_kind == "git-remote"
    assert workspace.identity_value == "github.com/dhk/chekov"


def test_explicit_workspace_marker_wins(tmp_path: Path) -> None:
    marker = tmp_path / ".chekov" / "workspace.json"
    marker.parent.mkdir()
    marker.write_text(json.dumps({"id": "durable-id"}))
    workspace = workspace_for(tmp_path)
    assert workspace.identity_kind == "explicit"
    assert workspace.identity_value == "durable-id"


def test_git_observation_counts_changed_files(tmp_path: Path) -> None:
    subprocess.run(["git", "init", str(tmp_path)], check=True, capture_output=True)
    (tmp_path / "one.txt").write_text("one")
    (tmp_path / "two.txt").write_text("two")
    observation = observe_git(workspace_for(tmp_path))
    assert observation is not None
    assert observation.changed_files == 2
    assert observation.source.kind == "git-status"


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
