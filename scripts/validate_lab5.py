"""Independently validate counts, percentile arithmetic, concurrency windows, and traceability."""

import csv
import hashlib
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/lab5/evidence"
run = json.loads((OUT / "run.json").read_text())
summary = json.loads((OUT / "summary.json").read_text())
validated = []
for phase in run["phases"]:
    folder = OUT / phase["id"]
    with (folder / "samples.csv").open() as source:
        rows = [row for row in csv.DictReader(source) if row["measured"] == "1"]
    latency = sorted(float(row["latency_ms"]) for row in rows)
    assert len(rows) == phase["requests"]
    assert abs(len(rows) / phase["duration_s"] - phase["rps"]) < 1e-8
    assert abs(latency[math.ceil(len(latency) * 0.95) - 1] - phase["p95_ms"]) < 1e-8
    assert sum(row["success"] != "1" for row in rows) == phase["errors"]
    assert phase["locust_exit"] == 0
    window = json.loads((folder / "window.json").read_text())
    assert window["shutdown_tail_s"] == 2
    with (folder / "locust_stats_history.csv").open() as source:
        history = list(csv.DictReader(source))
    begin = window["started_epoch"] + window["warmup_s"]
    end = begin + phase["duration_s"]
    steady = [row for row in history if begin <= float(row["Timestamp"]) <= end]
    assert steady and all(int(row["User Count"]) == phase["users"] for row in steady), phase["id"]
    with (folder / "locust_exceptions.csv").open() as source:
        assert not list(csv.DictReader(source))
    assert (folder / "locust.html").is_file()
    validated.append({"phase": phase["id"], "users": phase["users"], "history_rows_checked": len(steady)})
target = next(phase for phase in run["phases"] if phase["id"] == "target")
recovery = next(phase for phase in run["phases"] if phase["id"] == "recovery")
expected_target = target["requests"] >= 30 and target["rps"] >= 5 and target["p95_ms"] <= 1000 and target["error_percent"] <= 1
expected_recovery = (recovery["requests"] >= 30 and recovery["rps"] >= 0.8 * target["rps"]
    and recovery["p95_ms"] <= 1000 and recovery["error_percent"] <= 1
    and run["recovery_probes"]["healthy"] and run["recovery_probes"]["pid_unchanged"]
    and run["recovery_probes"]["elapsed_s"] <= 30)
assert summary["target_passed"] == expected_target
assert summary["recovery_passed"] == expected_recovery
trace = json.loads((OUT / "traceability-summary.json").read_text())
tests = json.loads((OUT / "test-inventory.json").read_text())
assert trace["requirements"] == trace["covered"] == 38 and not trace["uncovered"]
assert hashlib.sha256((ROOT / "docs/requirements.md").read_bytes()).hexdigest() == trace["srs_sha256"]
assert len(tests) == len({test["id"] for test in tests}) == 533 + 129 + len(run["phases"])
assert sum(not test["requirements"] for test in tests) == trace["unlinked_tests"] == 165
assert trace["unlinked_categories"]["SRS gap"] == 77
for test in tests:
    assert (ROOT / test["evidence"].split("#")[0]).exists(), test["evidence"]
for filename, digest in json.loads((OUT / "provenance.json").read_text()).items():
    assert hashlib.sha256((ROOT / filename).read_bytes()).hexdigest() == digest, filename
for doc in [*(ROOT / "docs/lab5").glob("*.md"), ROOT / "docs/requirements.md", ROOT / "README.md"]:
    for link in re.findall(r"\]\(([^)]+)\)", doc.read_text()):
        if "://" in link:
            continue
        name = link.split("#")[0]
        if name:
            assert (doc.parent / name).exists(), (doc, link)
for path in OUT.rglob("*"):
    if path.is_file() and path.suffix in [".json", ".csv", ".log", ".html"]:
        assert not re.search(r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+", path.read_text(errors="ignore")), path
assert "Documentation built" in (OUT / "mkdocs.log").read_text()
assert json.loads((OUT / "lint-final.json").read_text()) == []
assert json.loads((OUT / "lint-tools-final.json").read_text()) == []
assert "470 passed" in (OUT / "unit-regression.log").read_text()
result = {"artifact_integrity": "Passed", "concurrency_windows": validated,
          "target_slo_passed": expected_target, "recovery_slo_passed": expected_recovery,
          "requirements_covered": "38/38", "unlinked_tests": 165}
(OUT / "validation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
(OUT / "artifact-validation.log").write_text("PASS: raw counts/p95/errors, constant VU windows, task exceptions, SLO calculation, traceability, hashes, links, secret redaction, lint, unit regression and docs build.\n")
print(json.dumps(result, ensure_ascii=False))
