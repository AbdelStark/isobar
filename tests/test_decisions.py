from copy import deepcopy

import pytest

from isobar.decisions import inspect_decision
from isobar.engine import branch, simulate
from isobar.models import Action, Scenario
from isobar.scenarios import get_scenario


def world():
    scenario = get_scenario("world")
    scenario.horizon = 4
    return scenario


def test_decision_instrumentation_is_observational_and_pre_action():
    scenario = world()
    expected = simulate(scenario)
    observations = []

    def capture(tick, actor, view, action):
        observations.append((tick, actor, deepcopy(view), action.model_copy()))
        # An inspector cannot mutate the kernel's decision or observation.
        view["own"]["capability"] = 9000
        view["beliefs"].clear()
        action.train = 0

    assert simulate(scenario, on_decision=capture) == expected
    tick, actor, view, action = next(item for item in observations if item[:2] == (0, "usa"))
    assert (tick, actor) == (0, "usa")
    assert view["own"]["capability"] == scenario.actors[0].capability
    assert action.model_dump(mode="json") == expected["actions"]["0:usa"]
    assert set(view) == {
        "own",
        "beliefs",
        "permitted_training",
        "restart_eligible",
        "detection_probability",
        "expected_sanction",
        "progress_rate",
        "safety_rate",
        "reference_capacity",
    }


@pytest.mark.parametrize("actor", ["usa", "chn", "ind", "fra"])
def test_explanation_matches_actual_choice_and_scoring_rule(actor):
    result = simulate(world())
    decision = inspect_decision(result, 1, actor, actor)
    assert decision["selected_action"] == result["actions"][f"1:{actor}"]
    assert decision["source"] == "strategy"
    rows = decision["alternatives"]
    assert len(rows) == 6
    for row in rows:
        assert row["utility"] == pytest.approx(
            row["capability"]
            + row["service"]
            + row["safety"]
            - row["sanction"]
            - row["concealment"]
        )
    if decision["strategy"] == "myopic":
        assert decision["selected_payoff"]["utility"] == max(row["utility"] for row in rows)
    if decision["strategy"] == "bounded":
        assert sum(row["probability"] for row in rows) == pytest.approx(1)
        assert all(0 <= row["probability"] <= 1 for row in rows)
    else:
        assert all(row["probability"] is None for row in rows)


def test_private_rival_parameters_do_not_enter_decision_explanation():
    scenario = world()
    original = inspect_decision(simulate(scenario), 0, "usa", "usa")
    config = scenario.model_dump(mode="json")
    config["actors"][1].update(hidden_capacity=123, capability_weight=9, strategy="myopic")
    changed = inspect_decision(simulate(Scenario.model_validate(config)), 0, "usa", "usa")
    assert changed == original


def test_nested_override_is_the_decision_explained():
    parent = simulate(world())
    first = Action(train=0, safety=0.5, service=0.5, idle=0).model_dump(mode="json")
    second = Action(train=0.2, safety=0.3, service=0.4, idle=0.1).model_dump(mode="json")
    child = branch(parent, 1, "usa", first)
    child = branch(child, 2, "chn", second)
    for tick, actor, action in [(1, "usa", first), (2, "chn", second)]:
        explanation = inspect_decision(child, tick, actor, "truth")
        assert explanation["selected_action"] == action
        assert explanation["source"] == "recorded override"
    assert (
        inspect_decision(child, 3, "chn", "truth")["selected_action"] == child["actions"]["3:chn"]
    )


@pytest.mark.parametrize("view", ["public", "chn"])
def test_other_observation_boundaries_cannot_inspect_private_incentives(view):
    with pytest.raises(PermissionError):
        inspect_decision(simulate(world()), 0, "usa", view)


@pytest.mark.parametrize("tick", [-1, 4, True, 0.5, "0"])
def test_decision_tick_must_identify_completed_decision(tick):
    with pytest.raises(ValueError, match="completed decision"):
        inspect_decision(simulate(world()), tick, "usa", "truth")
