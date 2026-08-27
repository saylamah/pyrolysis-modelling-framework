from __future__ import annotations
import json
from pathlib import Path

def load_benchmark_registry(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if "benchmarks" not in data or not isinstance(data["benchmarks"], list):
        raise ValueError("invalid benchmark registry")
    ids = [b["id"] for b in data["benchmarks"]]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate benchmark IDs")
    return data
