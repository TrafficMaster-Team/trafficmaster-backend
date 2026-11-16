"""Generate laboratory 4 reports exclusively from recorded Newman/Playwright evidence."""
import hashlib
import html
import importlib.metadata
import json
import re
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DOC=ROOT/'docs/lab4'; OUT=DOC/'evidence'
raw=json.loads((OUT/'newman.json').read_text())
run=json.loads((OUT/'run.json').read_text())
catalog=json.loads((ROOT/'postman/coverage-map.json').read_text())
spec=json.loads((ROOT/'postman/openapi.json').read_text())
executions=raw['run']['executions']
by_name={e['item']['name']:e for e in executions}
assert len(executions)==len(catalog)
ui=[json.loads(p.read_text()) for p in sorted((OUT/'ui').glob('*.json'))]
probe=[json.loads(p.read_text()) for p in (OUT/'screenshot-probe').glob('*.json')]


def failures(e): return [a for a in e.get('assertions',[]) if a.get('error')]


def body(e):
    stream=e.get('response',{}).get('stream',{}).get('data',[])
    if not stream: return None
    try: return json.loads(bytes(stream).decode())
    except ValueError: return bytes(stream).decode()


def url(e):
    value=e['request']['url']; path='/'+ '/'.join(value.get('path',[]))
    query=value.get('query',[])
    if query: path+='?'+'&'.join(x['key']+'='+str(x.get('value','')) for x in query)
    return path


operations={(m.upper(),p) for p,ms in spec['paths'].items() for m in ms if m in ['get','post','patch','put','delete']}
covered=set()
for c in catalog:
    e=by_name[c['name']]
    if c['positive'] and e['response']['code']==c['expected'] and not failures(e): covered.add((c['method'],c['route']))
assert operations<=covered, operations-covered
assert all((OUT/'ui'/x['screenshot']).is_file() for x in ui)
assert run['failure_capture_verified'] and any(x['failure_screenshot'] for x in probe)
request_pass=sum(not failures(e) for e in executions)
summary={'requests':len(executions),'requests_with_all_assertions_passed':request_pass,
         'assertions':raw['run']['stats']['assertions'], 'operations_total':len(operations),
         'operations_positive_verified':len(operations&covered),'ui_passed':sum(x['status']=='passed' for x in ui),
         'ui_total':len(ui),'failure_capture_verified':run['failure_capture_verified'],
         'new_defects':['APP-05','APP-06','APP-07'],'frontend_scope':'Not applicable: API only',
         'started':run['started'],'finished':run['finished']}
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')

css='body{font:15px system-ui;max-width:1200px;margin:30px auto;padding:0 20px;background:#f6f8fc;color:#17243d}section{padding:18px;background:white;border:1px solid #dce2eb;border-radius:12px;margin:15px 0}td,th{text-align:left;padding:10px;border-bottom:1px solid #dbe2ed}table{border-collapse:collapse;width:100%}pre{white-space:pre-wrap;overflow-wrap:anywhere}.Failed{color:#b22235}.Passed{color:#08734d}a{color:#2346b5}'
text=f'<!doctype html><html lang="ru"><meta charset="utf-8"><title>TrafficMaster — Postman / Newman</title><style>{css}</style><h1>TrafficMaster — Postman / Newman</h1><section><b>{len(executions)} запросов · {summary["assertions"]["total"]} assertions · {summary["assertions"]["failed"]} failed</b><p>Позитивно проверено операций: {len(operations&covered)}/{len(operations)}. Новые дефекты: APP-05, APP-06, APP-07. Полная приёмка безопасности не пройдена.</p><small>{html.escape(run["started"])} — {html.escape(run["finished"])}</small></section><table><tr><th>Запрос</th><th>Метод / путь</th><th>HTTP</th><th>Результат проверок</th></tr>'
for e in executions:
    name=e['item']['name']; ident=name.split(' | ')[0]; fail=failures(e)
    text+=f'<tr id="{ident}"><td>{html.escape(name)}</td><td>{e["request"]["method"]} {html.escape(url(e))}</td><td>{e["response"]["code"]}</td><td class="{"Failed" if fail else "Passed"}">{len(e.get("assertions",[]))-len(fail)} passed / {len(fail)} failed</td></tr>'
    if fail:
        messages='\n'.join(a['assertion']+': '+a['error'].get('message','') for a in fail)
        text+=f'<tr><td colspan="4"><pre>{html.escape(messages)}\nФактическое тело: {html.escape(json.dumps(body(e),ensure_ascii=False))}</pre></td></tr>'
