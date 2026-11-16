"""Bounded Locust experiment on disposable dependencies; keep the API PID across recovery."""

import asyncio
import concurrent.futures
import importlib.metadata
import json
import os
import platform
import socket
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

import asyncpg
import httpx
import psutil
from alembic import command
from alembic.config import Config
from loadtests.metrics import phase_metrics
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

from tests.integration.conftest import _apply_env
from tests.integration.lab3.test_acceptance import card_body, config_body

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/lab5/evidence"
MAX_USERS = 200


async def connection() -> asyncpg.Connection:
    return await asyncpg.connect(
        host=os.environ["POSTGRES_HOST"],
        port=int(os.environ["POSTGRES_PORT"]),
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        database=os.environ["POSTGRES_DB"],
        server_settings={"application_name": "lab5-monitor"},
    )


async def clone_accounts(seed: dict[str, object]) -> list[dict[str, object]]:
    conn = await connection()
    try:
        templates = {}
        for table, key in [("users", "user"), ("deck_configs", "config"), ("decks", "deck")]:
            # Identifiers come only from the fixed table list above, never from HTTP data.
            templates[table] = dict(
                await conn.fetchrow(f'SELECT * FROM "{table}" WHERE id=$1', seed[key])  # noqa: S608
            )
        cards = [dict(row) for row in await conn.fetch("SELECT * FROM cards WHERE deck_id=$1", seed["deck"])]
        batches = {table: [] for table in ["users", "deck_configs", "decks", "cards"]}
        result = []
        for index in range(MAX_USERS):
            user, config, deck = uuid4(), uuid4(), uuid4()
            email = f"load_{index}_{uuid4().hex[:6]}@example.com"
            record = {**templates["users"], "id": user, "email": email, "name": f"LoadUser-{index}"}
            batches["users"].append(record)
            batches["deck_configs"].append({**templates["deck_configs"], "id": config, "owner_id": user})
            batches["decks"].append({**templates["decks"], "id": deck, "deck_config_id": config, "owner_id": user})
            ids = []
            for original in cards:
                card_id = uuid4()
                options = json.loads(original["answer_options"])
                for option in options:
                    option["id"] = str(uuid4())
                batches["cards"].append(
                    {**original, "id": card_id, "deck_id": deck, "answer_options": json.dumps(options)}
                )
                ids.append(str(card_id))
            result.append({"user": str(user), "email": email, "deck": str(deck), "cards": ids})
        for table, records in batches.items():
            columns = list(records[0])
            names = ",".join(f'"{name}"' for name in columns)
            placeholders = ",".join(f"${index + 1}" for index in range(len(columns)))
            await conn.executemany(
                f'INSERT INTO "{table}" ({names}) VALUES ({placeholders})',  # noqa: S608 - trusted schema names; bound values
                [tuple(row[name] for name in columns) for row in records],
            )
        return result
    finally:
        await conn.close()


async def database_sample() -> dict[str, object]:
    conn = await connection()
    try:
        row = await conn.fetchrow("""SELECT count(*) AS connections,
          count(*) FILTER (WHERE state='active') AS active,
          count(*) FILTER (WHERE wait_event_type='Lock') AS lock_waits,
          count(*) FILTER (WHERE state='idle in transaction') AS idle_transactions
          FROM pg_stat_activity WHERE datname=current_database() AND pid<>pg_backend_pid()""")
        return dict(row)
    finally:
        await conn.close()


def prepare(url: str) -> list[dict[str, object]]:
    with httpx.Client(base_url=url, trust_env=False, timeout=20) as api:
        email = f"load_seed_{uuid4().hex[:8]}@example.com"
        response = api.post(
            "/v1/auth/signup", json={"email": email, "name": "Load-Seed", "password": "LearningSecure123"}
        )
        assert response.status_code == 201, response.text

        user = UUID(response.json()["id"])
        assert api.post("/v1/auth/login", json={"email": email, "password": "LearningSecure123"}).status_code == 204
        body = config_body(str(user))
        body["daily_limits"] = {"new_cards_per_day": 999, "max_reviews_per_day": 999}
        response = api.post("/v1/deck-config/", json=body)
        assert response.status_code == 201, response.text
        config = UUID(response.json()["id"])
        response = api.post(
            "/v1/deck/", json={"owner_id": str(user), "deck_config_id": str(config), "title": "Load deck"}
        )
        assert response.status_code == 201, response.text
        deck = UUID(response.json()["id"])
        for index in range(20):
            response = api.post("/v1/card/", json=card_body(str(deck), f"Load question {index}"))
            assert response.status_code == 201, response.text
    accounts = asyncio.run(clone_accounts({"user": user, "config": config, "deck": deck}))

    def log_in(account: dict[str, object]) -> dict[str, object]:
        with httpx.Client(base_url=url, trust_env=False, timeout=30) as api:
            response = api.post("/v1/auth/login", json={"email": account["email"], "password": "LearningSecure123"})
            assert response.status_code == 204, response.text
            return {**account, "token": api.cookies["access_token"]}

    prepared = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for account in pool.map(log_in, accounts):
            prepared.append(account)
            if len(prepared) % 25 == 0:
                print(f"Prepared real sessions: {len(prepared)}/{MAX_USERS}", flush=True)
    return prepared


