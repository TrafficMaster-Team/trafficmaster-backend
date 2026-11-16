# Матрица трассируемости ЛР1…ЛР5

Актуальная SRS 1.1: **38 требований** — 3 BR, 7 UR, 20 FR, 8 NFR. NFR-07/08 добавлены до измерений ЛР5. Базовый набор SRS 1.0 отдельно содержит 36 требований. [Машиночитаемый результат](evidence/traceability-summary.json).

## Методика подсчёта

Инвентаризация: 667 записей — 533 отдельных pytest node IDs с параметризациями, 129 запросов Postman и 5 измеренных ступеней Locust. TC-001…042 — **алиасы уже учтённых** pytest-параметров, не дополнительные 42 теста. 352 assertions Postman не выдаются за 352 отдельных тест-кейса. LOAD-строка — один экспериментальный кейс, а не каждый его HTTP-запрос.

Покрытие требования = наличие хотя бы одного связанного теста / эксперимента с сохранённым доказательством; покрытие **не равно** успешной приёмке и не означает проверки всех сочетаний входов. Низкоуровневые проверки параметров/инвариантов дополняют прямые сценарии, а не заменяют их. Для составных BR/UR назначены явные интеграционные сценарии целиком; произвольный unit-тест не назначается всем бизнес-целям автоматически.

**Покрытие требований тестами: 38/38 ×100 = 100.00%.** Исходный набор SRS 1.0 также покрыт: 36/36=100%. Формальные 42 карточки ЛР3 покрывают все FR: 20/20=100%. Таблица ниже использует полный набор работ ЛР2…5; метрика покрытия кода 90,08% из ЛР2 имеет другой смысл и не подставляется в эту формулу.

**Требования без тестов:** не обнаружены в пределах текущей явно ограниченной SRS (0). Это не означает полноты самой спецификации: пробелы SRS выявлены по несвязанным тестам ниже.

## Матрица

ЛР1 — определение каждого требования в [SRS](../requirements.md) и исходной [верификации](../verification.md); ЛР2 — pytest unit/integration; ЛР3 — чек-лист и документированные TC; ЛР4 — Postman/Swagger/security; ЛР5 — нагрузка, статическая проверка и данная трассировка. Линтер проверяет качество кода всего проекта и не подменяет функциональный кейс конкретного FR.

