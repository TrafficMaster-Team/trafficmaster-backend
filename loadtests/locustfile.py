"""Locust workload for private learning data; no production endpoints or credentials."""

import csv
import itertools
import json
import os
import random
import time
from pathlib import Path
from typing import TYPE_CHECKING

import gevent
from locust import HttpUser, between, events, task

if TYPE_CHECKING:
    from locust.env import Environment


class RequestRecorder:
    def __init__(self) -> None:
        self.started = 0.0
        self.warmup = float(os.environ.get("LAB5_WARMUP", "5"))
        self.duration = float(os.environ.get("LAB5_DURATION", "25"))
        self.output = Path(os.environ["LAB5_PHASE_DIR"])
        self.file = None
        self.writer = None

    def start(self, environment: "Environment") -> None:
        self.started = time.time()
        self.file = (self.output / "samples.csv").open("w", newline="")
        self.writer = csv.DictWriter(
            self.file,
            fieldnames=["timestamp", "elapsed_s", "method", "name", "latency_ms", "success", "error", "measured"],
        )
        self.writer.writeheader()
        gevent.spawn_later(self.warmup, environment.stats.reset_all)
        # Anchor shutdown to the same event as measurement. CLI --run-time starts earlier.
        # Two unmeasured seconds prevent a rounded history timestamp from crossing the window.
        gevent.spawn_later(self.warmup + self.duration + 2, environment.runner.quit)
        (self.output / "window.json").write_text(
            json.dumps(
                {
                    "started_epoch": self.started,
                    "warmup_s": self.warmup,
                    "measured_s": self.duration,
                    "shutdown_tail_s": 2,
                    "criterion": "request started after warmup and completed before window end",
                },
                indent=2,
            )
            + "\n"
        )

    def request(self, request_type: str, name: str, response_time: float, exception: object, **_kwargs: object) -> None:
        if self.writer is None:
            return
        now = time.time()
        elapsed = now - self.started
        start = elapsed - response_time / 1000
        measured = start >= self.warmup and elapsed <= self.warmup + self.duration
        self.writer.writerow(
            {
                "timestamp": now,
                "elapsed_s": elapsed,
                "method": request_type,
                "name": name,
                "latency_ms": response_time,
                "success": int(exception is None),
                "error": str(exception)[:180] if exception else "",
                "measured": int(measured),
            }
        )

    def close(self) -> None:
        if self.file:
            self.file.close()


recorder = RequestRecorder()
accounts = json.loads(Path(os.environ["LAB5_ACCOUNTS"]).read_text())
account_index = itertools.count()


@events.test_start.add_listener
def test_started(environment: "Environment", **_kwargs: object) -> None:
    random.seed(20261116 + int(os.environ.get("LAB5_USERS", "1")))
    recorder.start(environment)


@events.request.add_listener
def request_finished(request_type: str, name: str, response_time: float, exception: object, **kwargs: object) -> None:
    recorder.request(request_type, name, response_time, exception, **kwargs)


@events.quitting.add_listener
def test_finished(**_kwargs: object) -> None:
    recorder.close()


class LearningUser(HttpUser):
    wait_time = between(0.5, 1.5)

    def on_start(self) -> None:
        self.account = accounts[next(account_index)]
        self.client.cookies.set("access_token", self.account["token"])

    def card(self) -> str:
        return random.choice(self.account["cards"])  # noqa: S311 - synthetic test data selection

    @task(30)
    def queue(self) -> None:
        with self.client.get(
            "/v1/review/queue",
            params={"deck_id": self.account["deck"], "limit": 10},
            name="GET queue",
            catch_response=True,
            timeout=5,
        ) as response:
            if response.status_code != 200:
                response.failure(f"HTTP {response.status_code}")
            elif not isinstance(response.json().get("items"), list):
                response.failure("queue.items is not an array")

    @task(20)
    def read_card(self) -> None:
        card = self.card()
        with self.client.get(f"/v1/card/{card}", name="GET card", catch_response=True, timeout=5) as response:
            if response.status_code != 200:
                response.failure(f"HTTP {response.status_code}")
            elif response.json().get("id") != card:
                response.failure("wrong card ID")

    @task(20)
    def review(self) -> None:
        rating = random.choice([1, 2, 3, 4])  # noqa: S311
        with self.client.post(
            f"/v1/review/card/{self.card()}",
            json={"rating": rating},
            name="POST review",
            catch_response=True,
            timeout=5,
        ) as response:
            if response.status_code != 200:
                response.failure(f"HTTP {response.status_code}")
            elif response.json().get("state") not in ["learning", "review", "relearning"]:
                response.failure("invalid progress state")

    @task(15)
    def stats(self) -> None:
        with self.client.get(
            f"/v1/review/deck/{self.account['deck']}/stats", name="GET stats", catch_response=True, timeout=5
        ) as response:
            if response.status_code != 200:
                response.failure(f"HTTP {response.status_code}")
            elif response.json().get("total_cards") != 20:
                response.failure("card count changed")

    @task(10)
    def history(self) -> None:
        with self.client.get(
            f"/v1/review/card/{self.card()}/logs", name="GET history", catch_response=True, timeout=5
        ) as response:
            if response.status_code != 200:
                response.failure(f"HTTP {response.status_code}")
            elif any(log["user_id"] != self.account["user"] for log in response.json()["logs"]):
                response.failure("history belongs to another user")

    @task(5)
    def log_in(self) -> None:
        # A fresh sign-in, not a login with an existing session (which correctly returns 409).
        self.client.cookies.clear()
        with self.client.post(
            "/v1/auth/login",
            json={"email": self.account["email"], "password": "LearningSecure123"},
            name="POST login",
            catch_response=True,
            timeout=5,
        ) as response:
            if response.status_code != 204:
                response.failure(f"HTTP {response.status_code}")
            elif "access_token=" not in response.headers.get("set-cookie", ""):
                response.failure("login did not set cookie")
