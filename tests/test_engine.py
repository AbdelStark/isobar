import json
from copy import deepcopy

import pytest

from isobar.artifacts import package_run, verify_bundle
from isobar.engine import branch, deterrence_payoff, project, simulate
from isobar.models import Scenario
from isobar.scenarios import get_scenario


def configured(id="s2", **sections):
    config = get_scenario(id).model_dump(mode="json")
    for name, patch in sections.items():
        if isinstance(patch, dict):
            config[name].update(patch)
        else:
            config[name] = patch
    return Scenario.model_validate(config)


def action(train=0.75, **fields):
    return {"train": train, "safety": 0.0, "service": 1 - train, "idle": 0.0, **fields}


def kinds(run, kind):
    return [event for event in run["events"] if event["kind"] == kind]


@pytest.mark.parametrize("id", [f"s{n}" for n in range(1, 7)] + ["world"])
def test_all_scenarios_replay_and_have_causal_finite_outcomes(id):
    scenario = get_scenario(id)
    result = simulate(scenario)
    assert result == simulate(scenario)
    assert result["completed_ticks"] == scenario.horizon
    assert len(result["metrics"]["distribution"]) == len(scenario.actors)
    json.dumps(result, allow_nan=False)
    seen = set()
    for event in result["events"]:
        assert set(event["causes"]) <= seen
        assert event["id"] not in seen
        seen.add(event["id"])
    for frame in result["frames"]:
        assert frame["institution"]["budget"] >= -1e-10
        for actor in frame["actors"]:
            assert min(actor["work"].values()) >= 0
            restriction = max(actor["restrictions"].values(), default=0)
            expected = actor["declared_capacity"] * (1 - restriction) + actor["hidden_capacity"]
            assert sum(actor["work"].values()) == pytest.approx(expected)
            assert actor["exception_used"] <= scenario.policy.exception_total + 1e-9


@pytest.mark.parametrize("policy", ["unrestricted", "voluntary", "reciprocal", "freeze"])
@pytest.mark.parametrize("strategy", ["compliant", "reciprocal", "myopic", "bounded"])
def test_policy_strategy_cross_product(policy, strategy):
    config = get_scenario("s2").model_dump(mode="json")
    config["policy"]["family"] = policy
    for actor in config["actors"]:
        actor["strategy"] = strategy
    result = simulate(Scenario.model_validate(config))
    assert result["status"] == "completed"
    assert len(result["actions"]) == 2 * config["horizon"]


@pytest.mark.parametrize("hazard", ["flat", "threshold", "exponential"])
def test_alternative_hazards_and_terminal_accounting(hazard):
    scenario = configured(
        dynamics={"hazard": hazard, "control_base": 1.0, "terminal_on_control": True}
    )
    run = simulate(scenario)
    assert run["status"] == "terminal"
    assert run["completed_ticks"] < scenario.horizon
    assert run["terminal_cause"] == "control_incident"
    assert len(run["actions"]) == 2 * run["completed_ticks"]
    assert run["metrics"]["service_total"] == run["frames"][-1]["metrics"]["service_total"]


def test_actor_order_invariant_and_zero_length_cancellation():
    scenario = get_scenario("s2")
    config = scenario.model_dump(mode="json")
    config["actors"].reverse()
    assert simulate(scenario) == simulate(Scenario.model_validate(config))
    empty = simulate(scenario, stop_at=0)
    assert empty["status"] == "cancelled"
    assert empty["frames"] == []
    assert empty["metrics"]["appeal_success_fraction"] is None
    assert empty["metrics"]["cooperation_fraction"] is None


def test_cancelled_prefix_resumes_by_deterministic_replay():
    scenario = get_scenario("s2")
    prefix = simulate(scenario, stop_at=7)
    full = simulate(scenario)
    assert prefix["status"] == "cancelled"
    assert prefix["frames"] == full["frames"][:7]
    assert prefix["events"] == [e for e in full["events"] if e["tick"] < 7]


def test_action_overrides_invalid_fallback_and_offline_replay():
    scenario = get_scenario("s2")
    inputs = {
        "0:aurora": action(0.3),
        "1:aurora": {"train": "invalid"},
        "2:aurora": action(float("nan")),
    }
    run = simulate(scenario, actions=inputs)
    assert len(kinds(run, "invalid_action")) == 2
    assert run["actions"]["1:aurora"]["idle"] == 1
    assert run == simulate(scenario, actions=run["input_actions"])
    offline = simulate(scenario, actions=run["actions"])
    assert offline["frames"] == run["frames"]
    assert offline["metrics"] == run["metrics"]


@pytest.mark.parametrize(
    "overrides", [{"-1:aurora": {}}, {"24:aurora": {}}, {"0:missing": {}}, {"01:aurora": {}}]
)
def test_bad_override_address_rejected(overrides):
    with pytest.raises(ValueError, match="action key"):
        simulate(get_scenario("s2"), actions=overrides)


