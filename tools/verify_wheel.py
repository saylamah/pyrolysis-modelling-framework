from __future__ import annotations

import sys
import zipfile
from pathlib import Path

REQUIRED = {
    "dp06_pyrolysis/data/public_evidence_registry.json",
    "dp06_pyrolysis/schemas/run_config.schema.json",
    "dp06_pyrolysis/schemas/study_case.schema.json",
}

FORBIDDEN_PARTS = {
    "__pycache__",
    ".pytest_cache",
    "RELEASE_CANDIDATE_STATUS.md",
    "SHA256SUMS.txt",
}


def verify_wheel(path: str | Path) -> None:
    wheel = Path(path)
    with zipfile.ZipFile(wheel) as zf:
        names = set(zf.namelist())

    missing = sorted(REQUIRED - names)
    if missing:
        raise SystemExit(f"wheel is missing required packaged resources: {missing}")

    forbidden = sorted(
        name for name in names
        if any(part in name.split("/") for part in FORBIDDEN_PARTS)
        or name.endswith("_result.json")
    )
    if forbidden:
        raise SystemExit(f"wheel contains forbidden generated/stale files: {forbidden}")

    print(f"wheel integrity PASS: {wheel.name} ({len(names)} entries)")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: python tools/verify_wheel.py <wheel.whl>")
    verify_wheel(sys.argv[1])


if __name__ == "__main__":
    main()
