# Postman: коллекция и покрытие API

Коллекция: `postman/TrafficMaster.postman_collection.json`; environment: `postman/local.postman_environment.json`. Версия коллекции — Postman v2.1, импортируется в Postman через Import. Схема взята из реально работающего `/openapi.json`. В коллекции **129 запросов**, позитивно выполнены **55/55 операций**.

## Сценарии и проверки

Проверяются сервисные ручки, signup/login/me/logout, пароль и профиль, создание/чтение/изменение/удаление конфигураций, колод и карточек, каталог, копирование, очередь, preview, повторения, прогресс, история, статистика, reset. Дополнительно покрыты административные операции: создание пользователя, список, активация и смена роли — с отдельным тестовым superadmin. Это шире обязательных use case ЛР1.

У позитивных ответов проверяются HTTP-код, JSON Schema из OpenAPI и значения полей: сохранённые UUID/владельцы, конфигурация, содержимое карточки, новые значения после PATCH, состояния и даты повторений, изоляция истории, результаты удаления. Для 204 проверяется отсутствие тела; изменения проверяются последующими GET.

Негативные сценарии: неправильный пароль, повтор email, неверные email/имя/пароль, пустой вопрос, рейтинг 5, нулевой лимит, некорректный UUID, отсутствующая сущность, отсутствующий маршрут, прямой доступ гостя и подмена ID. Для ошибок дополнительно проверяется отсутствие stack trace, SQL и серверных путей. Проверка схем 401/422 намеренно остаётся красной при расхождении с опубликованным контрактом (APP-06).

## Связывание и изоляция сессий

Login возвращает **HttpOnly cookie**, а не JSON-токен. Test-script извлекает `access_token` из Set-Cookie и сохраняет отдельные `token_a`, `token_b`, `token_admin`; prerequest-script явно подставляет нужную cookie в дальнейшие запросы. UUID из create-ответов используются в следующих URL и JSON. Анонимные запросы не получают cookie.

Автоматический cookie jar отключён через `protocolProfileBehavior.disableCookies`: иначе Newman мог бы незаметно подставить сессию предыдущего пользователя. Это проверено фактическими ответами гостя 401 и правильными владельцами при работе двух пользователей. Каждый полный запуск создаёт уникальные email; сценарные запросы внутри коллекции намеренно связаны и выполняются по порядку.

## Запуск и отчёты

Автоматический одноразовый стенд: см. [README](README.md). При ручном запуске на собственном тестовом стенде укажите base_url и данные **тестового** superadmin в environment. Не импортируйте настоящие production-токены.

```bash
npm ci --prefix postman
npm test --prefix postman
```

Runner ЛР4 использует те же коллекцию и Newman с `-r cli,json,junit`; после завершения создаётся дополнительный HTML на основе native JSON. Для пересборки HTML и Markdown:

```bash
.venv/bin/python scripts/build_lab4_report.py
```

[HTML-отчёт](evidence/newman.html) · [JSON](evidence/newman.json) · [JUnit XML](evidence/newman.xml) · [CLI](evidence/newman.log).

Newman выполнил 129 HTTP-запросов без транспортных сбоев. Assertions: 352, из них 18 failed. Это не «все тесты прошли»: сбои связаны с найденными дефектами, [подробности](security.md).

## Трассировка всех операций

Для каждой строки ниже есть хотя бы один позитивный запрос с совпавшим кодом и всеми успешными assertions. Негативные запросы и их ошибки видны в полном HTML. Пара method+path определяет операцию; число URL без учёта метода было бы неверной метрикой.

