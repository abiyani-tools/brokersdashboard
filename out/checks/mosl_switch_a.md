# MOSL switch m-a (reported quarters from the data book): independent recompute

Script: `out/checks/mosl_switch_a_check.py` (stdlib json/math/csv/re; run from the repo root). Inputs: `docs/MOSL_ADR_Methodology.md`, `docs/MOSL_LIVE_SPEC.md`, `snapshot/mosl_snapshot_2026-10-23.json`, `snapshot/mosl_facts_reviewed_2026-11-02.json`, `snapshot/mosl_lake_2026-11-02.json`, `snapshot/db_snapshot_2026-10-23.json` (calendar, MCX, industry MTF book); `snapshot/mosl_fixtures_2026-10-23.json` only to prove the parity rebuild. No file under `src/engine/` or `src/live/` was read.

**Result: 324/324 items agree** (213 to 1e-6 relative; the rest agree to the print precision of the bridge).

| Item kind | Checked | Agree | Agree at 1e-6 |
|---|---:|---:|---:|
| ADR | 30 | 30 | 30 |
| summary | 5 | 5 | 5 |
| param | 80 | 80 | 5 |
| week/weekday | 25 | 25 | 25 |
| daily | 4 | 4 | 4 |
| count | 3 | 3 | 3 |
| input | 37 | 37 | 9 |
| input-equal | 73 | 73 | 73 |
| facts-tie | 20 | 20 | 20 |
| tie | 30 | 30 | 30 |
| spec | 8 | 8 | 0 |
| pin | 9 | 9 | 9 |

No disagreement with the bridge.

## ADR, Rs crore per trading day (all panels shown by the bridge)

| Period | Panel | My before | Bridge before | My after | Bridge after | Max rel diff | Verdict |
|---|---|---:|---:|---:|---:|---:|---|
| FY 2027 | Consolidated | 5.793069 | 5.793069 | 6.083537 | 6.083537 | 2.5e-08 | agree |
| FY 2027 | Broking | 1.805429 | 1.805429 | 1.871544 | 1.871544 | 1.4e-07 | agree |
| FY 2027 | MTF | 3.987640 | 3.987640 | 4.211993 | 4.211993 | 9.7e-08 | agree |
| FY 2027 | F&O | 1.805429 | 1.805429 | 1.871544 | 1.871544 | 1.4e-07 | agree |
| FY 2027 | Cash | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.0e+00 | agree |
| FY 2027 | Commodities | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.0e+00 | agree |
| Q2 FY 2027 | Consolidated | 8.306287 | 8.306287 | 8.967060 | 8.967060 | 4.9e-08 | agree |
| Q2 FY 2027 | Broking | 4.015205 | 4.015205 | 4.247980 | 4.247980 | 9.1e-08 | agree |
| Q2 FY 2027 | MTF | 4.291082 | 4.291082 | 4.719079 | 4.719079 | 3.7e-08 | agree |
| Q2 FY 2027 | F&O | 1.581762 | 1.581762 | 1.694618 | 1.694618 | 2.6e-07 | agree |
| Q2 FY 2027 | Cash | 1.664697 | 1.664697 | 2.031303 | 2.031303 | 2.6e-07 | agree |
| Q2 FY 2027 | Commodities | 0.768746 | 0.768746 | 0.522060 | 0.522060 | 4.6e-07 | agree |
| Q1 FY 2027 | Consolidated | 8.174450 | 8.174450 | 8.197926 | 8.197926 | 5.9e-08 | agree |
| Q1 FY 2027 | Broking | 4.521111 | 4.521111 | 4.544588 | 4.544588 | 6.8e-08 | agree |
| Q1 FY 2027 | MTF | 3.653339 | 3.653339 | 3.653339 | 3.653339 | 9.6e-08 | agree |
| Q1 FY 2027 | F&O | 1.967174 | 1.967174 | 1.963321 | 1.963321 | 9.1e-08 | agree |
| Q1 FY 2027 | Cash | 2.030666 | 2.030666 | 2.060675 | 2.060675 | 1.3e-07 | agree |
| Q1 FY 2027 | Commodities | 0.523271 | 0.523271 | 0.520592 | 0.520592 | 4.5e-07 | agree |
| FY 2027 October | Consolidated | 2.177250 | 2.177250 | 2.332592 | 2.332592 | 6.8e-08 | agree |
| FY 2027 October | Broking | 2.177250 | 2.177250 | 2.332592 | 2.332592 | 6.8e-08 | agree |
| FY 2027 October | MTF | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.0e+00 | agree |
| FY 2027 October | F&O | 2.177250 | 2.177250 | 2.332592 | 2.332592 | 6.8e-08 | agree |
| FY 2027 October | Cash | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.0e+00 | agree |
| FY 2027 October | Commodities | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.0e+00 | agree |
| FY 2026 | Consolidated | 7.643822 | 7.643822 | 7.642700 | 7.642700 | 1.6e-08 | agree |
| FY 2026 | Broking | 4.330415 | 4.330415 | 4.329293 | 4.329293 | 7.3e-08 | agree |
| FY 2026 | MTF | 3.313407 | 3.313407 | 3.313407 | 3.313407 | 5.9e-08 | agree |
| FY 2026 | F&O | 1.849851 | 1.849851 | 1.849289 | 1.849289 | 2.7e-07 | agree |
| FY 2026 | Cash | 1.881511 | 1.881511 | 1.880952 | 1.880952 | 2.6e-07 | agree |
| FY 2026 | Commodities | 0.599053 | 0.599053 | 0.599053 | 0.599053 | 3.9e-07 | agree |

