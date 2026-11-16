"""Create plots and the load-testing protocol from raw, windowed Locust events."""

import csv
import hashlib
import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/trafficmaster-lab5-matplotlib")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from loadtests.metrics import phase_metrics

ROOT=Path(__file__).resolve().parents[1]
DOC=ROOT/'docs/lab5'; OUT=DOC/'evidence'
run=json.loads((OUT/'run.json').read_text())
phases=run['phases']
for phase in phases:
    recalculated=phase_metrics(OUT/phase['id'],phase['duration_s'])
    for key in ['requests','errors','rps','p95_ms','error_percent']:
        assert abs(phase[key]-recalculated[key]) < 1e-8,(phase['id'],key)
main=[p for p in phases if p['id']!='recovery']
target=next(p for p in phases if p['id']=='target')
recovery=next(p for p in phases if p['id']=='recovery')
first_bad=next((p for p in main if p['p95_ms']>1000 or p['error_percent']>1),None)
previous=main[main.index(first_bad)-1] if first_bad and main.index(first_bad)>0 else None
target_pass=target['slo_passed'] and target['rps']>=5
recovery_pass=(recovery['slo_passed'] and recovery['rps']>=0.8*target['rps']
 and run['recovery_probes']['healthy'] and run['recovery_probes']['pid_unchanged'] and run['recovery_probes']['elapsed_s']<=30)
summary={'target_passed':target_pass,'recovery_passed':recovery_pass,'first_degraded_users':first_bad['users'] if first_bad else None,
 'last_non_degraded_users':previous['users'] if previous else None,'recovery_rps_ratio':recovery['rps']/target['rps'],
 'recovery_seconds':run['recovery_probes']['elapsed_s'],'max_users_tested':max(p['users'] for p in phases),
 'total_measured_requests':sum(p['requests'] for p in phases),'errors':sum(p['errors'] for p in phases),
 'per_phase':[{k:p[k] for k in ['id','users','requests','rps','error_percent','mean_ms','p50_ms','p95_ms','p99_ms']} for p in phases]}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
with (OUT/'measured-summary.csv').open('w',newline='') as stream:
    writer=csv.DictWriter(stream,fieldnames=list(summary['per_phase'][0]));writer.writeheader();writer.writerows(summary['per_phase'])

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
x=[p['users'] for p in main]
fig,ax=plt.subplots(figsize=(10,5.6),layout='constrained')
ax.plot(x,[p['p95_ms'] for p in main],'o-',color='#2446b5',label='p95')
ax.plot(x,[p['mean_ms'] for p in main],'s--',color='#168069',label='Среднее')
ax.scatter([10],[recovery['p95_ms']],marker='D',s=75,color='#b44c9b',label='После восстановления, p95',zorder=5)
ax.axhline(1000,color='#b33c37',linestyle=':',label='Порог p95: 1000 мс')
if first_bad and previous:
    ax.axvspan(previous['users'],first_bad['users'],color='#f1c56a',alpha=0.2,label='Интервал начала деградации')
for p in main:
    ax.annotate(f"{p['p95_ms']:.0f}",(p['users'],p['p95_ms']),textcoords='offset points',xytext=(4,9),fontsize=9)
ax.set(xlabel='Одновременные виртуальные пользователи',ylabel='Время HTTP-отклика, мс',
       title='TrafficMaster: задержка при росте нагрузки')
