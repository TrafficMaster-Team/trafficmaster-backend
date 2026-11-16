"""Rebuild laboratory 3 documentation from the case catalogue and genuine execution traces."""

import hashlib
import html
import importlib.metadata
import json
import platform
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / 'docs/lab3'
EVIDENCE = DOC / 'evidence'
CASES = json.loads((DOC / 'cases.json').read_text())
RESULTS = {p.stem: json.loads(p.read_text()) for p in EVIDENCE.glob('TC-*.json')}
MANIFEST = json.loads((EVIDENCE / 'screenshot-manifest.json').read_text()) if (EVIDENCE / 'screenshot-manifest.json').is_file() else {}


def valid_screenshot(case):
    entry = MANIFEST.get(case['id'], {})
    image = EVIDENCE / f'{case["id"]}.jpg'
    trace = EVIDENCE / f'{case["id"]}.json'
    return image.is_file() and trace.is_file() and entry.get('trace_sha256') == hashlib.sha256(trace.read_bytes()).hexdigest() and entry.get('image_sha256') == hashlib.sha256(image.read_bytes()).hexdigest()


def pct(n, d):
    return f'{n / d * 100:.2f}%' if d else 'N/A'


def esc(value):
    return html.escape(str(value))


def status(case):
    return RESULTS.get(case['id'], {}).get('status', 'Not run')


def screenshot(case):
    return f'evidence/{case["id"]}.jpg'


# A complete self-contained case card is generated from a versioned source catalogue.
text = '''# Каталог тест-кейсов — ЛР3

42 кейса. [Машиночитаемый каталог](cases.json). FR и приоритеты: [спецификация](../requirements.md); проверки: [чек-лист](checklist.md); результаты: [протокол](execution.md).

## Общие исходные данные и предусловия

Каждый кейс выполняется с новым HTTP-клиентом и собственными сущностями на одноразовой PostgreSQL с миграциями head, Redis и сетевым Uvicorn. `<uuid>` — новый случайный идентификатор; реальные значения сохранены в JSON-трассе кейса. A — владелец, B — другой обычный пользователь. Связанные UUID из ответов подставляются в последующие URL. Cookie хранятся только внутри клиента; тестовая смена пароля затрагивает исключительно созданный кейсом аккаунт.

**Набор M:** A регистрируется как Lab-User с уникальным email `lab3_<uuid>@example.com` и паролем `LearningSecure123`, входит. Создаётся конфигурация: name=Lab config, daily_limits={new_cards_per_day:1,max_reviews_per_day:20}, new_cards={learning_steps:[1,10],graduating_interval:1,easy_interval:4,new_card_order:sequential}, lapses={relearning_steps:[10],min_interval:1}, advanced={max_interval:36500,ease_factor:2.5,easy_factor:1.3,interval_modifier:1.0,hard_interval:1.2,new_interval:0.0}. Затем своя приватная колода Traffic rules и карточка: question=What does a red traffic light mean?, answerOptions=[{text:Stop,isCorrect:true,rationale:Red prohibits movement}], hint=Think about safety, tags=[signals]. Для публичных сценариев is_public=true. Создание M — предусловие; сбой предусловия не считается проверкой целевого требования.

Все исходные данные кейса — объединение общих предусловий, M (если указан) и его собственной строки данных. Реальные HTTP-запросы/ответы и SQL-подготовка доступны по ссылке на трассу. Снимок показывает фактический отчёт выполнения, а не макет интерфейса продукта.

'''
for case in CASES:
    result = RESULTS.get(case['id'], {})
    text += f'<a id="{case["id"].lower()}"></a>\n\n## {case["id"]} — {case["title"]}\n\n'
    text += f'- **Приоритет:** {case["priority"]}.\n- **Требование:** [{case["requirement"]}](../requirements.md); проверка CL-{case["requirement"][3:]}-{("P" if case["kind"] != "negative" else "N")}.\n'
    text += f'- **Модуль / подмодуль:** {case["module"]}.\n- **Вид:** {case["kind"]}.\n- **Исходные данные:** {case["data"]}\n\n**Шаги:**\n\n'
    text += ''.join(f'{i}. {step}\n' for i, step in enumerate(case['steps'], 1))
    text += f'\n**Ожидаемый результат:** {case["expected"]}\n\n'
    if result:
        actual = result.get('error') or f'Выполнено проверок: {len(result["checks"])}; все успешны. HTTP-ответы и сохранённые значения приведены в трассе.'
        text += f'**Фактический результат:** {actual}\n\n**Статус:** {result["status"]}. Дефект: {result.get("defect") or "не обнаружен в этом кейсе"}.\n\n'
    text += f'[JSON-трасса](evidence/{case["id"]}.json) · [HTML-результат](evidence/{case["id"]}.html) · [Скриншот]({screenshot(case)})\n\n'
