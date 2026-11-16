"""Executable laboratory 3 cases; the catalogue and transcript are submission artifacts."""

import json
import os
import socket
import subprocess
import sys
import time
import traceback
from collections.abc import AsyncIterator, Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

import asyncpg
import httpx
import pytest
import pytest_asyncio

CATALOGUE = Path(__file__).parents[3] / "docs/lab3/cases.json"
CASES = json.loads(CATALOGUE.read_text())
PASSWORD = "LearningSecure123"  # noqa: S105
pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest.fixture(scope="session")
def live_server(_migrated_database: None, tmp_path_factory: pytest.TempPathFactory) -> Iterator[str]:
    """Use real HTTP, the assembled application, and disposable migrated dependencies."""
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    url = f"http://127.0.0.1:{port}"
    with (
        (tmp_path_factory.mktemp("lab3") / "uvicorn.log").open("w+") as output,
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
            deadline = time.monotonic() + 30
            with httpx.Client(base_url=url, trust_env=False, timeout=2) as probe:
                while True:
                    assert process.poll() is None, "Uvicorn exited before startup"
                    try:
                        ready = probe.get("/healthcheck/ready")
                        if ready.status_code == 200:
                            break
                    except httpx.TransportError:
                        pass
                    assert time.monotonic() < deadline, "Application startup timed out"
                    time.sleep(0.1)
            yield url
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


@pytest_asyncio.fixture(loop_scope="session")
async def lab_client(live_server: str) -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(base_url=live_server, trust_env=False, timeout=10) as client:
        yield client


def config_body(owner: str) -> dict[str, Any]:
    return {
        "owner_id": owner,
        "name": "Lab config",
        "daily_limits": {"new_cards_per_day": 1, "max_reviews_per_day": 20},
        "new_cards": {
            "learning_steps": [1, 10],
            "graduating_interval": 1,
            "easy_interval": 4,
            "new_card_order": "sequential",
        },
        "lapses": {"relearning_steps": [10], "min_interval": 1},
        "advanced": {
            "max_interval": 36500,
            "ease_factor": 2.5,
            "easy_factor": 1.3,
            "interval_modifier": 1.0,
            "hard_interval": 1.2,
            "new_interval": 0.0,
        },
    }


def card_body(deck: str, question: str = "What does a red traffic light mean?") -> dict[str, Any]:
    return {
        "deck_id": deck,
        "question": question,
        "answerOptions": [{"text": "Stop", "isCorrect": True, "rationale": "Red prohibits movement"}],
        "hint": "Think about safety",
        "tags": ["signals"],
    }


class Scenario:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self.client = client
        self.events: list[dict[str, Any]] = []
        self.checks: list[dict[str, Any]] = []

    def check(self, condition: bool, expectation: str, actual: object) -> None:
        self.checks.append({"expectation": expectation, "passed": bool(condition), "actual": actual})
        assert condition, f"{expectation}; actual={actual!r}"

    def status(self, response: httpx.Response, expected: int) -> None:
        self.check(
            response.status_code == expected,
            f"{response.request.method} {response.request.url.path}: HTTP {expected}",
            {"status": response.status_code, "body": response.text},
        )

    async def http(self, method: str, path: str, expected: int | None = None, **kwargs: Any) -> httpx.Response:  # noqa: ANN401
        response = await self.client.request(method, path, **kwargs)
        payload = dict(kwargs.get("json", {}))
        if "password" in payload:
            payload["password"] = "<test-password-redacted>"  # noqa: S105
        self.events.append(
            {
                "type": "HTTP",
                "method": method,
                "path": path,
                "params": kwargs.get("params"),
                "request": payload,
                "status": response.status_code,
                "response": response.json() if response.content else None,
                "cookie_set": "access_token=" in response.headers.get("set-cookie", ""),
                "httponly": "httponly" in response.headers.get("set-cookie", "").lower(),
            }
        )
        if expected is not None:
            self.status(response, expected)
        return response

    async def identity(self) -> tuple[str, str]:
        self.client.cookies.clear()
        email = f"lab3_{uuid4().hex[:12]}@example.com"
        response = await self.http(
            "POST", "/v1/auth/signup", 201, json={"email": email, "name": "Lab-User", "password": PASSWORD}
        )
        user = str(response.json()["id"])
        UUID(user)
        await self.login(email)
        return user, email

    async def login(self, email: str, password: str = PASSWORD, expected: int = 204) -> None:
        self.client.cookies.clear()
        await self.http("POST", "/v1/auth/login", expected, json={"email": email, "password": password})

    async def material(self, *, public: bool = False) -> tuple[str, str, str, str]:
        user, _ = await self.identity()
        config = (await self.http("POST", "/v1/deck-config/", 201, json=config_body(user))).json()["id"]
        deck = (
            await self.http(
                "POST",
                "/v1/deck/",
                201,
                json={"owner_id": user, "deck_config_id": config, "title": "Traffic rules", "is_public": public},
            )
        ).json()["id"]
        card = await self.add_card(deck)
        return user, config, deck, card

    async def add_card(self, deck: str) -> str:
        return str((await self.http("POST", "/v1/card/", 201, json=card_body(deck))).json()["id"])

    async def review(self, card: str, rating: int = 4) -> dict[str, Any]:
        return (await self.http("POST", f"/v1/review/card/{card}", 200, json={"rating": rating})).json()

    async def logs(self, card: str) -> list[dict[str, Any]]:
        return (await self.http("GET", f"/v1/review/card/{card}/logs", 200)).json()["logs"]

    async def queue(self, deck: str, limit: int = 10) -> list[dict[str, Any]]:
        return (await self.http("GET", "/v1/review/queue", 200, params={"deck_id": deck, "limit": limit})).json()[
            "items"
        ]

    async def sql(self, statement: str, *args: object) -> None:
        connection = await asyncpg.connect(
            host=os.environ["POSTGRES_HOST"],
            port=int(os.environ["POSTGRES_PORT"]),
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            database=os.environ["POSTGRES_DB"],
        )
        try:
            result = await connection.execute(statement, *args)
            self.events.append(
                {
                    "type": "SQL test-data preparation",
                    "statement": statement,
                    "arguments": [str(arg) for arg in args],
                    "result": result,
                }
            )
            self.check(result.endswith(" 1"), "Exactly one test row updated", result)
        finally:
            await connection.close()

    async def due(self, card: str) -> None:
        await self.sql(
            "UPDATE card_progress SET next_review_at=$1 WHERE card_id=$2",
            datetime.now(UTC) - timedelta(minutes=1),
            UUID(card),
        )

    async def history_states(self, card: str) -> list[str]:
        connection = await asyncpg.connect(
            host=os.environ["POSTGRES_HOST"],
            port=int(os.environ["POSTGRES_PORT"]),
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            database=os.environ["POSTGRES_DB"],
        )
        try:
            statement = "SELECT card_state::text FROM review_logs WHERE card_id=$1 ORDER BY reviewed_at"
            rows = await connection.fetch(statement, UUID(card))
            states = [row["card_state"] for row in rows]
            self.events.append(
                {"type": "SQL verification", "statement": statement, "arguments": [card], "result": states}
            )
            return states
        finally:
            await connection.close()

    async def yesterday(self, card: str) -> None:
        yesterday = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(microseconds=1)
        await self.sql("UPDATE review_logs SET reviewed_at=$1 WHERE card_id=$2", yesterday, UUID(card))


async def execute(case: dict[str, Any], s: Scenario) -> None:  # noqa: C901, PLR0912, PLR0915
    fr = int(case["requirement"].split("-")[1])
    positive = case["kind"] == "positive"
    if case["kind"] == "boundary":
        s.client.cookies.clear()
        email = (
            "valid-address-longer-than-fifty-characters-123@example.com"
            if case["known_issue"] == "APP-01"
            else f"lab3_{uuid4().hex[:12]}@example.com"
        )
        name = "Valid-Name" if case["known_issue"] == "APP-01" else "ValidUsernameLongerThan20"
        response = await s.http(
            "POST", "/v1/auth/signup", 201, json={"email": email, "name": name, "password": PASSWORD}
        )
        UUID(response.json()["id"])
        return

    if fr <= 4:
        user, email = await s.identity()
        if fr == 1:
            if positive:
                me = (await s.http("GET", "/v1/auth/me", 200)).json()
                s.check(
                    me["id"] == user and me["email"] == email and me["name"] == "Lab-User", "Saved identity matches", me
                )
            else:
                s.client.cookies.clear()
                await s.http(
                    "POST", "/v1/auth/signup", 409, json={"email": email, "name": "Lab-User", "password": PASSWORD}
                )
        elif fr == 2:
            if positive:
                response = await s.http("POST", "/v1/auth/logout", 204)
                response = await s.http("POST", "/v1/auth/login", 204, json={"email": email, "password": PASSWORD})
                s.check(
                    "access_token" in s.client.cookies and "httponly" in response.headers["set-cookie"].lower(),
                    "HttpOnly session cookie",
                    "present",
                )
                me = (await s.http("GET", "/v1/auth/me", 200)).json()
                s.check(me["id"] == user and me["email"] == email, "Current user matches login", me)
            else:
                await s.login(email, "WrongSecure123", 401)
                await s.http("GET", "/v1/auth/me", 401)
        elif fr == 3:
            stale = dict(s.client.cookies)
            await s.http("POST", "/v1/auth/logout", 204)
            s.client.cookies.update(stale if positive else {"access_token": "invalid-token"})
            await s.http("GET", "/v1/auth/me", 401)
        elif positive:
            stale = dict(s.client.cookies)
            await s.http("PATCH", f"/v1/user/{user}/password", 204, json={"password": "ChangedSecure456"})
            s.client.cookies.update(stale)
            await s.http("GET", "/v1/auth/me", 401)
            await s.login(email, PASSWORD, 401)
            await s.login(email, "ChangedSecure456")
        else:
            await s.identity()
            await s.http("PATCH", f"/v1/user/{user}/password", 403, json={"password": "ChangedSecure456"})
            await s.login(email)
        return

    user, config, deck, card = await s.material(public=(fr == 10 and positive) or fr == 17)
    owner_cookie = dict(s.client.cookies)
    config_path = f"/v1/deck-config/{config}"
    deck_path = f"/v1/deck/{deck}"
    card_path = f"/v1/card/{card}"
    review_path = f"/v1/review/card/{card}"
    if fr == 5:
        if positive:
            saved = (await s.http("GET", config_path, 200)).json()
            expected = config_body(user)
            s.check(
                all(saved[key] == value for key, value in expected.items()), "All configuration fields persisted", saved
            )
        else:
            s.client.cookies.clear()
            await s.http("POST", "/v1/deck-config/", 401, json=config_body(user))
    elif fr == 6:
        if positive:
            await s.http("PATCH", config_path + "/name", 204, json={"name": "Updated config"})
            limits = {"new_cards_per_day": 2, "max_reviews_per_day": 10}
            await s.http("PATCH", config_path + "/daily-limits", 204, json=limits)
            saved = (await s.http("GET", config_path, 200)).json()
            s.check(
                saved["name"] == "Updated config" and saved["daily_limits"] == limits,
                "Changed configuration persisted",
                saved,
            )
        else:
            await s.http(
                "PATCH", config_path + "/daily-limits", 400, json={"new_cards_per_day": 0, "max_reviews_per_day": 10}
            )
            saved = (await s.http("GET", config_path, 200)).json()
            s.check(
                saved["daily_limits"] == config_body(user)["daily_limits"],
                "Invalid update did not persist",
                saved["daily_limits"],
            )
    elif fr == 7:
        if positive:
            saved = (await s.http("GET", deck_path, 200)).json()
            s.check(
                saved["owner_id"] == user and saved["deck_config_id"] == config and saved["title"] == "Traffic rules",
                "Deck identity and contents persisted",
                saved,
            )
        else:
            await s.http(
                "POST",
                "/v1/deck/",
                404,
                json={"owner_id": user, "deck_config_id": str(uuid4()), "title": "Should not exist"},
            )
            decks = (await s.http("GET", "/v1/deck/", 200, params={"user_id": user})).json()["decks"]
            s.check(all(item["title"] != "Should not exist" for item in decks), "No deck created on failure", decks)
    elif fr == 8:
        if not positive:
            await s.identity()
        await s.http("PATCH", deck_path + "/title", 204 if positive else 403, json={"title": "Updated title"})
        await s.http("PATCH", deck_path + "/privacy", 204 if positive else 403, json={"is_public": True})
        s.client.cookies.clear()
        s.client.cookies.update(owner_cookie)
        saved = (await s.http("GET", deck_path, 200)).json()
        s.check(
            saved["title"] == ("Updated title" if positive else "Traffic rules") and saved["is_public"] == positive,
            "Deck matches permitted changes",
            saved,
        )
    elif fr == 9:
        if positive:
            public_ids = []
            for index in range(2):
                created = await s.http(
                    "POST",
                    "/v1/deck/",
                    201,
                    json={"owner_id": user, "deck_config_id": config, "title": f"Public {index}", "is_public": True},
                )
                public_ids.append(created.json()["id"])
            decks = (await s.http("GET", "/v1/deck/public", 200, params={"limit": 100})).json()["decks"]
            ids = {item["id"] for item in decks}
            s.check(set(public_ids) <= ids and deck not in ids, "Public included; private excluded", list(ids))
            pages = [
                (await s.http("GET", "/v1/deck/public", 200, params={"limit": 1, "offset": offset})).json()["decks"]
                for offset in (0, 1)
            ]
            s.check(
                all(len(page) == 1 for page in pages) and pages[0][0]["id"] != pages[1][0]["id"],
                "Pagination applies limit and offset",
                pages,
            )
        else:
            for params in ({"limit": 0}, {"offset": -1}):
                await s.http("GET", "/v1/deck/public", 422, params=params)
    elif fr == 10:
        if positive:
            await s.review(card)
        other, _ = await s.identity()
        response = await s.http("POST", deck_path + "/copy", 201 if positive else 403)
        if positive:
            copied = response.json()
            copy_deck = (await s.http("GET", f"/v1/deck/{copied['deck_id']}", 200)).json()
            s.check(
                copy_deck["owner_id"] == other
                and copy_deck["is_public"] is False
                and copied["deck_id"] != deck
                and copied["deck_config_id"] != config,
                "Independent private copy",
                copy_deck,
            )
            config_copy = (await s.http("GET", f"/v1/deck-config/{copied['deck_config_id']}", 200)).json()
            s.check(
                config_copy["owner_id"] == other and config_copy["daily_limits"] == config_body(user)["daily_limits"],
                "Copied configuration owned by recipient",
                config_copy,
            )
            cards = (await s.http("GET", "/v1/card/", 200, params={"deck_id": copied["deck_id"]})).json()["cards"]
            s.check(
                len(cards) == 1 and cards[0]["id"] != card and cards[0]["question"] == card_body(deck)["question"],
                "Copied card has new ID and same question",
                cards,
            )
            await s.http("GET", f"/v1/review/card/{cards[0]['id']}/progress", 404)
    elif fr == 11:
        if positive:
            saved = (await s.http("GET", card_path, 200)).json()
            expected = card_body(deck)
            s.check(
                all(saved[key] == expected[key] for key in ("question", "hint", "tags")),
                "Card content persisted",
                saved,
            )
            option = saved["answerOptions"][0]
            s.check(
                all(option[key] == value for key, value in expected["answerOptions"][0].items()),
                "Answer options persisted",
                option,
            )
        else:
            await s.http("POST", "/v1/card/", 422, json=card_body(deck, ""))
            cards = (await s.http("GET", "/v1/card/", 200, params={"deck_id": deck})).json()["cards"]
            s.check(len(cards) == 1, "No extra card on validation error", len(cards))
    elif fr == 12:
        if positive:
            await s.http("PATCH", card_path + "/question", 204, json={"question": "Updated question"})
            await s.http("POST", card_path + "/tags", 204, json={"tag": "lab"})
            await s.http("PATCH", card_path + "/image", 204, json={"image_path": "images/signal.png"})
            saved = (await s.http("GET", card_path, 200)).json()
            s.check(
                saved["question"] == "Updated question"
                and "lab" in saved["tags"]
                and saved["image_path"] == "images/signal.png",
                "All card changes persisted",
                saved,
            )
            await s.http("PATCH", card_path + "/image", 204, json={"image_path": None})
            saved = (await s.http("GET", card_path, 200)).json()
            s.check(saved["image_path"] is None, "Image path cleared", saved["image_path"])
        else:
            await s.identity()
            await s.http("PATCH", card_path + "/question", 403, json={"question": "Updated question"})
            s.client.cookies.clear()
            s.client.cookies.update(owner_cookie)
            saved = (await s.http("GET", card_path, 200)).json()
            s.check(
                saved["question"] == card_body(deck)["question"],
                "Unauthorized change did not persist",
                saved["question"],
            )
    elif fr == 13:
        if positive:
            await s.http(
                "PATCH", config_path + "/daily-limits", 204, json={"new_cards_per_day": 10, "max_reviews_per_day": 20}
            )
            await s.review(card, 1)
            await s.due(card)
            review_card = await s.add_card(deck)
            await s.review(review_card)
            await s.due(review_card)
            await s.yesterday(review_card)
            new_card = await s.add_card(deck)
            queue = await s.queue(deck)
            s.check(
                [item["reason"] for item in queue] == ["learning", "review", "new"]
                and [item["card_id"] for item in queue] == [card, review_card, new_card],
                "Queue ordering by learning, review, new",
                queue,
            )
            limited = await s.queue(deck, 1)
            s.check(len(limited) == 1 and limited[0]["card_id"] == card, "Queue limit applies", limited)
        else:
            await s.identity()
            await s.http("GET", "/v1/review/queue", 403, params={"deck_id": deck})
    elif fr == 14:
        if positive:
            await s.http(
                "PATCH", config_path + "/daily-limits", 204, json={"new_cards_per_day": 1, "max_reviews_per_day": 1}
            )
            await s.review(card)
            await s.due(card)
            await s.yesterday(card)
            second = await s.add_card(deck)
            await s.review(second)
            await s.due(second)
            await s.yesterday(second)
            await s.add_card(deck)
            await s.review(card)
            queue = await s.queue(deck)
            s.check(all(item["reason"] != "review" for item in queue), "Today's REVIEW consumes review quota", queue)
            # Move just the newest log, keeping the old NEW log unchanged.
            yesterday = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(microseconds=1)
            await s.sql(
                "UPDATE review_logs SET reviewed_at=$1 WHERE id=(SELECT id FROM review_logs "
                "WHERE card_id=$2 AND card_state='REVIEW' ORDER BY reviewed_at DESC LIMIT 1)",
                yesterday,
                UUID(card),
            )
            queue = await s.queue(deck)
            s.check(
                any(item["card_id"] == second and item["reason"] == "review" for item in queue),
                "Yesterday's REVIEW does not consume today's quota",
                queue,
            )
            await s.review(second)
            learning = await s.add_card(deck)
            await s.review(learning, 1)
            await s.due(learning)
            queue = await s.queue(deck)
            s.check(
                [item["card_id"] for item in queue] == [learning],
                "Learning bypasses exhausted new/review quotas",
                queue,
            )
        else:
            await s.add_card(deck)
            queue = await s.queue(deck)
            s.check(len(queue) == 1, "Only one new card issued", queue)
            await s.review(queue[0]["card_id"])
            queue = await s.queue(deck)
            s.check(queue == [], "No second new card after daily quota consumed", queue)
    elif fr == 15:
        if positive:
            progress_id = None
            for rating, state in [(1, "learning"), (3, "learning"), (3, "review"), (1, "relearning"), (3, "review")]:
                result = await s.review(card, rating)
                progress_id = progress_id or result["card_progress_id"]
                s.check(
                    result["state"] == state
                    and result["card_progress_id"] == progress_id
                    and datetime.fromisoformat(result["next_review_at"]) > datetime.now(UTC),
                    f"Transition to {state} with stable ID and future due date",
                    result,
                )
            saved = (await s.http("GET", review_path + "/progress", 200)).json()
            s.check(saved["state"] == "review", "Final persisted state REVIEW", saved)
            logs = await s.logs(card)
            s.check(len(logs) == 5, "One history row per transition", logs)
            states = await s.history_states(card)
            s.check(
                states == ["NEW", "LEARNING", "LEARNING", "REVIEW", "RELEARNING"],
                "Persisted source states follow the transition sequence",
                states,
            )
        else:
            for rating in (0, 5):
                await s.http("POST", review_path, 422, json={"rating": rating})
            await s.http("GET", review_path + "/progress", 404)
            s.check(await s.logs(card) == [], "Invalid ratings do not write history", [])
    elif fr == 16:
        if positive:
            preview = (await s.http("GET", review_path + "/preview", 200)).json()["items"]
            s.check(
                {item["rating"] for item in preview} == {1, 2, 3, 4} and len(preview) == 4,
                "Preview includes all ratings",
                preview,
            )
            await s.http("GET", review_path + "/progress", 404)
            logs = await s.logs(card)
            s.check(logs == [], "Preview does not write history", logs)
        else:
            await s.identity()
            await s.http("GET", review_path + "/preview", 403)
    elif fr == 17:
        first = await s.review(card)
        other, _ = await s.identity()
        if positive:
            second = await s.review(card, 1)
            logs = await s.logs(card)
            saved = (await s.http("GET", review_path + "/progress", 200)).json()
            s.check(
                saved["state"] == "learning"
                and second["card_progress_id"] != first["card_progress_id"]
                and len(logs) == 1
                and logs[0]["user_id"] == other,
                "Second learner has independent progress/history",
                {"progress": saved, "logs": logs},
            )
            s.client.cookies.clear()
            s.client.cookies.update(owner_cookie)
            saved = (await s.http("GET", review_path + "/progress", 200)).json()
            logs = await s.logs(card)
            s.check(
                saved["state"] == "review" and len(logs) == 1 and logs[0]["user_id"] == user,
                "First learner unchanged",
                {"progress": saved, "logs": logs},
            )
        else:
            await s.http("GET", review_path + "/progress", 404)
            logs = await s.logs(card)
            s.check(logs == [], "No access to another learner's logs", logs)
    elif fr == 18:
        if positive:
            await s.add_card(deck)
            await s.review(card)
            stats = (await s.http("GET", f"/v1/review/deck/{deck}/stats", 200)).json()
            expected = {"total_cards": 2, "new_count": 1, "review_count": 1, "learning_count": 0, "new_done_today": 1}
            s.check(
                all(stats[key] == value for key, value in expected.items()),
                "Counts match this user's card states",
                stats,
            )
        else:
            await s.identity()
            await s.http("GET", f"/v1/review/deck/{deck}/stats", 403)
    elif fr == 19:
        first = await s.review(card)
        if positive:
            await s.http("POST", review_path + "/reset", 204)
            await s.http("GET", review_path + "/progress", 404)
            logs = await s.logs(card)
            s.check(len(logs) == 1, "Reset preserves history", logs)
            second = await s.review(card)
            s.check(first["card_progress_id"] != second["card_progress_id"], "Restart has a new progress ID", second)
        else:
            await s.identity()
            await s.http("POST", review_path + "/reset", 403)
            s.client.cookies.clear()
            s.client.cookies.update(owner_cookie)
            saved = (await s.http("GET", review_path + "/progress", 200)).json()
            s.check(
                saved["id"] == first["card_progress_id"] and saved["state"] == "review",
                "Owner progress not reset",
                saved,
            )
    elif fr == 20:
        if not positive:
            await s.identity()
        for path in (card_path, deck_path, config_path):
            await s.http("DELETE", path, 204 if positive else 403)
            if positive:
                await s.http("GET", path, 404)
        if not positive:
            s.client.cookies.clear()
            s.client.cookies.update(owner_cookie)
            for path in (card_path, deck_path, config_path):
                await s.http("GET", path, 200)


@pytest.mark.parametrize("case", CASES, ids=[case["id"] for case in CASES])
async def test_documented_acceptance_case(case: dict[str, Any], lab_client: httpx.AsyncClient, tmp_path: Path) -> None:
    # Arrange: isolated client, unique identities, and a new scenario transcript.
    scenario = Scenario(lab_client)
    started = datetime.now(ZoneInfo("Europe/Minsk"))
    result: dict[str, Any] = {
        "id": case["id"],
        "requirement": case["requirement"],
        "started": started.isoformat(),
        "status": "Passed",
        "defect": None,
        "error": None,
    }
    try:
        # Act and Assert: each scenario checks statuses and persisted state at every stage.
        await execute(case, scenario)
    except Exception as error:
        result.update(status="Failed", error=str(error), traceback=traceback.format_exc())
        known = case.get("known_issue")
        if known and isinstance(error, AssertionError) and scenario.events and scenario.events[-1].get("status") == 401:
            result["defect"] = known
            pytest.xfail(f"{known}: actual 401, required 201; acceptance result is Failed")
        raise
    finally:
        result.update(
            finished=datetime.now(ZoneInfo("Europe/Minsk")).isoformat(), events=scenario.events, checks=scenario.checks
        )
        output = Path(os.environ.get("LAB3_EVIDENCE_DIR", str(tmp_path)))
        output.mkdir(parents=True, exist_ok=True)  # noqa: ASYNC240
        (output / f"{case['id']}.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