ax.set_xticks(x);ax.grid(alpha=0.2);ax.legend(loc='upper left',fontsize=9)
fig.savefig(OUT/'latency-vs-users.png',dpi=180,bbox_inches='tight',pad_inches=0.2);fig.savefig(OUT/'latency-vs-users.svg',bbox_inches='tight',pad_inches=0.2);plt.close(fig)
fig,(left,right)=plt.subplots(1,2,figsize=(11,4.8),layout='constrained')
left.plot(x,[p['rps'] for p in main],'o-',color='#2446b5');left.scatter([10],[recovery['rps']],marker='D',color='#b44c9b')
left.set(title='Пропускная способность',xlabel='VU',ylabel='Завершённые запросы / с');left.set_xticks(x);left.grid(alpha=0.2)
right.plot(x,[p['resource_summary']['api_cpu_mean'] for p in main],'o-',color='#bb493d',label='Средний CPU API')
right.plot(x,[p['resource_summary']['generator_cpu_max'] for p in main],'s--',color='#168069',label='Максимальный CPU Locust')
right.set(title='CPU процессов (100% = одно ядро)',xlabel='VU',ylabel='%');right.set_xticks(x);right.grid(alpha=0.2);right.legend(fontsize=9)
fig.savefig(OUT/'throughput-cpu.png',dpi=180,bbox_inches='tight',pad_inches=0.2);fig.savefig(OUT/'throughput-cpu.svg',bbox_inches='tight',pad_inches=0.2);plt.close(fig)

fmt=lambda value:f'{value:.2f}'
text=f'''# Результаты нагрузочного тестирования — ЛР5

Фактический прогон: {run['started']} — {run['finished']}, Europe/Minsk. [План, профиль и критерии](test-plan.md) заданы до измерений. Исходники: loadtests/locustfile.py, loadtests/metrics.py, scripts/run_lab5.py. [Полный runtime JSON](evidence/run.json), [CSV-сводка](evidence/measured-summary.csv), [сырой stdout](evidence/run.log).

## Исправление измерительного стенда

Предварительный отладочный прогон сохранён в evidence/preliminary и исключён из итоговых чисел: CLI --run-time отсчитывался раньше test_start, поэтому в последних строках target/stress-25 число VU успевало снизиться. Остановка перенесена в событие test_start, спустя прогрев, полное окно и 2 неизмеряемые секунды. Профиль, SLO, число VU и длительности измерения не менялись. Итоговый повтор проверен по native CSV User Count: во всех измерительных окнах поддерживается заданное число пользователей. Это исправление инструмента тестирования, не оптимизация продукта.

## Измеренные результаты

Из каждого окна исключены 5 с прогрева и запросы, пересекающие границы измерения. p95 рассчитан nearest-rank по исходным событиям, а не средним из процентов. Все HTTP/семантические ошибки учитывались; ожидаемых 4xx в профиле нет.

| Прогон | VU | Окно, с | Запросы | RPS | Ошибки | Среднее, мс | p50, мс | p95, мс | p99, мс |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
'''
for p in phases:
    text+=f'| {p["id"]} | {p["users"]} | {p["duration_s"]} | {p["requests"]} | {p["rps"]:.2f} | {p["errors"]} ({p["error_percent"]:.2f}%) | {p["mean_ms"]:.2f} | {p["p50_ms"]:.2f} | {p["p95_ms"]:.2f} | {p["p99_ms"]:.2f} |\n'
text+=f'''
Всего measured-запросов: **{summary['total_measured_requests']}**, ошибок: **{summary['errors']}**. Нулевой error rate не означает отсутствие деградации: задержки нарушают SLO раньше, чем появляются отказы. Native Locust CSV/HTML и полный samples.csv сохранены для каждой ступени.

![Время отклика от числа пользователей](evidence/latency-vs-users.png)

[Векторный SVG](evidence/latency-vs-users.svg). Линии соединяют измеренные точки для наглядности; дополнительных измерений между ступенями нет. Восстановление при 10 VU показано отдельным ромбом, а не как ещё одна ступень нарастающей нагрузки.

## Начало деградации и восстановление

'''
if first_bad and previous:
    text+=f'Первая измеренная деградация — **{first_bad["users"]} VU**, p95={first_bad["p95_ms"]:.2f} мс. Предыдущая ступень **{previous["users"]} VU** имела p95={previous["p95_ms"]:.2f} мс. Поэтому граница локализована в интервале **({previous["users"]}; {first_bad["users"]}] VU** для данного профиля и хоста. Точное значение внутри интервала не измерялось.\n\n'
else:
    text+='В пределах фактически выполненных ступеней деградация по заданному порогу не найдена; границу отказа нельзя выдумывать.\n\n'
