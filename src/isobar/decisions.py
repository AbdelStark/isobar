"""Replay a decision with the kernel's original pre-action observation."""

from .engine import simulate
from .models import Action, Scenario
from .strategies import explain


def inspect_decision(result: dict, tick: int, actor_id: str, view: str) -> dict:
    scenario = Scenario.model_validate(result["scenario"])
    if actor_id not in {actor.id for actor in scenario.actors}:
        raise ValueError("Decision actor must exist.")
    if view not in {"truth", actor_id}:
        raise PermissionError(
            "Choose this nation's observations or post-run truth to inspect incentives."
        )
    if type(tick) is not int or not 0 <= tick < result["completed_ticks"]:
        raise ValueError("Decision tick must identify a completed decision.")
    inspection = {}

    def capture(at: int, actor: str, observation: dict, action: Action) -> None:
        if at == tick and actor == actor_id:
            inspection.update(explain(observation, action))

    overrides = result.get("input_actions", {})
    simulate(scenario, actions=overrides, stop_at=tick + 1, on_decision=capture)
    return {
        "tick": tick,
        "actor_id": actor_id,
        "source": "recorded override" if f"{tick}:{actor_id}" in overrides else "strategy",
        **inspection,
    }