## Parameters that moved

| Segment | Quantity | Quarter | My before | Bridge before | My after | Bridge after | Bridge d% | Max rel diff | Verdict |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| Cash | 'delivery ratio' H | Q1 FY 2025 | — | — | 2.5087 | 2.5087 |  | 1.6e-06 | agree |
| Cash | 'delivery ratio' H | Q2 FY 2025 | — | — | 2.44274 | 2.4427 |  | 1.7e-05 | agree |
| Cash | 'delivery ratio' H | Q3 FY 2025 | 2.52354 | 2.5235 | 2.52384 | 2.5238 | +0.012% | 1.7e-05 | agree |
| Cash | 'delivery ratio' H | Q4 FY 2025 | 2.71989 | 2.7199 | 2.7194 | 2.7194 | -0.018% | 3.6e-06 | agree |
| Cash | 'delivery ratio' H | Q4 FY 2026 | 2.90525 | 2.9053 | 2.89592 | 2.8959 | -0.321% | 1.6e-05 | agree |
| Cash | 'delivery ratio' H | Q1 FY 2027 | 2.78748 | 2.7875 | 2.77827 | 2.7783 | -0.330% | 1.1e-05 | agree |
| Cash | 'delivery ratio' H | Q2 FY 2027 | 2.78457 | 2.7846 | 2.76177 | 2.7618 | -0.819% | 1.2e-05 | agree |
| Cash | 'delivery ratio' H | Q3 FY 2027 | 2.82577 | 2.8258 | 2.81199 | 2.8120 | -0.488% | 1.2e-05 | agree |
| Cash | gross per Rs of reported ADTO J | Q1 FY 2025 | — | — | 0.0736273 | 0.0736 |  | 3.7e-04 | agree |
| Cash | gross per Rs of reported ADTO J | Q2 FY 2025 | — | — | 0.0783396 | 0.0783 |  | 5.1e-04 | agree |
| Cash | gross per Rs of reported ADTO J | Q3 FY 2025 | 0.0686303 | 0.0686 | 0.0685444 | 0.0685 | -0.125% | 6.5e-04 | agree |
| Cash | gross per Rs of reported ADTO J | Q4 FY 2025 | 0.0653772 | 0.0654 | 0.0655226 | 0.0655 | +0.222% | 3.5e-04 | agree |
| Cash | gross per Rs of reported ADTO J | Q4 FY 2026 | 0.0633378 | 0.0633 | 0.0632518 | 0.0633 | -0.136% | 7.6e-04 | agree |
| Cash | gross per Rs of reported ADTO J | Q1 FY 2027 | 0.0633378 | 0.0633 | 0.0642652 | 0.0643 | +1.464% | 6.0e-04 | agree |
| Cash | gross per Rs of reported ADTO J | Q2 FY 2027 | 0.0633378 | 0.0633 | 0.0636376 | 0.0636 | +0.473% | 6.0e-04 | agree |
| Cash | gross per Rs of reported ADTO J | Q3 FY 2027 | 0.0633378 | 0.0633 | 0.0636376 | 0.0636 | +0.473% | 6.0e-04 | agree |
| Cash | model gross brokerage Rs Cr | Q1 FY 2025 | — | — | 313.176 | 313.18 |  | 1.4e-05 | agree |
| Cash | model gross brokerage Rs Cr | Q2 FY 2025 | — | — | 359.444 | 359.44 |  | 1.2e-05 | agree |
| Cash | model gross brokerage Rs Cr | Q3 FY 2025 | 233 | 233.00 | 232.68 | 232.68 | -0.137% | 9.1e-07 | agree |
| Cash | model gross brokerage Rs Cr | Q4 FY 2025 | 169 | 169.00 | 169.407 | 169.41 | +0.241% | 2.0e-05 | agree |
| Cash | model gross brokerage Rs Cr | Q4 FY 2026 | 189 | 189.00 | 188.744 | 188.74 | -0.135% | 2.1e-05 | agree |
| Cash | model gross brokerage Rs Cr | Q1 FY 2027 | 224.976 | 224.98 | 228.301 | 228.30 | +1.478% | 1.8e-05 | agree |
| Cash | model gross brokerage Rs Cr | Q2 FY 2027 | 200.16 | 200.16 | 237.794 | 237.79 | +18.802% | 1.5e-05 | agree |
| Cash | model gross brokerage Rs Cr | Q3 FY 2027 | 197.462 | 197.46 | 233.808 | 233.81 | +18.407% | 8.2e-06 | agree |
| Cash | model net brokerage Rs Cr | Q1 FY 2025 | — | — | 164.046 | 164.05 |  | 2.2e-05 | agree |
| Cash | model net brokerage Rs Cr | Q2 FY 2025 | — | — | 193.282 | 193.28 |  | 9.3e-06 | agree |
| Cash | model net brokerage Rs Cr | Q3 FY 2025 | 128.128 | 128.13 | 127.952 | 127.95 | -0.137% | 1.9e-05 | agree |
| Cash | model net brokerage Rs Cr | Q4 FY 2025 | 91.101 | 91.1010 | 91.3202 | 91.3202 | +0.241% | 5.4e-07 | agree |
| Cash | model net brokerage Rs Cr | Q4 FY 2026 | 101.988 | 101.99 | 101.85 | 101.85 | -0.135% | 1.5e-05 | agree |
| Cash | model net brokerage Rs Cr | Q1 FY 2027 | 121.84 | 121.84 | 123.641 | 123.64 | +1.478% | 4.1e-06 | agree |
| Cash | model net brokerage Rs Cr | Q2 FY 2027 | 108.205 | 108.21 | 132.035 | 132.03 | +22.022% | 4.4e-05 | agree |
| Cash | net / gross | Q2 FY 2027 | 0.540595 | 0.5406 | 0.555249 | 0.5552 | +2.711% | 8.8e-05 | agree |
| Cash | share (cancels) | Q1 FY 2025 | — | — | 0.0809329 | 0.0809 |  | 4.1e-04 | agree |
| Cash | share (cancels) | Q2 FY 2025 | — | — | 0.0807394 | 0.0807 |  | 4.9e-04 | agree |
| Cash | share (cancels) | Q4 FY 2026 | 0.068 | 0.0680 | 0.0677819 | 0.0678 | -0.321% | 2.7e-04 | agree |
| Cash | share (cancels) | Q1 FY 2027 | 0.068 | 0.0680 | 0.0677844 | 0.0678 | -0.317% | 2.3e-04 | agree |
| Cash | share (cancels) | Q2 FY 2027 | 0.068 | 0.0680 | 0.0797467 | 0.0797 | +17.275% | 5.9e-04 | agree |
| Cash | share (cancels) | Q3 FY 2027 | 0.068 | 0.0680 | 0.0797467 | 0.0797 | +17.275% | 5.9e-04 | agree |
| Commodities | gross Rs per MOSL contract | Q1 FY 2027 | 7.32651 | 7.3265 | 7.2687 | 7.2687 | -0.789% | 1.2e-06 | agree |
| Commodities | gross Rs per MOSL contract | Q2 FY 2027 | 7.32651 | 7.3265 | 5.44149 | 5.4415 | -25.729% | 2.6e-06 | agree |
| Commodities | model gross brokerage Rs Cr | Q1 FY 2027 | 55 | 55.0000 | 54.7184 | 54.7184 | -0.512% | 6.0e-07 | agree |
| Commodities | model gross brokerage Rs Cr | Q2 FY 2027 | 86.4739 | 86.4739 | 57.9686 | 57.9686 | -32.964% | 4.5e-07 | agree |
| Commodities | model net brokerage Rs Cr | Q1 FY 2027 | 33.4894 | 33.4894 | 33.3179 | 33.3179 | -0.512% | 1.2e-06 | agree |
| Commodities | model net brokerage Rs Cr | Q2 FY 2027 | 50.7373 | 50.7373 | 34.4559 | 34.4559 | -32.089% | 1.4e-06 | agree |
| Commodities | net / gross | Q2 FY 2027 | 0.586735 | 0.5867 | 0.59439 | 0.5944 | +1.305% | 6.0e-05 | agree |
| Commodities | share | Q1 FY 2027 | 0.077 | 0.0770 | 0.077215 | 0.0772 | +0.279% | 1.9e-04 | agree |
| Commodities | share | Q2 FY 2027 | 0.0869754 | 0.0870 | 0.0785026 | 0.0785 | -9.742% | 2.8e-04 | agree |
| F&O | gross Rs per contract | Q1 FY 2025 | 0 | 0.0000 | 0.749805 | 0.7498 |  | 6.4e-06 | agree |
| F&O | gross Rs per contract | Q2 FY 2025 | 0 | 0.0000 | 0.660645 | 0.6606 |  | 6.8e-05 | agree |
| F&O | gross Rs per contract | Q3 FY 2025 | 0.744971 | 0.7450 | 0.743441 | 0.7434 | -0.205% | 5.5e-05 | agree |
| F&O | gross Rs per contract | Q4 FY 2025 | 1.67298 | 1.6730 | 1.6758 | 1.6758 | +0.168% | 9.4e-06 | agree |
| F&O | gross Rs per contract | Q4 FY 2026 | 1.47591 | 1.4759 | 1.4671 | 1.4671 | -0.597% | 4.4e-06 | agree |
| F&O | gross Rs per contract | Q1 FY 2027 | 1.42759 | 1.4276 | 1.43976 | 1.4398 | +0.852% | 2.6e-05 | agree |
| F&O | gross Rs per contract | Q2 FY 2027 | 1.42759 | 1.4276 | 1.31765 | 1.3176 | -7.702% | 3.6e-05 | agree |
| F&O | gross Rs per contract | Q3 FY 2027 | 1.42759 | 1.4276 | 1.31765 | 1.3176 | -7.702% | 3.6e-05 | agree |
| F&O | model gross brokerage Rs Cr | Q1 FY 2025 | 0 | 0.0000 | 262.708 | 262.71 |  | 7.8e-06 | agree |
| F&O | model gross brokerage Rs Cr | Q2 FY 2025 | 0 | 0.0000 | 268.795 | 268.80 |  | 1.7e-05 | agree |
| F&O | model gross brokerage Rs Cr | Q3 FY 2025 | 225 | 225.00 | 224.538 | 224.54 | -0.205% | 9.1e-06 | agree |
| F&O | model gross brokerage Rs Cr | Q4 FY 2025 | 182 | 182.00 | 182.307 | 182.31 | +0.168% | 1.9e-05 | agree |
| F&O | model gross brokerage Rs Cr | Q4 FY 2026 | 203 | 203.00 | 202.758 | 202.76 | -0.119% | 8.5e-06 | agree |
| F&O | model gross brokerage Rs Cr | Q1 FY 2027 | 206 | 206.00 | 205.597 | 205.60 | -0.196% | 1.7e-05 | agree |
| F&O | model gross brokerage Rs Cr | Q2 FY 2027 | 179.13 | 179.13 | 188.468 | 188.47 | +5.212% | 1.3e-05 | agree |
| F&O | model gross brokerage Rs Cr | Q3 FY 2027 | 49.3136 | 49.3136 | 51.884 | 51.8840 | +5.212% | 8.7e-07 | agree |
| F&O | model net brokerage Rs Cr | Q1 FY 2025 | 0 | 0.0000 | 149.58 | 149.58 |  | 1.9e-06 | agree |
| F&O | model net brokerage Rs Cr | Q2 FY 2025 | 0 | 0.0000 | 154.764 | 154.76 |  | 2.3e-05 | agree |
| F&O | model net brokerage Rs Cr | Q3 FY 2025 | 135.253 | 135.25 | 134.975 | 134.98 | -0.205% | 3.7e-05 | agree |
| F&O | model net brokerage Rs Cr | Q4 FY 2025 | 106.943 | 106.94 | 107.123 | 107.12 | +0.168% | 3.0e-05 | agree |
| F&O | model net brokerage Rs Cr | Q4 FY 2026 | 116.718 | 116.72 | 116.579 | 116.58 | -0.119% | 1.5e-05 | agree |
| F&O | model net brokerage Rs Cr | Q1 FY 2027 | 118.03 | 118.03 | 117.799 | 117.80 | -0.196% | 6.3e-06 | agree |
| F&O | model net brokerage Rs Cr | Q2 FY 2027 | 102.815 | 102.81 | 110.15 | 110.15 | +7.135% | 4.4e-05 | agree |
| F&O | model net brokerage Rs Cr | Q3 FY 2027 | 28.3043 | 28.3043 | 30.3237 | 30.3237 | +7.135% | 1.7e-06 | agree |
| F&O | net / gross | Q2 FY 2027 | 0.573965 | 0.5740 | 0.584452 | 0.5845 | +1.827% | 8.3e-05 | agree |
| F&O | net / gross | Q3 FY 2027 | 0.573965 | 0.5740 | 0.584452 | 0.5845 | +1.827% | 8.3e-05 | agree |
| F&O | premium share (cancels) | Q4 FY 2026 | 0.07 | 0.0700 | 0.0703365 | 0.0703 | +0.481% | 5.2e-04 | agree |
| F&O | premium share (cancels) | Q1 FY 2027 | 0.076911 | 0.0769 | 0.0761116 | 0.0761 | -1.039% | 1.5e-04 | agree |
| F&O | premium share (cancels) | Q2 FY 2027 | 0.076911 | 0.0769 | 0.0876721 | 0.0877 | +13.992% | 3.2e-04 | agree |
| F&O | premium share (cancels) | Q3 FY 2027 | 0.076911 | 0.0769 | 0.0876721 | 0.0877 | +13.992% | 3.2e-04 | agree |
| MTF | NII yield | Q3 FY 2027 | — | — | 0.129383 | 0.1294 |  | 1.3e-04 | agree |
| MTF | share of industry book | Q2 FY 2027 | 0.0577589 | 0.0578 | 0.0635198 | 0.0635 | +9.974% | 7.1e-04 | agree |
| MTF | share of industry book | Q3 FY 2027 | — | — | 0.0635198 | 0.0635 |  | 3.1e-04 | agree |