text+=f'''На {max(p['users'] for p in phases)} VU стресс остановлен по заранее заданному условию: {run.get("stress_stop", "достигнут максимальный предел VU")}. Ступени выше последней измеренной из верхнего плана **не выполнялись**, поскольку сработало ограничение стресса; 200 — ограничитель, не достигнутая нагрузка. Полный crash не произошёл, что соответствует заданию «до деградации или отказа».

После снятия нагрузки три пары liveness/readiness прошли за **{run['recovery_probes']['elapsed_s']:.2f} с**, PID API не менялся. Это время подтверждения трёх здоровых точек, не длительность недоступности: полного отказа не наблюдалось. Затем при 10 VU p95={recovery['p95_ms']:.2f} мс, error={recovery['error_percent']:.2f}%, RPS={recovery['rps']:.2f} — **{recovery['rps']/target['rps']*100:.2f}%** исходного целевого RPS.

- **NFR-07:** {'Passed' if target_pass else 'Failed'} на локальном стенде: p95≤1000 мс, ошибки≤1%, RPS≥5, достаточная выборка.
- **NFR-08:** {'Passed' if recovery_pass else 'Failed'}: восстановление≤30 с без перезапуска, стабильные health и последующая нагрузка с RPS≥80% исходного.

Невыполнение целевого NFR-07 в данном итоговом прогоне зарегистрировано как **PERF-01** в ISSUES.md. Это локальное измеренное несоответствие экспериментальному SLO, а не утверждение о производственной аварии.

Recovery и исходный target могут различаться из-за коротких окон, фактического случайного микса и изменившейся БД; более быстрый recovery не означает оптимизацию или гарантированную ёмкость.

Превышение SLO на стрессовых ступенях само по себе не является нарушением обещания NFR-07, которое задано на 10 VU; это измеренный предел данного экземпляра. Подтверждение SLO не отменяет открытые функциональные/безопасностные дефекты ЛР4.

## Показатели по операциям

Глобальный p95 не следует подменять p95 каждой ручки: например, при 10 VU отдельные login/review имеют p95 около/выше 1 с, {"агрегатный критерий выдержан" if target_pass else "агрегатный критерий в этом прогоне также нарушен"}. У baseline {phases[0]["requests"]} запросов и {phases[0]["operations"].get("POST login", {}).get("requests", 0)} login, поэтому он слабо характеризует хвост распределения аутентификации. Короткие окна не дают доверительных интервалов или гарантии длительной стабильности.

| Прогон | Действие | Число | Фактическая доля | p95, мс |
| --- | --- | --- | --- | --- |
'''
for p in phases:
    for name,op in p['operations'].items(): text+=f'| {p["id"]} | {name} | {op["requests"]} | {op["requests"]/p["requests"]*100:.2f}% | {op["p95_ms"]:.2f} |\n'
text+='''
## Предположение об узком месте

| Прогон | Средний CPU API | Максимум API | Максимум Locust | Соединения БД, max | Активные SQL, max | Lock wait, max |
| --- | --- | --- | --- | --- | --- | --- |
'''
for p in phases:
    r=p['resource_summary'];text+=f'| {p["id"]} | {r["api_cpu_mean"]:.2f}% | {r["api_cpu_max"]:.2f}% | {r["generator_cpu_max"]:.2f}% | {r["db_connections_max"]} | {r["db_active_max"]} | {r["db_lock_waits_max"]} |\n'