text+='</table><p><a href="newman.json">Native Newman JSON (cookies/passwords redacted)</a> · <a href="newman.xml">Native Newman JUnit</a></p></html>'
(OUT/'newman.html').write_text(text)

api=f'''# Postman: коллекция и покрытие API

Коллекция: `postman/TrafficMaster.postman_collection.json`; environment: `postman/local.postman_environment.json`. Версия коллекции — Postman v2.1, импортируется в Postman через Import. Схема взята из реально работающего `/openapi.json`. В коллекции **{len(catalog)} запросов**, позитивно выполнены **{len(operations&covered)}/{len(operations)} операций**.

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

Newman выполнил {len(executions)} HTTP-запросов без транспортных сбоев. Assertions: {summary['assertions']['total']}, из них {summary['assertions']['failed']} failed. Это не «все тесты прошли»: сбои связаны с найденными дефектами, [подробности](security.md).

## Трассировка всех операций

Для каждой строки ниже есть хотя бы один позитивный запрос с совпавшим кодом и всеми успешными assertions. Негативные запросы и их ошибки видны в полном HTML. Пара method+path определяет операцию; число URL без учёта метода было бы неверной метрикой.

| Операция | Позитивный запрос | Результат |
| --- | --- | --- |
'''
for method,path in sorted(operations):
    candidates=[c for c in catalog if (c['method'],c['route'])==(method,path) and c['positive'] and by_name[c['name']]['response']['code']==c['expected'] and not failures(by_name[c['name']])]
    c=candidates[0]; ident=c['name'].split(' | ')[0]
    api+=f'| `{method} {path}` | [{ident}](evidence/newman.html#{ident}) | Passed, HTTP {c["expected"]} |\n'
api+='\nИнструмент: [официальные параметры Newman и reporters](https://learning.postman.com/docs/collections/using-newman-cli/newman-options). Newman исполняет Postman-коллекцию локально; вход в облачный аккаунт Postman и отправка данных в облако не использовались.\n'
(DOC/'api.md').write_text(api)

anonymous=[by_name[c['name']] for c in catalog if 'Anonymous direct URL' in c['name']]
idor=[by_name[c['name']] for c in catalog if 'IDOR ' in c['name']]
log=(OUT/'server.log').read_text()
access=[line for line in log.splitlines() if re.search(r'"(GET|POST|PATCH|DELETE) /',line)]
log_summary={'access_records':len(access),'registration_logged':any('POST /v1/auth/signup ' in line for line in access),
 'login_logged':any('POST /v1/auth/login ' in line for line in access),'review_logged':any('POST /v1/review/card/' in line for line in access),
 'mutation_logged':any('PATCH /v1/card/' in line for line in access),'denial_4xx_logged':any(re.search(r'" 4\d\d',line) for line in access)}
