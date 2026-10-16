"""Generate the fixed S2 monitoring study; see docs/studies/s2-monitoring/protocol.md."""

from __future__ import annotations

import argparse
import hashlib
import math
import subprocess
from collections import Counter
from copy import deepcopy
from pathlib import Path

from isobar.artifacts import atomic_json, environment, package_run, read_json, verify_bundle
from isobar.engine import simulate
from isobar.experiments import compare
from isobar.models import Scenario
from isobar.scenarios import get_scenario

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs/studies/s2-monitoring/protocol.md"
POLICIES = ["unrestricted", "reciprocal"]
SEEDS = list(range(20))
CONDITIONS = (
    ("f01-r00", 0.01, 0.0),
    ("f01-r30", 0.01, 0.3),
    ("f10-r00", 0.10, 0.0),
    ("f10-r30", 0.10, 0.3),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_summary(stats: dict, values: list[float | None]) -> None:
    finite = [value for value in values if value is not None]
    assert stats["n"] == len(finite), "Incorrect valid sample count"
    if finite:
        assert math.isclose(stats["mean"], math.fsum(finite) / len(finite), abs_tol=1e-12)
    else:
        assert all(stats[key] is None for key in ("mean", "sd", "ci_low", "ci_high"))


def verify_report(report: dict, scenario: Scenario, output: Path, condition: str) -> None:
    assert report["status"] == "completed" and report["paired"] and report["view"] == "truth"
    assert report["environment"] == environment()
    assert report["baseline"] == POLICIES[0] and report["seeds"] == SEEDS
    assert report["config"] == {
        "scenario": scenario.model_dump(mode="json"),
        "policies": POLICIES,
        "seeds": SEEDS,
    }
    rows = {(row["policy"], row["seed"]): row for row in report["runs"]}
    assert len(rows) == len(report["runs"]) == 40
    assert set(rows) == {(policy, seed) for policy in POLICIES for seed in SEEDS}
    for (policy, seed), row in rows.items():
        raw = deepcopy(report["config"]["scenario"])
        raw["policy"]["family"], raw["seed"] = policy, seed
        run = simulate(Scenario.model_validate(raw))
        assert run["status"] == row["status"] in {"completed", "terminal"}
        assert run["metrics"] == row["metrics"] and run["digests"] == row["digests"]
        bundle = package_run(run)
        verify_bundle(bundle, require_environment=True)
        if seed == 0:
            atomic_json(output / f"{condition}-{policy}-seed0.json", bundle, overwrite=False)

    for stats in [*report["summaries"], *report["differences"]]:
        for group in [None, *range(len(scenario.actors))]:

            def metrics(policy: str, seed: int, index: int | None = group) -> dict:
                data = rows[policy, seed]["metrics"]
                return data if index is None else data["distribution"][index]

            selected = stats if group is None else stats["distribution"][group]
            if group is not None:
                expected = metrics(stats["policy"], SEEDS[0])
                assert all(
                    selected[key] == expected[key] for key in ("actor_id", "name", "population")
                )
            for metric, summary in selected["metrics"].items():
                values = []
                for seed in SEEDS:
                    value = metrics(stats["policy"], seed)[metric]
                    if "baseline" in stats:
                        baseline = metrics(stats["baseline"], seed)[metric]
                        value = None if value is None or baseline is None else value - baseline
                    values.append(value)
                check_summary(summary, values)


def cell(stats: dict) -> str:
    if stats["mean"] is None:
        return "undefined; n=0"
    interval = (
        f"[{stats['ci_low']:.6g}, {stats['ci_high']:.6g}]"
        if stats["ci_low"] is not None
        else "interval undefined"
    )
    return f"{stats['mean']:.6g} {interval}; n={stats['n']}"


def metric_table(rows: list[dict]) -> list[str]:
    lines = ["| Metric | Unrestricted | Reciprocal | Paired difference |", "|---|---:|---:|---:|"]
    for metric in rows[0]["metrics"]:
        lines.append(
            f"| `{metric}` | " + " | ".join(cell(row["metrics"][metric]) for row in rows) + " |"
        )
    return lines


def render(reports: dict[str, dict]) -> str:
    lines = [
        "# S2 monitoring sensitivity: generated tables",
        "",
        "Generated from the adjacent JSON reports by `scripts/sensitivity_study.py`.",
        "Post-run truth from synthetic fixtures; no policy ranking or empirical claim.",
        "",
        "Cells show mean [95% normal-approximation Monte Carlo interval]; n=valid runs",
        "or pairs. Differences are reciprocal minus unrestricted. Undefined denominators",
        "stay undefined. Intervals condition on each model configuration, exclude structural",
        "uncertainty and can have poor coverage at 20 seeds. All terminal runs are retained.",
        "Ratios are averaged over runs, not pooled; privacy is exposure per audit record.",
        "",
        "## Sensitivity across conditions",
        "",
        "Each column is a separate paired policy contrast; these conditions are not pooled.",
        "",
        "| Metric | " + " | ".join(reports) + " |",
        "|---|" + "---:|" * len(reports),
    ]
    for metric in next(iter(reports.values()))["differences"][0]["metrics"]:
        lines.append(
            f"| `{metric}` | "
            + " | ".join(
                cell(report["differences"][0]["metrics"][metric]) for report in reports.values()
            )
            + " |"
        )
    for condition, report in reports.items():
        config = report["config"]["scenario"]
        verification = config["verification"]
        lines += [
            "",
            f"## {condition}",
            "",
            f"[Saved comparison]({condition}.json): false-positive rate "
            f"{verification['false_positive_rate']}, shared-root failure "
            f"{verification['shared_root_failure']}; horizon {config['horizon']}.",
            "",
        ]
        for policy in POLICIES:
            counts = Counter(row["status"] for row in report["runs"] if row["policy"] == policy)
            lines.append(
                f"- {policy}: {counts['completed']} completed, {counts['terminal']} terminal; "
                f"[seed-0 replay bundle]({condition}-{policy}-seed0.json)."
            )
        rows = [*report["summaries"], report["differences"][0]]
        lines += ["", *metric_table(rows)]
        for index, group in enumerate(rows[0]["distribution"]):
            lines += [
                "",
                f"### {group['name']} ({group['actor_id']})",
                "",
                f"Synthetic population weight: {group['population']}.",
                "",
                *metric_table([row["distribution"][index] for row in rows]),
            ]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "output", type=Path, help="Fresh output directory; existing paths are refused"
    )
    args = parser.parse_args()
    if not __debug__:
        parser.error("Run without -O: the study requires its assertion-based checks.")
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    patch = subprocess.check_output(
        ["git", "diff", "HEAD", "--", "src/isobar", "uv.lock"],
        cwd=ROOT,
        text=True,
    )
    untracked = subprocess.check_output(
        ["git", "ls-files", "--others", "--exclude-standard", "src/isobar"],
        cwd=ROOT,
        text=True,
    )
    if patch or untracked:
        parser.error(
            "Use an unchanged, committed kernel and dependency lock for this reference study."
        )
    try:
        args.output.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        parser.error("Output already exists; choose a fresh directory. No files were changed.")
    inputs = {
        "checkout_revision": revision,
        "generator_sha256": sha256(Path(__file__)),
        "protocol_sha256": sha256(PROTOCOL),
        "uv_lock_sha256": sha256(ROOT / "uv.lock"),
        "environment": environment(),
    }
    reports = {}
    for condition, false_positive, shared_root in CONDITIONS:
        raw = get_scenario("s2").model_dump(mode="json")
        raw["verification"].update(
            false_positive_rate=false_positive, shared_root_failure=shared_root
        )
        scenario = Scenario.model_validate(raw)
        path = args.output / f"{condition}.json"
        atomic_json(path, compare(scenario, POLICIES, SEEDS), overwrite=False)
        reports[condition] = read_json(path)
        verify_report(reports[condition], scenario, args.output, condition)
        print(f"{condition}: all 40 runs regenerated and replay-verified", flush=True)
    with (args.output / "tables.md").open("x") as stream:
        stream.write(render(reports))
    assert inputs["environment"] == environment(), "Source/runtime changed during study"
    assert inputs["generator_sha256"] == sha256(Path(__file__))
    assert inputs["protocol_sha256"] == sha256(PROTOCOL)
    assert inputs["uv_lock_sha256"] == sha256(ROOT / "uv.lock")
    atomic_json(
        args.output / "manifest.json",
        {
            **inputs,
            "verified_runs": 160,
            "retained_full_bundles": 8,
            "files": {path.name: sha256(path) for path in sorted(args.output.iterdir())},
        },
        overwrite=False,
    )
    print(
        f"PASS: 160 replay-verified runs, eight retained bundles; {args.output / 'manifest.json'}"
    )


if __name__ == "__main__":
    main()