def phase(name: str, users: int, seconds: int, url: str, accounts: Path, api_pid: int) -> dict[str, object]:
    directory = OUT / name
    directory.mkdir(exist_ok=True)
    warmup = 5
    env = {
        **os.environ,
        "LAB5_ACCOUNTS": str(accounts),
        "LAB5_PHASE_DIR": str(directory),
        "LAB5_USERS": str(users),
        "LAB5_WARMUP": str(warmup),
        "LAB5_DURATION": str(seconds),
    }
    args = [
        sys.executable,
        "-m",
        "locust",
        "-f",
        "loadtests/locustfile.py",
        "--headless",
        "--host",
        url,
        "--users",
        str(users),
        "--spawn-rate",
        str(max(1, users)),
        "--stop-timeout",
        "6",
        "--csv",
        str(directory / "locust"),
        "--csv-full-history",
        "--html",
        str(directory / "locust.html"),
    ]
    worker = psutil.Process(api_pid)
    worker.cpu_percent()
    samples = []
    print(f"START {name}: {users} users, {seconds}s measured + {warmup}s warmup", flush=True)
    with (
        (directory / "locust.log").open("w") as log,
        subprocess.Popen(args, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT) as process,  # noqa: S603 - fixed Python/Locust argv
    ):
        generator = psutil.Process(process.pid)
        generator.cpu_percent()
        started = time.monotonic()
        last_notice = 0
        while process.poll() is None:
            sample = {
                "elapsed_s": time.monotonic() - started,
                "api_cpu_percent": worker.cpu_percent(),
                "api_rss_mb": worker.memory_info().rss / 1024 / 1024,
                "generator_cpu_percent": generator.cpu_percent(),
                **asyncio.run(database_sample()),
            }
            samples.append(sample)
            if sample["elapsed_s"] - last_notice >= 10:
                print(f"  {name}: {sample['elapsed_s']:.0f}s, API CPU {sample['api_cpu_percent']:.0f}%", flush=True)
                last_notice = sample["elapsed_s"]
            if time.monotonic() - started > seconds + warmup + 30:
                process.terminate()
                message = "Locust phase deadline exceeded"
                raise RuntimeError(message)
            time.sleep(1)
        code = process.returncode
    (directory / "resources.json").write_text(json.dumps(samples, indent=2) + "\n")
    if not (directory / "samples.csv").exists():
        message = f"Locust did not start; see {directory / 'locust.log'}"
        raise RuntimeError(message)
    result = {"id": name, "users": users, "locust_exit": code, **phase_metrics(directory, seconds)}
    measured = [s for s in samples if warmup <= s["elapsed_s"] <= seconds + warmup]
    result["resource_summary"] = {
        "api_cpu_mean": sum(s["api_cpu_percent"] for s in measured) / len(measured),
        "api_cpu_max": max(s["api_cpu_percent"] for s in measured),
        "generator_cpu_max": max(s["generator_cpu_percent"] for s in measured),
        "db_connections_max": max(s["connections"] for s in measured),
        "db_active_max": max(s["active"] for s in measured),
        "db_lock_waits_max": max(s["lock_waits"] for s in measured),
    }
    (directory / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(
        f"END {name}: RPS={result['rps']:.2f}, p95={result['p95_ms']:.1f}ms, errors={result['error_percent']:.2f}%",
        flush=True,
    )
    return result


def recover(url: str, worker: subprocess.Popen) -> dict[str, object]:
    start = time.monotonic()
    probes = []
    consecutive = 0
    with httpx.Client(base_url=url, trust_env=False, timeout=3) as api:
        while time.monotonic() - start < 30:
            before = time.monotonic()
            try:
                live = api.get("/healthcheck/live")
                ready = api.get("/healthcheck/ready")
                latency = (time.monotonic() - before) * 1000
                good = live.status_code == ready.status_code == 200 and latency <= 1000
                probes.append(
                    {
                        "elapsed_s": time.monotonic() - start,
                        "pair_latency_ms": latency,
                        "live_status": live.status_code,
                        "ready_status": ready.status_code,
                    }
                )
            except httpx.HTTPError as error:
                good = False
                probes.append({"elapsed_s": time.monotonic() - start, "error": str(error)})
            consecutive = consecutive + 1 if good else 0
            if consecutive == 3:
                break
            time.sleep(1)
    return {
        "elapsed_s": time.monotonic() - start,
        "healthy": consecutive == 3,
        "pid_unchanged": worker.poll() is None,
        "probes": probes,
    }


def await_startup(url: str, worker: subprocess.Popen) -> None:
    deadline = time.monotonic() + 30
    with httpx.Client(base_url=url, trust_env=False, timeout=2) as api:
        while True:
            try:
                if api.get("/healthcheck/ready").status_code == 200:
                    return
            except httpx.HTTPError:
                pass
            assert time.monotonic() < deadline, "API startup timed out"
            assert worker.poll() is None, "API exited before startup"
            time.sleep(0.1)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    result = {"started": datetime.now(ZoneInfo("Europe/Minsk")).isoformat(), "phases": []}
    postgres = PostgresContainer("postgres:16-alpine", username="postgres", password="postgres", dbname="trafficmaster")
    redis = RedisContainer("redis:7-alpine", password="secret")
    with postgres, redis, tempfile.TemporaryDirectory(prefix="trafficmaster-lab5-") as private:
        _apply_env(postgres, redis)
        cfg = Config(str(ROOT / "alembic.ini"))
        command.upgrade(cfg, "head")
        command.check(cfg)
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]
        url = f"http://127.0.0.1:{port}"
        with (
            (OUT / "server.log").open("w") as log,
            subprocess.Popen(  # noqa: S603 - fixed Python/Uvicorn argv
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
                cwd=ROOT,
                stdout=log,
                stderr=subprocess.STDOUT,
            ) as worker,
        ):
            try:
                await_startup(url, worker)
                prepared = prepare(url)
                secret = Path(private) / "accounts.json"
                secret.write_text(json.dumps(prepared))
                secret.chmod(0o600)
                result["data"] = {
                    "users": len(prepared),
                    "cards_per_user": 20,
                    "initial_cards": len(prepared) * 20,
                    "preparation": "one seed, SQL clones, individual HTTP logins; excluded from load measurements",
                }
                result["phases"].append(phase("baseline", 1, 45, url, secret, worker.pid))
                result["phases"].append(phase("target", 10, 30, url, secret, worker.pid))
                violations = 0
                for users in [25, 50, 100, 200]:
                    current = phase(f"stress-{users}", users, 25, url, secret, worker.pid)
                    result["phases"].append(current)
                    violations = violations + 1 if not current["slo_passed"] else 0
                    if current["error_percent"] > 5 or current["p95_ms"] > 5000 or violations >= 2:
                        result["stress_stop"] = "bounded stop: >5% errors, p95>5s, or two consecutive SLO violations"
                        break
                result["recovery_probes"] = recover(url, worker)
                result["phases"].append(phase("recovery", 10, 30, url, secret, worker.pid))
            finally:
                worker.terminate()
                try:
                    worker.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    worker.kill()
                    worker.wait(timeout=5)
    result["finished"] = datetime.now(ZoneInfo("Europe/Minsk")).isoformat()
    result["environment"] = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "logical_cpus": os.cpu_count(),
        "uvicorn_workers": 1,
        "db_pool_size": 10,
        "db_max_overflow": 10,
        "request_timeout_s": 5,
        "versions": {
            name: importlib.metadata.version(name)
            for name in ["locust", "gevent", "psutil", "fastapi", "bcrypt", "sqlalchemy", "asyncpg"]
        },
    }
    (OUT / "run.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print("Load experiment complete", flush=True)


if __name__ == "__main__":
    main()