@pytest.mark.parametrize("stop_at", [-1, 25, True, 1.5])
def test_invalid_cancel_boundary_rejected(stop_at):
    with pytest.raises(ValueError, match="stop_at"):
        simulate(get_scenario("s2"), stop_at=stop_at)


def test_branch_preserves_history_parent_and_lineage():
    parent = simulate(get_scenario("s2"))
    snapshot = deepcopy(parent)
    child = branch(parent, 5, "aurora", action(0.0))
    assert child["frames"][:5] == parent["frames"][:5]
    assert child["actions"]["5:aurora"]["train"] == 0
    assert parent == snapshot
    assert child["branch"]["parent_id"] == parent["id"]
    nested = branch(child, 8, "boreal", action(0.2))
    assert nested["branch"]["parent_branch"] == child["branch"]
    assert "parent_input_actions" not in json.dumps(project(nested)["branch"])
    with pytest.raises(ValueError):
        branch(parent, 30, "aurora", action())
    with pytest.raises(ValueError):
        branch(parent, 1, "missing", action())
    with pytest.raises(ValueError):
        branch(project(parent), 1, "aurora", action())


def test_sixteen_branches_replay_but_seventeenth_is_rejected():
    run = simulate(configured("s1", horizon=1))
    for index in range(16):
        run = branch(run, 0, "aurora", action(index / 20))
    assert verify_bundle(package_run(run)) == run
    snapshot = deepcopy(run)
    with pytest.raises(ValueError, match="16-level limit"):
        branch(run, 0, "aurora", action(0.0))
    assert run == snapshot


def test_projection_filters_every_surface_and_keeps_own_information():
    result = simulate(get_scenario("s2"))
    saved = deepcopy(result)
    public = project(result)
    own = project(result, "boreal")
    assert result == saved
    assert "hidden_capacity" not in json.dumps(public)
    assert "beliefs" not in json.dumps(public)
    assert "actual_breach" not in json.dumps(public)
    assert "input_actions" not in public and "actions" not in public
    assert "seed" not in public and "seed" not in public["scenario"]
    assert "dynamics" not in public["scenario"]
    assert public["metrics"]["breaches"] is None
    assert public["metrics"]["readiness_gap"] is None
    assert public["frames"][0]["actors"][0]["knowledge"].startswith("declared-work")
    assert own["frames"][0]["actors"][1]["hidden_capacity"] == 3
    assert "hidden_capacity" not in own["frames"][0]["actors"][0]
    visible = {e["id"] for e in public["events"]}
    assert all(set(e["causes"]) <= visible for e in public["events"])
    with pytest.raises(ValueError):
        project(result, "unknown")


def test_hidden_state_and_simultaneous_actions_do_not_enter_rival_choice():
    scenario = configured(verification={"coverage": 0.0}, horizon=4)
    changed = scenario.model_dump(mode="json")
    changed["actors"][1]["hidden_capacity"] = 100
    normal = simulate(scenario)
    hidden = simulate(Scenario.model_validate(changed))
    assert [a for key, a in normal["actions"].items() if "aurora" in key] == [
        a for key, a in hidden["actions"].items() if "aurora" in key
    ]
    override = simulate(scenario, actions={"0:boreal": action(0.0)})
    assert normal["actions"]["0:aurora"] == override["actions"]["0:aurora"]


def test_perfect_zero_detection_delays_and_shared_root_failure():
    scenario = configured(
        policy={
            "activation_tick": 0,
            "activation_delay": 0,
            "cap_fraction": 0.0,
            "exception_per_tick": 0.0,
        },
        verification={
            "coverage": 1.0,
            "audit_rate": 1.0,
            "sensitivity": 1.0,
            "false_positive_rate": 0.0,
            "record_loss": 0.0,
            "shared_root_failure": 0.0,
            "delay": 0,
        },
        horizon=5,
    )
    inputs = {f"{t}:{a.id}": action() for t in range(5) for a in scenario.actors}
    run = simulate(scenario, actions=inputs)
    flags = kinds(run, "evidence_delivered")
    assert flags and min(event["tick"] for event in flags) == 1
    assert all(event["data"]["result"] == "flag" for event in flags)
    for override in ({"coverage": 0.0}, {"sensitivity": 0.0}, {"shared_root_failure": 1.0}):
        config = scenario.model_dump(mode="json")
        config["verification"].update(override)
        result = simulate(Scenario.model_validate(config), actions=inputs)
        assert not kinds(result, "allegation")
        assert result["metrics"]["breaches"] == 10
        if "shared_root_failure" in override:
            assert len(kinds(result, "shared_root_failure")) == 5
            assert not kinds(result, "evidence_created")


