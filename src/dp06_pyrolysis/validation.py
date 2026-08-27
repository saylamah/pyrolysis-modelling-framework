from __future__ import annotations
import math
from typing import Sequence

def _pairs(pred, ref):
    if len(pred) != len(ref):
        raise ValueError("pred and ref must have equal length")
    if len(pred) == 0:
        raise ValueError("pred and ref cannot be empty")
    return [(float(p), float(r)) for p, r in zip(pred, ref)]

def mae(pred: Sequence[float], ref: Sequence[float]) -> float:
    pairs = _pairs(pred, ref)
    return sum(abs(p-r) for p,r in pairs) / len(pairs)

def rmse(pred: Sequence[float], ref: Sequence[float]) -> float:
    pairs = _pairs(pred, ref)
    return math.sqrt(sum((p-r)**2 for p,r in pairs) / len(pairs))

def integrated_absolute_error(pred: Sequence[float], ref: Sequence[float], x: Sequence[float]) -> float:
    if len(pred) != len(ref) or len(pred) != len(x) or len(x) < 2:
        raise ValueError("pred, ref, x must have equal length >= 2")
    area = 0.0
    for i in range(len(x)-1):
        dx = float(x[i+1]) - float(x[i])
        if dx <= 0:
            raise ValueError("x must be strictly increasing")
        e0 = abs(float(pred[i])-float(ref[i]))
        e1 = abs(float(pred[i+1])-float(ref[i+1]))
        area += 0.5*(e0+e1)*dx
    return area
