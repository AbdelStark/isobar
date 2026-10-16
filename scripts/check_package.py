"""Build from source, install a wheel outside the checkout, and exercise its public interfaces."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile
from email.parser import BytesParser
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="isobar-package-") as directory:
        work = Path(directory)
        env = {k: v for k, v in os.environ.items() if k not in {"PYTHONPATH", "PYTHONHOME"}}

        def command(*args: str | Path, cwd: Path = work) -> str:
            result = subprocess.run(
                list(map(str, args)), cwd=cwd, env=env, capture_output=True, text=True, timeout=120
            )
            if result.returncode:
                raise RuntimeError(f"{args[0]} failed:\n{result.stdout}\n{result.stderr}")
            return result.stdout

        command("uv", "build", "--out-dir", work / "dist", cwd=ROOT)
        wheels = list((work / "dist").glob("*.whl"))
        assert len(wheels) == 1
        with zipfile.ZipFile(wheels[0]) as wheel:
            metadata_path = next(
                name for name in wheel.namelist() if name.endswith(".dist-info/METADATA")
            )
            metadata = BytesParser().parsebytes(wheel.read(metadata_path))
            assert metadata["License-Expression"] == "MIT"
            assert metadata["License-File"] == "LICENSE"
            license_path = metadata_path.removesuffix("METADATA") + "licenses/LICENSE"
            assert wheel.read(license_path) == (ROOT / "LICENSE").read_bytes()
        command(
            "uv",
            "export",
            "--locked",
            "--no-dev",
            "--no-emit-project",
            "--output-file",
            work / "runtime.txt",
            cwd=ROOT,
        )
        command("uv", "venv", "--python", sys.executable, work / "venv")
        python = work / "venv" / "bin" / "python"
        executable = work / "venv" / "bin" / "isobar"
        command(
            "uv",
            "pip",
            "install",
            "--python",
            python,
            "--require-hashes",
            "-r",
            work / "runtime.txt",
        )
        command("uv", "pip", "install", "--python", python, "--no-deps", wheels[0])
        module = Path(command(python, "-I", "-c", "import isobar; print(isobar.__file__)").strip())
        assert module.is_relative_to(work / "venv"), module
        assert (module.parent / "py.typed").is_file()

        def cli(*args: str) -> dict | list:
            return json.loads(command(executable, *args))

        assert len(cli("catalog")) == 7
        assert cli("validate", "s2")["valid"]
        assert cli("schema")["title"] == "Scenario"
        assert cli("run", "s2", "--stop-at", "3", "-o", "partial.json")["status"] == "cancelled"
        assert cli("resume", "partial.json", "-o", "complete.json")["status"] == "completed"
        assert cli("replay", "complete.json", "--view", "aurora")["verified"]
        cli(
            "branch",
            "complete.json",
            "--tick",
            "1",
            "--actor",
            "aurora",
            "--action",
            '{"train":0,"safety":0.5,"service":0.5,"idle":0}',
            "-o",
            "branch.json",
        )
        assert cli("export", "branch.json", "--public", "-o", "export.json")["exported"]
        assert cli("replay", "export.json")["verified"]
        comparison = ["compare", "s2", "--seeds", "1", "2", "--checkpoint", "batch.json"]
        assert (
            cli(*comparison, "--stop-after", "1", "-o", "batch-partial.json")["status"]
            == "cancelled"
        )
        assert cli(*comparison, "-o", "comparison.json")["status"] == "completed"
        original = (work / "complete.json").read_bytes()
        refused = subprocess.run(
            [str(executable), "run", "s2", "-o", "complete.json"],
            cwd=work,
            env=env,
            capture_output=True,
            timeout=30,
        )
        assert refused.returncode == 2 and (work / "complete.json").read_bytes() == original

        server_code = (
            "from isobar.server import LocalServer\n"
            "with LocalServer(0) as server:\n"
            " print(f'http://127.0.0.1:{server.server_port}', flush=True)\n"
            " server.serve_forever()\n"
        )
        with subprocess.Popen(
            [str(python), "-I", "-c", server_code],
            cwd=work,
            env=env,
            stdout=subprocess.PIPE,
            text=True,
        ) as server:
            try:
                assert server.stdout is not None
                base = server.stdout.readline().strip()
                assert base.startswith("http://127.0.0.1:"), base

                def request(path: str, body: dict | None = None) -> bytes:
                    req = Request(
                        base + path,
                        data=json.dumps(body).encode() if body is not None else None,
                        headers={"Content-Type": "application/json"},
                    )
                    with urlopen(req, timeout=15) as response:
                        assert response.status == 200
                        return response.read()

                html = request("/").decode()
                assets = re.findall(r'(?:src|href)="(/[^\"]+)"', html)
                assert any(asset.endswith(".js") for asset in assets)
                assert any(asset.endswith(".css") for asset in assets)
                for asset in assets:
                    assert request(asset)
                assert b"Mike Bostock" in request("/third-party.txt")
                scenario = next(
                    item
                    for item in json.loads(request("/api/catalog"))["scenarios"]
                    if item["id"] == "world"
                )
                run = json.loads(request("/api/run", {"scenario": scenario, "view": "public"}))
                assert run["completed_ticks"] > 0
                assert "hidden_capacity" not in json.dumps(run)
                assert len(run["frames"][0]["actors"]) == 8
                decision = json.loads(
                    request(
                        "/api/decision",
                        {
                            "scenario": scenario,
                            "actor_id": "usa",
                            "tick": 0,
                            "view": "usa",
                        },
                    )
                )
                assert len(decision["alternatives"]) == 6
                assert decision["selected_action"]["train"] >= 0
                bundle = request("/api/export", {"scenario": scenario, "public": True})
                (work / "browser-export.json").write_bytes(bundle)
                assert cli("replay", "browser-export.json")["verified"]
            finally:
                server.terminate()
                server.wait(timeout=10)
        print(
            "Package check passed: isolated wheel, CLI lifecycle, bundled assets, "
            "world run/decision/export/replay."
        )


if __name__ == "__main__":
    main()
