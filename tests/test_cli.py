import json
import subprocess
import sys


def cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "isobar.cli", *map(str, args)],
        capture_output=True,
        text=True,
        timeout=30,
    )


def test_documented_cli_run_replay_and_resume(tmp_path):
    assert cli("--help").returncode == 0
    assert len(json.loads(cli("catalog").stdout)) == 7
    assert json.loads(cli("validate", "S2").stdout)["valid"]
    partial = tmp_path / "partial.json"
    done = tmp_path / "done.json"
    run = cli("run", "S2", "--stop-at", "3", "-o", partial)
    assert run.returncode == 0, run.stderr
    assert json.loads(run.stdout)["status"] == "cancelled"
    replay = cli("replay", partial)
    assert replay.returncode == 0, replay.stderr
    resume = cli("resume", partial, "-o", done)
    assert resume.returncode == 0, resume.stderr
    assert json.loads(resume.stdout)["status"] == "completed"
    assert cli("replay", done).returncode == 0


def test_compare_does_not_overwrite_its_checkpoint(tmp_path):
    same = tmp_path / "same.json"
    result = cli("compare", "S2", "--output", same, "--checkpoint", same, "--stop-after", "1")
    assert result.returncode == 2
    assert "different paths" in result.stderr
    assert not same.exists()


def test_invalid_preset_returns_actionable_error():
    result = cli("validate", "not-a-scenario")
    assert result.returncode == 2
    assert "scenario" in result.stderr.lower()
