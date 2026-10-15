"""Versioned, strict input contracts for the synthetic reference model."""

from __future__ import annotations

import math
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

UnitFraction = Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]
Nonnegative = Annotated[float, Field(ge=0, le=1e6, allow_inf_nan=False)]
Positive = Annotated[float, Field(ge=1e-6, le=1e6, allow_inf_nan=False)]
Identifier = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_-]{0,39}$")]
StrategyName = Literal["compliant", "reciprocal", "myopic", "bounded"]
PolicyName = Literal["unrestricted", "voluntary", "reciprocal", "freeze"]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)


class Units(Contract):
    time: Literal["synthetic_tick"]
    compute: Literal["normalized_compute"]
    capability: Literal["dimensionless_index"]
    population: Literal["synthetic_weight"]
    service: Literal["normalized_service"]
    budget: Literal["normalized_budget"]


class Assumption(Contract):
    parameter: Annotated[str, Field(min_length=1, max_length=200)]
    evidence_type: Literal["synthetic", "literature-bound", "measured", "elicited"]
    rationale: Annotated[str, Field(min_length=1, max_length=2000)]
    source: Annotated[str, Field(min_length=1, max_length=500)]


class Action(Contract):
    train: UnitFraction
    safety: UnitFraction
    service: UnitFraction
    idle: UnitFraction
    conceal: UnitFraction = 0.0
    appeal: bool = True
    renew: bool = False
    request_restart: bool = False
    inspect: bool = True

    @model_validator(mode="after")
    def budget(self) -> Self:
        if not math.isclose(
            self.train + self.safety + self.service + self.idle, 1.0, rel_tol=0, abs_tol=1e-9
        ):
            raise ValueError("train, safety, service and idle must sum to 1")
        return self


class Actor(Contract):
    id: Identifier
    name: Annotated[str, Field(min_length=1, max_length=80)]
    strategy: StrategyName
    member: bool
    declared_capacity: Positive
    hidden_capacity: Nonnegative
    capability: Nonnegative
    safety: Nonnegative
    population: Positive
    demand: Positive = 6.0
    capability_weight: Nonnegative = 6.0
    service_weight: Nonnegative = 1.0
    safety_weight: Nonnegative = 1.0
    sanction_weight: Nonnegative = 1.0
    concealment_cost: Nonnegative = 0.4
    temperature: Annotated[float, Field(ge=0, le=100, allow_inf_nan=False)] = 2.0
    belief_prior: UnitFraction = 0.15
    belief_learning: bool = True
    reciprocity_threshold: UnitFraction = 0.6
    forgiveness: UnitFraction = 0.08


class Policy(Contract):
    family: PolicyName
    cap_fraction: UnitFraction = 0.25
    activation_tick: Annotated[int, Field(ge=0, le=240)] = 1
    activation_delay: Annotated[int, Field(ge=0, le=24)] = 1
    duration: Annotated[int, Field(ge=1, le=240)] = 10
    exception_per_tick: Nonnegative = 0.25
    exception_total: Nonnegative = 1.0
    renewals_allowed: bool = True
    restart_clear_ticks: Annotated[int, Field(ge=1, le=24)] = 2
    restart_gap: Nonnegative = 0.2


class Verification(Contract):
    coverage: UnitFraction = 0.8
    audit_rate: UnitFraction = 0.8
    sensitivity: UnitFraction = 0.9
    false_positive_rate: UnitFraction = 0.03
    delay: Annotated[int, Field(ge=0, le=24)] = 1
    shared_root_failure: UnitFraction = 0.05
    record_loss: UnitFraction = 0.02
    privacy_exposure: UnitFraction = 0.1
    monitors: Annotated[int, Field(ge=1, le=8)] = 2
    audit_cost: Nonnegative = 0.05
    strength: Literal["statistical", "evidentiary", "hardware-attested", "cryptographic"] = (
        "evidentiary"
    )


