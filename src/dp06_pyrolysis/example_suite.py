from __future__ import annotations
from pathlib import Path
import argparse, hashlib, json, tempfile

from .preflight import preflight_config
from .unified import run_unified_config

def verify_example_suite(manifest_path: str | Path, reruns: int=2):
    manifest_path=Path(manifest_path).resolve()
    base=manifest_path.parent
    manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
    results=[]

    for entry in manifest["examples"]:
        run_path=base/entry["run_file"]
        pre=preflight_config(run_path)
        if pre.status!="PASS":
            raise RuntimeError(
                f"{entry['example_id']}: preflight failed: "
                + "; ".join(x["message"] for x in pre.issues)
            )

        first_bytes=None
        final=None
        with tempfile.TemporaryDirectory(prefix="pyrolysis-example-") as td:
            out_path=Path(td)/f"{entry['example_id']}_result.json"
            for _ in range(max(1,reruns)):
                out=Path(run_unified_config(run_path, output_override=out_path))
                raw=out.read_bytes()
                if first_bytes is None:
                    first_bytes=raw
                elif raw!=first_bytes:
                    raise RuntimeError(f"{entry['example_id']}: non-deterministic result bytes")
                final=json.loads(raw)

        if final["selected_model"]!=entry["expected_model"]:
            raise RuntimeError(f"{entry['example_id']}: unexpected selected model")
        if final["evidence_passport"]["evidence"]["result_status"]!=entry["expected_evidence_status"]:
            raise RuntimeError(f"{entry['example_id']}: unexpected evidence status")

        if "expected_run_sha256" in entry and final["run_sha256"]!=entry["expected_run_sha256"]:
            raise RuntimeError(f"{entry['example_id']}: run hash differs from frozen manifest")
        if "expected_passport_sha256" in entry and final["evidence_passport"]["passport_sha256"]!=entry["expected_passport_sha256"]:
            raise RuntimeError(f"{entry['example_id']}: passport hash differs from frozen manifest")

        results.append({
            "example_id":entry["example_id"],
            "status":"PASS",
            "selected_model":final["selected_model"],
            "evidence_status":final["evidence_passport"]["evidence"]["result_status"],
            "total_volatile_yield_fraction":final["outputs"]["total_volatile_yield_fraction"],
            "remaining_solid_fraction":final["outputs"]["remaining_solid_fraction"],
            "mass_closure_residual":final["mass_ledger"]["closure_residual"],
            "preflight_sha256":final["preflight"]["report_sha256"],
            "passport_sha256":final["evidence_passport"]["passport_sha256"],
            "run_sha256":final["run_sha256"],
            "exact_rerun_count":max(1,reruns),
        })
    return {
        "schema":"PyrolysisFramework_ExampleSuiteReport_v1",
        "suite_id":manifest["suite_id"],
        "example_count":len(results),
        "all_pass":True,
        "results":results,
    }

def main(argv=None):
    ap=argparse.ArgumentParser(description="Verify the qualified Pyrolysis Modelling Framework example suite.")
    ap.add_argument("manifest")
    ap.add_argument("--reruns",type=int,default=2)
    ap.add_argument("--report",default=None)
    args=ap.parse_args(argv)
    report=verify_example_suite(args.manifest,args.reruns)
    txt=json.dumps(report,indent=2,sort_keys=True)
    print(txt)
    if args.report:
        Path(args.report).write_text(txt,encoding="utf-8")

if __name__=="__main__":
    main()
