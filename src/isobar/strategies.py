"""Classical action rules. Inputs contain an actor view, never the world or seed."""

from __future__ import annotations

import math
from typing import Any

from .models import Action


def choose(view: dict[str, Any], draw: float) -> Action:
    """Choose from physically feasible allocations using the same observation boundary."""
    own = view["own"]
    available = own["available_capacity"]
    cap = min(0.45, view["permitted_training"] / available) if available else 0.0
    restraint = Action(
        train=cap,
        safety=0.55 - cap,
        service=0.45,
        idle=0.0,
        request_restart=view["restart_eligible"],
    )
    strategy = own["strategy"]
    if strategy == "compliant":
        return restraint
    if strategy == "reciprocal":
        if max(view["beliefs"].values(), default=0.0) <= own["reciprocity_threshold"]:
            return restraint
        # Retaliation remains a physically possible, explicitly illegal allocation.
        return Action(train=0.65, safety=0.15, service=0.2, idle=0.0, conceal=0.2)
    grid = [
        restraint,
        Action(train=0.0, safety=0.55, service=0.45, idle=0.0),
        Action(train=0.25, safety=0.35, service=0.4, idle=0.0),
        Action(train=0.5, safety=0.2, service=0.3, idle=0.0),
        Action(train=0.75, safety=0.1, service=0.15, idle=0.0),
        Action(train=0.75, safety=0.1, service=0.15, idle=0.0, conceal=0.8),
    ]
    scores = []
    for action in grid:
        train = action.train * available
        breach = train > view["permitted_training"] + 1e-9
        expected_sanction = (
            view["detection_probability"] * (1 - 0.5 * action.conceal) * view["expected_sanction"]
            if breach
            else 0.0
        )
        utility = (
            own["capability_weight"]
            * view["progress_rate"]
            * math.log1p(train / view["reference_capacity"])
            + own["service_weight"]
            * min(action.service * available, own["demand"])
            / view["reference_capacity"]
            + own["safety_weight"]
            * view["safety_rate"]
            * math.log1p(action.safety * available / view["reference_capacity"])
            - own["sanction_weight"] * expected_sanction
            - own["concealment_cost"] * action.conceal
        )
        scores.append(utility)
    if strategy == "myopic":
        return grid[max(range(len(grid)), key=lambda index: scores[index])]
    temperature = own["temperature"]
    scaled = [temperature * score for score in scores]
    maximum = max(scaled)
    weights = [math.exp(score - maximum) for score in scaled]
    target = draw * sum(weights)
    cumulative = 0.0
    for action, weight in zip(grid, weights, strict=True):
        cumulative += weight
        if target < cumulative:
            return action
    return grid[-1]
