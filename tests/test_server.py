import json
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from isobar.artifacts import verify_bundle
from isobar.scenarios import get_scenario
from isobar.server import LocalServer


@pytest.fixture
def local_server(tmp_path):
    static = tmp_path / "assets"
    static.mkdir()
    (static / "index.html").write_text("<!doctype html><title>Isobar</title>")
    (tmp_path / "secret.txt").write_text("not an asset")
    server = LocalServer(0, static)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)


def request(base, path, body=None, headers=None):
    req = Request(
        base + path,
        data=None if body is None else json.dumps(body).encode(),
        headers={"Content-Type": "application/json", **(headers or {})},
    )
    try:
        with urlopen(req, timeout=15) as response:
            return response.status, response.read(), response.headers
    except HTTPError as exc:
        return exc.code, exc.read(), exc.headers


def test_catalog_and_workbench_assets(local_server):
    status, body, headers = request(local_server, "/api/catalog")
    assert status == 200
    assert len(json.loads(body)["scenarios"]) == 6
    assert "frame-ancestors 'none'" in headers["Content-Security-Policy"]
    assert request(local_server, "/")[0] == 200
    assert request(local_server, "/%2e%2e/secret.txt")[0] == 404
    assert request(local_server, "/api/unknown")[0] == 404


def test_cross_origin_and_dns_rebinding_blocked(local_server):
    assert (
        request(local_server, "/api/catalog", headers={"Origin": "https://evil.example"})[0] == 403
    )
    assert request(local_server, "/api/catalog", headers={"Host": "evil.example"})[0] == 403
    assert request(local_server, "/api/catalog", headers={"Sec-Fetch-Site": "cross-site"})[0] == 403


def test_run_validation_and_private_export(local_server):
    scenario = get_scenario("S2").model_dump(mode="json")
    scenario["horizon"] = 4
    status, body, _ = request(local_server, "/api/run", {"scenario": scenario})
    assert status == 200, body
    result = json.loads(body)
    assert result["completed_ticks"] == 4
    scenario["verification"]["coverage"] = -1
    status, body, _ = request(local_server, "/api/run", {"scenario": scenario})
    assert status == 422
    assert "coverage" in body.decode()
    scenario["verification"]["coverage"] = 0.5
    scenario["classification"] = "private"
    assert request(local_server, "/api/export", {"scenario": scenario, "public": True})[0] == 403


def test_comparison_limits(local_server):
    scenario = get_scenario("S2").model_dump(mode="json")
    status, body, _ = request(
        local_server,
        "/api/compare",
        {"scenario": scenario, "seeds": list(range(21)), "view": "truth"},
    )
    assert status == 400
    assert b"20 seeds" in body


def test_branch_chain_retains_provenance_across_views_and_export(local_server):
    scenario = get_scenario("S2").model_dump(mode="json")
    scenario["horizon"] = 4
    intervention = {
        "tick": 1,
        "actor_id": "aurora",
        "action": {"train": 0.0, "safety": 0.5, "service": 0.5, "idle": 0.0},
    }
    status, body, _ = request(
        local_server, "/api/branch", {"scenario": scenario, **intervention, "view": "truth"}
    )
    assert status == 200, body
    child = json.loads(body)
    payload = {"scenario": scenario, "interventions": [intervention]}
    status, projected, _ = request(local_server, "/api/run", {**payload, "view": "public"})
    assert status == 200
    assert json.loads(projected)["branch"] is not None
    status, exported, _ = request(local_server, "/api/export", {**payload, "public": True})
    assert status == 200, exported
    bundle = json.loads(exported)
    assert bundle["result"]["id"] == child["id"]
    verify_bundle(bundle)