| Требование | Pytest (ЛР2/4) | TC ЛР3 | Postman ЛР4 | Load ЛР5 | Дефекты / приёмка |
| --- | --- | --- | --- | --- | --- |
| BR-01 | 1; `tests/integration/http/v1/routes/test_learning.py::test_learning_lifecycle_and_history` | — | — | — | — |
| BR-02 | 1; `tests/integration/http/v1/routes/test_learning.py::test_public_deck_has_independent_user_progress_and_can_be_copied` | — | — | — | — |
| BR-03 | 1; `tests/integration/http/v1/routes/test_learning.py::test_public_deck_has_independent_user_progress_and_can_be_copied` | — | — | — | APP-04 |
| UR-01 | 4; `tests/e2e/test_swagger.py::test_swagger_register_login_me_logout[chromium]` | — | — | — | APP-01, APP-02 |
| UR-02 | 1; `tests/integration/http/v1/routes/test_learning.py::test_learning_lifecycle_and_history` | — | — | — | — |
| UR-03 | 2; `tests/integration/http/v1/routes/test_learning.py::test_private_material_is_denied_to_another_user` | — | — | — | APP-07 |
| UR-04 | 1; `tests/integration/http/v1/routes/test_learning.py::test_public_deck_has_independent_user_progress_and_can_be_copied` | — | — | — | APP-04 |
| UR-05 | 2; `tests/e2e/test_swagger.py::test_swagger_progress_lifecycle_and_reset[chromium]` | — | — | — | APP-03 |
| UR-06 | 2; `tests/e2e/test_swagger.py::test_swagger_progress_lifecycle_and_reset[chromium]` | — | — | — | — |
| UR-07 | 3; `tests/e2e/test_swagger.py::test_swagger_register_login_me_logout[chromium]` | — | — | — | — |
| FR-01 | 81; `tests/e2e/test_swagger.py::test_swagger_register_login_me_logout[chromium]` | TC-001, TC-002, TC-041, TC-042 | R004, R008, R009, R061 | — | APP-01, APP-02, APP-06; есть открытые дефекты, не принято полностью |
| FR-02 | 13; `tests/e2e/test_swagger.py::test_swagger_register_login_me_logout[chromium]` | TC-003, TC-004 | R005, R006, R007, R062, R066, R100, R115, R116, R117, R119, R120, R128 | — | — |
| FR-03 | 5; `tests/e2e/test_swagger.py::test_swagger_register_login_me_logout[chromium]` | TC-005, TC-006 | R118 | — | — |
| FR-04 | 6; `tests/integration/http/v1/routes/test_auth.py::test_changing_password_revokes_existing_session` | TC-007, TC-008 | R087, R114 | — | — |
| FR-05 | 36; `tests/integration/http/v1/routes/test_learning.py::test_learning_lifecycle_and_history` | TC-009, TC-010 | R010, R011, R012, R019, R063, R070, R079, R091 | — | — |
| FR-06 | 8; `tests/integration/http/v1/routes/test_learning.py::test_material_edits_validation_and_deletion` | TC-011, TC-012 | R014, R015, R020, R086 | — | — |
| FR-07 | 14; `tests/integration/http/v1/routes/test_learning.py::test_learning_lifecycle_and_history` | TC-013, TC-014 | R021, R022, R023, R028, R029, R030, R064, R068, R077, R099 | — | APP-06 |
| FR-08 | 9; `tests/integration/http/v1/routes/test_learning.py::test_material_edits_validation_and_deletion` | TC-015, TC-016 | R025, R084, R096 | — | — |
| FR-09 | 6; `tests/integration/http/v1/routes/test_learning.py::test_public_deck_has_independent_user_progress_and_can_be_copied` | TC-017, TC-018 | R097 | — | — |
| FR-10 | 8; `tests/integration/http/v1/routes/test_learning.py::test_public_deck_has_independent_user_progress_and_can_be_copied` | TC-019, TC-020 | R098 | — | APP-04 |
| FR-11 | 39; `tests/e2e/test_swagger.py::test_swagger_rejects_empty_card_question[chromium]` | TC-021, TC-022 | R031, R032, R033, R038, R043, R044, R065, R069, R078, R092, R094, R095, R122 | — | APP-03, APP-06 |
| FR-12 | 21; `tests/integration/http/v1/routes/test_learning.py::test_material_edits_validation_and_deletion` | TC-023, TC-024 | R034, R036, R037, R040, R085 | — | — |
| FR-13 | 5; `tests/integration/http/v1/routes/test_learning.py::test_learning_lifecycle_and_history` | TC-025, TC-026 | R045, R071, R080 | — | APP-03 |
| FR-14 | 5; `tests/integration/http/v1/routes/test_learning.py::test_new_card_daily_limit_is_applied_to_queue` | TC-027, TC-028 | — | — | — |
| FR-15 | 74; `tests/e2e/test_swagger.py::test_swagger_progress_lifecycle_and_reset[chromium]` | TC-029, TC-030 | R048, R049, R050, R051, R052, R060, R088 | — | APP-06 |
| FR-16 | 5; `tests/integration/http/v1/routes/test_learning.py::test_learning_lifecycle_and_history` | TC-031, TC-032 | R046, R073, R081 | — | — |
| FR-17 | 9; `tests/integration/http/v1/routes/test_learning.py::test_public_deck_has_independent_user_progress_and_can_be_copied` | TC-033, TC-034 | R047, R053, R054, R055, R058, R059, R072, R074, R082 | — | DOC-03 |
| FR-18 | 5; `tests/integration/http/v1/routes/test_learning.py::test_learning_lifecycle_and_history` | TC-035, TC-036 | R056, R075, R083 | — | — |
| FR-19 | 6; `tests/e2e/test_swagger.py::test_swagger_progress_lifecycle_and_reset[chromium]` | TC-037, TC-038 | R057, R089 | — | DOC-03 |
| FR-20 | 10; `tests/integration/http/v1/routes/test_learning.py::test_material_edits_validation_and_deletion` | TC-039, TC-040 | R121, R123, R124, R125, R126 | — | — |
| NFR-01 | 1; `tests/unit/infrastructure/adapters/common/test_password_hasher_bcrypt.py::test_password_hash_is_salted_and_verification_depends_on_password_and_pepper` | — | — | — | — |
| NFR-02 | 41; `tests/e2e/test_swagger.py::test_swagger_idor_and_anonymous_direct_url[chromium]` | — | R007, R066, R067, R068, R069, R070, R071, R072, R073, R074, R075, R076, R077, R078, R079, R080, R081, R082, R083, R084, R085, R086, R087, R088, R089, R090, R091, R092, R095, R115, R116, R119, R127, R128 | — | APP-05, APP-06, APP-07; есть открытые дефекты, не принято полностью |
| NFR-03 | 11; `tests/e2e/test_swagger.py::test_swagger_register_login_me_logout[chromium]` | — | R005, R007, R062, R087, R100, R114, R116, R117, R118, R120 | — | — |
| NFR-04 | 10; `tests/integration/http/v1/common/test_healthcheck.py::test_liveness_returns_ok` | — | R002, R003 | LOAD-RECOVERY | DOC-04 |
| NFR-05 | 8; `tests/unit/setup/test_cfg_asgi.py::test_asgi_rejects_wildcard_origin_with_credentials` | — | — | — | — |
| NFR-06 | 5; `tests/integration/http/v1/routes/test_learning.py::test_learning_lifecycle_and_history` | — | — | — | DOC-01, DOC-02, DOC-03 |
| NFR-07 | — | — | — | LOAD-BASE, LOAD-TARGET | PERF-01; целевой SLO Failed |
| NFR-08 | — | — | — | LOAD-STRESS-25, LOAD-STRESS-50, LOAD-RECOVERY | —; восстановление Passed |