## Consolidated week / weekday tables (as of the last date of each segment)

| Table | Row | My before | Bridge before | My after | Bridge after | Max rel diff | Verdict |
|---|---|---:|---:|---:|---:|---:|---|
| Week | Last 5 trading days | 9.081894 | 9.081894 | 9.774980 | 9.774980 | 5.3e-08 | agree |
| Week | Last 5 trading days | vs 45D | 9.081894 | 9.081894 | 9.774980 | 9.774980 | 5.3e-08 | agree |
| Week | Previous 5 trading days | 9.529330 | 9.529330 | 9.998240 | 9.998240 | 3.8e-08 | agree |
| Week | Last 45 trading days | 8.526564 | 8.526564 | 9.189508 | 9.189508 | 1.0e-08 | agree |
| Week | Last 20 trading days | 9.053290 | 9.053290 | 9.699266 | 9.699266 | 2.5e-08 | agree |
| Weekday | Monday | 9.706808 | 9.706808 | 10.577803 | 10.577803 | 4.5e-08 | agree |
| Weekday | Monday | vs 10 | 9.706808 | 9.706808 | 10.577803 | 10.577803 | 4.5e-08 | agree |
| Weekday | Average of last 3 Mondays | 8.532289 | 8.532289 | 9.257750 | 9.257750 | 1.8e-08 | agree |
| Weekday | Average of last 10 Mondays | 8.047581 | 8.047581 | 8.641918 | 8.641918 | 4.9e-08 | agree |
| Weekday | Tuesday | 9.406722 | 9.406722 | 10.274615 | 10.274615 | 3.4e-08 | agree |
| Weekday | Tuesday | vs 10 | 9.406722 | 9.406722 | 10.274615 | 10.274615 | 3.4e-08 | agree |
| Weekday | Average of last 3 Tuesdays | 9.555182 | 9.555182 | 10.293089 | 10.293089 | 1.7e-08 | agree |
| Weekday | Average of last 10 Tuesdays | 8.849795 | 8.849795 | 9.605023 | 9.605023 | 3.3e-08 | agree |
| Weekday | Wednesday | 8.106165 | 8.106165 | 8.856868 | 8.856868 | 2.0e-08 | agree |
| Weekday | Wednesday | vs 10 | 8.106165 | 8.106165 | 8.856868 | 8.856868 | 2.0e-08 | agree |
| Weekday | Average of last 3 Wednesdays | 8.776472 | 8.776472 | 9.281215 | 9.281215 | 2.6e-08 | agree |
| Weekday | Average of last 10 Wednesdays | 8.004871 | 8.004871 | 8.649845 | 8.649845 | 4.8e-08 | agree |
| Weekday | Thursday | 10.954808 | 10.954808 | 11.580231 | 11.580231 | 1.3e-08 | agree |
| Weekday | Thursday | vs 10 | 10.954808 | 10.954808 | 11.580231 | 11.580231 | 1.3e-08 | agree |
| Weekday | Average of last 3 Thursdays | 11.594884 | 11.594884 | 12.007931 | 12.007931 | 3.9e-08 | agree |
| Weekday | Average of last 10 Thursdays | 9.792755 | 9.792755 | 10.476552 | 10.476552 | 3.9e-08 | agree |
| Weekday | Friday | 8.609751 | 8.609751 | 9.058258 | 9.058258 | 3.7e-08 | agree |
| Weekday | Friday | vs 10 | 8.609751 | 8.609751 | 9.058258 | 9.058258 | 3.7e-08 | agree |
| Weekday | Average of last 3 Fridays | 7.899023 | 7.899023 | 8.495864 | 8.495864 | 1.1e-08 | agree |
| Weekday | Average of last 10 Fridays | 7.506215 | 7.506215 | 8.120077 | 8.120077 | 3.2e-08 | agree |

