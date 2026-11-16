"""Calculate exact windowed metrics from Locust's request event samples."""

import csv
import math
from collections import defaultdict
from pathlib import Path


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    return ordered[max(0, math.ceil(len(ordered) * fraction) - 1)] if ordered else 0.0


def phase_metrics(directory: Path, duration: float) -> dict[str, object]:
    with (directory / "samples.csv").open() as source:
        rows = [row for row in csv.DictReader(source) if row["measured"] == "1"]
    latency = [float(row["latency_ms"]) for row in rows]
    errors = sum(row["success"] != "1" for row in rows)
    by_operation = defaultdict(list)
    for row in rows:
        by_operation[row["name"]].append(float(row["latency_ms"]))
    result = {
        "requests": len(rows),
        "errors": errors,
        "error_percent": errors / len(rows) * 100 if rows else 100,
        "rps": len(rows) / duration,
        "mean_ms": sum(latency) / len(latency) if latency else 0,
        "p50_ms": percentile(latency, 0.5),
        "p95_ms": percentile(latency, 0.95),
        "p99_ms": percentile(latency, 0.99),
        "duration_s": duration,
        "operations": {
            name: {"requests": len(times), "p95_ms": percentile(times, 0.95)}
            for name, times in sorted(by_operation.items())
        },
    }
    result["slo_passed"] = bool(len(rows) >= 30 and result["p95_ms"] <= 1000 and result["error_percent"] <= 1)
    return result
