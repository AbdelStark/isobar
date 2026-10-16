"""Atomic, identity-checked run artifacts. Checksums are not third-party proofs."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import tempfile
from importlib.metadata import version
from pathlib import Path
from typing import Any

from isobar import __version__
from isobar.engine import MAX_BRANCH_DEPTH, simulate
from isobar.engine import branch as branch_run
from isobar.models import Scenario

MAX_ARTIFACT_BYTES = 64 * 1024 * 1024


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def environment() -> dict:
    source = Path(__file__).parent
    code = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(source.glob("*.py"))}
    return {
        "package": __version__,
        "python": platform.python_version(),
        "pydantic": version("pydantic"),
        "platform": platform.system(),
        "code_digest": digest(code),
        "source_digests": code,
    }


def atomic_json(path: Path, data: Any, *, overwrite: bool = True) -> None:
    payload = canonical(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.write(b"\n")
            stream.flush()
            os.fsync(stream.fileno())
        if overwrite:
            os.replace(temporary, path)
        else:
            # Link the complete file atomically; an existence precheck races other writers.
            os.link(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def read_json(path: Path) -> Any:
    if path.stat().st_size > MAX_ARTIFACT_BYTES:
        raise ValueError("Artifact exceeds the 64 MiB local limit.")

    def reject_constant(value: str) -> None:
        raise ValueError(f"Non-finite JSON value: {value}")

    return json.loads(path.read_text(), parse_constant=reject_constant)


def package_run(result: dict, *, public: bool = False) -> dict:
    scenario = Scenario.model_validate(result["scenario"])
    if public and scenario.classification != "public":
        raise PermissionError("Private scenarios cannot be exported as public artifacts.")
    return {
        "artifact_version": 1,
        "kind": "isobar-run",
        "classification": scenario.classification,
        "contains_post_run_truth": True,
        "environment": environment(),
        "result_digest": digest(result),
        "result": result,
        "limitations": "Synthetic model output. Identity checks are not external validation.",
    }


def verify_bundle(bundle: dict, *, replay: bool = True, require_environment: bool = False) -> dict:
    if (
        not isinstance(bundle, dict)
        or type(bundle.get("artifact_version")) is not int
        or bundle.get("artifact_version") != 1
    ):
        raise ValueError("Unsupported artifact version.")
    if bundle.get("kind") != "isobar-run" or not isinstance(bundle.get("result"), dict):
        raise ValueError("Expected an Isobar run bundle.")
    result = bundle["result"]
    if digest(result) != bundle.get("result_digest"):
        raise ValueError("Run checksum mismatch; the artifact is corrupt or was modified.")
    scenario = Scenario.model_validate(result.get("scenario"))
    if bundle.get("classification") != scenario.classification:
        raise ValueError("Artifact classification disagrees with its scenario.")
    if require_environment:
        current = environment()
        previous = bundle.get("environment", {})
        if not isinstance(previous, dict):
            raise ValueError("Checkpoint environment must be an object.")
        for field in ("package", "python", "pydantic", "code_digest"):
            if previous.get(field) != current[field]:
                raise ValueError(f"Checkpoint {field} mismatch; create a new run instead.")
    if replay:
        rebuilt = _reconstruct(scenario, result)
        if digest(rebuilt) != digest(result):
            raise ValueError(
                "Offline replay differs from the full run, including identity or lineage."
            )
    return result


def _reconstruct(scenario: Scenario, record: dict, depth: int = 0) -> dict:
    if depth > MAX_BRANCH_DEPTH:
        raise ValueError(f"Branch lineage exceeds the {MAX_BRANCH_DEPTH}-level verification limit.")
    lineage = record.get("branch")
    if lineage is not None:
        if not isinstance(lineage, dict):
            raise ValueError("Invalid branch lineage.")
        required = {
            "parent_id",
            "tick",
            "actor_id",
            "action",
            "parent_input_actions",
            "parent_branch",
            "parent_completed_ticks",
        }
        if set(lineage) != required:
            raise ValueError("Incomplete or unknown branch lineage fields.")
        parent = _reconstruct(
            scenario,
            {
                "branch": lineage["parent_branch"],
                "input_actions": lineage["parent_input_actions"],
                "completed_ticks": lineage["parent_completed_ticks"],
            },
            depth + 1,
        )
        if parent["id"] != lineage["parent_id"]:
            raise ValueError("Branch parent identity mismatch.")
        return branch_run(parent, lineage["tick"], lineage["actor_id"], lineage["action"])
    completed = record.get("completed_ticks")
    if type(completed) is not int or not 0 <= completed <= scenario.horizon:
        raise ValueError("Invalid completed tick count.")
    stop = completed if completed < scenario.horizon else None
    return simulate(scenario, actions=record.get("input_actions", {}), stop_at=stop)


def resume_bundle(bundle: dict) -> dict:
    result = verify_bundle(bundle, require_environment=True)
    if result["status"] != "cancelled":
        raise ValueError("Only a cancelled run can be resumed.")
    return simulate(
        Scenario.model_validate(result["scenario"]), actions=result.get("input_actions", {})
    )


def save_run(path: Path, result: dict, *, public: bool = False) -> dict:
    if path.exists():
        raise FileExistsError("Output already exists; choose a new artifact path.")
    bundle = package_run(result, public=public)
    atomic_json(path, bundle, overwrite=False)
    return bundle