## Daily revenue rows that changed

| Segment | Mine | Bridge | Verdict | Note |
|---|---|---|---|---|
| F&O | days 757->757, changed 446, added 0, dropped 0, first 2024-04-01, last 2026-10-21, ratio 0.997946459..1.071347780 | days 757->757, changed 446, added 0, dropped 0, first 2024-04-01, last 2026-10-21, ratio 0.997946459..1.071347780 | agree |  |
| Cash | days 509->634, changed 309, added 125, dropped 0, first 2024-10-01, last 2026-09-30, ratio 0.998627514..1.220224128 | days 509->634, changed 309, added 125, dropped 0, first 2024-10-01, last 2026-09-30, ratio 0.998627514..1.220224128 | agree |  |
| Commodities | days 653->653, changed 130, added 0, dropped 0, first 2026-04-01, last 2026-09-30, ratio 0.679105448..0.994879402 | days 653->653, changed 130, added 0, dropped 0, first 2026-04-01, last 2026-09-30, ratio 0.679105448..0.994879402 | agree |  |
| MTF | days 495->495, changed 65, added 0, dropped 0, first 2026-07-01, last 2026-09-30, ratio 1.099741078..1.099741078 | days 495->495, changed 65, added 0, dropped 0, first 2026-07-01, last 2026-09-30, ratio 1.099741078..1.099741078 | agree |  |