def test_false_allegation_appeal_restoration_causal_chain():
    result = simulate(get_scenario("s4"))
    assert kinds(result, "allegation")
    assert kinds(result, "appeal_overturned")
    assert kinds(result, "restriction_applied")
    assert kinds(result, "restoration")
    assert result["metrics"]["breaches"] == 0
    assert result["metrics"]["appeal_success_fraction"] == 1
    overturned = kinds(result, "appeal_overturned")[0]
    assert any(
        event["kind"] == "restoration" and overturned["id"] in event["causes"]
        for event in result["events"]
    )


def test_denied_inspection_is_not_proven_breach():
    scenario = configured(
        policy={"activation_tick": 0, "activation_delay": 0},
        horizon=3,
        verification={
            "coverage": 1.0,
            "audit_rate": 1.0,
            "shared_root_failure": 0.0,
            "record_loss": 0.0,
        },
    )
    result = simulate(scenario, actions={"0:aurora": action(0.0, inspect=False)})
    denied = [
        e
        for e in kinds(result, "evidence_delivered")
        if e["actor_id"] == "aurora" and e["data"]["period"] == 0
    ]
    assert denied and all(e["data"]["result"] == "denied_access" for e in denied)
    assert kinds(result, "dispute_unresolved")
    assert all(
        e["id"] not in decision["causes"] for e in denied for decision in kinds(result, "decision")
    )


def test_freeze_does_not_erase_existing_capability_safety_or_misuse():
    scenario = configured(
        "s3",
        policy={
            "activation_delay": 0,
            "exception_per_tick": 0.0,
            "exception_total": 0.0,
            "duration": 6,
        },
        horizon=8,
        dynamics={"misuse_base": 1.0, "diffusion": 0.1},
    )
    result = simulate(scenario)
    during = result["frames"][:6]
    assert all(a["training"] == 0 for f in during for a in f["actors"])
    assert all(a["safety_work"] > 0 for f in during for a in f["actors"])
    assert during[-1]["actors"][0]["capability"] > scenario.actors[0].capability
    assert kinds(result, "misuse_incident")
    assert kinds(result, "mandate_expired")[0]["tick"] == 6
    assert kinds(result, "restart")[0]["tick"] == 6
    assert result["frames"][6]["actors"][0]["training"] > 0


def test_explicit_majority_renewal_and_independent_restart():
    scenario = configured("s3", policy={"activation_delay": 0, "duration": 3}, horizon=7)
    votes = {f"2:{a.id}": action(0.0, renew=True) for a in scenario.actors}
    result = simulate(scenario, actions=votes)
    assert kinds(result, "mandate_renewed")[0]["tick"] == 3
    assert kinds(result, "mandate_expired")[0]["tick"] == 6
    restart = configured(
        "s4",
        policy={"activation_delay": 0, "restart_clear_ticks": 1, "restart_gap": 100.0},
        horizon=4,
    )
    assert kinds(simulate(restart), "restart")[0]["tick"] == 2


def test_budget_failure_and_capture_are_not_automatic_compliance():
    no_money = configured("s4", institution={"budget": 0.0})
    unfunded = simulate(no_money)
    assert kinds(unfunded, "enforcement_unfunded")
    assert kinds(unfunded, "appeal_timed_out")
    assert not kinds(unfunded, "restriction_applied")
    captured = simulate(configured("s4", institution={"capture_rate": 1.0}))
    assert kinds(captured, "capture")
    assert kinds(captured, "appeal_upheld")
    assert captured["metrics"]["appeal_success_fraction"] == 0


def test_nonmember_and_efficiency_shock_remain_independent_of_rules():
    result = simulate(get_scenario("s5"))
    assert kinds(result, "efficiency_shock")[0]["tick"] == 6
    outsider = result["frames"][7]["actors"][2]
    assert outsider["member"] is False
    assert outsider["training"] > 0
    assert outsider["breaches"] == 0


def test_no_learning_control_preserves_prior_and_private_adapter_warns():
    config = get_scenario("s4").model_dump(mode="json")
    config["actors"][1]["belief_learning"] = False
    config["classification"] = "private"
    config["adapter"] = {
        "id": "local-design",
        "source_snapshot": "local-version-1",
        "review_status": "unreviewed",
        "notes": "Uncalibrated local mapping.",
    }
    run = simulate(Scenario.model_validate(config))
    assert run["warnings"]
    assert all(
        frame["actors"][1]["beliefs"]["aurora"] == config["actors"][1]["belief_prior"]
        for frame in run["frames"]
    )