Полный список всех связей находится в [test-inventory.csv](evidence/test-inventory.csv) / [JSON](evidence/test-inventory.json). Для каждого теста сохранены основание связи, статус и путь доказательства. Unit-статусы подтверждены свежим прогоном ЛР5 (470 passed), интеграционные/Swagger — сохранёнными прогонами ЛР3/4. Общий полный набор не выдаётся за новый прогон ЛР5; актуальная инвентаризация получена `pytest --collect-only`. Нагрузочные кейсы выполнены в ЛР5.

## Тесты без требования

**165 записей не связаны ни с одним точным SRS-требованием.** Они намеренно не прикреплены к случайному FR ради улучшения метрики. Полный перечень и причины: [несвязанные тесты](orphan-tests.md). Категории: Infrastructure=3, SRS gap=77, Technical=55, Technical configuration regression=30.

Примеры недостающего объёма SRS: административные CRUD/роли/активация, изменение профиля, изменение шагов/коэффициентов конфигурации, перемещение и изменение содержимого карточки, удаление тега, описание/переназначение конфигурации колоды, агрегаты пользователя, единый формат и безопасные сообщения ошибок. Эти функции реализованы и проверяются, но не описаны точными обязательными FR/NFR текущей SRS. Категория SRS gap означает отсутствие точной связи, а не безусловную обязанность расширить продукт: часть администрирования ранее явно вынесена за обязательные UR и может оставаться дополнительной регрессией. Решение — согласовать новые требования либо явно исключить возможности из продукта; автоматически добавлять требования после теста только ради 100% нельзя.

Классификация текущего инвентаря: **77 тестов** указывают на недостающие точные требования; **88 тестов** технические/инфраструктурные и избыточны именно для продуктовой SRS-матрицы, но полезны в инженерной регрессии. Это не указание удалять их из общего набора.

Часть orphan-тестов — полезная техническая регрессия идентичности, immutable value objects и настроек; screenshot_probe подтверждает тестовую инфраструктуру. Отсутствие связи с SRS не делает такие тесты автоматически избыточными для инженерной регрессии и не является указанием их удалить.

## Связь с выполненными работами по заданиям