## Inputs replaced by reviewed facts (37 listed in the bridge)

| Input | Period | My workbook | Bridge workbook | My live | Bridge live | My facts | Bridge facts | Verdict |
|---|---|---:|---:|---:|---:|---|---|---|
| adto_cash_mosl | Q1 FY 2025 | — | — | 4253.53 | 4,253.53 | 20001 | 20001 | agree |
| adto_cash_mosl | Q2 FY 2025 | — | — | 4588.28 | 4,588.28 | 20002 | 20002 | agree |
| adto_cash_mosl | Q3 FY 2025 | 3395 | 3,395.00 | 3394.59 | 3,394.59 | 20003 | 20003 | agree |
| adto_cash_mosl | Q4 FY 2025 | 2585 | 2,585.00 | 2585.47 | 2,585.47 | 20004 | 20004 | agree |
| adto_cash_mosl | Q4 FY 2026 | 2984 | 2,984.00 | 2984.01 | 2,984.01 | 20008 | 20008 | agree |
| adto_cash_mosl | Q1 FY 2027 | 3552 | 3,552.00 | 3552.47 | 3,552.47 | 20009 | 20009 | agree |
| adto_cash_mosl | Q2 FY 2027 | — | — | 3736.68 | 3,736.68 | 20010 | 20010 | agree |
| gross_cash_cr | Q1 FY 2025 | — | — | 313.176 | 313.18 | 20061 | 20061 | agree |
| gross_cash_cr | Q2 FY 2025 | — | — | 359.444 | 359.44 | 20062 | 20062 | agree |
| gross_cash_cr | Q3 FY 2025 | 233 | 233.00 | 232.68 | 232.68 | 20063 | 20063 | agree |
| gross_cash_cr | Q4 FY 2025 | 169 | 169.00 | 169.407 | 169.41 | 20064 | 20064 | agree |
| gross_cash_cr | Q4 FY 2026 | 189 | 189.00 | 188.744 | 188.74 | 20068 | 20068 | agree |
| gross_cash_cr | Q1 FY 2027 | 228 | 228.00 | 228.301 | 228.30 | 20069 | 20069 | agree |
| gross_cash_cr | Q2 FY 2027 | — | — | 237.794 | 237.79 | 20070 | 20070 | agree |
| gross_comm_cr | Q1 FY 2027 | 55 | 55.0000 | 54.7184 | 54.7184 | 20089 | 20089 | agree |
| gross_comm_cr | Q2 FY 2027 | — | — | 57.9686 | 57.9686 | 20090 | 20090 | agree |
| gross_fo_cr | Q1 FY 2025 | — | — | 262.708 | 262.71 | 20071 | 20071 | agree |
| gross_fo_cr | Q2 FY 2025 | — | — | 268.795 | 268.80 | 20072 | 20072 | agree |
| gross_fo_cr | Q3 FY 2025 | 225 | 225.00 | 224.538 | 224.54 | 20073 | 20073 | agree |
| gross_fo_cr | Q4 FY 2025 | 182 | 182.00 | 182.307 | 182.31 | 20074 | 20074 | agree |
| gross_fo_cr | Q4 FY 2026 | 203 | 203.00 | 202.758 | 202.76 | 20078 | 20078 | agree |
| gross_fo_cr | Q1 FY 2027 | 206 | 206.00 | 205.597 | 205.60 | 20079 | 20079 | agree |
| gross_fo_cr | Q2 FY 2027 | — | — | 188.468 | 188.47 | 20080 | 20080 | agree |
| mtf_book_closing | Q2 FY 2027 | — | — | 9600 | 9,600.00 | 20200 | 20200 | agree |
| net_gross_cash | Q2 FY 2027 | — | — | 0.555249 | 0.5552 | 20120, 20070 | 20120, 20070 | agree |
| net_gross_comm | Q2 FY 2027 | — | — | 0.59439 | 0.5944 | 20140, 20090 | 20140, 20090 | agree |
| net_gross_fo | Q2 FY 2027 | — | — | 0.584452 | 0.5845 | 20130, 20080 | 20130, 20080 | agree |
| share_cash | Q1 FY 2025 | — | — | 0.0809329 | 0.0809 | 20161 | 20161 | agree |
| share_cash | Q2 FY 2025 | — | — | 0.0807394 | 0.0807 | 20162 | 20162 | agree |
| share_cash | Q4 FY 2026 | 0.068 | 0.0680 | 0.0677819 | 0.0678 | 20168 | 20168 | agree |
| share_cash | Q1 FY 2027 | 0.068 | 0.0680 | 0.0677844 | 0.0678 | 20169 | 20169 | agree |
| share_cash | Q2 FY 2027 | — | — | 0.0797467 | 0.0797 | 20170 | 20170 | agree |
| share_comm | Q1 FY 2027 | 0.077 | 0.0770 | 0.077215 | 0.0772 | 20189 | 20189 | agree |
| share_comm | Q2 FY 2027 | — | — | 0.0785026 | 0.0785 | 20190 | 20190 | agree |
| share_fo | Q4 FY 2026 | 0.07 | 0.0700 | 0.0703365 | 0.0703 | 20178 | 20178 | agree |
| share_fo | Q1 FY 2027 | — | — | 0.0761116 | 0.0761 | 20179 | 20179 | agree |
| share_fo | Q2 FY 2027 | — | — | 0.0876721 | 0.0877 | 20180 | 20180 | agree |