def test_deterrence_exact_limit_and_validation():
    assert deterrence_payoff(10, 2, 0.5, 0.8, 0.9, 2, 20) == pytest.approx(1.52)
    for inputs in [
        (10, 2, 2, 1, 1, 0, 2),
        (10, 2, 1, 1, 1, -1, 2),
        (float("nan"), 2, 1, 1, 1, 0, 2),
        (10, 2, 1, 1, 1, True, 2),
        (-1e308, 1e308, 1, 1, 1, 0, 2),
        (10, 2, 1, 1, 0.9, 10**1000, 2),
    ]:
        with pytest.raises(ValueError):
            deterrence_payoff(*inputs)


def test_capture_is_latent_until_an_authorized_observation():
    clear = project(simulate(configured("s1", horizon=1, institution={"capture_rate": 0.0})))
    hidden = project(simulate(configured("s1", horizon=1, institution={"capture_rate": 1.0})))
    assert clear["frames"] == hidden["frames"]
    assert clear["metrics"] == hidden["metrics"]
    assert clear["events"] == hidden["events"]
    assert clear["scenario"] == hidden["scenario"]
    assert clear["id"] == hidden["id"]


def test_extreme_valid_config_remains_finite():
    config = get_scenario("s1").model_dump(mode="json")
    config["dynamics"].update(
        reference_capacity=1e-6, progress_rate=1e6, safety_rate=1e6, control_growth=20.0
    )
    for actor in config["actors"]:
        actor.update(
            declared_capacity=1e6,
            hidden_capacity=1e6,
            population=1e-6,
            capability_weight=1e6,
            service_weight=1e6,
            temperature=100.0,
            strategy="bounded",
        )
    result = simulate(Scenario.model_validate(config))
    json.dumps(result, allow_nan=False)


def test_projection_identity_and_narrative_cannot_encode_hidden_state():
    one = get_scenario("s2").model_dump(mode="json")
    two = deepcopy(one)
    two["actors"][1]["hidden_capacity"] = 4.0
    two["assumptions"][0]["rationale"] = "SECRET private latent capability"
    two["description"] = "SECRET"
    public_one = project(simulate(Scenario.model_validate(one), stop_at=0))
    public_two = project(simulate(Scenario.model_validate(two), stop_at=0))
    assert public_one == public_two
    assert "SECRET" not in json.dumps(public_two)


def test_adding_monitor_does_not_shift_common_case_randomness():
    scenario = configured(
        "s2",
        horizon=8,
        seed=1,
        policy={
            "activation_tick": 0,
            "activation_delay": 0,
            "cap_fraction": 0.0,
            "exception_per_tick": 0.0,
            "exception_total": 0.0,
        },
        verification={
            "coverage": 1.0,
            "audit_rate": 1.0,
            "sensitivity": 1.0,
            "false_positive_rate": 0.0,
            "shared_root_failure": 0.0,
            "record_loss": 0.0,
            "monitors": 1,
            "audit_cost": 0.0,
        },
        institution={
            "enforcement_success": 0.5,
            "enforcement_cost": 0.0,
            "review_cost": 0.0,
            "review_accuracy": 0.5,
            "appeal_independence": 0.5,
            "disclosure": 0.5,
        },
    )
    inputs = {f"{tick}:{actor.id}": action(1.0) for tick in range(8) for actor in scenario.actors}
    more = scenario.model_dump(mode="json")
    more["verification"]["monitors"] = 2
    one = simulate(scenario, actions=inputs)
    two = simulate(Scenario.model_validate(more), actions=inputs)
    for period in (0, 1, 2):

        def chain(run, period=period):
            report = next(
                e
                for e in kinds(run, "evidence_delivered")
                if e["actor_id"] == "aurora"
                and e["data"]["period"] == period
                and e["data"]["monitor"] == 0
            )
            decision = next(e for e in kinds(run, "decision") if e["data"]["case"] == report["id"])
            filing = next(
                e for e in kinds(run, "appeal_filed") if e["data"]["case"] == report["id"]
            )
            responses = [
                e
                for e in run["events"]
                if decision["id"] in e["causes"] or filing["id"] in e["causes"]
            ]
            return report, decision, filing, responses

        assert chain(one) == chain(two)


def test_no_lawful_restriction_for_pre_mandate_report_but_late_reports_survive_expiry():
    before = configured(
        "s4",
        horizon=6,
        policy={"activation_tick": 10, "activation_delay": 0},
        dynamics={"false_allegation_tick": 0},
    )
    early = simulate(before)
    assert kinds(early, "allegation")
    assert not kinds(early, "decision")
    assert not kinds(early, "restriction_applied")
    after = configured(
        "s4",
        horizon=8,
        policy={"activation_tick": 0, "activation_delay": 0, "duration": 1},
        dynamics={"false_allegation_tick": 0},
    )
    late = simulate(after)
    assert kinds(late, "mandate_expired")[0]["tick"] == 1
    assert kinds(late, "decision")[0]["tick"] == 1
    assert kinds(late, "restriction_applied")[0]["tick"] == 2
