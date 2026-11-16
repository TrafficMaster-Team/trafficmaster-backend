# Верификация требований и протокол проверки

> Последующая проверка ЛР4 обнаружила APP-05/07 (повышение роли и перенос карточки в чужую приватную колоду) и APP-06 (контракт ошибок). Успешные проверки ниже относятся к перечисленным сценариям; полная приёмка NFR-02 сейчас не подтверждена. Актуальные ограничения: [безопасность ЛР4](lab4/security.md).

Дата: 16.11.2026. Базовая спецификация: [requirements.md](requirements.md), версия 1.0. Проверялись текущие исходники рабочего дерева. Требования сформулированы до итогового прогона; обнаруженные расхождения сохранены в `ISSUES.md`, включая исправленные дефекты.

## Окружение и воспроизведение

Python 3.13.5; зависимости из `uv.lock`, uv 0.9.26; Docker 29.1.3; PostgreSQL 16 и Redis 7 в Testcontainers. Локальный Compose использует PostgreSQL 16 и Redis 8.0.2; совместимость именно этого состава проверяется отдельно от интеграционного набора. Глобальный uv 0.13.5 не заменялся: для синхронизации использована изолированная версия 0.9.26.

```bash
uv sync --locked --group dev --group docs
.venv/bin/pytest tests/unit -q --no-cov
.venv/bin/pytest tests/integration -q --no-cov -rx
.venv/bin/ruff check --no-fix .
.venv/bin/ruff format --check .
.venv/bin/mypy --config-file pyproject.toml
.venv/bin/mkdocs build --strict
```

`--no-cov` отключает только отчёт покрытия; покрытие кода в этом протоколе не измеряется. Интеграционные тесты требуют Docker и создают временную БД с миграциями. Тест Uvicorn поднимает отдельный процесс на свободном localhost-порту и проверяет реальные сетевые HTTP-запросы.

## Обозначения доказательств

| Код | Исполняемое доказательство |
| --- | --- |
| I-AUTH | `tests/integration/http/v1/routes/test_auth.py`: signup/login/me/logout, повтор email, неизвестный email, смена пароля и восстановление отозванной cookie. |
| I-LIFE | `tests/integration/http/v1/routes/test_learning.py`::test_learning_lifecycle_and_history: конфигурация → колода → карточка → очередь → preview → оценки → прогресс/история/статистика → reset → новый прогресс. |
| I-SHARE | тот же файл ::test_public_deck_has_independent_user_progress_and_can_be_copied: два пользователя, независимые состояния/история, копирование карточек. |
| I-ACCESS | тот же файл ::test_private_material_is_denied_to_another_user: 401/403 на чтение, изменение и повторение. |
| I-EDIT | тот же файл ::test_material_edits_validation_and_deletion: сохранение изменений, 422 на неверный вопрос/оценку, удаление и 404. |
| I-LIMIT | тот же файл ::test_new_card_daily_limit_is_applied_to_queue: две карточки при дневном лимите 1. |
| I-LONG | тот же файл ::test_registration_accepts_valid_long_identity[email/username]: два известных дефекта, strict xfail. Для обычного падающего воспроизведения: `pytest tests/integration/http/v1/routes/test_learning.py -k valid_long_identity --runxfail --no-cov`. |
| I-RUN | `tests/integration/test_runtime.py`::test_uvicorn_serves_docs_and_health_with_real_dependencies. |
| U-QUEUE | `tests/unit/application/queries/card_progress/test_read_review_queue.py`: порядок learning/review/new и остановка на limit; зависимости gateway подменены. |
| U-SRS | `tests/unit/domain/card_progress/services/test_card_progress_service.py`: интервалы, границы, шаги и матрица 4 состояния × 4 оценки; пустое переучивание. |
| U-PREVIEW | `tests/unit/application/queries/card_progress/test_preview_review_intervals.py`: все четыре оценки; отсутствие сохранения дополнительно подтверждает I-LIFE. |
| U-DECK | `tests/unit/infrastructure/adapters/persistence/test_alchemy_deck_gateway.py`: SQL-фильтр публичности и пагинация. |
| U-HASH | `tests/unit/infrastructure/adapters/common/test_password_hasher_bcrypt.py`: реальный bcrypt, соль, неверные пароль/pepper. |
| U-HEALTH | `tests/unit/infrastructure/adapters/common/test_system_health_checker.py` и `tests/unit/presentation/http/v1/common/test_healthcheck.py`: внедрение отказов и тайм-аутов через stubs. |
| U-CONFIG | `tests/unit/setup/test_cfg_settings.py`: безопасные/небезопасные production-настройки. |