## Data-book facts: gross / net total = cash + F&O + commodity + currency (Rs Mn)

| Quarter | Quantity | Sum of segments | Fact total | Rel diff | Verdict |
|---|---|---:|---:|---:|---|
| Q1 FY 2025 | gross | 6106.9105 | 6106.9105 | 1.6e-13 | agree |
| Q1 FY 2025 | net | 3345.1430 | 3345.1430 | 3.0e-13 | agree |
| Q2 FY 2025 | gross | 6655.7381 | 6655.7381 | 0.0e+00 | agree |
| Q2 FY 2025 | net | 3717.6092 | 3717.6092 | 1.2e-16 | agree |
| Q3 FY 2025 | gross | 4977.9784 | 4977.9784 | 0.0e+00 | agree |
| Q3 FY 2025 | net | 2883.2677 | 2883.2677 | 0.0e+00 | agree |
| Q4 FY 2025 | gross | 3919.5609 | 3919.5609 | 0.0e+00 | agree |
| Q4 FY 2025 | net | 2241.6903 | 2241.6903 | 0.0e+00 | agree |
| Q1 FY 2026 | gross | 4867.2254 | 4867.2254 | 2.1e-13 | agree |
| Q1 FY 2026 | net | 2867.1937 | 2867.1937 | 0.0e+00 | agree |
| Q2 FY 2026 | gross | 4441.9144 | 4441.9144 | 0.0e+00 | agree |
| Q2 FY 2026 | net | 2495.3766 | 2495.3766 | 1.8e-16 | agree |
| Q3 FY 2026 | gross | 4833.7389 | 4833.7389 | 1.9e-16 | agree |
| Q3 FY 2026 | net | 2717.4471 | 2717.4471 | 3.7e-13 | agree |
| Q4 FY 2026 | gross | 4831.1151 | 4831.1151 | 2.1e-13 | agree |
| Q4 FY 2026 | net | 2701.5405 | 2701.5405 | 0.0e+00 | agree |
| Q1 FY 2027 | gross | 4905.9107 | 4905.9107 | 0.0e+00 | agree |
| Q1 FY 2027 | net | 2758.5247 | 2758.5247 | 1.6e-16 | agree |
| Q2 FY 2027 | gross | 4855.0361 | 4855.0361 | 2.1e-13 | agree |
| Q2 FY 2027 | net | 2774.1423 | 2774.1423 | 3.6e-13 | agree |