text+='''
![Пропускная способность и CPU](evidence/throughput-cpu.png)

Основная **гипотеза** — насыщение CPU одного Uvicorn worker и блокировка event loop синхронным bcrypt. В `application/auth/log_in.py` async-обработчик непосредственно вызывает синхронный `UserService.verify_password`; адаптер `password_hasher_bcrypt.py` вызывает `bcrypt.checkpw` без передачи работы executor. Во время тяжёлого входа другие async-запросы могут ожидать тот же event loop. Это согласуется с ростом latency всех операций и CPU API около одного ядра, при гораздо меньшем CPU генератора.

При этом пул достигает **20 соединений** (10+10): ограничение пула может дополнительно усиливать очередь. Его нельзя объявить свободным. Снимки показывают существенно меньше активных SQL и нулевые Lock waits, но это **не доказывает**, что БД не влияет: редкий sampling пропускает краткие пики, а завершившийся SQL может удерживать соединение, пока приложение занято CPU. Slow query log, время checkout и CPU-профиль не снимались; отсутствие индекса не установлено и не объявляется причиной.

Для подтверждения нужны отдельные контролируемые опыты: CPU-профиль; ожидание checkout/transaction duration; EXPLAIN ANALYZE главных SQL; A/B вынесение bcrypt из event loop и изменение числа workers. Нельзя ускорять тест снижением bcrypt cost и затем выдавать результат за тот же профиль защиты. Оптимизация кода в этом задании не выполнялась.

## Ограничения интерпретации

Один хост для API, контейнеров и Locust; 1 worker; 20 карточек на аккаунт; 5% входов по весу; короткие окна, одна реализация каждой ступени. Повторения для статистического разброса и длительный soak не проводились. Это выполненная базовая лабораторная проверка, не production capacity planning. CPU считается для процесса (100%=одно логическое ядро), а не как процент всех ядер хоста. Окно CPU привязано к запуску процесса Locust, окно HTTP — к его test_start; возможен небольшой сдвиг старта, поэтому CPU-summary используется как диагностическая оценка, не как точный профиль каждого запроса. Время восстановления из таблицы отсчитывается после завершения процесса Locust; до этого предусмотрен graceful drain запросов до 6 с.

## Исходные файлы

| Прогон | Сырые события | Locust CSV | Native HTML | Ресурсы | Сводка |
| --- | --- | --- | --- | --- | --- |
'''
for p in phases:
    folder='evidence/'+p['id']
    text+=f'| {p["id"]} | [samples.csv]({folder}/samples.csv) | [stats]({folder}/locust_stats.csv), [history]({folder}/locust_stats_history.csv) | [HTML]({folder}/locust.html) | [JSON]({folder}/resources.json) | [JSON]({folder}/summary.json) |\n'
(DOC/'results.md').write_text(text)

baseline=json.loads((OUT/'lint-baseline.json').read_text())
before=json.loads((OUT/'lint-new-before.json').read_text())
candidate=json.loads((OUT/'lint-candidate.json').read_text())
lint=f'''# Статическая проверка и исправления

Инструмент — Ruff с правилами из pyproject.toml. Сохранены прежнее исключение setup/config и специальные правила для миграций; результаты относятся к объявленной области проверки. До доработок исходный набор src/tests имел **{len(baseline)} нарушений** ([JSON](evidence/lint-baseline.json)). Отсутствующие старые нарушения не выдумываются. Новые loadtests включены в общий Ruff scope; runner проверяется отдельным явным путём.

Для нового runner при первом применении полного профиля приложения было {len(before)} замечаний ([сырое состояние](evidence/lint-new-before.json)). Часть относилась к допустимым для стенда тестовым конструкциям: assert, числовые параметры опыта, stdout-прогресс и синтетический пароль. Для loadtests/runner заданы узкие per-file исключения по этим соглашениям; правила приложения не ослаблены. После этого осталось **{len(candidate)} замечаний** ([кандидат](evidence/lint-candidate.json)). Нельзя выдавать смену области/правил за исправление 55 дефектов продукта.

| Замечание | Действие |
| --- | --- |
| F401, I001 | Удалён неиспользуемый UTC, импорты упорядочены Ruff. |
| E402 / INP001 / PLC0415 | Runner оформлен как модуль scripts.run_lab5, добавлен scripts/__init__.py; убрана модификация sys.path и локальный импорт UUID. |
| ANN001 / ANN202 | Добавлены типы подготовительного helper входа. |
| E501 | Длинные строки/списки форматированы и разбиты. |
| EM101 / EM102 | Сообщения исключений вынесены в переменные. |
| PLR0915 / PT018 | Ожидание старта вынесено в отдельную функцию; составная проверка deadline/PID разбита. |
| S608 (2 места) | Ручная проверка: имена таблиц и колонок только из фиксированного списка/доверенной схемы, значения связаны параметрами asyncpg. Узкий inline noqa с обоснованием, не отключение SQL-проверок проекта. |
| S603 (2 места) | Ручная проверка: фиксированный Python и argv Locust/Uvicorn, shell не используется; разрешён узкий inline noqa. |

Таким образом, 7 замечаний из 11 исправлены структурно, 4 security-предупреждения признаны ложноположительными для фиксированного стенда и документированы локально. Финальный результат проверяется командами:

```bash
.venv/bin/ruff check --no-fix .
.venv/bin/ruff check --no-fix loadtests scripts/run_lab5.py
.venv/bin/ruff format --check .
.venv/bin/ruff format --check loadtests scripts/run_lab5.py
.venv/bin/mypy --config-file pyproject.toml
```

Сборщики Markdown/графиков не входят в прикладной Ruff scope; для них дополнительно проверен синтаксис Python и фактическая генерация. Mypy сохраняет прежнюю область src (441 файл), не выдаётся за типизацию всей тестовой инфраструктуры. [Итоговый лог](evidence/quality.log). Продуктовая логика и bcrypt cost при устранении lint-замечаний не изменялись.
'''
(DOC/'static-analysis.md').write_text(lint)
provenance={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'loadtests/locustfile.py',ROOT/'loadtests/metrics.py',ROOT/'scripts/run_lab5.py',ROOT/'pyproject.toml',OUT/'run.json']}
(OUT/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False))

