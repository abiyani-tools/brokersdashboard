Data notice (no schema change), as `docs/BROKERS_INTEGRATION.md` asks. Brokers-dashboard project `everjfpbnlbcpuarnhob`, 2 Nov 2026:

- **`sb_calendar`:**
  - 83 days added, 2023-06-01 .. 2023-09-28. The calendar now starts on 1 June 2023.
  - `is_mcx_day` corrected to `true` on 121 existing days, 2023-09-29 .. 2024-03-28. MCX traded on those days, but the original seed marked them closed.
- **`sb_market_daily`:** rows for 2023-06-01 .. 2023-09-28 from your public dashboard JSON (source `exchangesdash_json`), so the daily refresh now starts on 1 June 2023.
- **Published figures:** no published ADR value changed. The new runs (Angel One `e0604af8`, Groww `c616af75`, MOSL `db9e9d6f`) differ from the previous ones only in "insufficient data" note wording, plus Groww's open-quarter MTF cells, which moved with Groww's own investor-relations page.

The views in this PR need no change.