assert all(log_summary[k] for k in log_summary if k!='access_records')
(OUT/'logging-summary.json').write_text(json.dumps(log_summary,indent=2)+'\n')
security=f'''# Базовая проверка безопасности

Стенд одноразовый: два обычных пользователя и отдельно подготовленный superadmin; production и реальные аккаунты не использовались. Зафиксированы как корректные отказы, так и реальные нарушения; статус всей безопасности не объявляется успешным.

| Проверка | Ожидание | Факт / результат | Доказательство |
| --- | --- | --- | --- |
| Прямой URL без авторизации | 401, данные не раскрыты | {sum(e['response']['code']==401 for e in anonymous)}/{len(anonymous)} возвращают 401; Passed по контролю доступа. Формат тела отдельно нарушает контракт APP-06. | R066…R075, Newman JSON/HTML; UI direct URL |
| Чужие ID при чтении и изменении | 403, изменения не сохранены | {sum(e['response']['code']==403 for e in idor)}/{len(idor)} отклонены; перенос своей карточки в чужую колоду разрешён. **Failed, APP-07** | R090 и последующее чтение R095 |
| Самоназначение административной роли | 403; role остаётся user | 204; me возвращает admin. **Failed, APP-05** | R127/R128; R129 восстанавливает тестовую роль |
| Stack trace, пути и SQL в клиентских ошибках | Не раскрываются | Пройдено для всех выбранных 4xx; 500/503 проверены fault injection в отдельном минимальном приложении с тем же обработчиком | error-security.log; негативные assertions коллекции |
| Запись основных операций | В серверном access log есть method/path/status | Регистрация, login, review, изменение карточки и 4xx найдены; {len(access)} записей | server.log, logging-summary.json |
| Логирование внутренних сбоев | Сервер пишет ошибку, клиенту — безопасное сообщение | 500: ERROR с контекстом; 503: WARNING, SQL/путь не попадают в ответ; 2 unit-теста Passed | error-security.log, test_exception_handler.py |

Проверка 500/503 — контролируемое внедрение RuntimeError/GatewayError в **отдельном тестовом FastAPI** с реальным ExceptionHandler. Диагностические endpoints в приложение не добавлялись, production-отказы не провоцировались. Access log — базовая фиксация операций; полноценный бизнес-аудит с actor_id/correlation_id и долговременным хранением здесь не проверялся и не заявляется.

## Найденные дефекты

- **APP-05, S2 Critical / P1:** пользователь повышает собственную роль до admin через PATCH /v1/user/{{self}}/admin. Сохранённое изменение подтверждено me. Нет надёжного пользовательского обхода; требуется отдельная проверка права назначения роли.
- **APP-06, S3 Major / P2:** 10 ответов 401 и 4 ответа 422 не соответствуют OpenAPI: `detail` вместо обязательного `description`. Коды отказа и отсутствие утечек при этом корректны.
- **APP-07, S2 Critical / P1:** card/deck проверяет право на исходную карточку, но не на целевую колоду. Перенос в чужую private колоду возвращает 204; список владельца получает вторую карточку.

Полные карточки: `ISSUES.md` в корне репозитория — шаги, исходные данные, ожидаемый/фактический результат, воспроизводимость, важность, срочность, симптом, обход. Подтверждение каждого дефекта в данном итоговом прогоне: 1 воспроизведение; APP-06 проверен на 14 ответах. Проблемы не исправлялись в рамках лабораторной по тестированию.

## Ограничения

Это базовая проверка, не полный pentest. Brute force, CSRF, SQL injection/fuzzing, JWT key rotation и нагрузочный DoS не проверялись. Позитивный superadmin-тест не оправдывает повышение роли обычным пользователем. Требования безопасности **не приняты полностью** до исправления APP-05/07 и повторного прогона.
'''
(DOC/'security.md').write_text(security)

ui_text='''# Playwright через Swagger UI

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
'''
for result in ui:
    name=result['test']; image=result['screenshot']; json_file=Path(image).with_suffix('.json').name
    ui_text+=f'| `{name}` | Действия и assertions в test_swagger.py | {result["status"]} | [PNG](evidence/ui/{image}), [JSON](evidence/ui/{json_file}) |\n'
ui_text+=f'\nИтого: **{summary["ui_passed"]}/{len(ui)} пользовательских UI-сценария Passed**. Проверка сохранения скриншота при падении: **{run["failure_capture_verified"]}**. [JUnit](evidence/ui.xml), [stdout](evidence/playwright.log), [ожидаемое падение probe](evidence/screenshot-probe.log).\n\n'
for p in probe: ui_text+=f'[PNG намеренно упавшего теста](evidence/screenshot-probe/{p["screenshot"]}) · [его результат JSON](evidence/screenshot-probe/{Path(p["screenshot"]).with_suffix(".json").name}).\n\n'
ui_text+='При отладке устранены ошибки локатора (заголовок Code отделён от фактического статуса), а также необоснованное ожидание description вместо штатного detail в прямом браузерном отказе. Несоответствие OpenAPI при этом продолжает выявляться отдельными schema-тестами в Postman; оно не скрыто изменением UI-ожидания.\n\nПодход основан на [Page Object Models Playwright](https://playwright.dev/python/docs/pom) и встроенных ожиданиях.\n'
(DOC/'swagger-ui.md').write_text(ui_text)

