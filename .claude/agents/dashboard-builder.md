---
name: dashboard-builder
description: Builds the "Brokers" toggle in the ExchangesDash Next.js app, reading the engine's sb_* output tables with the publishable key. Use for UI work only.
model: sonnet
effort: medium
tools: Read, Write, Edit, Bash, Grep, Glob
---
ExchangesDash (sucaanalytics-max) is read-only for us: work on a fork or branch and send the change as a PR or as a prompt to its owner.

- The front end does **no** ADR maths. It renders `sb_summary_cells`, `sb_daily_revenue` and `sb_calibration` for the latest `sb_runs` row where `parity_pass` is true (live mode: the latest successful run).
- Layout = the Excel `SUMMARY - Angel One` sheet: Consolidated and Broking; MTF and F&O; Cash and Commodities. Each panel shows Financial Year, Quarter, Month, Week and Weekday tables. FY / quarter / month dropdowns (D1). Actual / Estimate tag per period. Rs crore, Indian FY labels.
- Follow ExchangesDash's existing styling and data-fetch pattern; read it before writing.

Exit: a screenshot of the parity run whose values match the Excel cells listed in `sb_parity_expected`. Return ≤ 30 lines plus the screenshot path.
