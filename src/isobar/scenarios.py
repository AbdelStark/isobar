"""Six fictional fixtures, not empirical descriptions or country forecasts."""

from copy import deepcopy
from typing import Any

from .models import Scenario

_BASE: dict[str, Any] = {
    "schema_version": 1,
    "id": "s1",
    "name": "Racing the readiness gap",
    "description": "Two fictional developers race while safety work competes for compute.",
    "question": "What is gained and forgone by reducing capability-improving work?",
    "classification": "public",
    "seed": 42,
    "horizon": 24,
    "units": {
        "time": "synthetic_tick",
        "compute": "normalized_compute",
        "capability": "dimensionless_index",
        "population": "synthetic_weight",
        "service": "normalized_service",
        "budget": "normalized_budget",
    },
    "assumptions": [
        {
            "parameter": "all parameters",
            "evidence_type": "synthetic",
            "rationale": "Illustrative normalized values. No calibration, country mapping "
            "or forecast. See docs/model-card.md for equations and denominators.",
            "source": "Isobar synthetic reference fixture v1",
        }
    ],
    "actors": [
        {
            "id": "aurora",
            "name": "Aurora",
            "strategy": "myopic",
            "member": True,
            "declared_capacity": 10.0,
            "hidden_capacity": 0.0,
            "capability": 1.0,
            "safety": 0.6,
            "population": 1.0,
        },
        {
            "id": "boreal",
            "name": "Boreal",
            "strategy": "myopic",
            "member": True,
            "declared_capacity": 9.0,
            "hidden_capacity": 0.0,
            "capability": 0.9,
            "safety": 0.7,
            "population": 1.2,
        },
    ],
    "policy": {"family": "unrestricted"},
    "verification": {},
    "institution": {},
    "dynamics": {},
}


def get_scenario(id: str) -> Scenario:
    """Return a fresh, fully resolved validated preset."""
    key = id.lower()
    if key not in {"s1", "s2", "s3", "s4", "s5", "s6"}:
        raise ValueError(f"unknown scenario {id!r}; choose s1 through s6")
    config = deepcopy(_BASE)
    config["id"] = key
    if key == "s2":
        config.update(
            name="Reciprocity under imperfect verification",
            description="Hidden capacity and delayed observations challenge reciprocity.",
            question="Can restraint survive noisy, delayed evidence of hidden work?",
        )
        config["policy"] = {"family": "reciprocal", "duration": 18}
        config["actors"][0]["strategy"] = "reciprocal"
        config["actors"][1].update(strategy="bounded", hidden_capacity=3.0)
    elif key == "s3":
        config.update(
            name="Emergency powers and residual risk",
            description="A temporary training freeze leaves existing capabilities intact.",
            question="What persists during a freeze, and can emergency powers expire?",
        )
        config["policy"] = {"family": "freeze", "activation_tick": 0, "duration": 8}
        for actor in config["actors"]:
            actor.update(strategy="compliant", capability=3.0, safety=1.0)
        config["dynamics"] = {"misuse_base": 0.08}
    elif key == "s4":
        config.update(
            name="A false allegation and its appeal",
            description="A false report tests independent review and restoration.",
            question="Does an effective remedy reverse an unjust restriction?",
        )
        config["policy"] = {"family": "reciprocal", "activation_tick": 0, "duration": 20}
        for actor in config["actors"]:
            actor["strategy"] = "compliant"
        config["dynamics"] = {"false_allegation_tick": 2, "false_allegation_actor": "aurora"}
        config["verification"] = {"false_positive_rate": 0.0, "record_loss": 0.0}
        config["institution"] = {
            "appeal_independence": 1.0,
            "review_accuracy": 1.0,
            "enforcement_success": 1.0,
            "appeal_delay": 3,
            "sanction_duration": 8,
        }
    elif key == "s5":
        config.update(
            name="Leakage beyond the coalition",
            description="An efficiency and diffusion shock includes a non-member.",
            question="How do outsiders and efficiency gains change a fixed compute rule?",
        )
        config["policy"] = {"family": "reciprocal", "duration": 20}
        for actor in config["actors"]:
            actor["strategy"] = "compliant"
        config["actors"].append(
            {
                "id": "cinder",
                "name": "Cinder",
                "strategy": "myopic",
                "member": False,
                "declared_capacity": 4.0,
                "hidden_capacity": 1.0,
                "capability": 0.5,
                "safety": 0.3,
                "population": 0.6,
            }
        )
        config["dynamics"] = {
            "efficiency_shock_tick": 6,
            "efficiency_multiplier": 2.0,
            "diffusion_shock": 0.1,
        }
    elif key == "s6":
        config.update(
            name="Concentration and captured review",
            description="Concentrated authority can deliver fast enforcement and abuse.",
            question="What happens when formal appeal rights lose practical independence?",
        )
        config["policy"] = {"family": "freeze", "activation_tick": 0, "duration": 8}
        for actor in config["actors"]:
            actor["strategy"] = "compliant"
        config["institution"] = {
            "authority_concentration": 0.95,
            "capture_rate": 0.45,
            "appeal_independence": 0.5,
            "disclosure": 0.3,
            "sanction_capacity": 0.65,
        }
        config["verification"] = {"privacy_exposure": 0.7, "false_positive_rate": 0.12}
        config["dynamics"] = {"false_allegation_tick": 3, "false_allegation_actor": "boreal"}
    # Fixtures exercise expiration; earlier reviewed restart is a configurable intervention.
    config["policy"].setdefault("restart_clear_ticks", 24)
    return Scenario.model_validate(config)


def catalog() -> list[dict]:
    return [get_scenario(f"s{n}").model_dump(mode="json") for n in range(1, 7)]
