"""Classical action rules and inspectable incentives from the same actor observation."""

from __future__ import annotations

import math
from typing import Any

from .models import Action


def candidates(view: dict[str, Any]) -> list[Action]:
    own = view["own"]
    available = own["available_capacity"]
    cap = min(0.45, view["permitted_training"] / available) if available else 0.0
    return [
        Action(
            train=cap,
            safety=0.55 - cap,
            service=0.45,
            idle=0.0,
            request_restart=view["restart_eligible"],
        ),
        Action(train=0.0, safety=0.55, service=0.45, idle=0.0),
        Action(train=0.25, safety=0.35, service=0.4, idle=0.0),
        Action(train=0.5, safety=0.2, service=0.3, idle=0.0),
        Action(train=0.75, safety=0.1, service=0.15, idle=0.0),
        Action(train=0.75, safety=0.1, service=0.15, idle=0.0, conceal=0.8),
    ]


def payoff(view: dict[str, Any], action: Action) -> dict:
    own = view["own"]
    available = own["available_capacity"]
    train = action.train * available
    breach = train > view["permitted_training"] + 1e-9
    expected_sanction = (
        view["detection_probability"] * (1 - 0.5 * action.conceal) * view["expected_sanction"]
        if breach
        else 0.0
    )
    capability = (
        own["capability_weight"]
        * view["progress_rate"]
        * math.log1p(train / view["reference_capacity"])
    )
    service = (
        own["service_weight"]
        * min(action.service * available, own["demand"])
        / view["reference_capacity"]
    )
    safety = (
        own["safety_weight"]
        * view["safety_rate"]
        * math.log1p(action.safety * available / view["reference_capacity"])
    )
    sanction = own["sanction_weight"] * expected_sanction
    concealment = own["concealment_cost"] * action.conceal
    return {
        "capability": capability,
        "service": service,
        "safety": safety,
        "sanction": sanction,
        "concealment": concealment,
        "utility": capability + service + safety - sanction - concealment,
        "breach": breach,
    }


def _weights(scores: list[float], temperature: float) -> list[float]:
    scaled = [temperature * score for score in scores]
    maximum = max(scaled)
    return [math.exp(score - maximum) for score in scaled]


def choose(view: dict[str, Any], draw: float) -> Action:
    """Choose from physically feasible allocations using the same observation boundary."""
    own = view["own"]
    grid = candidates(view)
    if own["strategy"] == "compliant":
        return grid[0]
    if own["strategy"] == "reciprocal":
        if max(view["beliefs"].values(), default=0.0) <= own["reciprocity_threshold"]:
            return grid[0]
        return Action(train=0.65, safety=0.15, service=0.2, idle=0.0, conceal=0.2)
    scores = [payoff(view, action)["utility"] for action in grid]
    if own["strategy"] == "myopic":
        return grid[max(range(len(grid)), key=lambda index: scores[index])]
    weights = _weights(scores, own["temperature"])
    target = draw * sum(weights)
    cumulative = 0.0
    for action, weight in zip(grid, weights, strict=True):
        cumulative += weight
        if target < cumulative:
            return action
    return grid[-1]


def explain(view: dict[str, Any], selected: Action) -> dict:
    """Describe the actual rule and its counterfactual grid without using rival truth."""
    grid = candidates(view)
    scores = [payoff(view, action) for action in grid]
    own = view["own"]
    weights = _weights([row["utility"] for row in scores], own["temperature"])
    total = sum(weights)
    names = ["Rule-constrained", "Safety first", "Balanced", "Accelerate", "Race", "Concealed race"]
    return {
        "strategy": own["strategy"],
        "available_capacity": own["available_capacity"],
        "permitted_training": view["permitted_training"],
        "detection_probability": view["detection_probability"],
        "beliefs": view["beliefs"],
        "reciprocity_threshold": own["reciprocity_threshold"],
        "selected_action": selected.model_dump(mode="json"),
        "selected_payoff": payoff(view, selected),
        "alternatives": [
            {
                "label": name,
                "action": action.model_dump(mode="json"),
                **score,
                "probability": weight / total if own["strategy"] == "bounded" else None,
            }
            for name, action, score, weight in zip(names, grid, scores, weights, strict=True)
        ],
        "note": "One-period subjective utility, not welfare or an equilibrium. "
        "Compliant and reciprocal actors follow rules; "
        "only myopic and bounded actors use this grid.",
    }
