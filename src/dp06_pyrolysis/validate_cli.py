from __future__ import annotations
import argparse
from .preflight import preflight_config, render_preflight_text, write_preflight_report

def main(argv=None):
    ap=argparse.ArgumentParser(
        description="Validate a Pyrolysis Modelling Framework run configuration without executing kinetics."
    )
    ap.add_argument("config")
    ap.add_argument("--json-report",default=None)
    args=ap.parse_args(argv)
    report=preflight_config(args.config)
    print(render_preflight_text(report))
    if args.json_report:
        write_preflight_report(report,args.json_report)
    raise SystemExit(0 if report.status=="PASS" else 2)

if __name__=="__main__":
    main()