(DOC / 'test-cases.md').write_text(text)

text = '# Чек-лист функциональных требований — ЛР3\n\nВсе FR-01…FR-20, сгруппированные по предметным модулям. P — позитивная проверка, N — негативная. Связи с [кейcами](test-cases.md) и их статусами задают трассировку; наличие кейса не означает успешную приёмку требования.\n\n'
last_module = None
for fr in range(1, 21):
    related = [c for c in CASES if c['requirement'] == f'FR-{fr:02}']
    module = related[0]['module'].split(' / ')[0]
    if module != last_module:
        text += f'\n## {module}\n\n| ID | FR / приоритет | Проверка | Ожидаемый результат | Кейсы / результат |\n| --- | --- | --- | --- | --- |\n'
        last_module = module
    for kind, letter in [('positive', 'P'), ('negative', 'N')]:
        selected = [c for c in related if c['kind'] == kind or kind == 'positive' and c['kind'] == 'boundary']
        expectation = '<br>'.join(c['expected'] for c in selected)
        title = '<br>'.join(c['title'] for c in selected)
        links = '<br>'.join(f'[{c["id"]}](test-cases.md#{c["id"].lower()}) — {status(c)}' for c in selected)
        text += f'| CL-{fr:02}-{letter} | FR-{fr:02} / {related[0]["priority"]} | {title} | {expectation} | {links} |\n'
text += '\nДля дополнительных прямых запретов используются NFR-02/03. Изменение пароля B, операции над приватными материалами, некорректные рейтинги и граничные значения проверяются на реальном API. Негативные кейсы проверяют отказ, отсутствие побочных изменений — там, где это входит в их шаги.\n'
(DOC / 'checklist.md').write_text(text)

n = len(CASES)
p = sum(status(c) == 'Passed' for c in CASES)
f = sum(status(c) == 'Failed' for c in CASES)
b = sum(status(c) == 'Blocked' for c in CASES)
u = n-p-f-b
requirements = sorted({c['requirement'] for c in CASES})
passed_requirements = [r for r in requirements if all(status(c) == 'Passed' for c in CASES if c['requirement'] == r)]
high = [c for c in CASES if c['priority'] == 'High']
high_p = sum(status(c) == 'Passed' for c in high)
high_f = sum(status(c) == 'Failed' for c in high)
environment = {
    'python': platform.python_version(), 'platform': platform.platform(),
    'dependencies': {name: importlib.metadata.version(name) for name in ['pytest', 'pytest-asyncio', 'pytest-cov', 'httpx', 'asyncpg', 'fastapi', 'sqlalchemy', 'testcontainers', 'redis', 'uvicorn']},
    'git_base_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
    'worktree': 'uncommitted working tree; hashes identify catalogue and runner',
    'sha256': {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in [DOC/'cases.json', ROOT/'tests/integration/lab3/test_acceptance.py', ROOT/'pyproject.toml']},
    'postgres_image': 'postgres:16-alpine', 'redis_image': 'redis:7-alpine',
}
(EVIDENCE / 'environment.json').write_text(json.dumps(environment, ensure_ascii=False, indent=2)+'\n')
summary = dict(planned=n, passed=p, failed=f, blocked=b, not_run=u, executed=p+f,
               execution_rate=pct(p+f,n), pass_rate=pct(p,p+f), requirement_coverage=pct(len(requirements),20),
               passed_requirement_rate=pct(len(passed_requirements),20), high_pass_rate=pct(high_p,high_p+high_f),
               high_total=len(high), high_passed=high_p, high_failed=high_f,
               evidence_json=sum((EVIDENCE/f'{c["id"]}.json').is_file() for c in CASES),
               screenshots=sum(valid_screenshot(c) for c in CASES))
