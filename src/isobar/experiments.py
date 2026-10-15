"""Paired, explicitly conditional comparisons; never a policy league table."""

from __future__ import annotations

import math
from pathlib import Path
from statistics import mean, stdev

from isobar.artifacts import atomic_json, digest, environment, read_json
from isobar.engine import simulate
from isobar.models import Scenario

POLICIES = ("unrestricted", "voluntary", "reciprocal", "freeze")
STRATEGIES = ("compliant", "reciprocal", "myopic", "bounded")


def summary(values: list[float | None]) -> dict:
    if any(x is not None and (type(x) not in (int, float) or not math.isfinite(x)) for x in values):
        raise ValueError("Non-finite or nonnumeric metric; the comparison is invalid.")
    finite = [float(x) for x in values if x is not None]
    if not finite:
        return {"mean": None, "sd": None, "ci_low": None, "ci_high": None, "n": 0}
    center = mean(finite)
    if len(finite) < 2:
        return {"mean": center, "sd": None, "ci_low": None, "ci_high": None, "n": 1}
    spread = stdev(finite)
    # Normal-approximation Monte Carlo interval, not a calibrated real-world probability.
    width = 1.96 * spread / math.sqrt(len(finite))
    return {
        "mean": center,
        "sd": spread,
        "ci_low": center - width,
        "ci_high": center + width,
        "n": len(finite),
    }


def validate_comparison(policies: list[str], seeds: list[int]) -> None:
    if not 2 <= len(policies) <= 4 or len(set(policies)) != len(policies):
        raise ValueError("Choose two to four distinct policies.")
    if any(p not in POLICIES for p in policies):
        raise ValueError("Unknown policy family.")
    if not 2 <= len(seeds) <= 1000 or len(set(seeds)) != len(seeds):
        raise ValueError("Use two to 1000 distinct seeds for a paired comparison.")
    if any(type(seed) is not int or not 0 <= seed < 2**32 for seed in seeds):
        raise ValueError("Seeds must be integers in [0, 2^32).")


