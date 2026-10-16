"""One kernel, both headless experiments and the local workbench."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pydantic import ValidationError

from isobar.artifacts import (
    atomic_json,
    read_json,
    resume_bundle,
    save_run,
    verify_bundle,
)
from isobar.engine import branch, project, simulate
from isobar.experiments import POLICIES, compare
from isobar.models import Scenario
from isobar.scenarios import catalog, get_scenario


def scenario_arg(value: str) -> Scenario:
    path = Path(value)
    return Scenario.model_validate(read_json(path)) if path.is_file() else get_scenario(value)


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Isobar: synthetic, conditional governance simulations."
    )
    commands = p.add_subparsers(dest="command", required=True)
    commands.add_parser("catalog", help="List built-in synthetic scenarios")
    schema = commands.add_parser("schema", help="Print the versioned input JSON Schema")
    schema.add_argument("--output", type=Path)
    validate = commands.add_parser("validate", help="Validate a scenario file or preset ID")
    validate.add_argument("scenario")
    run = commands.add_parser("run", help="Run a scenario into a reproducible bundle")
    run.add_argument("scenario")
    run.add_argument("--output", "-o", type=Path, required=True)
    run.add_argument(
        "--actions", type=Path, help="Recorded human/model action map, never executable code"
    )
    run.add_argument(
        "--stop-at", type=int, help="Cancel after this many ticks, retaining a checkpoint"
    )
    replay = commands.add_parser("replay", help="Verify artifact identity and offline replay")
    replay.add_argument("artifact", type=Path)
    replay.add_argument("--view", default="public", help="public, truth, or an actor ID")
    replay.add_argument("--output", "-o", type=Path)
    resume = commands.add_parser("resume", help="Resume a checked cancelled run")
    resume.add_argument("artifact", type=Path)
    resume.add_argument("--output", "-o", type=Path, required=True)
    branch_p = commands.add_parser("branch", help="Branch a verified run with one actor action")
    branch_p.add_argument("artifact", type=Path)
    branch_p.add_argument("--tick", type=int, required=True)
    branch_p.add_argument("--actor", required=True)
    branch_p.add_argument("--action", required=True, help="JSON action or path to action JSON")
    branch_p.add_argument("--output", "-o", type=Path, required=True)
    comp = commands.add_parser("compare", help="Paired policy comparison over shared seeds")
    comp.add_argument("scenario")
    comp.add_argument("--policies", nargs="+", default=list(POLICIES))
    comp.add_argument("--seeds", nargs="+", type=int, default=list(range(8)))
    comp.add_argument("--output", "-o", type=Path, required=True)
    comp.add_argument("--checkpoint", type=Path)
    comp.add_argument("--stop-after", type=int)
    export = commands.add_parser(
        "export", help="Export a verified run; private inputs cannot be public"
    )
    export.add_argument("artifact", type=Path)
    export.add_argument("--output", "-o", type=Path, required=True)
    export.add_argument("--public", action="store_true")
    web = commands.add_parser("serve", help="Start the loopback-only browser workbench")
    web.add_argument("--port", type=int, default=4318)
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "catalog":
            print(
                json.dumps(
                    [
                        {"id": s["id"], "name": s["name"], "question": s["question"]}
                        for s in catalog()
                    ],
                    indent=2,
                )
            )
        elif args.command == "schema":
            data = Scenario.model_json_schema()
            if args.output:
                if args.output.exists():
                    raise FileExistsError("Output already exists; choose a new path.")
                atomic_json(args.output, data, overwrite=False)
            else:
                print(json.dumps(data, indent=2))
        elif args.command == "validate":
            s = scenario_arg(args.scenario)
            print(json.dumps({"valid": True, "id": s.id, "classification": s.classification}))
        elif args.command == "run":
            s = scenario_arg(args.scenario)
            actions = read_json(args.actions) if args.actions else None
            result = simulate(s, actions=actions, stop_at=args.stop_at)
            save_run(args.output, result)
            print(
                json.dumps(
                    {"id": result["id"], "status": result["status"], "output": str(args.output)}
                )
            )
        elif args.command == "replay":
            result = verify_bundle(read_json(args.artifact))
            filtered = project(result, args.view)
            if args.output:
                if args.output.exists():
                    raise FileExistsError("Output already exists; choose a new path.")
                atomic_json(args.output, filtered, overwrite=False)
            print(json.dumps({"verified": True, "id": result["id"], "view": args.view}))
        elif args.command == "resume":
            result = resume_bundle(read_json(args.artifact))
            save_run(args.output, result)
            print(json.dumps({"status": result["status"], "id": result["id"]}))
        elif args.command == "branch":
            result = verify_bundle(read_json(args.artifact))
            action = (
                json.loads(args.action)
                if args.action.lstrip().startswith("{")
                else read_json(Path(args.action))
            )
            child = branch(result, args.tick, args.actor, action)
            save_run(args.output, child)
            print(json.dumps({"id": child["id"], "parent_id": result["id"]}))
        elif args.command == "compare":
            if args.checkpoint and args.output.resolve() == args.checkpoint.resolve():
                raise ValueError("Comparison output and checkpoint must use different paths.")
            if args.output.exists():
                raise FileExistsError("Output already exists; choose a new path.")
            result = compare(
                scenario_arg(args.scenario),
                args.policies,
                args.seeds,
                checkpoint=args.checkpoint,
                stop_after=args.stop_after,
            )
            atomic_json(args.output, result, overwrite=False)
            print(json.dumps({"status": result["status"], "output": str(args.output)}))
        elif args.command == "export":
            result = verify_bundle(read_json(args.artifact))
            save_run(args.output, result, public=args.public)
            print(
                json.dumps(
                    {"exported": True, "classification": result["scenario"]["classification"]}
                )
            )
        elif args.command == "serve":
            from isobar.server import serve

            serve(args.port)
        return 0
    except (ValueError, TypeError, KeyError, OSError, ValidationError) as exc:
        print(f"isobar: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
