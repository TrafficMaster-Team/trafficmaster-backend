"""Swagger UI tests use a disposable API started by scripts/run_lab4.py."""

import json
import os
import re
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from playwright.sync_api import Page


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    if not os.environ.get("LAB4_BASE_URL"):
        for item in items:
            if "/e2e/" in str(item.path):
                item.add_marker(pytest.mark.skip(reason="Run with scripts/run_lab4.py or set LAB4_BASE_URL"))


@pytest.fixture
def api_url() -> str:
    return os.environ["LAB4_BASE_URL"]


@pytest.fixture
def ui_page(page: Page, request: pytest.FixtureRequest) -> Page:
    page.set_default_timeout(15000)
    errors: list[str] = []
    network: list[dict[str, Any]] = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on("requestfailed", lambda req: network.append({"url": req.url, "failure": req.failure}))
    request.node.ui_errors = errors
    request.node.ui_network = network
    return page


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]) -> Iterator[None]:  # noqa: ARG001
    outcome = yield
    report = outcome.get_result()
    if report.when != "call":
        return
    page = item.funcargs.get("ui_page")
    if page is None:
        return
    output = Path(os.environ.get("LAB4_EVIDENCE_DIR", "test-results/lab4"))
    output.mkdir(parents=True, exist_ok=True)
    name = re.sub(r"[^a-zA-Z0-9_.-]", "_", item.name)
    screenshot = output / f"{name}.png"
    page.screenshot(path=str(screenshot))
    result = {
        "test": item.name,
        "status": report.outcome,
        "screenshot": screenshot.name,
        "console_errors": getattr(item, "ui_errors", []),
        "network_failures": getattr(item, "ui_network", []),
        "error": str(report.longrepr) if report.failed else None,
        "failure_screenshot": report.failed,
    }
    (output / f"{name}.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
