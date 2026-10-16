"""Deterministic, partially observable synthetic governance simulation.

Policy changes legal obligations. Only a successful, paid enforcement event changes
physical capacity. Event IDs explain the chain without turning allegations into facts.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Callable
from copy import deepcopy
from typing import Any

from pydantic import ValidationError

from .models import Action, Scenario
from .strategies import choose

MODEL_VERSION = "isobar-reference-v1"
RNG_VERSION = "sha256-keyed-u53-v1"
MAX_BRANCH_DEPTH = 16


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def _draw(seed: int, tick: int, actor: str, process: str, index: int | str = 0) -> float:
    """Stateless independent streams; no draw shifts when a policy adds events."""
    raw = hashlib.sha256(f"{RNG_VERSION}|{seed}|{tick}|{actor}|{process}|{index}".encode()).digest()
    return (int.from_bytes(raw[:8], "big") >> 11) / 2**53


def deterrence_payoff(
    gain: float,
    concealment_cost: float,
    probability: float,
    credibility: float,
    discount: float,
    delay: int,
    sanction: float,
) -> float:
    values = (gain, concealment_cost, probability, credibility, discount, sanction)
    if any(
        isinstance(v, bool) or not isinstance(v, (float, int)) or not math.isfinite(v)
        for v in values
    ):
        raise ValueError("deterrence inputs must be finite numbers")
    if (
        concealment_cost < 0
        or sanction < 0
        or any(not 0 <= v <= 1 for v in (probability, credibility, discount))
        or type(delay) is not int
        or delay < 0
    ):
        raise ValueError("invalid cost, probability, credibility, discount, delay or sanction")
    try:
        value = gain - concealment_cost - probability * credibility * discount**delay * sanction
    except OverflowError as error:
        raise ValueError("deterrence calculation exceeded the finite numeric range") from error
    if not math.isfinite(value):
        raise ValueError("deterrence calculation exceeded the finite numeric range")
    return value


def _safe_input(value: Any) -> Any:
    """Nonfinite invalid actions remain invalid, but their records are JSON-safe."""
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    if isinstance(value, dict):
        return {str(k): _safe_input(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_safe_input(v) for v in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return repr(value)


def simulate(
    scenario: Scenario,
    *,
    actions: dict | None = None,
    stop_at: int | None = None,
    on_decision: Callable[[int, str, dict, Action], None] | None = None,
) -> dict:
    """Run simultaneous decisions, from tick 0, with replayable recorded overrides."""
    scenario = Scenario.model_validate(scenario.model_dump(mode="json"))
    config = scenario.model_dump(mode="json")
    config["actors"].sort(key=lambda actor: actor["id"])
    scenario = Scenario.model_validate(config)
    if stop_at is not None and (type(stop_at) is not int or not 0 <= stop_at <= scenario.horizon):
        raise ValueError("stop_at must be an integer between 0 and horizon")
    horizon = scenario.horizon if stop_at is None else stop_at
    if actions is not None and not isinstance(actions, dict):
        raise ValueError("actions must be an object keyed by '<tick>:<actor_id>'")
    overrides = _safe_input(actions or {})
    actor_ids = {a.id for a in scenario.actors}
    for key in overrides:
        parts = key.split(":")
        if (
            len(parts) != 2
            or not parts[0].isdigit()
            or parts[1] not in actor_ids
            or str(int(parts[0])) != parts[0]
            or not 0 <= int(parts[0]) < scenario.horizon
        ):
            raise ValueError(f"unknown actor or invalid tick in action key {key!r}")
    p, v, inst, dyn = (
        scenario.policy,
        scenario.verification,
        scenario.institution,
        scenario.dynamics,
    )
    states: dict[str, dict[str, Any]] = {}
    for actor in scenario.actors:
        states[actor.id] = {
            **actor.model_dump(),
            "observed_capability": actor.capability,
            "observed_safety": actor.safety,
            "service": 0.0,
            "training": 0.0,
            "safety_work": 0.0,
            "exception_used": 0.0,
            "breaches": 0,
            "restrictions": {},
            "beliefs": {
                rival.id: actor.belief_prior for rival in scenario.actors if rival.id != actor.id
            },
            "appeals": 0,
            "denied": 0.0,
            "requested": 0.0,
            "privacy": 0.0,
            "records": 0,
            "control_incidents": 0,
            "misuse_incidents": 0,
        }
    events: list[dict[str, Any]] = []
    frames: list[dict[str, Any]] = []
    pending: list[dict[str, Any]] = []
    cases: dict[str, dict[str, Any]] = {}
    action_log: dict[str, Any] = {}
    event_counts: dict[str, int] = {}
    warnings: list[str] = []
    if scenario.adapter is not None and scenario.adapter.review_status == "unreviewed":
        warnings.append("Unreviewed private adapter: this mapping is not a validated design test.")
    office: dict[str, Any] = {
        "active": False,
        "expires_at": None,
        "budget": inst.budget,
        "captured": False,
        "appeals_filed": 0,
        "appeals_resolved": 0,
        "appeals_overturned": 0,
        "decisions": 0,
        "public_decisions": 0,
        "clear_ticks": 0,
        "renewal_votes": [],
        "restart_votes": [],
        "authority_concentration": inst.authority_concentration,
    }
    opportunities = 0
    compliant = 0
    terminal_cause = None

    def emit(
        tick: int,
        kind: str,
        actor_id: str | None,
        summary: str,
        *,
        causes: list[str] | None = None,
        visibility: str = "public",
        **data: Any,
    ) -> str:
        key = _digest([tick, kind, actor_id, causes or [], data])
        ordinal = event_counts.get(key, 0)
        event_counts[key] = ordinal + 1
        event_id = "e-" + _digest([key, ordinal])[:16]
        events.append(
            {
                "id": event_id,
                "tick": tick,
                "kind": kind,
                "actor_id": actor_id,
                "summary": summary,
                "causes": causes or [],
                "visibility": visibility,
                "data": data,
            }
        )
        return event_id

    def available(state: dict) -> float:
        fraction = max(state["restrictions"].values(), default=0.0)
        return state["declared_capacity"] * (1 - fraction) + state["hidden_capacity"]

    def allowed(state: dict) -> tuple[float, float]:
        if not office["active"] or not state["member"]:
            return available(state), 0.0
        base = state["declared_capacity"] * (0 if p.family == "freeze" else p.cap_fraction)
        exception = min(p.exception_per_tick, max(0.0, p.exception_total - state["exception_used"]))
        return base, exception

    def metrics() -> dict:
        values = list(states.values())
        requests = sum(s["requested"] for s in values)
        records = sum(s["records"] for s in values)
        capacity = sum(s["declared_capacity"] + s["hidden_capacity"] for s in values)
        return {
            "control_incidents": sum(s["control_incidents"] for s in values),
            "misuse_incidents": sum(s["misuse_incidents"] for s in values),
            "service_total": sum(s["service"] for s in values),
            "denial_fraction": sum(s["denied"] for s in values) / requests if requests else None,
            "privacy_fraction": sum(s["privacy"] for s in values) / records if records else None,
            "appeal_success_fraction": (
                office["appeals_overturned"] / office["appeals_resolved"]
                if office["appeals_resolved"]
                else None
            ),
            "appeal_resolution_fraction": (
                office["appeals_resolved"] / office["appeals_filed"]
                if office["appeals_filed"]
                else None
            ),
            "breaches": sum(s["breaches"] for s in values),
            "cooperation_fraction": compliant / opportunities if opportunities else None,
            "power_concentration": sum(
                ((s["declared_capacity"] + s["hidden_capacity"]) / capacity) ** 2 for s in values
            ),
            "authority_concentration": office["authority_concentration"],
            "auditability_fraction": office["public_decisions"] / office["decisions"]
            if office["decisions"]
            else None,
            "readiness_gap": max(
                max(0.0, s["capability"] - s["safety"] - dyn.readiness_threshold) for s in values
            ),
            "distribution": [
                {
                    "actor_id": s["id"],
                    "name": s["name"],
                    "population": s["population"],
                    "service": s["service"],
                    "service_per_population": s["service"] / s["population"],
                    "denial_fraction": s["denied"] / s["requested"] if s["requested"] else None,
                    "control_incidents": s["control_incidents"],
                    "misuse_incidents": s["misuse_incidents"],
                    "privacy_fraction": s["privacy"] / s["records"] if s["records"] else None,
                }
                for s in values
            ],
        }

    for tick in range(horizon):
        # Measures and due records precede observations; new records arrive next tick at earliest.
        for item in sorted([x for x in pending if x["due"] == tick], key=lambda x: x["id"]):
            actor_id = item["actor_id"]
            state = states[actor_id]
            if item["kind"] == "restore":
                if state["restrictions"].pop(item["case"], None) is not None:
                    emit(
                        tick,
                        "restoration",
                        actor_id,
                        "The temporary capacity restriction expired.",
                        causes=[item["id"]],
                        case=item["case"],
                    )
            elif item["kind"] == "enforce":
                case = cases[item["case"]]
                if case["status"] == "overturned":
                    continue
                if office["budget"] < inst.enforcement_cost:
                    emit(
                        tick,
                        "enforcement_unfunded",
                        actor_id,
                        "The decision could not be implemented within the remaining budget.",
                        causes=[item["id"]],
                    )
                    continue
                office["budget"] -= inst.enforcement_cost
                if _draw(scenario.seed, tick, actor_id, "enforcement", case["random_key"]) < (
                    inst.enforcement_success
                ):
                    state["restrictions"][item["case"]] = inst.sanction_capacity
                    eid = emit(
                        tick,
                        "restriction_applied",
                        actor_id,
                        "A paid enforcement attempt restricted declared capacity.",
                        causes=[item["id"]],
                        case=item["case"],
                        fraction=inst.sanction_capacity,
                        expires_at=tick + inst.sanction_duration,
                    )
                    pending.append(
                        {
                            "kind": "restore",
                            "due": tick + inst.sanction_duration,
                            "actor_id": actor_id,
                            "id": eid,
                            "case": item["case"],
                        }
                    )
                else:
                    emit(
                        tick,
                        "enforcement_failed",
                        actor_id,
                        "A paid enforcement attempt failed; capacity is unchanged.",
                        causes=[item["id"]],
                    )
            elif item["kind"] == "appeal":
                case = cases[item["case"]]
                if office["budget"] < inst.review_cost:
                    case["status"] = "timed_out"
                    emit(
                        tick,
                        "appeal_timed_out",
                        actor_id,
                        "The review deadline passed without a funded review.",
                        causes=[item["id"]],
                    )
                    continue
                office["budget"] -= inst.review_cost
                independent = (
                    not office["captured"]
                    and _draw(
                        scenario.seed, tick, actor_id, "review_independence", case["random_key"]
                    )
                    < inst.appeal_independence
                )
                accurate = _draw(
                    scenario.seed, tick, actor_id, "review_accuracy", case["random_key"]
                )
                finding = (
                    case["actual_breach"]
                    if accurate < inst.review_accuracy
                    else (not case["actual_breach"])
                )
                office["appeals_resolved"] += 1
                if independent and not finding:
                    case["status"] = "overturned"
                    office["appeals_overturned"] += 1
                    rid = emit(
                        tick,
                        "appeal_overturned",
                        actor_id,
                        "Independent review rejected the allegation.",
                        causes=[item["id"]],
                        case=item["case"],
                        evidence_result="not_substantiated",
                    )
                    state["restrictions"].pop(item["case"], None)
                    emit(
                        tick,
                        "restoration",
                        actor_id,
                        "The case restriction was removed; other restrictions remain independent.",
                        causes=[rid],
                        case=item["case"],
                    )
                else:
                    case["status"] = "upheld"
                    emit(
                        tick,
                        "appeal_upheld",
                        actor_id,
                        "Review did not overturn the restriction.",
                        causes=[item["id"]],
                        case=item["case"],
                        independent=independent,
                    )
            elif item["kind"] == "evidence":
                eid = emit(
                    tick,
                    "evidence_delivered",
                    actor_id,
                    "An audit report arrived. A report is not ground truth.",
                    causes=[item["id"]],
                    result=item["result"],
                    period=item["period"],
                    monitor=item["monitor"],
                    predicate="training exceeded the active allowance",
                    strength=v.strength,
                    scope="sampled modeled work",
                )
                if item["result"] == "denied_access":
                    emit(
                        tick,
                        "dispute_unresolved",
                        actor_id,
                        "Inspection access was denied. This does not prove a training violation.",
                        causes=[eid],
                    )
                    continue
                positive = item["result"] == "flag"
                for rival in states.values():
                    if rival["id"] != actor_id and rival["belief_learning"]:
                        prior = rival["beliefs"][actor_id]
                        like_bad = v.sensitivity if positive else 1 - v.sensitivity
                        like_good = v.false_positive_rate if positive else 1 - v.false_positive_rate
                        denominator = prior * like_bad + (1 - prior) * like_good
                        if denominator:
                            rival["beliefs"][actor_id] = prior * like_bad / denominator
                        else:
                            emit(
                                tick,
                                "belief_misspecification",
                                rival["id"],
                                "The report had zero likelihood under both belief categories; "
                                "the prior is retained.",
                                causes=[eid],
                                visibility=f"actor:{rival['id']}",
                            )
                if not positive:
                    continue
                case_id = eid
                random_key = _digest([actor_id, item["period"], item["monitor"]])
                cases[case_id] = {
                    "status": "alleged",
                    "actor_id": actor_id,
                    "actual_breach": item["actual_breach"],
                    "appealed": False,
                    "evidence_id": eid,
                    "decision_id": None,
                    "random_key": random_key,
                }
                aid = emit(
                    tick,
                    "allegation",
                    actor_id,
                    "An audit flag opened a case; the subject may challenge it.",
                    causes=[eid],
                    case=case_id,
                )
                if (
                    p.family in {"reciprocal", "freeze"}
                    and state["member"]
                    and item["mandate_active"]
                ):
                    disclosed = _draw(scenario.seed, tick, actor_id, "disclosure", random_key) < (
                        inst.disclosure
                    )
                    did = emit(
                        tick,
                        "decision",
                        actor_id,
                        "The institution substantiated the report under its synthetic rule.",
                        causes=[aid, eid],
                        case=case_id,
                        rule="one-positive-report-v1",
                        effective_at=tick + max(1, inst.response_delay),
                        visibility="public" if disclosed else f"actor:{actor_id}",
                    )
                    cases[case_id].update(status="substantiated", decision_id=did)
                    office["decisions"] += 1
                    office["public_decisions"] += int(disclosed)
                    pending.append(
                        {
                            "kind": "enforce",
                            "due": tick + max(1, inst.response_delay),
                            "actor_id": actor_id,
                            "id": did,
                            "case": case_id,
                        }
                    )
        pending = [item for item in pending if item["due"] > tick]

        members = [s for s in states.values() if s["member"]]
        quorum = len(members) // 2 + 1
        if office["active"] and office["expires_at"] == tick:
            if p.renewals_allowed and len(office["renewal_votes"]) >= quorum:
                office["expires_at"] = tick + p.duration
                emit(
                    tick,
                    "mandate_renewed",
                    None,
                    "An explicit member majority renewed the rule.",
                    voters=office["renewal_votes"],
                    expires_at=office["expires_at"],
                )
            else:
                office["active"] = False
                emit(tick, "mandate_expired", None, "The mandate expired without a valid renewal.")
                emit(tick, "restart", None, "Normal training is legally permitted again.")
        elif (
            office["active"]
            and office["clear_ticks"] >= p.restart_clear_ticks
            and len(office["restart_votes"]) >= quorum
            and not office["captured"]
        ):
            office["active"] = False
            emit(
                tick,
                "restart",
                None,
                "A member majority approved restart after consecutive clear observed reviews.",
                voters=office["restart_votes"],
            )
        if p.family != "unrestricted" and tick == p.activation_tick:
            emit(
                tick,
                "warning",
                None,
                "A scenario-supplied public warning triggered the activation rule.",
                activates_at=tick + p.activation_delay,
            )
        if p.family != "unrestricted" and tick == p.activation_tick + p.activation_delay:
            office["active"] = True
            office["expires_at"] = tick + p.duration
            emit(
                tick,
                "mandate_activated",
                None,
                "The declared rule took legal effect.",
                family=p.family,
                expires_at=office["expires_at"],
            )
        if tick == dyn.efficiency_shock_tick:
            emit(
                tick,
                "efficiency_shock",
                None,
                "A synthetic efficiency and diffusion shock arrived.",
                multiplier=dyn.efficiency_multiplier,
                diffusion=dyn.diffusion_shock,
            )
        if (
            not office["captured"]
            and office["budget"] >= inst.capture_cost
            and _draw(scenario.seed, tick, "institution", "capture") < inst.capture_rate
        ):
            office["captured"] = True
            office["budget"] -= inst.capture_cost
            office["authority_concentration"] = max(office["authority_concentration"], 0.95)
            emit(
                tick,
                "capture",
                None,
                "A synthetic capture shock disabled independent review.",
                visibility="truth",
                cost=inst.capture_cost,
            )

        # Freeze every actor view before choosing any action: no same-tick lookahead.
        chosen: dict[str, Action] = {}
        for actor_id, state in states.items():
            base, exception = allowed(state)
            own = deepcopy(state)
            own["available_capacity"] = available(state)
            observation = {
                "own": own,
                "beliefs": deepcopy(state["beliefs"]),
                "permitted_training": base + exception,
                "restart_eligible": office["clear_ticks"] >= p.restart_clear_ticks,
                "detection_probability": v.coverage
                * v.audit_rate
                * v.sensitivity
                * (1 - v.shared_root_failure)
                * (1 - v.record_loss),
                "expected_sanction": inst.sanction_capacity
                * state["declared_capacity"]
                * inst.enforcement_success
                if p.family in {"reciprocal", "freeze"}
                else 0.0,
                "progress_rate": dyn.progress_rate,
                "safety_rate": dyn.safety_rate,
                "reference_capacity": dyn.reference_capacity,
            }
            key = f"{tick}:{actor_id}"
            if key in overrides:
                try:
                    chosen[actor_id] = Action.model_validate(overrides[key])
                except (ValidationError, ValueError, TypeError):
                    chosen[actor_id] = Action(
                        train=0.0, safety=0.0, service=0.0, idle=1.0, appeal=False, inspect=False
                    )
                    emit(
                        tick,
                        "invalid_action",
                        actor_id,
                        "Invalid structured action: a labeled no-action fallback was applied.",
                        visibility=f"actor:{actor_id}",
                        fallback="idle",
                    )
                    warnings.append(f"Invalid action at {key}; no-action fallback.")
            else:
                chosen[actor_id] = choose(
                    observation, _draw(scenario.seed, tick, actor_id, "strategy")
                )
            action_log[key] = chosen[actor_id].model_dump(mode="json")
            if on_decision is not None:
                on_decision(tick, actor_id, deepcopy(observation), chosen[actor_id].model_copy())
        office["renewal_votes"] = [
            aid for aid, a in chosen.items() if a.renew and states[aid]["member"]
        ]
        office["restart_votes"] = [
            aid for aid, a in chosen.items() if a.request_restart and states[aid]["member"]
        ]
        shared_failure = _draw(scenario.seed, tick, "verification", "shared_root") < (
            v.shared_root_failure
        )
        if shared_failure:
            emit(
                tick,
                "shared_root_failure",
                None,
                "All monitors sharing the root missed work.",
                visibility="truth",
            )
        for actor_id, state in states.items():
            action = chosen[actor_id]
            capacity = available(state)
            base, exception = allowed(state)
            work = {
                name: capacity * getattr(action, name)
                for name in ("train", "safety", "service", "idle")
            }
            active_member = office["active"] and state["member"]
            breach = bool(active_member and work["train"] > base + exception + 1e-9)
            if active_member:
                opportunities += 1
                compliant += int(not breach)
                state["breaches"] += int(breach)
                exempt = min(exception, max(0.0, work["train"] - base))
                if exempt:
                    state["exception_used"] += exempt
                    emit(
                        tick,
                        "exception_work",
                        actor_id,
                        "Training used an allowance, counted once in actual work.",
                        visibility="truth",
                        work=exempt,
                        cumulative=state["exception_used"],
                    )
                if breach:
                    emit(
                        tick,
                        "breach",
                        actor_id,
                        "Actual work exceeded the legal allowance.",
                        visibility="truth",
                        actual=work["train"],
                        permitted=base + exception,
                    )
            efficiency = dyn.efficiency_multiplier if tick >= dyn.efficiency_shock_tick else 1.0
            diffusion = dyn.diffusion + (
                dyn.diffusion_shock if tick >= dyn.efficiency_shock_tick else 0.0
            )
            declared_available = capacity - state["hidden_capacity"]
            declared_train = action.train * declared_available * (1 - action.conceal)
            state["capability"] += (
                dyn.progress_rate * math.log1p(work["train"] * efficiency / dyn.reference_capacity)
                + diffusion
            )
            state["safety"] = max(
                0.0,
                state["safety"]
                + dyn.safety_rate * math.log1p(work["safety"] / dyn.reference_capacity)
                - dyn.safety_decay,
            )
            state["observed_capability"] += (
                dyn.progress_rate * math.log1p(declared_train * efficiency / dyn.reference_capacity)
                + diffusion
            )
            state["observed_safety"] = max(
                0.0,
                state["observed_safety"]
                + dyn.safety_rate
                * math.log1p(action.safety * declared_available / dyn.reference_capacity)
                - dyn.safety_decay,
            )
            state["training"] = work["train"]
            state["safety_work"] = work["safety"]
            state["work"] = work
            state["last_action"] = action.model_dump(mode="json")
            service = min(work["service"], state["demand"])
            state["service"] += dyn.service_value * service
            state["requested"] += state["demand"]
            state["denied"] += state["demand"] - service
            gap = max(0.0, state["capability"] - state["safety"] - dyn.readiness_threshold)
            if dyn.hazard == "exponential":
                hazard = dyn.control_base * math.exp(min(50.0, dyn.control_growth * gap))
            elif dyn.hazard == "threshold":
                hazard = dyn.control_base * (1 + 20 * int(gap > 1))
            else:
                hazard = dyn.control_base
            if _draw(scenario.seed, tick, actor_id, "control_incident") < -math.expm1(-hazard):
                state["control_incidents"] += 1
                emit(
                    tick,
                    "control_incident",
                    actor_id,
                    "A synthetic control incident was sampled under the selected hazard.",
                )
                if dyn.terminal_on_control:
                    terminal_cause = "control_incident"
            misuse_hazard = (
                dyn.misuse_base
                * state["capability"]
                * (service / state["demand"])
                / (1 + state["safety"])
            )
            if _draw(scenario.seed, tick, actor_id, "misuse_incident") < -math.expm1(
                -misuse_hazard
            ):
                state["misuse_incidents"] += 1
                emit(
                    tick,
                    "misuse_incident",
                    actor_id,
                    "A synthetic misuse incident involved an already deployed capability.",
                )
            emit(
                tick,
                "allocation",
                actor_id,
                "Physical work was executed independently of legality.",
                visibility=f"actor:{actor_id}",
                work=work,
                legal=not breach,
                available_capacity=capacity,
            )

            if active_member:
                for monitor in range(v.monitors):
                    if (
                        office["budget"] < v.audit_cost
                        or shared_failure
                        or _draw(scenario.seed, tick, actor_id, "coverage", monitor)
                        >= v.coverage * (1 - 0.5 * action.conceal)
                        or _draw(scenario.seed, tick, actor_id, "audit", monitor) >= v.audit_rate
                    ):
                        continue
                    office["budget"] -= v.audit_cost
                    state["records"] += 1
                    state["privacy"] += v.privacy_exposure
                    result = (
                        "denied_access"
                        if not action.inspect
                        else "flag"
                        if _draw(scenario.seed, tick, actor_id, "finding", monitor)
                        < (v.sensitivity if breach else v.false_positive_rate)
                        else "clear"
                    )
                    eid = emit(
                        tick,
                        "evidence_created",
                        actor_id,
                        "A monitor produced a synthetic report, pending delivery.",
                        visibility="truth",
                        result=result,
                        monitor=monitor,
                    )
                    if _draw(scenario.seed, tick, actor_id, "record_loss", monitor) < v.record_loss:
                        emit(
                            tick,
                            "evidence_lost",
                            actor_id,
                            "The report was lost before delivery.",
                            causes=[eid],
                            visibility="truth",
                        )
                    else:
                        pending.append(
                            {
                                "kind": "evidence",
                                "due": tick + max(1, v.delay),
                                "actor_id": actor_id,
                                "id": eid,
                                "result": result,
                                "actual_breach": breach,
                                "period": tick,
                                "monitor": monitor,
                                "mandate_active": bool(active_member),
                            }
                        )
            if tick == dyn.false_allegation_tick and actor_id == dyn.false_allegation_actor:
                eid = emit(
                    tick,
                    "injected_report" if breach else "injected_false_report",
                    actor_id,
                    "The fixture injected an independent report asserting a violation.",
                    visibility="truth",
                )
                pending.append(
                    {
                        "kind": "evidence",
                        "due": tick + 1,
                        "actor_id": actor_id,
                        "id": eid,
                        "result": "flag",
                        "actual_breach": breach,
                        "period": tick,
                        "monitor": "independent-synthetic-report",
                        "mandate_active": bool(active_member),
                    }
                )
            for case_id, case in cases.items():
                if (
                    case["actor_id"] == actor_id
                    and case["decision_id"]
                    and not case["appealed"]
                    and action.appeal
                ):
                    case["appealed"] = True
                    office["appeals_filed"] += 1
                    state["appeals"] += 1
                    aid = emit(
                        tick,
                        "appeal_filed",
                        actor_id,
                        "The subject requested independent review of this case.",
                        causes=[case["decision_id"]],
                        case=case_id,
                        due=tick + inst.appeal_delay,
                    )
                    pending.append(
                        {
                            "kind": "appeal",
                            "due": tick + inst.appeal_delay,
                            "actor_id": actor_id,
                            "id": aid,
                            "case": case_id,
                        }
                    )
            if state["belief_learning"]:
                for rival_id in state["beliefs"]:
                    state["beliefs"][rival_id] = state["belief_prior"] + (
                        state["beliefs"][rival_id] - state["belief_prior"]
                    ) * (1 - state["forgiveness"])
        observed_gap = max(
            max(0.0, s["observed_capability"] - s["observed_safety"] - dyn.readiness_threshold)
            for s in states.values()
        )
        office["clear_ticks"] = office["clear_ticks"] + 1 if observed_gap <= p.restart_gap else 0
        frames.append(
            {
                "tick": tick,
                "actors": deepcopy(list(states.values())),
                "institution": deepcopy(office),
                "metrics": metrics(),
            }
        )
        if terminal_cause:
            emit(
                tick,
                "terminal",
                None,
                "The run stopped after this completed synthetic period.",
                cause=terminal_cause,
            )
            break
    result_metrics = metrics()
    completed_ticks = len(frames)
    status = (
        "terminal"
        if terminal_cause
        else ("cancelled" if completed_ticks < scenario.horizon else "completed")
    )
    run = {
        "schema_version": 1,
        "model_version": MODEL_VERSION,
        "rng_version": RNG_VERSION,
        "id": _digest([MODEL_VERSION, config, overrides, completed_ticks]),
        "status": status,
        "scenario": config,
        "seed": scenario.seed,
        "policy": p.family,
        "completed_ticks": completed_ticks,
        "terminal_cause": terminal_cause,
        "frames": frames,
        "events": events,
        "metrics": result_metrics,
        "actions": action_log,
        "input_actions": overrides,
        "warnings": warnings,
        "branch": None,
        "view": "truth",
        "view_label": "Post-run researcher truth (contains hidden state)",
        "digests": {
            "scenario": _digest(config),
            "trace": _digest([frames, events]),
            "metrics": _digest(result_metrics),
        },
    }
    return run


_PUBLIC_ACTOR = {
    "id",
    "name",
    "member",
    "declared_capacity",
    "population",
    "demand",
    "service",
    "control_incidents",
    "misuse_incidents",
}
_PRIVATE_METRICS = {
    "breaches",
    "cooperation_fraction",
    "readiness_gap",
    "privacy_fraction",
    "auditability_fraction",
    "power_concentration",
    "authority_concentration",
}


def project(result: dict, view: str = "public") -> dict:
    """Return a deep filtered projection, including config, events, actions and metrics."""
    ids = {actor["id"] for actor in result["scenario"]["actors"]}
    if view not in {"truth", "public", *ids}:
        raise ValueError("view must be public, truth, or a scenario actor ID")
    output = deepcopy(result)
    if view == "truth":
        return output
    output["view"] = view
    output["view_label"] = "Public observations" if view == "public" else f"Actor view: {view}"
    output.pop("seed", None)
    output.pop("digests", None)
    output.pop("input_actions", None)
    output.pop("actions", None)
    output["warnings"] = [
        event["summary"]
        for event in result["events"]
        if event["kind"] == "invalid_action" and event["actor_id"] == view
    ]
    config = output["scenario"]
    for field in ("seed", "dynamics", "name", "description", "question", "assumptions", "adapter"):
        config.pop(field, None)
    config["actors"] = [
        actor
        if actor["id"] == view
        else {key: value for key, value in actor.items() if key in _PUBLIC_ACTOR}
        for actor in config["actors"]
    ]
    # These are latent institutional risks, not observed capture state or a usable seed.
    config["institution"].pop("capture_rate", None)
    config["institution"].pop("review_accuracy", None)
    if output["branch"]:
        output["branch"] = {
            key: value for key, value in output["branch"].items() if key in {"tick", "actor_id"}
        }

    def filtered_metrics(values: dict) -> dict:
        filtered = deepcopy(values)
        for key in _PRIVATE_METRICS:
            filtered[key] = None
        filtered["unavailable"] = sorted(_PRIVATE_METRICS)
        for group in filtered["distribution"]:
            group["privacy_fraction"] = None
        return filtered

    output["metrics"] = filtered_metrics(output["metrics"])
    for frame in output["frames"]:
        frame["metrics"] = filtered_metrics(frame["metrics"])
        frame["institution"].pop("captured", None)
        # Budget changes can encode covert capture and lost, undelivered audits.
        frame["institution"].pop("budget", None)
        frame["institution"]["authority_concentration"] = None
        for index, actor in enumerate(frame["actors"]):
            if actor["id"] == view:
                actor["knowledge"] = "own state"
                continue
            frame["actors"][index] = {
                **{key: value for key, value in actor.items() if key in _PUBLIC_ACTOR},
                "capability": actor["observed_capability"],
                "safety": actor["observed_safety"],
                "knowledge": "declared-work estimate, not latent capability",
            }
    output["events"] = [
        event for event in output["events"] if event["visibility"] in {"public", f"actor:{view}"}
    ]
    visible_ids = {event["id"] for event in output["events"]}
    for event in output["events"]:
        event["causes"] = [cause for cause in event["causes"] if cause in visible_ids]
    output.pop("id", None)
    output["id"] = "view-" + _digest(output)
    return output


def branch(result: dict, tick: int, actor_id: str, action: dict) -> dict:
    """Intervene at one decision, preserving earlier state and keyed exogenous draws."""
    if result.get("view", "truth") != "truth":
        raise ValueError("branch requires a complete truth result, not a filtered view")
    lineage = result.get("branch")
    depth = 0
    while lineage is not None:
        if not isinstance(lineage, dict):
            raise ValueError("invalid branch lineage")
        depth += 1
        if depth >= MAX_BRANCH_DEPTH:
            raise ValueError(f"branch lineage exceeds the {MAX_BRANCH_DEPTH}-level limit")
        lineage = lineage.get("parent_branch")
    scenario = Scenario.model_validate(result["scenario"])
    if type(tick) is not int or not 0 <= tick < result["completed_ticks"]:
        raise ValueError("branch tick must identify a completed parent decision")
    if actor_id not in {actor.id for actor in scenario.actors}:
        raise ValueError("branch actor must exist")
    overrides = deepcopy(result.get("input_actions", {}))
    overrides[f"{tick}:{actor_id}"] = action
    child = simulate(scenario, actions=overrides)
    child["branch"] = {
        "parent_id": result["id"],
        "tick": tick,
        "actor_id": actor_id,
        "action": _safe_input(action),
        "parent_input_actions": deepcopy(result.get("input_actions", {})),
        "parent_branch": deepcopy(result.get("branch")),
        "parent_completed_ticks": result["completed_ticks"],
    }
    child["id"] = _digest([child["id"], child["branch"]])
    if child["frames"][:tick] != result["frames"][:tick]:
        raise ValueError("parent history is inconsistent with deterministic replay")
    return child