## Tie-out of calibrated quarters: sum of daily gross revenue vs the reported gross (Rs Cr)

| Segment | Quarter | Reported gross | Sum of daily gross | Rel diff | Verdict |
|---|---|---:|---:|---:|---|
| F&O | Q1 FY 2025 | 262.707939 | 262.707939 | 0.0e+00 | agree |
| F&O | Q2 FY 2025 | 268.795420 | 268.795420 | 4.2e-16 | agree |
| F&O | Q3 FY 2025 | 224.537953 | 224.537953 | 0.0e+00 | agree |
| F&O | Q4 FY 2025 | 182.306512 | 182.306512 | 1.6e-16 | agree |
| F&O | Q1 FY 2026 | 186.413500 | 186.413500 | 3.0e-16 | agree |
| F&O | Q2 FY 2026 | 188.027571 | 188.027571 | 0.0e+00 | agree |
| F&O | Q3 FY 2026 | 200.926973 | 200.926973 | 4.2e-16 | agree |
| F&O | Q4 FY 2026 | 202.758269 | 202.758269 | 1.4e-16 | agree |
| F&O | Q1 FY 2027 | 205.596528 | 205.596528 | 2.8e-16 | agree |
| F&O | Q2 FY 2027 | 188.467550 | 188.467550 | 1.5e-16 | agree |
| Cash | Q1 FY 2025 | 313.175677 | 313.175677 | 1.8e-16 | agree |
| Cash | Q2 FY 2025 | 359.444249 | 359.444249 | 4.7e-16 | agree |
| Cash | Q3 FY 2025 | 232.680211 | 232.680211 | 2.4e-16 | agree |
| Cash | Q4 FY 2025 | 169.406639 | 169.406639 | 6.7e-16 | agree |
| Cash | Q1 FY 2026 | 252.562529 | 252.562529 | 2.3e-16 | agree |
| Cash | Q2 FY 2026 | 204.686622 | 204.686622 | 2.8e-16 | agree |
| Cash | Q3 FY 2026 | 196.852518 | 196.852518 | 2.9e-16 | agree |
| Cash | Q4 FY 2026 | 188.744040 | 188.744040 | 1.5e-16 | agree |
| Cash | Q1 FY 2027 | 228.300533 | 228.300533 | 5.0e-16 | agree |
| Cash | Q2 FY 2027 | 237.793685 | 237.793685 | 2.4e-16 | agree |
| Commodities | Q1 FY 2025 | 33.292943 | 33.292943 | 2.1e-16 | agree |
| Commodities | Q2 FY 2025 | 36.708572 | 36.708572 | 1.9e-16 | agree |
| Commodities | Q3 FY 2025 | 39.917879 | 39.917879 | 3.6e-16 | agree |
| Commodities | Q4 FY 2025 | 39.462309 | 39.462309 | 1.8e-16 | agree |
| Commodities | Q1 FY 2026 | 46.521134 | 46.521134 | 3.1e-16 | agree |
| Commodities | Q2 FY 2026 | 50.517904 | 50.517904 | 1.4e-16 | agree |
| Commodities | Q3 FY 2026 | 84.228522 | 84.228522 | 1.7e-16 | agree |
| Commodities | Q4 FY 2026 | 90.109043 | 90.109043 | 4.7e-16 | agree |
| Commodities | Q1 FY 2027 | 54.718367 | 54.718367 | 5.2e-16 | agree |
| Commodities | Q2 FY 2027 | 57.968626 | 57.968626 | 4.9e-16 | agree |