(EVIDENCE / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n')

text = f'''# Протокол выполнения и метрики — ЛР3

Дата: 16.11.2026, Europe/Minsk. Тестируется текущее рабочее дерево, а не только git HEAD. [Окружение и SHA-256 каталога/исполняемых кейсов](evidence/environment.json). Реальные времена начала/окончания каждого кейса находятся в JSON-трассах. Источник плана: [test-plan.md](test-plan.md).

## Запуск

```bash
LAB3_EVIDENCE_DIR=docs/lab3/evidence .venv/bin/pytest tests/integration/lab3 -q --no-cov --tb=short
.venv/bin/python scripts/build_lab3_report.py
```

Первый отладочный прогон содержал две ошибки проверок: ожидание 422 вместо документируемого доменного 400 на нулевой лимит и попытку читать card_state из публичного ответа истории, где поля нет. Проверки исправлены: доменный отказ ожидается как 400; исходные состояния проверяются SELECT в одноразовой БД. Эти ошибки тестового кода не зарегистрированы как дефекты приложения. Итоговая таблица построена по повторному полному прогону текущего каталога. JSON-подготовка данных и SQL-проверки обозначены отдельно от HTTP.

Стандартный вывод итогового прогона 42 кейсов: [pytest.log](evidence/pytest.log). Регрессия ранее существовавшего набора и покрытие: [regression.log](evidence/regression.log). Наборы выполнены отдельными командами: первая попытка общего запуска была прервана средой с кодом 143 без итогового отчёта и не учитывается как успешный прогон. Затем исходный набор повторён с `--ignore=tests/integration/lab3`; каталог ЛР3 полностью выполнен отдельным прогоном выше. Для известных дефектов pytest использует xfail, но здесь их приёмочный статус — Failed. Ошибки инфраструктуры должны отражаться Blocked/Not run, а не успешным результатом; текущие счётчики ниже вычислены по реально записанным кейсам.

Команда регрессии исходного набора:

```bash
.venv/bin/pytest tests/ --ignore=tests/integration/lab3 -q --cov-report=term --cov-report=html --cov-report=xml
```

## Метрики

| Метрика | Расчёт | Значение |
| --- | --- | --- |
| Выполнение | (Passed + Failed) / planned ×100 | ({p}+{f})/{n} = {pct(p+f,n)} |
| Успешное прохождение | Passed / executed ×100 | {p}/{p+f} = {pct(p,p+f)} |
| Покрытие требований кейсами | FR с кейсами / все FR ×100 | {len(requirements)}/20 = {pct(len(requirements),20)} |
| FR с полностью успешными кейсами | FR, все кейсы которых Passed / все FR ×100 | {len(passed_requirements)}/20 = {pct(len(passed_requirements),20)} |
| High-кейсы успешно | Passed High / executed High ×100 | {high_p}/{high_p+high_f} = {pct(high_p,high_p+high_f)} |
| Blocked / Not run | Абсолютные значения | {b} / {u} |
| JSON-доказательства | кейсы с трассой / planned | {summary['evidence_json']}/{n} |
| Скриншоты | кейсы со снимком / planned | {summary['screenshots']}/{n} |

Исходный регрессионный набор: **483 passed, 2 xfailed**; отдельно каталог ЛР3: **40 passed, 2 xfailed**. Суммарно в двух непересекающихся наборах: 523 passed, 4 xfailed. Два из четырёх xfail — повторные автоматизированные воспроизведения тех же APP-01/02, а не четыре различных дефекта. Покрытие кода по исходному набору — **90,08%** (строки 91,31%, ветви 78,90%); [машиночитаемый расчёт](evidence/coverage-summary.json). Порог 70% выполнен. Дополнительные кейсы ЛР3 не использовались для повышения этого показателя, поскольку приложение для них работает отдельным процессом.

Формулы и соглашения приведены в плане; методичка не предоставлена, точное совпадение с её разделом 6.2 не подтверждается. Покрытие кода — отдельная метрика и не используется вместо покрытия FR. Если успешность считать от всех запланированных, в этом прогоне результат совпадает, поскольку все кейсы выполнены.

### Устранение дефектов по важности

Фиксированный набор — **8 записей ISSUES.md**, включая исторические исправления. Verified fixed: APP-03/04, DOC-03/04; Open: APP-01/02; Resolved awaiting full retest: DOC-01/02. Числитель включает только подтверждённые исправления. Это статус реестра, а не утверждение, что все восемь дефектов вновь обнаружены в этом прогоне.

| Важность | Всего Ds | Подтверждённо устранено Vs | Vs/Ds ×100 |
| --- | --- | --- | --- |
| S1 Blocker | 0 | 0 | N/A |
| S2 Critical: APP-03/04, DOC-01 | 3 | 2 | 66,67% |
| S3 Major: APP-01/02, DOC-02/04 | 4 | 1 | 25,00% |
| S4 Minor: DOC-03 | 1 | 1 | 100,00% |
| Все важности | 8 | 4 | 50,00% |

Отдельно в актуальном API-прогоне воспроизведены два открытых S3 (APP-01/02): устранено 0/2=0%. S2 APP-03/04 не воспроизведены при регрессии TC-025/027/028 и TC-019. Исторические описания и повторные проверки сохранены в ISSUES.md.

## Результаты каждого кейса

| ID | FR | Приоритет | Фактический результат | Статус | Дефект | Доказательства |
| --- | --- | --- | --- | --- | --- | --- |
'''
for case in CASES:
    result = RESULTS.get(case['id'], {})
    actual = (result.get('error') or f'{len(result.get("checks",[]))} проверок успешны').replace('|','/').replace('\n',' ')
    text += f'| {case["id"]} | {case["requirement"]} | {case["priority"]} | {actual} | {status(case)} | {result.get("defect") or "—"} | [JSON](evidence/{case["id"]}.json), [снимок]({screenshot(case)}), [HTML](evidence/{case["id"]}.html) |\n'
text += '''
## Дополнительные проверки комплекта

Ruff: All checks passed; форматирование: 610 files already formatted; mypy: Success, 441 source files. Строгая сборка документации MkDocs прошла. Лог сборки: [mkdocs.log](evidence/mkdocs.log). Синтаксис генератора, наличие всех полей кейсов, пары позитив/негатив для каждого FR и соответствие снимков трассам проверены отдельно.

## Решение по критериям

Все 42 кейса выполнены, каждый Failed связан с дефектом. Условия завершения тестирования оцениваются по счётчикам трасс и снимков выше. **Продукт не принят полностью:** High-кейсы TC-041/042 не прошли, FR-01 не выполнен для допустимых длинных данных. Общий pass rate ≥95% не отменяет провала обязательного требования. Условие отсутствия открытых S1/S2 по полному реестру также не подтверждено закрытием DOC-01: он ожидает полного повторного запуска. Решение о переносе дефектов пользователем не получено.

После исправления необходимо повторить граничные кейсы и полную регрессию; это будущая работа по исправлению продукта, а не недостающая запись результата текущего тестирования. Нагрузочные, полный ручной UI-прогон, production-deploy и реальные отключения зависимостей не выполнены и не выдаются за результаты текущего этапа.

## Скриншоты и первичные данные

Снимки `TC-001.jpg`…`TC-042.jpg` получены в браузере с HTML-страниц **реально выполненного отчёта**. Это скриншоты результатов API-тестов, не изображения ответов Swagger и не синтетические макеты. Каждая HTML-страница содержит критерий, статус, фактические HTTP-коды и последние ответы; полный набор запросов и проверок — в соответствующем JSON. Пароли и токены удалены из трасс. [Обзор результатов](evidence/index.html). [Манифест снимков](evidence/screenshot-manifest.json) содержит время съёмки и SHA-256 снимков и исходных трасс; после нового запуска несовпадающие снимки не засчитываются в метрику доказательств.

![Снимок сводных результатов](evidence/overview.jpg)
'''
(DOC / 'execution.md').write_text(text)

css = '''body{font:16px system-ui;margin:28px auto;max-width:1100px;background:#f4f6fa;color:#142039;padding:0 20px}h1{font-size:27px;margin-bottom:8px}h2{font-size:18px}header{border-left:7px solid #224cd8;padding-left:18px;margin:22px 0}section{background:white;padding:16px 22px;margin:15px 0;border:1px solid #dce2ee;border-radius:12px}pre{font:13px ui-monospace,monospace;white-space:pre-wrap;overflow-wrap:anywhere;max-height:220px;overflow:auto;margin:10px 0}.Passed{color:#087448}.Failed{color:#b42136}small{color:#526079}a{color:#214cc7}td,th{padding:9px 14px;text-align:left;border-bottom:1px solid #dde3ee}table{border-collapse:collapse;width:100%}.badge{font-size:21px;font-weight:bold}details{margin-top:15px}'''
for case in CASES:
    result = RESULTS.get(case['id'], {})
    events = result.get('events', [])
    latest = events[-2:]
    preview = ''
    for event in latest:
        if event['type'] == 'HTTP':
            detail = f'{event["method"]} {event["path"]} → HTTP {event["status"]}'
            body = json.dumps(event['response'], ensure_ascii=False, indent=2)
        else:
            detail = event['type']
            body = json.dumps(event, ensure_ascii=False, indent=2)
        preview += f'<section><b>{esc(detail)}</b><pre>{esc(body)}</pre></section>'
    page = f'''<!doctype html><html lang="ru"><meta charset="utf-8"><title>{case['id']} — результат выполнения</title><style>{css}</style>
    <header><small>TrafficMaster · ЛР3 · реальный HTTP / PostgreSQL / Redis</small><h1>{esc(case['id'])} — {esc(case['title'])}</h1><b>{case['requirement']} · {case['priority']} · {esc(case['module'])}</b></header>
    <section><span class="badge {status(case)}">{status(case)}</span> · {len(result.get('checks', []))} проверок · {esc(result.get('defect') or 'дефект не обнаружен')}<br><small>{esc(result.get('started'))} — {esc(result.get('finished'))} · Europe/Minsk</small><p><b>Ожидание:</b> {esc(case['expected'])}</p><p><b>Факт:</b> {esc(result.get('error') or 'Все проверки кейса успешны; ответы приведены ниже.')}</p></section>
    {preview}<details><summary>Полная трасса и проверки</summary><pre>{esc(json.dumps(result, ensure_ascii=False, indent=2))}</pre></details><p><a href="{case['id']}.json">Первичные данные JSON</a> · <a href="index.html">Все результаты</a></p></html>'''
    (EVIDENCE / f'{case["id"]}.html').write_text(page)
rows=''.join(f'<tr><td><a href="{c["id"]}.html">{c["id"]}</a></td><td>{c["requirement"]}</td><td>{esc(c["title"])}</td><td class="{status(c)}">{status(c)}</td></tr>' for c in CASES)
(EVIDENCE / 'index.html').write_text(f'<!doctype html><html lang="ru"><meta charset="utf-8"><title>TrafficMaster — ЛР3 результаты</title><style>{css}</style><h1>TrafficMaster — результаты ЛР3</h1><section><b>{p} Passed · {f} Failed · {b} Blocked · {u} Not run</b><p>Выполнение: {pct(p+f,n)} · Успешность: {pct(p,p+f)} · FR покрыты: {len(requirements)}/20</p><p>APP-01/02 открыты. Продукт не принят полностью.</p><small>Первичные данные: реальные HTTP-запросы и ответы. Снимки этих страниц не являются UI-тестами приложения.</small></section><table><tr><th>Кейс</th><th>FR</th><th>Проверка</th><th>Статус</th></tr>{rows}</table></html>')
print(json.dumps(summary, ensure_ascii=False))
