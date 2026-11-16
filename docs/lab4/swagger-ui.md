# Playwright через Swagger UI

Отдельного frontend нет. UI-автоматизация выполняет операции через существующие кнопки и поля Swagger, без проверки вёрстки, мобильных размеров или трёх браузеров. Используется один Chromium, поставляемый Playwright.

## Реализация рекомендаций

- **Page Object:** `tests/e2e/pages.py` содержит SwaggerPage (открытие документации, выбор операции, Try it out, JSON/параметры, Execute, ожидание ответа) и ApiErrorPage (прямой URL и безопасный отказ).
- **Независимость:** pytest-playwright создаёт отдельный browser context на тест; каждый тест регистрирует уникального пользователя и создаёт свой материал. Подготовка данных для сценариев обучения/валидации выполняется API-вызовами, целевые действия — через Swagger UI.
- **Явные ожидания:** Playwright expect для видимости/редактируемости/кликабельности и page.expect_response для соответствующих method/path; фиксированных sleep/wait_for_timeout в UI-тестах нет.
- **Скриншот при падении:** hook pytest_runtest_makereport сохраняет screenshot, статус, ошибку и диагностические события. Скриншоты успешных тестов также приложены.
- **Проверка механизма:** отдельный screenshot_probe намеренно падает после открытия Swagger. Его код завершения 1 и сохранённый PNG подтверждены runner. Это ожидаемое падение инфраструктурной проверки, не дефект приложения и не пятый пользовательский UI-сценарий.

В обычном `pytest tests/` эти тесты пропускаются при отсутствии LAB4_BASE_URL, поскольку им нужен отдельный сетевой стенд. Для полного воспроизведения используйте scripts/run_lab4.py; для готового стенда:

```bash
LAB4_BASE_URL=http://127.0.0.1:8080 .venv/bin/pytest tests/e2e -q --no-cov --browser chromium -k 'not failure_screenshot_probe'
```

## Выполненные сценарии

| Тест | Проверка | Статус | Скриншот / данные |
| --- | --- | --- | --- |
| `test_swagger_idor_and_anonymous_direct_url[chromium]` | Действия и assertions в test_swagger.py | passed | [PNG](evidence/ui/test_swagger_idor_and_anonymous_direct_url_chromium_.png), [JSON](evidence/ui/test_swagger_idor_and_anonymous_direct_url_chromium_.json) |
| `test_swagger_progress_lifecycle_and_reset[chromium]` | Действия и assertions в test_swagger.py | passed | [PNG](evidence/ui/test_swagger_progress_lifecycle_and_reset_chromium_.png), [JSON](evidence/ui/test_swagger_progress_lifecycle_and_reset_chromium_.json) |
| `test_swagger_register_login_me_logout[chromium]` | Действия и assertions в test_swagger.py | passed | [PNG](evidence/ui/test_swagger_register_login_me_logout_chromium_.png), [JSON](evidence/ui/test_swagger_register_login_me_logout_chromium_.json) |
| `test_swagger_rejects_empty_card_question[chromium]` | Действия и assertions в test_swagger.py | passed | [PNG](evidence/ui/test_swagger_rejects_empty_card_question_chromium_.png), [JSON](evidence/ui/test_swagger_rejects_empty_card_question_chromium_.json) |

Итого: **4/4 пользовательских UI-сценария Passed**. Проверка сохранения скриншота при падении: **True**. [JUnit](evidence/ui.xml), [stdout](evidence/playwright.log), [ожидаемое падение probe](evidence/screenshot-probe.log).

[PNG намеренно упавшего теста](evidence/screenshot-probe/test_failure_screenshot_probe_chromium_.png) · [его результат JSON](evidence/screenshot-probe/test_failure_screenshot_probe_chromium_.json).

При отладке устранены ошибки локатора (заголовок Code отделён от фактического статуса), а также необоснованное ожидание description вместо штатного detail в прямом браузерном отказе. Несоответствие OpenAPI при этом продолжает выявляться отдельными schema-тестами в Postman; оно не скрыто изменением UI-ожидания.

Подход основан на [Page Object Models Playwright](https://playwright.dev/python/docs/pom) и встроенных ожиданиях.