overview='''# Лабораторная работа № 5

Объект — API TrafficMaster, без отдельной клиентской части.

- [План нагрузки и критерии](test-plan.md).
- [Фактические измерения, графики и гипотеза узкого места](results.md).
- [Статическая проверка и исправления](static-analysis.md).
- [Матрица трассируемости ЛР1…ЛР5](traceability.md).
- [Тесты без точного требования SRS](orphan-tests.md).

## Итоговые измерения

Это повторный прогон после исправления таймера стенда; предварительные данные сохранены отдельно и в таблицу не включены.

| Прогон | VU | RPS | p95, мс | Ошибки |
| --- | --- | --- | --- | --- |
'''
for p in phases:
    overview+=f'| {p["id"]} | {p["users"]} | {p["rps"]:.2f} | {p["p95_ms"]:.2f} | {p["error_percent"]:.2f}% |\n'
if first_bad and previous:
    overview+=f'\nПервая наблюдаемая деградация — {first_bad["users"]} VU; интервал её начала **({previous["users"]}; {first_bad["users"]}]**. Внутри интервала отдельных измерений нет.\n'
overview+=f'''
NFR-07 на целевых 10 VU: **{'Passed' if target_pass else 'Failed'}**. NFR-08 восстановления: **{'Passed' if recovery_pass else 'Failed'}**. Health-проверки после снятия нагрузки заняли {run['recovery_probes']['elapsed_s']:.2f} с без смены PID; восстановительный RPS составил {recovery['rps']/target['rps']*100:.2f}% исходного целевого.

NFR-07/08 добавлены перед измерениями как экспериментальные SLO локального стенда, не как производственный SLA. Целевое несоответствие зарегистрировано как PERF-01; открытые дефекты безопасности APP-05/07 также сохраняются. Предел и фактический критерий остановки стресса описаны в протоколе; невыполненные верхние ступени не выдаются за измерения.

Матрица покрывает все 38 требований SRS 1.1; требования без тестов не обнаружены в пределах этой спецификации. Тесты без точной связи с SRS перечислены с причинами отдельно: пробелы спецификации и техническая/инфраструктурная регрессия. Покрытие требования не означает его успешную приёмку.

## Воспроизведение

```bash
uv sync --locked --group dev --group docs
.venv/bin/python -m scripts.run_lab5
.venv/bin/python -m scripts.build_lab5_report
.venv/bin/python -m scripts.build_traceability
.venv/bin/mkdocs build --strict
```

Нужен Docker daemon. Runner использует только временные контейнеры и localhost API. Токены нагрузки не включаются в отчёт. Сборщики таблиц/графиков читают реальные samples.csv и проверяют совпадение с runtime-сводками.
'''
(DOC/'README.md').write_text(overview)
