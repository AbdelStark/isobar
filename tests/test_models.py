from copy import deepcopy

import pytest
from pydantic import ValidationError

from isobar.models import Action, Scenario
from isobar.scenarios import catalog, get_scenario


def test_complete_catalog_is_fresh_and_versioned():
    scenarios = catalog()
    assert len(scenarios) == 6
    assert len({s["id"] for s in scenarios}) == 6
    for scenario in scenarios:
        assert Scenario.model_validate(scenario).model_dump(mode="json") == scenario
        assert scenario["units"]["time"] == "synthetic_tick"
        assert scenario["assumptions"][0]["evidence_type"] == "synthetic"
    scenarios[0]["actors"][0]["name"] = "Changed"
    assert get_scenario("S1").actors[0].name == "Aurora"
    with pytest.raises(ValueError, match="unknown scenario"):
        get_scenario("not-a-scenario")


@pytest.mark.parametrize(
    "path,value",
    [
        (("schema_version",), 2),
        (("horizon",), 0),
        (("horizon",), True),
        (("horizon",), "24"),
        (("seed",), -1),
        (("units", "time"), "months"),
        (("verification", "coverage"), 1.1),
        (("verification", "coverage"), float("nan")),
        (("verification", "coverage"), float("inf")),
        (("verification", "delay"), -1),
        (("institution", "budget"), -1),
        (("dynamics", "hazard"), "unknown"),
        (("actors", 0, "hidden_capacity"), -1),
        (("actors", 0, "strategy"), "eval"),
        (("actors", 0, "declared_capacity"), 0),
        (("actors", 0, "population"), 0),
        (("assumptions",), []),
        (("actors",), []),
        (("units",), {}),
    ],
)
def test_scenario_rejects_invalid_inputs(path, value):
    config = get_scenario("s2").model_dump(mode="json")
    target = config
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    with pytest.raises(ValidationError):
        Scenario.model_validate(config)


def test_cross_field_and_unknown_fields_rejected():
    config = get_scenario("s1").model_dump(mode="json")
    for mutation in ("duplicate", "unknown", "exception", "allegation", "private"):
        candidate = deepcopy(config)
        if mutation == "duplicate":
            candidate["actors"][1]["id"] = candidate["actors"][0]["id"]
        elif mutation == "unknown":
            candidate["arbitrary_python"] = "import os"
        elif mutation == "exception":
            candidate["policy"]["exception_total"] = 0.0
        elif mutation == "allegation":
            candidate["dynamics"]["false_allegation_tick"] = 1
        else:
            candidate["adapter"] = {
                "id": "mapping",
                "source_snapshot": "local snapshot",
                "review_status": "unreviewed",
                "notes": "synthetic",
            }
        with pytest.raises(ValidationError):
            Scenario.model_validate(candidate)


@pytest.mark.parametrize(
    "patch",
    [
        {"train": -0.1},
        {"train": 2.0},
        {"train": "0.2"},
        {"train": float("nan")},
        {"train": True},
        {"idle": 0.5},
        {"conceal": 2.0},
        {"appeal": 1},
        {"extra": 0},
    ],
)
def test_action_contract_rejects_impossible_or_untyped_allocations(patch):
    payload = {"train": 0.2, "safety": 0.3, "service": 0.5, "idle": 0.0, **patch}
    with pytest.raises(ValidationError):
        Action.model_validate(payload)


def test_action_tolerance_does_not_renormalize_a_material_violation():
    assert Action(train=0.1, safety=0.2, service=0.7, idle=0.0).conceal == 0
    with pytest.raises(ValidationError):
        Action(train=0.1, safety=0.2, service=0.71, idle=0.0)


def test_tiny_denominators_and_bool_version_rejected():
    config = get_scenario("s1").model_dump(mode="json")
    for path in [
        ("dynamics", "reference_capacity"),
        ("actors", 0, "population"),
        ("actors", 0, "declared_capacity"),
        ("actors", 0, "demand"),
    ]:
        candidate = deepcopy(config)
        cursor = candidate
        for key in path[:-1]:
            cursor = cursor[key]
        cursor[path[-1]] = 5e-324
        with pytest.raises(ValidationError):
            Scenario.model_validate(candidate)
    config["schema_version"] = True
    with pytest.raises(ValidationError):
        Scenario.model_validate(config)