## Матрица верификации

«Пройдено» относится к указанному критерию и уровню проверки. «Не пройдено» — зафиксированное расхождение, а не отсутствие способа проверки. Unit-тесты не выданы за проверку сетевого окружения.

| ID | Метод / доказательство | Критерий проверки | Фактический результат / статус |
| --- | --- | --- | --- |
| BR-01 | HTTP, I-LIFE | Завершить цепочку подготовки и повторения, затем прочитать историю. | Цепочка выполнена, 5 записей истории; пройдено. |
| BR-02 | HTTP, I-SHARE | Пользователи оценивают одну карточку по-разному и видят собственные данные. | У первого REVIEW, у второго LEARNING, ID и история различаются; пройдено. |
| BR-03 | HTTP, I-SHARE | Найти публичную колоду и скопировать с карточками другому владельцу. | Приватная копия и новые ID; пройдено после APP-04. |
| UR-01 | HTTP, I-AUTH + I-LONG | Регистрация/вход, повтор email, допустимые длинные данные. | Обычные данные работают; длинные отклоняются на сохранении. Не пройдено полностью: APP-01/02. |
| UR-02 | HTTP, I-LIFE + I-EDIT | Создать и прочитать материал; пустой вопрос отклонить. | Создано; неверный вопрос → 422; пройдено. |
| UR-03 | HTTP, I-EDIT + I-ACCESS | Изменить/удалить свой материал, отказать постороннему. | Значения сохранены, 204/404 и 403; пройдено. |
| UR-04 | HTTP, I-SHARE | Каталог и собственная копия чужой публичной колоды. | Копия принадлежит второму пользователю; пройдено. |
| UR-05 | HTTP + доменные тесты, I-LIFE, I-LIMIT, U-SRS | Очередь, preview, оценки, дата повторения и лимит. | Номинальный цикл и ограничения проверены; пройдено после APP-03. |
| UR-06 | HTTP, I-LIFE + I-SHARE | История/статистика/сброс и изоляция. | Сброс убирает прогресс, не историю; пройдено. |
| UR-07 | HTTP, I-AUTH | Восстановленная старая cookie после logout/смены пароля не даёт доступ. | 401, новый пароль подходит; пройдено. |
| FR-01 | HTTP, I-AUTH + I-LONG | 201 для допустимых данных, 409 на дубликат. | Обычная регистрация/дубликат проходят; длинные email/имя → 401 вместо 201. Не пройдено: APP-01/02. |
| FR-02 | HTTP, I-AUTH | 204, cookie, me совпадает с созданным пользователем. | Пройдено. |
| FR-03 | HTTP, I-AUTH | 204 на logout и 401 с восстановленной cookie. | Пройдено. |
| FR-04 | HTTP, I-AUTH | Старые пароль/сессия отклонены, новый пароль принят. | Пройдено. |
| FR-05 | HTTP, I-LIFE | 201 на конфигурацию и 200 при повторном чтении. | Пройдено; все переданные параметры дополнительно сверяются в тесте. |
| FR-06 | HTTP, I-EDIT | Изменённые name и дневной лимит видны при GET. | Пройдено. |
| FR-07 | HTTP, I-LIFE | 201 на колоду и сохранённые title/owner. | Пройдено. |
| FR-08 | HTTP, I-EDIT | GET возвращает новое название и публичность. | Пройдено. |
| FR-09 | HTTP + SQL unit, I-SHARE, U-DECK | Публичная колода в каталоге, SQL исключает private и применяет пагинацию. | Пройдено на указанных уровнях. |
| FR-10 | HTTP, I-SHARE | Новые ID конфигурации/колоды/карточки, владелец и приватность; прогресс отсутствует у копии. | Пройдено после APP-04. |
| FR-11 | HTTP, I-LIFE | Карточка читается с исходным содержимым. | Пройдено после APP-03. |
| FR-12 | HTTP, I-EDIT | GET возвращает вопрос, тег и путь; очищенный путь равен null. | Пройдено. |
| FR-13 | HTTP + handler unit, I-LIFE, U-QUEUE | Только доступная колода; порядок категорий и верхняя граница limit. | Пройдено; порядок категорий проверен с mock gateway. |
| FR-14 | HTTP + SQL inspection, I-LIMIT и адаптер review log | Лимит новых 1 не выдаёт вторую карточку после первой оценки; review-остаток берётся с начала UTC-дня. | Пройдено: лимит новых — HTTP; review и UTC-фильтры — инспекция query handler/gateway и доменных часов. |
| FR-15 | HTTP + domain unit + inspection, I-LIFE, U-SRS | Матрица состояний/оценок, next_review_at и одна история на оценку; один commit для прогресса и лога. | Пройдено; атомарность подтверждена структурой обработчика/транзакции, конкурентная нагрузка не проверялась. |
| FR-16 | HTTP + unit, I-LIFE, U-PREVIEW | 4 preview; ни прогресса, ни истории не добавлено. | Пройдено. |
| FR-17 | HTTP, I-SHARE | Отдельные ID/состояния и ровно одна собственная запись истории. | Пройдено. |
| FR-18 | HTTP, I-LIFE | После цикла total_cards=1 и review_count=1. | Пройдено. |
| FR-19 | HTTP, I-LIFE | reset → 404; история остаётся, следующее повторение получает новый ID. | Пройдено. |
| FR-20 | HTTP, I-EDIT | Удаление → 204, затем GET → 404 для трёх объектов. | Пройдено. |
| NFR-01 | Реальный криптографический адаптер, U-HASH | bcrypt, разные соли, корректность пароль/pepper. | Пройдено. |
| NFR-02 | HTTP, I-ACCESS | 401 без сессии, 403 постороннему на чтение/изменение/оценку. | Пройдено. |
| NFR-03 | HTTP, I-AUTH + I-LIFE | HttpOnly и серверный отзыв восстановленной cookie. | Пройдено. |
| NFR-04 | Fault injection unit + реальный сервер, U-HEALTH, I-RUN | 503 при отказе БД, degraded/200 при отказе Redis, тайм-аут, успешный штатный health. | Пройдено на unit-уровне для отказов и HTTP для штатного режима; реальные контейнеры не отключались. |
| NFR-05 | Параметризованные тесты настроек, U-CONFIG | Все перечисленные небезопасные production-параметры отклонены. | Пройдено. |
| NFR-06 | PostgreSQL + HTTP, fixture миграций, I-LIFE, I-RUN | upgrade head + alembic check; чтение данных в новых запросах; сеть Uvicorn. | Пройдено. Перезапуск хоста/backup не проверялись и не обещаны. |