def compare(
    scenario: Scenario,
    policies: list[str],
    seeds: list[int],
    *,
    checkpoint: Path | None = None,
    stop_after: int | None = None,
) -> dict:
    validate_comparison(policies, seeds)
    if stop_after is not None and (type(stop_after) is not int or stop_after < 1):
        raise ValueError("stop_after must be a positive integer.")
    config = {"scenario": scenario.model_dump(mode="json"), "policies": policies, "seeds": seeds}
    identity = digest(config)
    env = environment()
    runs: dict[str, dict] = {}
    if checkpoint and checkpoint.exists():
        previous = read_json(checkpoint)
        if (
            not isinstance(previous, dict)
            or previous.get("artifact_version") != 1
            or previous.get("kind") != "isobar-batch"
        ):
            raise ValueError("Invalid batch checkpoint kind or version.")
        if (
            previous.get("config_digest") != identity
            or previous.get("code_digest") != env["code_digest"]
            or previous.get("config") != config
        ):
            raise ValueError("Batch checkpoint configuration or code mismatch.")
        for field in ("package", "python", "pydantic", "code_digest", "platform"):
            if previous.get("environment", {}).get(field) != env[field]:
                raise ValueError(f"Batch checkpoint environment {field} mismatch.")
        runs = previous.get("runs", {})
        expected_keys = {f"{policy}:{seed}" for policy in policies for seed in seeds}
        if not isinstance(runs, dict) or not set(runs).issubset(expected_keys):
            raise ValueError("Batch checkpoint contains unexpected run keys.")
        if previous.get("runs_digest") != digest(runs):
            raise ValueError("Batch checkpoint checksum mismatch.")
        expected_status = "completed" if len(runs) == len(expected_keys) else "cancelled"
        if previous.get("status") != expected_status:
            raise ValueError("Batch checkpoint status contradicts completed run count.")
        for key, cached in runs.items():
            policy, raw_seed = key.split(":")
            rebuilt = _run(scenario, policy, int(raw_seed))
            if digest(cached) != digest(rebuilt):
                raise ValueError("Batch checkpoint run differs from deterministic replay.")
    added = 0
    total = len(policies) * len(seeds)
    for policy in policies:
        for seed in seeds:
            key = f"{policy}:{seed}"
            if key in runs:
                continue
            runs[key] = _run(scenario, policy, seed)
            added += 1
            if checkpoint:
                atomic_json(
                    checkpoint,
                    {
                        "artifact_version": 1,
                        "kind": "isobar-batch",
                        "config": config,
                        "config_digest": identity,
                        "code_digest": env["code_digest"],
                        "environment": env,
                        "runs": runs,
                        "runs_digest": digest(runs),
                        "status": "completed" if len(runs) == total else "cancelled",
                    },
                )
            if stop_after is not None and added >= stop_after and len(runs) < total:
                return {
                    "status": "cancelled",
                    "completed_runs": len(runs),
                    "total_runs": total,
                    "config_digest": identity,
                    "note": "Partial batch, not a completed comparison.",
                }
    baseline = policies[0]
    metrics = [
        key
        for key, value in runs[f"{baseline}:{seeds[0]}"]["metrics"].items()
        if value is None or type(value) in (int, float)
    ]
    summaries = []
    differences = []
    for policy in policies:
        summaries.append(
            {
                "policy": policy,
                "n": len(seeds),
                "metrics": {
                    key: summary([runs[f"{policy}:{s}"]["metrics"][key] for s in seeds])
                    for key in metrics
                },
                "distribution": _group_summaries(runs, policy, seeds),
            }
        )
        if policy != baseline:
            paired = {}
            for metric in metrics:
                deltas = []
                for seed in seeds:
                    a = runs[f"{policy}:{seed}"]["metrics"][metric]
                    b = runs[f"{baseline}:{seed}"]["metrics"][metric]
                    deltas.append(None if a is None or b is None else a - b)
                paired[metric] = summary(deltas)
            differences.append(
                {
                    "policy": policy,
                    "baseline": baseline,
                    "metrics": paired,
                    "distribution": _group_summaries(runs, policy, seeds, baseline),
                }
            )
    return {
        "model_version": "isobar-reference-v1",
        "status": "completed",
        "paired": True,
        "view": "truth",
        "view_label": "Post-run research comparison (includes hidden state)",
        "baseline": baseline,
        "seeds": seeds,
        "summaries": summaries,
        "differences": differences,
        "runs": list(runs.values()),
        "config": config,
        "config_digest": identity,
        "note": "95% normal-approximation Monte Carlo intervals conditional on this model. "
        "Small samples may give poor coverage. Null denominators are excluded and n is shown. "
        "Terminal runs are retained. Structural uncertainty is not included. No global ranking.",
    }


def _group_summaries(
    runs: dict[str, dict], policy: str, seeds: list[int], baseline: str | None = None
) -> list[dict]:
    groups = []
    for index, group in enumerate(runs[f"{policy}:{seeds[0]}"]["metrics"]["distribution"]):
        stats = {}
        for metric in sorted(group.keys() - {"actor_id", "name", "population"}):
            values = []
            for seed in seeds:
                value = runs[f"{policy}:{seed}"]["metrics"]["distribution"][index][metric]
                if baseline is not None:
                    other = runs[f"{baseline}:{seed}"]["metrics"]["distribution"][index][metric]
                    value = None if value is None or other is None else value - other
                values.append(value)
            stats[metric] = summary(values)
        groups.append(
            {**{key: group[key] for key in ("actor_id", "name", "population")}, "metrics": stats}
        )
    return groups


def _run(scenario: Scenario, policy: str, seed: int) -> dict:
    raw = scenario.model_dump(mode="json")
    raw["seed"] = seed
    raw["policy"]["family"] = policy
    run = simulate(Scenario.model_validate(raw))
    return {
        "policy": policy,
        "seed": seed,
        "status": run["status"],
        "metrics": run["metrics"],
        "digests": run["digests"],
    }