| Операция | Позитивный запрос | Результат |
| --- | --- | --- |
| `DELETE /v1/card/{card_id}` | [R121](evidence/newman.html#R121) | Passed, HTTP 204 |
| `DELETE /v1/card/{card_id}/tags/{tag}` | [R039](evidence/newman.html#R039) | Passed, HTTP 204 |
| `DELETE /v1/deck-config/{deck_config_id}` | [R125](evidence/newman.html#R125) | Passed, HTTP 204 |
| `DELETE /v1/deck/{deck_id}` | [R123](evidence/newman.html#R123) | Passed, HTTP 204 |
| `DELETE /v1/user/{user_id}` | [R112](evidence/newman.html#R112) | Passed, HTTP 204 |
| `DELETE /v1/user/{user_id}/admin` | [R106](evidence/newman.html#R106) | Passed, HTTP 204 |
| `GET /` | [R001](evidence/newman.html#R001) | Passed, HTTP 200 |
| `GET /healthcheck/live` | [R002](evidence/newman.html#R002) | Passed, HTTP 200 |
| `GET /healthcheck/ready` | [R003](evidence/newman.html#R003) | Passed, HTTP 200 |
| `GET /v1/auth/me` | [R006](evidence/newman.html#R006) | Passed, HTTP 200 |
| `GET /v1/card/` | [R033](evidence/newman.html#R033) | Passed, HTTP 200 |
| `GET /v1/card/{card_id}` | [R032](evidence/newman.html#R032) | Passed, HTTP 200 |
| `GET /v1/deck-config/` | [R013](evidence/newman.html#R013) | Passed, HTTP 200 |
| `GET /v1/deck-config/{deck_config_id}` | [R012](evidence/newman.html#R012) | Passed, HTTP 200 |
| `GET /v1/deck/` | [R024](evidence/newman.html#R024) | Passed, HTTP 200 |
| `GET /v1/deck/public` | [R097](evidence/newman.html#R097) | Passed, HTTP 200 |
| `GET /v1/deck/{deck_id}` | [R023](evidence/newman.html#R023) | Passed, HTTP 200 |
| `GET /v1/review/card/{card_id}/logs` | [R054](evidence/newman.html#R054) | Passed, HTTP 200 |
| `GET /v1/review/card/{card_id}/preview` | [R046](evidence/newman.html#R046) | Passed, HTTP 200 |
| `GET /v1/review/card/{card_id}/progress` | [R053](evidence/newman.html#R053) | Passed, HTTP 200 |
| `GET /v1/review/deck/{deck_id}/stats` | [R056](evidence/newman.html#R056) | Passed, HTTP 200 |
| `GET /v1/review/logs` | [R055](evidence/newman.html#R055) | Passed, HTTP 200 |
| `GET /v1/review/queue` | [R045](evidence/newman.html#R045) | Passed, HTTP 200 |
| `GET /v1/user/` | [R102](evidence/newman.html#R102) | Passed, HTTP 200 |
| `GET /v1/user/stats` | [R111](evidence/newman.html#R111) | Passed, HTTP 200 |
| `GET /v1/user/{user_id}` | [R103](evidence/newman.html#R103) | Passed, HTTP 200 |
| `PATCH /v1/card/{card_id}/content` | [R035](evidence/newman.html#R035) | Passed, HTTP 204 |
| `PATCH /v1/card/{card_id}/deck` | [R041](evidence/newman.html#R041) | Passed, HTTP 204 |
| `PATCH /v1/card/{card_id}/image` | [R036](evidence/newman.html#R036) | Passed, HTTP 204 |
| `PATCH /v1/card/{card_id}/question` | [R034](evidence/newman.html#R034) | Passed, HTTP 204 |
| `PATCH /v1/deck-config/{deck_config_id}/advanced` | [R017](evidence/newman.html#R017) | Passed, HTTP 204 |
| `PATCH /v1/deck-config/{deck_config_id}/daily-limits` | [R015](evidence/newman.html#R015) | Passed, HTTP 204 |
| `PATCH /v1/deck-config/{deck_config_id}/lapses` | [R018](evidence/newman.html#R018) | Passed, HTTP 204 |
| `PATCH /v1/deck-config/{deck_config_id}/name` | [R014](evidence/newman.html#R014) | Passed, HTTP 204 |
| `PATCH /v1/deck-config/{deck_config_id}/new-cards` | [R016](evidence/newman.html#R016) | Passed, HTTP 204 |
| `PATCH /v1/deck/{deck_id}/config` | [R027](evidence/newman.html#R027) | Passed, HTTP 204 |
| `PATCH /v1/deck/{deck_id}/description` | [R026](evidence/newman.html#R026) | Passed, HTTP 204 |
| `PATCH /v1/deck/{deck_id}/privacy` | [R096](evidence/newman.html#R096) | Passed, HTTP 204 |
| `PATCH /v1/deck/{deck_id}/title` | [R025](evidence/newman.html#R025) | Passed, HTTP 204 |
| `PATCH /v1/user/{user_id}/activate` | [R107](evidence/newman.html#R107) | Passed, HTTP 204 |
| `PATCH /v1/user/{user_id}/admin` | [R104](evidence/newman.html#R104) | Passed, HTTP 204 |
| `PATCH /v1/user/{user_id}/email` | [R109](evidence/newman.html#R109) | Passed, HTTP 204 |
| `PATCH /v1/user/{user_id}/password` | [R114](evidence/newman.html#R114) | Passed, HTTP 204 |
| `PATCH /v1/user/{user_id}/username` | [R108](evidence/newman.html#R108) | Passed, HTTP 204 |
| `POST /v1/auth/login` | [R005](evidence/newman.html#R005) | Passed, HTTP 204 |
| `POST /v1/auth/logout` | [R118](evidence/newman.html#R118) | Passed, HTTP 204 |
| `POST /v1/auth/signup` | [R004](evidence/newman.html#R004) | Passed, HTTP 201 |
| `POST /v1/card/` | [R031](evidence/newman.html#R031) | Passed, HTTP 201 |
| `POST /v1/card/{card_id}/tags` | [R037](evidence/newman.html#R037) | Passed, HTTP 204 |
| `POST /v1/deck-config/` | [R010](evidence/newman.html#R010) | Passed, HTTP 201 |
| `POST /v1/deck/` | [R021](evidence/newman.html#R021) | Passed, HTTP 201 |
| `POST /v1/deck/{deck_id}/copy` | [R098](evidence/newman.html#R098) | Passed, HTTP 201 |
| `POST /v1/review/card/{card_id}` | [R048](evidence/newman.html#R048) | Passed, HTTP 200 |
| `POST /v1/review/card/{card_id}/reset` | [R057](evidence/newman.html#R057) | Passed, HTTP 204 |
| `POST /v1/user/` | [R101](evidence/newman.html#R101) | Passed, HTTP 201 |

Инструмент: [официальные параметры Newman и reporters](https://learning.postman.com/docs/collections/using-newman-cli/newman-options). Newman исполняет Postman-коллекцию локально; вход в облачный аккаунт Postman и отправка данных в облако не использовались.
