"""Page Objects for the application's existing Swagger interface."""

import json
from urllib.parse import urlsplit

from playwright.sync_api import Locator, Page, expect


class SwaggerPage:
    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url

    def open(self) -> None:
        self.page.goto(self.base_url + "/docs")
        expect(self.page.get_by_role("heading", name="TrafficMaster API", exact=False)).to_be_visible()
        expect(self.page.locator(".opblock").first).to_be_visible()

    def operation(self, method: str, path: str) -> Locator:
        return self.page.locator(f".opblock.opblock-{method.lower()}").filter(
            has=self.page.locator(f'[data-path="{path}"]')
        )

    def execute(
        self,
        method: str,
        path: str,
        expected: int,
        body: dict[str, object] | None = None,
        params: dict[str, str] | None = None,
    ) -> dict[str, object] | None:
        operation = self.operation(method, path)
        if "is-open" not in (operation.get_attribute("class") or ""):
            operation.locator(".opblock-summary").click()
        try_button = operation.get_by_role("button", name="Try it out", exact=True)
        if try_button.is_visible():
            try_button.click()
        if body is not None:
            text = operation.locator("textarea.body-param__text")
            expect(text).to_be_editable()
            text.fill(json.dumps(body))
        actual_path = path
        for key, value in (params or {}).items():
            field = operation.locator(f'tr[data-param-name="{key}"] input')
            expect(field).to_be_editable()
            field.fill(value)
            actual_path = actual_path.replace("{" + key + "}", value)
        button = operation.get_by_role("button", name="Execute", exact=True)
        expect(button).to_be_enabled()
        with self.page.expect_response(
            lambda response: response.request.method == method and urlsplit(response.url).path == actual_path
        ) as response_info:
            button.click()
        response = response_info.value
        assert response.status == expected, response.text()
        expect(operation.locator(".live-responses-table .response-col_status:not(.col_header)")).to_contain_text(
            str(expected)
        )
        return response.json() if response.body() else None


class ApiErrorPage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def open(self, url: str, status: int) -> None:
        response = self.page.goto(url)
        assert response is not None
        assert response.status == status
        expect(self.page.locator("body")).to_contain_text("Not authenticated")
        assert "Traceback" not in self.page.locator("body").inner_text()