Для FR-14 инспектируются `application/queries/card_progress/read_review_queue.py`, `infrastructure/adapters/persistence/alchemy_review_log_gateway.py` (count_new_done/count_reviews_done, фильтр since) и `infrastructure/adapters/common/clock_utc.py`. Для FR-15 — обработчик review_card и SQLAlchemyTransactionManager. Это конкретные способы проверки, а не общая ссылка на исходники.

## Протокол результатов

| Проверка | Результат итогового прогона |
| --- | --- |
| Unit | 469 passed |
| Integration | 14 passed, 2 xfailed |
| Ruff lint | All checks passed |
| Ruff format | 608 files already formatted |
| mypy | Success: no issues found in 441 source files |
| MkDocs strict build | Успешная строгая сборка, без предупреждений о документации |
| SVG диаграммы | Обе отрендерены и визуально проверены; присутствуют актёры, граница системы, состояния, начало/конец и условия. |

Два `xfail(strict=True)` — **воспроизведённые открытые дефекты**, не успешная приёмка FR-01. Восстановление требований после исправления требует убрать соответствующий xfail и повторить тест. Исправленные сбои APP-03/04 защищены обычными интеграционными тестами.

Полный запуск команды `just up` в пользовательском окружении не выполнялся: just отсутствует. Compose проверяется как конфигурация, а реальный сервер — отдельным сетевым тестом с временными сервисами. Инструкция содержит эквивалентные команды без just. Нагрузочные испытания, production-deploy и Docker build в этот протокол не включены.
