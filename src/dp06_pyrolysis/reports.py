from __future__ import annotations
from dataclasses import asdict
from enum import Enum
from pathlib import Path
import json

def _convert(v):
    if isinstance(v, Enum):
        return v.value
    if isinstance(v, dict):
        return {k:_convert(x) for k,x in v.items()}
    if isinstance(v, (list, tuple)):
        return [_convert(x) for x in v]
    return v

def result_to_dict(result):
    return _convert(asdict(result))

def write_result_json(result, path):
    Path(path).write_text(json.dumps(result_to_dict(result), indent=2), encoding="utf-8")