## Parity estimate of Q2 FY27 vs the reported quarter (spec table m-a; Methodology section 5)

| Quantity | Mine | Claim | Verdict |
|---|---:|---|---|
| F&O gross Q2 FY27 model (Rs Cr) | 179.13 | 179.13 | agree |
| F&O gross model vs reported (%) | -4.95426 | -4.95 | agree |
| Cash gross Q2 FY27 model (Rs Cr) | 200.16 | 200.16 | agree |
| Cash gross model vs reported (%) | -15.8264 | -15.83 | agree |
| Commodities gross Q2 FY27 model (Rs Cr) | 86.4739 | 86.47 | agree |
| Commodities gross model vs reported (%) | 49.1736 | 49.17 | agree |
| MTF closing book Q2 FY27 model (Rs Cr) | 8729.33 | 8,729 | agree |
| MTF book model vs reported (%) | -9.06951 | -9.1 | agree |

## Pins moved by m-a, tested through the daily rows

| Pin | Test | Result |
|---|---|---|
| fo_zero_quarters = none | Q1, Q2 FY25 F&O rows: 125, of which non-zero numeric 124, error 1 (31 May 2024 text key) | agree |
| fo_zero_quarters (parity) = Q1, Q2 FY25 | parity: 124 numeric rows, all zero: True | agree |
| cash_table_first_quarter = Q1 FY 2025 | first cash row after m-a 2024-04-01, before 2024-10-01; rows 509 -> 634 | agree |
| fo_last_actual_quarter = Q2 FY 2027 | Q2 FY27 daily gross sums to the reported 188.4675 (mine 188.4675) | agree |
| cash_last_actual_quarter = Q2 FY 2027 | Q2 FY27 daily gross sums to the reported 237.7937 (mine 237.7937) | agree |
| comm_last_actual_quarter = Q2 FY 2027 | Q2 FY27 daily gross sums to the reported 57.9686 (mine 57.9686) | agree |
| mtf_last_actual_quarter = Q2 FY 2027 | Q2 FY27 MTF share 0.063520 = 9600 / 30 Sep industry book 151133.98 | agree |
| cash take rate Q1 FY27 own (J52 = J51 dropped) | J(Q1 FY27) = 0.064265 = 228.30/3552.47, not J(Q4 FY26) = 0.063252 | agree |
| Q3 FY27 keeps the workbook rules (cash #N/A, commodities #N/A / blank, F&O carried) | cash Q3 rows 13 all error: True; commodity rows 7 error (to 2026-10-12), none after; F&O rate Q3 = Q2: True | agree |

## Notes

- Method. The parity state is rebuilt first from raw inputs (workbook NSE index-option + BSE contract series, NSE + BSE turnover, MCX contracts, the industry daily MTF book, the typed seed facts and assumptions) with the formulas of Methodology sections 3, 4 and 8b. It reproduces the four daily columns of `snapshot/mosl_fixtures_2026-10-23.json` (F&O 757 rows, cash 509, commodities 653, MTF 495) to 6e-16 relative and the 156 value cells of the Summary fixtures (all panels, FY / quarter / month / week / weekday) to 5e-16. m-a is then applied as the bridge and spec describe: every reported quarter Q1 FY25 - Q2 FY27 calibrates from the reviewed data-book facts, converted Rs Mn to Rs Cr (/10) and net / gross = net brokerage / gross brokerage of the same quarter.
- Formulas used. F&O: AF = share x (S/1e7) x rate, rate = gross / (share x sum S/1e7) (Rs per contract), AG = net/gross x AF, ADR = mean(AG)/10. Cash: AA = share x K / H x J / D, H = share x mean K / ADTO, J = gross / ADTO, D = rows in the quarter, AB = net/gross x AA. Commodities: L = MCX Mn contracts x share x take, take = gross x 10 / (share x contracts), O = net/gross x L, ADR = mean(O)/10. MTF: X = (book / industry close of the quarter) x daily industry book x NII / 247.
- F&O 31 May 2024: the workbook key cell is text, so that row is an error and is left out of the Q1 FY25 key sum; the Q1 FY25 rate 0.7498 (bridge) only reproduces with that exclusion. m-b then adds the day (0.7382).
- "73 inputs already equal" is reproduced with an equality tolerance of 1e-6 relative: the reviewed facts print shares to 9 digits where the workbook seed has 16, so exact equality would give 55 / 55 instead of 73 / 37. At any tolerance between 1e-8 and 1e-6 the changed set is exactly the 37 listed rows.
- Daily rows changed. For F&O the bridge counts every row whose float differs; mine counts rows whose relative difference exceeds 1e-9. Counts agree for all four segments in this bridge.
- Week / weekday rows printed "Monday | vs 10" repeat the Monday value in the bridge (the workbook column is a comparison; the bridge prints the level); I compare them with the level.

## Could not be verified from the stated inputs

- Nothing in this bridge was left unverified.
