from typing import Any
from uuid import uuid4

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def register_and_login(client: AsyncClient) -> str:
    client.cookies.clear()
    email = f"learner_{uuid4().hex[:12]}@example.com"
    credentials = {"email": email, "password": "LearningSecure123"}
    signup = await client.post("/v1/auth/signup", json={**credentials, "name": f"Learner-{uuid4().hex[:8]}"})
    assert signup.status_code == 201, signup.text
    login = await client.post("/v1/auth/login", json=credentials)
    assert login.status_code == 204, login.text
    assert "httponly" in login.headers["set-cookie"].lower()
    return str(signup.json()["id"])


async def create_material(client: AsyncClient, *, public: bool = False) -> tuple[str, str, str]:
    user_id = await register_and_login(client)
    config = await client.post(
        "/v1/deck-config/",
        json={
            "owner_id": user_id,
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
        },
    )
    assert config.status_code == 201, config.text
    config_id = str(config.json()["id"])
    saved_config = (await client.get(f"/v1/deck-config/{config_id}")).json()
    assert saved_config["owner_id"] == user_id
    assert saved_config["daily_limits"] == {"new_cards_per_day": 1, "max_reviews_per_day": 20}
    assert saved_config["new_cards"] == {
        "learning_steps": [1, 10],
        "graduating_interval": 1,
        "easy_interval": 4,
        "new_card_order": "sequential",
    }
    assert saved_config["lapses"] == {"relearning_steps": [10], "min_interval": 1}
    assert saved_config["advanced"] == {
        "max_interval": 36500,
        "ease_factor": 2.5,
        "easy_factor": 1.3,
        "interval_modifier": 1.0,
        "hard_interval": 1.2,
        "new_interval": 0.0,
    }
    deck = await client.post(
        "/v1/deck/",
        json={"owner_id": user_id, "deck_config_id": config_id, "title": "Traffic rules", "is_public": public},
    )
    assert deck.status_code == 201, deck.text
    deck_id = str(deck.json()["id"])
    assert (await client.get(f"/v1/deck/{deck_id}")).json()["owner_id"] == user_id
    card = await client.post(
        "/v1/card/",
        json={
            "deck_id": deck_id,
            "question": "What does a red traffic light mean?",
            "answerOptions": [{"text": "Stop", "isCorrect": True, "rationale": "Red prohibits movement"}],
            "hint": "Think about safety",
            "tags": ["signals"],
        },
    )
    assert card.status_code == 201, card.text
    card_id = str(card.json()["id"])
    saved_card = (await client.get(f"/v1/card/{card_id}")).json()
    assert saved_card["question"] == "What does a red traffic light mean?"
    assert saved_card["hint"] == "Think about safety"
    assert saved_card["answerOptions"][0]["text"] == "Stop"
    assert saved_card["answerOptions"][0]["isCorrect"] is True
    assert saved_card["answerOptions"][0]["rationale"] == "Red prohibits movement"
    return config_id, deck_id, card_id


