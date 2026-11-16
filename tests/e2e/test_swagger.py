import os
from uuid import uuid4

import pytest
from playwright.sync_api import Page

from tests.e2e.pages import ApiErrorPage, SwaggerPage
from tests.integration.lab3.test_acceptance import card_body, config_body


def identity(page: Page, url: str) -> tuple[str, str]:
    email = f"ui_{uuid4().hex[:10]}@example.com"
    payload = {"email": email, "name": "UI-Learner", "password": "LearningSecure123"}
    response = page.request.post(url + "/v1/auth/signup", data=payload)
    assert response.status == 201, response.text()
    user = response.json()["id"]
    response = page.request.post(url + "/v1/auth/login", data={"email": email, "password": payload["password"]})
    assert response.status == 204, response.text()
    return user, email


def material(page: Page, url: str) -> tuple[str, str]:
    user, _ = identity(page, url)
    response = page.request.post(url + "/v1/deck-config/", data=config_body(user))
    assert response.status == 201, response.text()
    config = response.json()["id"]
    response = page.request.post(
        url + "/v1/deck/", data={"owner_id": user, "deck_config_id": config, "title": "UI rules"}
    )
    assert response.status == 201, response.text()
    deck = response.json()["id"]
    response = page.request.post(url + "/v1/card/", data=card_body(deck))
    assert response.status == 201, response.text()
    return deck, response.json()["id"]


def test_swagger_register_login_me_logout(ui_page: Page, api_url: str) -> None:
    # Arrange: each test has its own browser context and a unique identity.
    swagger = SwaggerPage(ui_page, api_url)
    swagger.open()
    email = f"ui_{uuid4().hex[:10]}@example.com"
    # Act: all business operations in this scenario are executed through Swagger controls.
    created = swagger.execute(
        "POST", "/v1/auth/signup", 201, {"email": email, "name": "UI-Learner", "password": "LearningSecure123"}
    )
    swagger.execute("POST", "/v1/auth/login", 204, {"email": email, "password": "LearningSecure123"})
    me = swagger.execute("GET", "/v1/auth/me", 200)
    # Assert: compare persisted identity and verify server-side logout.
    assert me["id"] == created["id"]
    assert me["email"] == email
    swagger.execute("POST", "/v1/auth/logout", 204)
    swagger.execute("GET", "/v1/auth/me", 401)


def test_swagger_rejects_empty_card_question(ui_page: Page, api_url: str) -> None:
    deck, _ = material(ui_page, api_url)
    swagger = SwaggerPage(ui_page, api_url)
    swagger.open()
    result = swagger.execute("POST", "/v1/card/", 422, card_body(deck, ""))
    assert result is not None
    assert "detail" in result
    response = ui_page.request.get(api_url + "/v1/card/", params={"deck_id": deck})
    assert response.status == 200
    assert len(response.json()["cards"]) == 1


def test_swagger_progress_lifecycle_and_reset(ui_page: Page, api_url: str) -> None:
    _, card = material(ui_page, api_url)
    swagger = SwaggerPage(ui_page, api_url)
    swagger.open()
    params = {"card_id": card}
    for rating, state in [(1, "learning"), (3, "learning"), (3, "review"), (1, "relearning"), (3, "review")]:
        result = swagger.execute("POST", "/v1/review/card/{card_id}", 200, {"rating": rating}, params)
        assert result["state"] == state
    swagger.execute("POST", "/v1/review/card/{card_id}/reset", 204, params=params)
    swagger.execute("GET", "/v1/review/card/{card_id}/progress", 404, params=params)
    logs = swagger.execute("GET", "/v1/review/card/{card_id}/logs", 200, params=params)
    assert len(logs["logs"]) == 5


def test_swagger_idor_and_anonymous_direct_url(ui_page: Page, api_url: str) -> None:
    _, card = material(ui_page, api_url)
    ui_page.context.clear_cookies()
    identity(ui_page, api_url)
    swagger = SwaggerPage(ui_page, api_url)
    swagger.open()
    result = swagger.execute("GET", "/v1/card/{card_id}", 403, params={"card_id": card})
    assert result is not None
    assert "description" in result
    ui_page.context.clear_cookies()
    ApiErrorPage(ui_page).open(api_url + f"/v1/card/{card}", 401)


def test_failure_screenshot_probe(ui_page: Page, api_url: str) -> None:
    if os.environ.get("LAB4_SCREENSHOT_PROBE") != "1":
        pytest.skip("Infrastructure probe is run separately; it is not a product test")
    SwaggerPage(ui_page, api_url).open()
    pytest.fail("Intentional failure: verifying that the screenshot hook saves evidence")
