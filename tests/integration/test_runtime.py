import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest


@pytest.mark.usefixtures("_migrated_database")
def test_uvicorn_serves_docs_and_health_with_real_dependencies(tmp_path: Path) -> None:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]

    with (
        (tmp_path / "uvicorn.log").open("w+") as output,
        subprocess.Popen(  # noqa: S603
            [
                sys.executable,
                "-m",
                "uvicorn",
                "trafficmaster.web:create_fastapi_app",
                "--factory",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
            ],
            stdout=output,
            stderr=subprocess.STDOUT,
        ) as process,
    ):
        try:
            deadline = time.monotonic() + 20
            with httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=2, trust_env=False) as client:
                while True:
                    assert process.poll() is None, "Uvicorn exited before startup"
                    try:
                        live = client.get("/healthcheck/live")
                    except httpx.TransportError:
                        if time.monotonic() >= deadline:
                            raise
                        time.sleep(0.1)
                        continue
                    assert live.status_code == 200
                    break
                ready = client.get("/healthcheck/ready")
                assert ready.status_code == 200, ready.text
                assert ready.json() == {"status": "ready", "database": "up", "cache": "up"}
                assert client.get("/docs").status_code == 200
                assert "/v1/review/queue" in client.get("/openapi.json").json()["paths"]
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
