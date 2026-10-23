"""Filing watcher (PLAN 4.2) — new ANGELONE filings on NSE -> sb_documents + staged sb_disclosure_facts.

    python3 run_watch.py                      # dry run: last 45 days; writes out/filings/<date>/ only
    python3 run_watch.py --write              # ... and insert the new documents and staged facts
    python3 run_watch.py --since 2026-07-01   # a wider window
    python3 run_watch.py --force <url>        # dry-run replay of a filing that is already in sb_documents

Needs SUPABASE_SERVICE_KEY in the environment (reads sb_documents; writes only with --write) and `pdftotext`.
Exit 2 when NSE blocks the API call, 1 when a PDF could not be downloaded, else 0.

Where it runs: GitHub Actions (.github/workflows/filings.yml, 09:00 and 19:30 IST); NSE answered from CI on
23 Oct 2026. If CI starts exiting 2, run it from AB's Mac instead (NSE answers there too):
    brew install poppler; pip3 install -r requirements.txt
    set -a; . ~/.config/brokersdashboard/env; set +a      # SUPABASE_URL / SUPABASE_SERVICE_KEY, outside the repo
    WATCH_MAC_NOTIFY=1 python3 run_watch.py --write
"""
import sys

from src.extract.watch_filings import main

sys.exit(main())