async def test_learning_lifecycle_and_history(client: AsyncClient) -> None:
    config_id, deck_id, card_id = await create_material(client)
    assert (await client.get(f"/v1/deck-config/{config_id}")).status_code == 200
    assert (await client.get(f"/v1/deck/{deck_id}")).json()["title"] == "Traffic rules"
    queue = await client.get("/v1/review/queue", params={"deck_id": deck_id})
    assert queue.status_code == 200, queue.text
    assert [item["card_id"] for item in queue.json()["items"]] == [card_id]
    assert queue.json()["items"][0]["state"] is None

    preview = await client.get(f"/v1/review/card/{card_id}/preview")
    assert preview.status_code == 200, preview.text
    assert {item["rating"] for item in preview.json()["items"]} == {1, 2, 3, 4}
    assert (await client.get(f"/v1/review/card/{card_id}/progress")).status_code == 404
    assert (await client.get(f"/v1/review/card/{card_id}/logs")).json()["logs"] == []

    progress_id = None
    for rating, expected in [(1, "learning"), (3, "learning"), (3, "review"), (1, "relearning"), (3, "review")]:
        review = await client.post(f"/v1/review/card/{card_id}", json={"rating": rating})
        assert review.status_code == 200, review.text
        body = review.json()
        assert body["state"] == expected
        assert body["next_review_at"] is not None
        if progress_id is None:
            progress_id = body["card_progress_id"]
        assert body["card_progress_id"] == progress_id

    progress = await client.get(f"/v1/review/card/{card_id}/progress")
    assert progress.json()["state"] == "review"
    logs = await client.get(f"/v1/review/card/{card_id}/logs")
    assert logs.status_code == 200, logs.text
    assert len(logs.json()["logs"]) == 5
    stats = await client.get(f"/v1/review/deck/{deck_id}/stats")
    assert stats.status_code == 200, stats.text
    assert stats.json()["total_cards"] == 1
    assert stats.json()["review_count"] == 1

    assert (await client.post(f"/v1/review/card/{card_id}/reset")).status_code == 204
    assert (await client.get(f"/v1/review/card/{card_id}/progress")).status_code == 404
    assert len((await client.get(f"/v1/review/card/{card_id}/logs")).json()["logs"]) == 5
    restarted = await client.post(f"/v1/review/card/{card_id}", json={"rating": 4})
    assert restarted.status_code == 200, restarted.text
    assert restarted.json()["state"] == "review"
    assert restarted.json()["card_progress_id"] != progress_id


async def test_public_deck_has_independent_user_progress_and_can_be_copied(client: AsyncClient) -> None:
    config_id, deck_id, card_id = await create_material(client, public=True)
    first = await client.post(f"/v1/review/card/{card_id}", json={"rating": 4})
    assert first.status_code == 200, first.text
    first_cookie = dict(client.cookies)
    second_user_id = await register_and_login(client)
    public = await client.get("/v1/deck/public", params={"limit": 100})
    assert deck_id in {deck["id"] for deck in public.json()["decks"]}
    assert (await client.get(f"/v1/review/card/{card_id}/progress")).status_code == 404
    second = await client.post(f"/v1/review/card/{card_id}", json={"rating": 1})
    assert second.status_code == 200, second.text
    assert second.json()["state"] == "learning"
    assert second.json()["card_progress_id"] != first.json()["card_progress_id"]
    logs = (await client.get(f"/v1/review/card/{card_id}/logs")).json()["logs"]
    assert len(logs) == 1
    assert logs[0]["user_id"] == second_user_id
    copied = await client.post(f"/v1/deck/{deck_id}/copy")
    assert copied.status_code == 201, copied.text
    copy_id = copied.json()["deck_id"]
    assert copy_id != deck_id
    assert copied.json()["deck_config_id"] != config_id
    copied_deck = (await client.get(f"/v1/deck/{copy_id}")).json()
    assert copied_deck["owner_id"] == second_user_id
    assert copied_deck["is_public"] is False
    cards = await client.get("/v1/card/", params={"deck_id": copy_id})
    assert cards.status_code == 200, cards.text
    assert len(cards.json()["cards"]) == 1
    assert cards.json()["cards"][0]["id"] != card_id
    copied_card_id = cards.json()["cards"][0]["id"]
    assert (await client.get(f"/v1/review/card/{copied_card_id}/progress")).status_code == 404
    client.cookies.clear()
    client.cookies.update(first_cookie)
    own = await client.get(f"/v1/review/card/{card_id}/progress")
    assert own.json()["state"] == "review"
    assert len((await client.get(f"/v1/review/card/{card_id}/logs")).json()["logs"]) == 1


async def test_private_material_is_denied_to_another_user(client: AsyncClient) -> None:
    _, deck_id, card_id = await create_material(client)
    await register_and_login(client)
    for path in [f"/v1/deck/{deck_id}", f"/v1/card/{card_id}", f"/v1/review/queue?deck_id={deck_id}"]:
        response = await client.get(path)
        assert response.status_code == 403, response.text
    denied = await client.patch(f"/v1/card/{card_id}/question", json={"question": "Changed by stranger"})
    assert denied.status_code == 403, denied.text
    assert (await client.post(f"/v1/review/card/{card_id}", json={"rating": 4})).status_code == 403
    client.cookies.clear()
    assert (await client.get(f"/v1/card/{card_id}")).status_code == 401


