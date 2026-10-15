"""Loopback-only workbench server. Not a public deployment server."""

from __future__ import annotations

import json
import mimetypes
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

from pydantic import ValidationError

from isobar.artifacts import canonical, package_run, verify_bundle
from isobar.engine import MAX_BRANCH_DEPTH, branch, project, simulate
from isobar.experiments import POLICIES, STRATEGIES, compare
from isobar.models import Scenario
from isobar.scenarios import catalog

MAX_BODY = 2 * 1024 * 1024


def reconstruct_request(scenario: Scenario, body: dict) -> dict:
    interventions = body.get("interventions", [])
    if not isinstance(interventions, list) or len(interventions) > MAX_BRANCH_DEPTH:
        raise ValueError(f"Use at most {MAX_BRANCH_DEPTH} recorded interventions.")
    if interventions and body.get("stop_at") is not None:
        raise ValueError("Partial runs cannot include a completed branch chain.")
    result = simulate(scenario, actions=body.get("actions"), stop_at=body.get("stop_at"))
    for item in interventions:
        if not isinstance(item, dict) or set(item) != {"tick", "actor_id", "action"}:
            raise ValueError("Each intervention needs exactly tick, actor_id and action.")
        result = branch(result, item["tick"], item["actor_id"], item["action"])
    return result


def dispatch(path: str, body: dict) -> dict:
    if path == "/api/project":
        bundle = body.get("bundle")
        if bundle is None:
            bundle = package_run(body["result"])
        return project(verify_bundle(bundle), body.get("view", "public"))
    scenario = Scenario.model_validate(body.get("scenario"))
    actions = body.get("actions")
    if actions is not None and (not isinstance(actions, dict) or len(actions) > 1920):
        raise ValueError("actions must be an object with at most 1920 tick:actor entries.")
    view = body.get("view", "public")
    if path == "/api/run":
        return project(reconstruct_request(scenario, body), view)
    if path == "/api/branch":
        if len(body.get("interventions", [])) >= MAX_BRANCH_DEPTH:
            raise ValueError("Branch chain limit reached. Start a new experiment.")
        original = reconstruct_request(scenario, body)
        return project(branch(original, body["tick"], body["actor_id"], body["action"]), view)
    if path == "/api/compare":
        if view != "truth":
            raise ValueError("Policy comparisons require explicit post-run truth view.")
        seeds = body.get("seeds", list(range(8)))
        if not isinstance(seeds, list) or len(seeds) > 20 or scenario.horizon > 120:
            raise ValueError("Browser comparisons allow at most 20 seeds and 120 ticks.")
        return compare(scenario, body.get("policies", list(POLICIES)), seeds)
    if path == "/api/export":
        public = body.get("public", True)
        if type(public) is not bool:
            raise ValueError("public must be a boolean.")
        return package_run(reconstruct_request(scenario, body), public=public)
    raise ValueError("Unknown API operation.")


class LocalServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, port: int, static: Path | None = None):
        packaged = Path(__file__).parent / "static"
        development = Path(__file__).resolve().parents[2] / "web" / "dist"
        self.static = (static or (packaged if packaged.exists() else development)).resolve()
        super().__init__(("127.0.0.1", port), Handler)


class Handler(BaseHTTPRequestHandler):
    server: LocalServer
    server_version = "IsobarLocal/1"

    def setup(self) -> None:
        super().setup()
        self.connection.settimeout(15)

    def log_message(self, format: str, *args: Any) -> None:
        # Local scenario names and payloads must not become HTTP logs.
        return

    def _allowed(self) -> bool:
        port = self.server.server_port
        hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}
        if self.headers.get("Host") not in hosts:
            self._json({"error": "Only the local Isobar hostname is accepted."}, 403)
            return False
        origins = {f"http://{h}" for h in hosts} | {
            "http://127.0.0.1:5173",
            "http://localhost:5173",
        }
        origin = self.headers.get("Origin")
        if origin and origin not in origins:
            self._json({"error": "Cross-origin requests are not allowed."}, 403)
            return False
        if self.headers.get("Sec-Fetch-Site") == "cross-site":
            self._json({"error": "Cross-site requests are not allowed."}, 403)
            return False
        return True

    def _headers(self, status: int, kind: str, length: int) -> None:
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(length))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; connect-src 'self'; font-src 'self'; "
            "object-src 'none'; base-uri 'none'; frame-ancestors 'none'",
        )
        self.end_headers()

    def _json(self, value: Any, status: int = 200) -> None:
        payload = canonical(value)
        self._headers(status, "application/json; charset=utf-8", len(payload))
        self.wfile.write(payload)

    def do_GET(self) -> None:
        if not self._allowed():
            return
        path = urlsplit(self.path).path
        if path == "/api/catalog":
            self._json(
                {
                    "scenarios": catalog(),
                    "policies": POLICIES,
                    "strategies": STRATEGIES,
                    "model_version": "isobar-reference-v1",
                }
            )
            return
        if path == "/api/schema":
            self._json(Scenario.model_json_schema())
            return
        if path == "/api/health":
            self._json({"status": "ok", "mode": "local-only"})
            return
        if path.startswith("/api/"):
            self._json({"error": "Unknown API endpoint."}, 404)
            return
        relative = unquote(path).lstrip("/") or "index.html"
        target = (self.server.static / relative).resolve()
        if not target.is_relative_to(self.server.static) or not target.is_file():
            self._json(
                {"error": "Asset not found. Build the workbench with npm run build in web/."}, 404
            )
            return
        payload = target.read_bytes()
        kind = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        self._headers(200, kind, len(payload))
        self.wfile.write(payload)

    def do_POST(self) -> None:
        if not self._allowed():
            return
        if self.headers.get_content_type() != "application/json":
            self._json({"error": "Send an application/json request body."}, 415)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_BODY:
                self._json({"error": "JSON body must be between 1 byte and 2 MiB."}, 413)
                return

            def invalid_constant(value: str) -> None:
                raise ValueError(f"Non-finite value {value} is not accepted.")

            body = json.loads(self.rfile.read(length), parse_constant=invalid_constant)
            if not isinstance(body, dict):
                raise ValueError("The request body must be a JSON object.")
            result = dispatch(urlsplit(self.path).path, body)
            self._json(result)
        except ValidationError as exc:
            self._json(
                {
                    "error": "Scenario validation failed. Correct the listed fields.",
                    "details": [
                        {"path": ".".join(str(v) for v in e["loc"]), "message": e["msg"]}
                        for e in exc.errors()
                    ],
                },
                422,
            )
        except PermissionError as exc:
            self._json({"error": str(exc)}, 403)
        except (ValueError, TypeError, KeyError, UnicodeError) as exc:
            self._json({"error": str(exc)}, 400)
        except Exception:
            self._json(
                {"error": "The simulation failed. Check inputs or run the CLI for diagnostics."},
                500,
            )

    def do_OPTIONS(self) -> None:
        self._json({"error": "Cross-origin API access is disabled."}, HTTPStatus.FORBIDDEN)


def serve(port: int = 4318) -> None:
    with LocalServer(port) as server:
        print(f"Isobar: http://127.0.0.1:{server.server_port} (local-only)", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
