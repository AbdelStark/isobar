import pytest

from isobar.artifacts import atomic_json, digest, environment, read_json
from isobar.experiments import compare, summary, validate_comparison
from isobar.models import Scenario
from isobar.scenarios import get_scenario


def scenario():
    data = get_scenario("S2").model_dump(mode="json")
    data["horizon"] = 4
    return Scenario.model_validate(data)


def test_statistics_report_null_denominators_and_small_samples():
    assert summary([None, None])["n"] == 0
    assert summary([1.0])["ci_low"] is None
    result = summary([1, 2, 3])
    assert result["mean"] == 2
    assert result["sd"] == 1
    assert result["ci_low"] < 2 < result["ci_high"]


def test_paired_comparison_uses_each_seed_and_exact_deltas():
    result = compare(scenario(), ["unrestricted", "freeze"], [7, 11, 13])
    assert result["status"] == "completed"
    assert result["paired"] is True
    assert result["environment"] == environment()
    assert len(result["runs"]) == 6
    runs = {(r["policy"], r["seed"]): r for r in result["runs"]}
    expected = (
        sum(
            runs["freeze", s]["metrics"]["service_total"]
            - runs["unrestricted", s]["metrics"]["service_total"]
            for s in [7, 11, 13]
        )
        / 3
    )
    assert result["differences"][0]["metrics"]["service_total"]["mean"] == pytest.approx(expected)


def test_batch_checkpoint_resume_and_mismatch(tmp_path):
    checkpoint = tmp_path / "batch.json"
    partial = compare(
        scenario(), ["unrestricted", "freeze"], [1, 2], checkpoint=checkpoint, stop_after=1
    )
    assert partial["status"] == "cancelled"
    final = compare(scenario(), ["unrestricted", "freeze"], [1, 2], checkpoint=checkpoint)
    fresh = compare(scenario(), ["unrestricted", "freeze"], [1, 2])
    assert final == fresh
    with pytest.raises(ValueError, match="mismatch"):
        compare(scenario(), ["unrestricted", "voluntary"], [1, 2], checkpoint=checkpoint)


def test_group_summaries_preserve_outsiders_and_exact_paired_differences():
    result = compare(get_scenario("s5"), ["unrestricted", "freeze"], [1, 2])
    for row in result["summaries"]:
        assert {g["actor_id"] for g in row["distribution"]} == {"aurora", "boreal", "cinder"}
        assert all(g["metrics"]["service"]["n"] == 2 for g in row["distribution"])
    runs = {(r["policy"], r["seed"]): r for r in result["runs"]}
    for index, group in enumerate(result["differences"][0]["distribution"]):
        expected = (
            sum(
                runs["freeze", seed]["metrics"]["distribution"][index]["service_per_population"]
                - runs["unrestricted", seed]["metrics"]["distribution"][index][
                    "service_per_population"
                ]
                for seed in (1, 2)
            )
            / 2
        )
        assert group["metrics"]["service_per_population"]["mean"] == pytest.approx(expected)


@pytest.mark.parametrize(
    "policies,seeds",
    [
        (["freeze"], [1, 2]),
        (["freeze", "unrestricted"], [1, 1]),
        (["freeze", "unrestricted"], [True, 2]),
        (["nonsense", "freeze"], [1, 2]),
    ],
)
def test_invalid_experiments_rejected(policies, seeds):
    with pytest.raises(ValueError):
        validate_comparison(policies, seeds)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf"), True, "1"])
def test_invalid_numerics_are_not_silently_dropped(value):
    with pytest.raises(ValueError, match="metric"):
        summary([1.0, value])


@pytest.mark.parametrize(
    "mutation",
    [
        "version",
        "bool_version",
        "float_version",
        "config",
        "environment",
        "null_environment",
        "status",
        "metric",
    ],
)
def test_forged_batch_cache_is_rejected(tmp_path, mutation):
    checkpoint = tmp_path / "checkpoint.json"
    compare(scenario(), ["unrestricted", "freeze"], [1, 2], checkpoint=checkpoint, stop_after=1)
    saved = read_json(checkpoint)
    if mutation == "version":
        saved["artifact_version"] = 999
    elif mutation == "bool_version":
        saved["artifact_version"] = True
    elif mutation == "float_version":
        saved["artifact_version"] = 1.0
    elif mutation == "config":
        saved["config"] = {}
    elif mutation == "environment":
        saved["environment"]["python"] = "0.0"
    elif mutation == "null_environment":
        saved["environment"] = None
    elif mutation == "status":
        saved["status"] = "completed"
    else:
        saved["runs"]["unrestricted:1"]["metrics"]["service_total"] = 1e9
        saved["runs_digest"] = digest(saved["runs"])
    atomic_json(checkpoint, saved)
    with pytest.raises(ValueError):
        compare(scenario(), ["unrestricted", "freeze"], [1, 2], checkpoint=checkpoint)