async def test_material_edits_validation_and_deletion(client: AsyncClient) -> None:
    config_id, deck_id, card_id = await create_material(client)
    changes: list[tuple[str, dict[str, Any]]] = [
        (f"/v1/deck/{deck_id}/title", {"title": "Updated title"}),
        (f"/v1/deck/{deck_id}/privacy", {"is_public": True}),
        (f"/v1/deck-config/{config_id}/name", {"name": "Updated config"}),
        (f"/v1/deck-config/{config_id}/daily-limits", {"new_cards_per_day": 2, "max_reviews_per_day": 10}),
        (f"/v1/card/{card_id}/question", {"question": "Updated question"}),
        (f"/v1/card/{card_id}/image", {"image_path": "images/signal.png"}),
    ]
    for path, payload in changes:
        response = await client.patch(path, json=payload)
        assert response.status_code == 204, response.text
    tag = await client.post(f"/v1/card/{card_id}/tags", json={"tag": "lab"})
    assert tag.status_code == 204, tag.text
    config = (await client.get(f"/v1/deck-config/{config_id}")).json()
    assert config["name"] == "Updated config"
    assert config["daily_limits"]["new_cards_per_day"] == 2
    deck = (await client.get(f"/v1/deck/{deck_id}")).json()
    assert deck["title"] == "Updated title"
    assert deck["is_public"] is True
    card = (await client.get(f"/v1/card/{card_id}")).json()
    assert card["question"] == "Updated question"
    assert card["image_path"] == "images/signal.png"
    assert "lab" in card["tags"]
    assert (await client.patch(f"/v1/card/{card_id}/image", json={"image_path": None})).status_code == 204
    assert (await client.get(f"/v1/card/{card_id}")).json()["image_path"] is None
    assert (await client.patch(f"/v1/card/{card_id}/question", json={"question": ""})).status_code == 422
    assert (await client.post(f"/v1/review/card/{card_id}", json={"rating": 5})).status_code == 422
    assert (await client.delete(f"/v1/card/{card_id}")).status_code == 204
    assert (await client.get(f"/v1/card/{card_id}")).status_code == 404
    assert (await client.delete(f"/v1/deck/{deck_id}")).status_code == 204
    assert (await client.get(f"/v1/deck/{deck_id}")).status_code == 404
    assert (await client.delete(f"/v1/deck-config/{config_id}")).status_code == 204
    assert (await client.get(f"/v1/deck-config/{config_id}")).status_code == 404


async def test_new_card_daily_limit_is_applied_to_queue(client: AsyncClient) -> None:
    _, deck_id, _ = await create_material(client)
    second_card = await client.post(
        "/v1/card/",
        json={
            "deck_id": deck_id,
            "question": "Second question",
            "answerOptions": [{"text": "Answer", "isCorrect": True, "rationale": "Explanation"}],
            "hint": "",
        },
    )
    assert second_card.status_code == 201, second_card.text
    queue = await client.get("/v1/review/queue", params={"deck_id": deck_id})
    assert len(queue.json()["items"]) == 1
    selected = queue.json()["items"][0]["card_id"]
    assert (await client.post(f"/v1/review/card/{selected}", json={"rating": 4})).status_code == 200
    next_queue = await client.get("/v1/review/queue", params={"deck_id": deck_id})
    assert next_queue.json()["items"] == []


@pytest.mark.parametrize(
    ("name", "email", "issue"),
    [
        pytest.param("Valid-Name", "valid-address-longer-than-fifty-characters-123@example.com", "APP-01", id="email"),
        pytest.param("ValidUsernameLongerThan20", None, "APP-02", id="username"),
    ],
)
@pytest.mark.xfail(strict=True, reason="APP-01 / APP-02: DB columns are narrower than accepted registration input")
async def test_registration_accepts_valid_long_identity(
    client: AsyncClient, name: str, email: str | None, issue: str
) -> None:
    client.cookies.clear()
    response = await client.post(
        "/v1/auth/signup",
        json={"email": email or f"long_{uuid4().hex[:8]}@example.com", "name": name, "password": "LearningSecure123"},
    )
    assert response.status_code == 201, f"{issue}: {response.text}"