| Задание | Выполненные работы / доказательства | Связь с SRS |
| --- | --- | --- |
| ЛР1 | [Спецификация и use cases](../requirements.md), [верификация](../verification.md), [диаграмма состояний](../card-progress-lifecycle.md), ISSUES.md | BR/UR/FR/NFR, определение ожидаемого поведения; SRS 1.0 — историческая основа. |
| ЛР2 | [Unit/integration/scenario и покрытие кода](../lab2-verification.md): 90,08% без миграций/конфигурации | Доменные и прикладные правила, БД/HTTP, переходы FR-15/19. |
| ЛР3 | [План](../lab3/test-plan.md), [чек-лист](../lab3/checklist.md), [42 кейса](../lab3/test-cases.md), [протокол со снимками](../lab3/execution.md) | Все FR; составные пользовательские сценарии и метрики. |
| ЛР4 | [Postman 129 запросов](../lab4/api.md), [безопасность](../lab4/security.md), [Swagger Page Object и screenshot-on-failure](../lab4/swagger-ui.md) | API и NFR-01…06; новые дефекты APP-05…07. Вёрстка/мобильные размеры/3 браузера неприменимы: frontend отсутствует. |
| ЛР5 | [План](test-plan.md), [Locust + графики](results.md), [линтер](static-analysis.md), данная матрица и [orphan inventory](orphan-tests.md) | Экспериментальные NFR-07/08, проверка связей всех 38 требований. |

Статус «работа выполнена» означает наличие материала и фактических результатов, включая Failed, а не автоматическую приёмку продукта. Требования самого учебного задания (например, наличие линтера или screenshot hook) не добавлены в знаменатель SRS 38 без явного согласования.

## Зоны риска по дефектам

Считается число **различных ID дефектов**, включая исправленные исторические; один APP-06 даёт 14 schema failures, но остаётся одним дефектом. DOC-дефекты окружения/документации показаны отдельно от функциональных. Связь дефекта с несколькими требованиями допустима; суммы по строкам нельзя считать количеством уникальных дефектов проекта.

| Требование | Все связанные дефекты | Критические открытые | Интерпретация |
| --- | --- | --- | --- |
| **FR-01** | 3: APP-01, APP-02, APP-06 | — | Валидация регистрации и контракт ошибок |
| **NFR-02** | 3: APP-05, APP-06, APP-07 | APP-05, APP-07 | Контроль полномочий: высший приоритет исправления |
| **NFR-06** | 3: DOC-01, DOC-02, DOC-03 | — | Воспроизводимость запуска и документация схемы; не три новых сбоя БД |
| FR-11 | 2: APP-03, APP-06 | — | Исторические/документальные и функциональные расхождения; см. ID |
| UR-01 | 2: APP-01, APP-02 | — | Исторические/документальные и функциональные расхождения; см. ID |
| BR-03 | 1: APP-04 | — | Исторические/документальные и функциональные расхождения; см. ID |
| FR-07 | 1: APP-06 | — | Исторические/документальные и функциональные расхождения; см. ID |
| FR-10 | 1: APP-04 | — | Исторические/документальные и функциональные расхождения; см. ID |
| FR-13 | 1: APP-03 | — | Исторические/документальные и функциональные расхождения; см. ID |
| FR-15 | 1: APP-06 | — | Исторические/документальные и функциональные расхождения; см. ID |
| FR-17 | 1: DOC-03 | — | Исторические/документальные и функциональные расхождения; см. ID |
| FR-19 | 1: DOC-03 | — | Исторические/документальные и функциональные расхождения; см. ID |
| NFR-04 | 1: DOC-04 | — | Исторические/документальные и функциональные расхождения; см. ID |
| NFR-07 | 1: PERF-01 | — | Целевой локальный SLO задержки не выполнен; PERF-01 |
| UR-03 | 1: APP-07 | APP-07 | Контроль полномочий: высший приоритет исправления |
| UR-04 | 1: APP-04 | — | Исторические/документальные и функциональные расхождения; см. ID |
| UR-05 | 1: APP-03 | — | Исторические/документальные и функциональные расхождения; см. ID |

Наиболее существенная зона — NFR-02: два открытых S2 по полномочиям. FR-01 также имеет несколько открытых расхождений на границах и в контракте. NFR-06 получает несколько DOC-связей по воспроизводимости, что не означает три новых runtime-сбоя БД. Новые SLO ЛР5 оцениваются измерениями; намеренное превышение целевого SLO при стрессе за пределами 10 VU не объявляется дефектом NFR-07 автоматически.
