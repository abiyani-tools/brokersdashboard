"""Weekly Brokers Update (CIO note): fetch -> facts -> render.

  python3 run_weekly.py                    # today's date; fetch, build facts, render
  python3 run_weekly.py --date 2026-12-05  # a given report date
  python3 run_weekly.py --no-fetch         # rebuild from out/weekly/<date>/raw (e.g. after editing commentary)

Writes out/weekly/<date>/: raw/, facts.json, '<YYYYMMDD>_Weekly Brokers Update.html / .pdf'
(Tusk files start with the date, AB 28 Nov 2026).
Commentary is out/weekly/<date>/commentary.json (keys: takeaways, s1..s8, optional nse_ref); missing sections
print as [COMMENTARY NEEDED]. See src/report/weekly_brokers.py for the house rules (40/60 target, no per-order rates).
"""
import argparse
import datetime as dt
import json
from pathlib import Path

from src.report.weekly_brokers import TITLE, build_facts, fetch, render

ROOT = Path(__file__).resolve().parent


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--date", default=dt.date.today().isoformat(), help="report date (folder name)")
    ap.add_argument("--no-fetch", action="store_true", help="reuse raw/ already in the folder")
    a = ap.parse_args(argv)
    d = ROOT / "out" / "weekly" / a.date
    d.mkdir(parents=True, exist_ok=True)
    if not a.no_fetch:
        fetch(d / "raw")
    facts = build_facts(d / "raw")
    (d / "facts.json").write_text(json.dumps(facts, indent=1, default=str))
    asofs = {b: f["as_of"] for b, f in facts["brokers"].items()}
    if len(set(asofs.values())) > 1:
        print(f"WARNING: brokers are on different as-of dates: {asofs}")
    cpath = d / "commentary.json"
    commentary = json.loads(cpath.read_text()) if cpath.exists() else {}
    if not commentary:
        print(f"no {cpath.relative_to(ROOT)}: the note will show [COMMENTARY NEEDED]")
    pdf = render(facts, commentary, a.date, d / f"{a.date.replace('-', '')}_{TITLE}.html")
    print(f"as of {sorted(set(asofs.values()))} -> {pdf.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
