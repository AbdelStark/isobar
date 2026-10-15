from copy import deepcopy

import pytest

from isobar.artifacts import digest, package_run, read_json, resume_bundle, save_run, verify_bundle
from isobar.engine import branch, simulate
from isobar.models import Scenario
from isobar.scenarios import get_scenario


def small_scenario():
    raw = get_scenario("S2").model_dump(mode="json")
    raw["horizon"] = 6
    return Scenario.model_validate(raw)


def test_round_trip_and_tamper_detection(tmp_path):
    run = simulate(small_scenario())
    path = tmp_path / "run.json"
    save_run(path, run)
    assert verify_bundle(read_json(path))["digests"] == run["digests"]
    altered = read_json(path)
    altered["result"]["metrics"]["breaches"] = 999
    with pytest.raises(ValueError, match="checksum"):
        verify_bundle(altered)
    altered["result_digest"] = digest(altered["result"])
    with pytest.raises(ValueError, match="replay"):
        verify_bundle(altered)
    with pytest.raises(FileExistsError):
        save_run(path, run)


def test_cancel_resume_matches_complete():
    s = small_scenario()
    partial = simulate(s, stop_at=3)
    assert partial["status"] == "cancelled"
    resumed = resume_bundle(package_run(partial))
    complete = simulate(s)
    assert resumed["frames"] == complete["frames"]
    assert resumed["events"] == complete["events"]
    assert resumed["metrics"] == complete["metrics"]
    with pytest.raises(ValueError, match="cancelled"):
        resume_bundle(package_run(complete))


def test_environment_mismatch_blocks_resume():
    bundle = package_run(simulate(small_scenario(), stop_at=2))
    bundle["environment"]["code_digest"] = "different"
    with pytest.raises(ValueError, match="code_digest"):
        resume_bundle(bundle)


def test_private_export_denied_and_classification_checked():
    raw = small_scenario().model_dump(mode="json")
    raw["classification"] = "private"
    run = simulate(Scenario.model_validate(raw))
    with pytest.raises(PermissionError, match="Private"):
        package_run(run, public=True)
    bundle = package_run(run)
    bundle["classification"] = "public"
    with pytest.raises(ValueError, match="classification"):
        verify_bundle(bundle)


def test_branch_is_immutable_replayable_and_keeps_parent():
    original = simulate(small_scenario())
    saved = deepcopy(original)
    action = {"train": 0.0, "safety": 0.5, "service": 0.5, "idle": 0.0, "conceal": 0.0}
    actor = original["scenario"]["actors"][0]["id"]
    child = branch(original, 2, actor, action)
    assert original == saved
    assert child["branch"]["parent_id"] == original["id"]
    assert child["frames"][:2] == original["frames"][:2]
    verify_bundle(package_run(child))


@pytest.mark.parametrize(
    "key,value",
    [
        ("schema_version", 999),
        ("model_version", "forged"),
        ("id", "forged"),
        ("digests", {}),
        ("terminal_cause", "invented"),
        ("branch", {"parent_id": "forged"}),
    ],
)
def test_forged_identity_rejected_even_after_checksum_recomputed(key, value):
    bundle = package_run(simulate(small_scenario()))
    bundle["result"][key] = value
    bundle["result_digest"] = digest(bundle["result"])
    with pytest.raises(ValueError):
        verify_bundle(bundle)


def test_nested_branch_lineage_reconstructs():
    original = simulate(small_scenario())
    actor = original["scenario"]["actors"][0]["id"]
    action = {"train": 0.0, "safety": 0.5, "service": 0.5, "idle": 0.0}
    child = branch(original, 1, actor, action)
    grandchild = branch(child, 3, actor, action)
    verify_bundle(package_run(grandchild))
