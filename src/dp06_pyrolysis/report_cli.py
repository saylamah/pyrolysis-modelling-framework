from __future__ import annotations
from pathlib import Path
import argparse, json
from .reporting import load_result, build_user_report, render_user_report_text, render_user_report_markdown

def main(argv=None):
    ap=argparse.ArgumentParser(description="Render a human-facing Pyrolysis Modelling Framework result report.")
    ap.add_argument("result")
    ap.add_argument("--format",choices=["text","markdown","json"],default="text")
    ap.add_argument("--output",default=None)
    args=ap.parse_args(argv)

    report=build_user_report(load_result(args.result))
    if args.format=="text":
        rendered=render_user_report_text(report)
    elif args.format=="markdown":
        rendered=render_user_report_markdown(report)
    else:
        rendered=json.dumps(report,indent=2,sort_keys=True)

    if args.output:
        Path(args.output).write_text(rendered,encoding="utf-8")
    print(rendered)

if __name__=="__main__":
    main()