class Institution(Contract):
    response_delay: Annotated[int, Field(ge=0, le=24)] = 1
    appeal_delay: Annotated[int, Field(ge=1, le=24)] = 2
    appeal_independence: UnitFraction = 0.95
    review_accuracy: UnitFraction = 0.95
    sanction_capacity: UnitFraction = 0.35
    sanction_duration: Annotated[int, Field(ge=1, le=48)] = 3
    enforcement_success: UnitFraction = 0.9
    budget: Nonnegative = 100.0
    enforcement_cost: Nonnegative = 0.5
    review_cost: Nonnegative = 0.1
    authority_concentration: UnitFraction = 0.5
    capture_rate: UnitFraction = 0.0
    capture_cost: Nonnegative = 0.5
    disclosure: UnitFraction = 1.0


class Dynamics(Contract):
    progress_rate: Nonnegative = 0.3
    safety_rate: Nonnegative = 0.4
    safety_decay: Nonnegative = 0.02
    reference_capacity: Positive = 10.0
    readiness_threshold: Nonnegative = 0.5
    hazard: Literal["exponential", "threshold", "flat"] = "exponential"
    control_base: UnitFraction = 0.001
    control_growth: Annotated[float, Field(ge=0, le=20, allow_inf_nan=False)] = 0.6
    misuse_base: UnitFraction = 0.003
    service_value: Nonnegative = 1.0
    diffusion: Nonnegative = 0.01
    efficiency_shock_tick: Annotated[int, Field(ge=0, le=240)] = 240
    efficiency_multiplier: Annotated[float, Field(ge=1, le=10, allow_inf_nan=False)] = 1.0
    diffusion_shock: Nonnegative = 0.0
    terminal_on_control: bool = False
    false_allegation_tick: Annotated[int | None, Field(ge=0, le=240)] = None
    false_allegation_actor: Identifier | None = None

    @model_validator(mode="after")
    def allegation_pair(self) -> Self:
        if (self.false_allegation_tick is None) != (self.false_allegation_actor is None):
            raise ValueError("false allegation requires both tick and actor")
        return self


class Adapter(Contract):
    id: Identifier
    source_snapshot: Annotated[str, Field(min_length=1, max_length=500)]
    review_status: Literal["unreviewed", "reviewed"]
    notes: Annotated[str, Field(min_length=1, max_length=3000)]


class Scenario(Contract):
    schema_version: Literal[1]
    id: Identifier
    name: Annotated[str, Field(min_length=1, max_length=120)]
    description: Annotated[str, Field(min_length=1, max_length=3000)]
    question: Annotated[str, Field(min_length=1, max_length=1000)]
    classification: Literal["public", "private"]
    seed: Annotated[int, Field(ge=0, le=2**63 - 1)]
    horizon: Annotated[int, Field(ge=1, le=240)]
    units: Units
    assumptions: Annotated[list[Assumption], Field(min_length=1, max_length=100)]
    actors: Annotated[list[Actor], Field(min_length=2, max_length=8)]
    policy: Policy
    verification: Verification
    institution: Institution
    dynamics: Dynamics
    adapter: Adapter | None = None

    @field_validator("schema_version", mode="before")
    @classmethod
    def integer_version(cls, value: object) -> object:
        if type(value) is not int:
            raise ValueError("schema_version must be integer 1")
        return value

    @model_validator(mode="after")
    def identities(self) -> Self:
        ids = [actor.id for actor in self.actors]
        if len(set(ids)) != len(ids):
            raise ValueError("actor IDs must be unique")
        if (
            self.dynamics.false_allegation_actor is not None
            and self.dynamics.false_allegation_actor not in ids
        ):
            raise ValueError("false allegation actor must exist")
        if self.policy.exception_total < self.policy.exception_per_tick:
            raise ValueError("exception_total must cover exception_per_tick")
        if self.adapter is not None and self.classification != "private":
            raise ValueError("a design adapter requires private classification")
        return self