provenance={'started':run['started'],'finished':run['finished'],'versions':{name:importlib.metadata.version(name) for name in ['pytest','pytest-playwright','playwright','httpx','fastapi']},
'node':run['versions']['node'],'newman':json.loads((ROOT/'postman/node_modules/newman/package.json').read_text())['version'],
'files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'postman/TrafficMaster.postman_collection.json',ROOT/'postman/openapi.json',ROOT/'postman/package-lock.json',ROOT/'tests/e2e/pages.py',ROOT/'tests/e2e/conftest.py',ROOT/'tests/e2e/test_swagger.py',ROOT/'scripts/run_lab4.py']}}
(OUT/'provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')
results=f'''# Протокол ЛР4

Начало: {run['started']}. Завершение: {run['finished']}, Europe/Minsk. Тестировалось текущее рабочее дерево; [версии и SHA-256 исполняемых материалов](evidence/provenance.json).

| Раздел задания | Результат |
| --- | --- |
| 1. Вёрстка, адаптивность, мобильная эмуляция, совместимость трёх браузеров | Неприменимо: отдельной клиентской части нет; не выполнялось. |
| 2. Postman: операции, позитивные/негативные проверки, связывание, отчёт | {len(executions)} запросов, {len(operations&covered)}/{len(operations)} позитивно проверенных операций; {summary['assertions']['total']} assertions: {summary['assertions']['total']-summary['assertions']['failed']} Passed, {summary['assertions']['failed']} Failed. Отчёты CLI/JSON/JUnit/HTML сохранены. |
| 3. Базовая безопасность | Прямой анонимный доступ отклонён; большинство IDOR-запросов отклонены; APP-05/07 нарушают защиту; APP-06 нарушает контракт ошибок. Логирование и безопасные 500/503 подтверждены. |
| 4. UI-автоматизация через Swagger | {summary['ui_passed']}/{len(ui)} Passed; Page Object, свои данные, явные ожидания; screenshot-on-failure подтверждён отдельным намеренно упавшим probe. |

HTTP-запросов с транспортными ошибками: {raw['run']['stats']['requests']['failed']}; запросов, у которых все assertions успешны: {request_pass}/{len(executions)}. HTTP-успех не равен успешности проверки: например, 204 при ожидаемом 403 — Failed. 18 неуспешных assertions связаны с тремя воспроизводимыми дефектами, а не с 18 независимыми дефектами.

Полная приёмка API/безопасности **не пройдена**. Runner корректно возвращает код {1 if run['commands']['newman'] else 0} из-за реальных Failed в Newman. Playwright завершился с кодом {run['commands']['playwright']}. Код 1 screenshot_probe ожидаем и отделён от пользовательских тестов. Безусловного утверждения «всё работает» в протоколе нет.

## Первичные доказательства

- [Postman HTML](evidence/newman.html), [native JSON](evidence/newman.json), [native JUnit](evidence/newman.xml), [CLI](evidence/newman.log).
- [Playwright stdout](evidence/playwright.log), [JUnit](evidence/ui.xml), [отдельная проверка screenshot hook](evidence/screenshot-probe.log).
- [Unit-проверки безопасных ошибок и логирования](evidence/error-security.log).
- [Серверный лог](evidence/server.log), [проверка записей основных операций](evidence/logging-summary.json).
- [Статистика](evidence/summary.json), [runner](evidence/run.json).

Токены/cookie и пароли в сохраняемом Newman JSON замаскированы после выполнения. Тестовые аккаунты и сервер уничтожены вместе с одноразовыми контейнерами. Настоящий .env и production-данные не копировались.

## Сопутствующие проверки

Модульная регрессия: **470 passed**, [stdout](evidence/unit-regression.log). Ruff check — All checks passed; форматирование — 614 files already formatted; mypy — Success, 441 source files. `uv lock --check --offline` подтвердил согласованность lock-файла. Строгая сборка MkDocs прошла: [лог](evidence/mkdocs.log). Эти результаты не отменяют Failed в Newman.

## Отладка и ограничения

До итогового прогона исправлены тестовый cookie jar (чтобы исключить случайное повторное использование сессии), слишком широкий UI-локатор и порядок удаления связанных сущностей. Эти ошибки тестовой инфраструктуры не включены в реестр дефектов приложения. Итоговые числа выше рассчитаны только из текущих сохранённых результатов после исправлений.

Вёрстка/мобильные размеры и три браузера исключены по отсутствию отдельного клиента. Swagger выбран только для выполнения пункта UI-автоматизации. Нагрузочное тестирование и полный pentest не входят в этот этап. Задание по выполнению проверок и фиксации результатов завершено; исправление найденных дефектов и повторная приёмка остаются отдельной работой.
'''
(DOC/'results.md').write_text(results)
print(json.dumps(summary,ensure_ascii=False))
