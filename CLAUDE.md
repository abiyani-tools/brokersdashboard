# Brokers Dashboard — Angel One ADR engine

**Goal:** an online dashboard that reproduces the Excel sheet `SUMMARY - Angel One` exactly, then runs live every day. It estimates Angel One's daily revenue ("ADR") for F&O, cash, commodity broking and MTF from exchange data plus Angel's monthly and quarterly filings. More brokers will be added later; every table is keyed by `broker_id`.

**Read first:** `docs/PLAN.md` (phases, to-dos, agent routing). Read the docs below only when a task needs them:
- `docs/Angel_One_ADR_Methodology.md` — the formulas and Excel cell map
- `docs/Angel_One_ADR_Build_Plan.md` — decisions D1–D7 and the evidence behind them
- `README.md` — engine layout and the parity status

## Rules (non-negotiable)
1. **Never invent a number.** Every input traces to a filing and page (`sb_disclosure_facts.source_ref`) or to an Excel cell. If something can't be sourced, write `[SOURCE NEEDED: …]`. Sell-side and news are never the source of record.
2. **Show the arithmetic** for any derived figure. Use the Indian FY (Apr–Mar) and Rs crore for display.
3. **Parity mode is frozen.** `pytest tests/` must stay at 8,774 / 8,797 exact, with 0 unexplained. Every change from parity to live is a separate, named switch, shown as an ADR bridge (before → after).
4. **Data lake = read only.** The Supabase projects `vuswwmczfrlzjoxfvkzu` (NSE-BSE) and `avqwpebveqetwwzkmtux` (MCX) and the repos sucaanalytics-max/* and Research-Tusk/* get SELECT/GET only. Requests for changes go to their owners as a written prompt.
5. **Secrets.** Never commit keys and never ask for a service_role key in chat. CI reads `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` from GitHub secrets that AB adds himself. The publishable key is enough for reads.
6. **Write target:** only the Supabase project `everjfpbnlbcpuarnhob` (brokers-dashboard), and only its `sb_*` tables. Schema changes go through migrations.
7. AB likes a step-by-step explanation before anything irreversible: migrations, bulk updates, pushes.

## Units (the error class that hurts most)
- Exchange contracts and trades are stored as **raw counts** in `sb_market_daily`; the engine divides by 1e6.
- The quarterly funding book is in **Rs Mn**; the monthly book is in **Rs Bn**.
- Shares and revenue mix are stored as **fractions** (0.452, not 45.2).
- Daily revenue is in Rs Mn inside the engine and `revenue_cr` in the DB (÷10).

## Commands
```
python3 -m pytest tests/ -q          # parity gate (must pass before every commit)
python3 run_parity.py                # parity report
python3 src/extract/angel_monthly.py <pdf>   # parse a monthly business update → JSON facts
python3 src/extract/apply_review.py <dir>    # review-page decisions → SQL
```

## Agents (in `.claude/agents/`)
The main session runs on Opus and decides what the numbers mean. Hand bulk or mechanical work to subagents, which write their results to files so raw PDFs and query dumps stay out of the main context:
`filing-extractor` · `recompute-checker` · `engine-coder` · `lake-auditor` · `dashboard-builder` · `ops-runner`
