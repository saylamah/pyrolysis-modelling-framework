from __future__ import annotations
import argparse
from .unified import run_unified_config
from .reporting import load_result, build_user_report, render_user_report_text

def main(argv=None):
    ap=argparse.ArgumentParser(description="Pyrolysis Modelling Framework runner")
    ap.add_argument("config")
    ap.add_argument("--quiet",action="store_true")
    args=ap.parse_args(argv)

    out=run_unified_config(args.config)
    if args.quiet:
        print(out)
        return

    report=build_user_report(load_result(out))
    print(f"Result file: {out}")
    print()
    print(render_user_report_text(report))

if __name__=="__main__":
    main()
