# Bridge — MOSL switch (m-b)

Keys on the right dates: lake NSE + BSE cash turnover (and the F&O key) on their own dates.

Before: switches a · after: ab · series read to 2026-10-21

Consolidated ADR, Rs crore per trading day (net brokerage + MTF NII):

| Period | Before | After | Δ % |
|---|---:|---:|---:|
| FY 2027 | 6.083537 | 6.083537 | +0.0000% |
| Q2 FY 2027 | 8.967060 | 8.967060 | +0.0000% |
| Q1 FY 2027 | 8.197926 | 8.197926 | +0.0000% |
| FY 2027 October | 2.332592 | 2.332592 | +0.0000% |
| FY 2026 | 7.642700 | 7.642700 | +0.0000% |

Cash key: the lake's `nse_cash/turnover_cr` + `bse_cash/turnover_cr` on their own dates (ExchangesDash, snapshot/mosl_lake_2026-11-02.json) instead of the workbook's columns, which sit two rows off from 9 Jun 2025 (Methodology issue 5). The F&O key is read from the lake too (`nse_fo/io_contracts` + `bse_fo/contracts`): it equals the workbook's on all 756 common days, differs only on 31 May 2024 (the workbook has a text cell, the lake a number), and the lake adds the 2023-09-29 row. No premium ADTO is read (it cancels).

ADR, Rs crore per trading day (net brokerage + MTF NII):

| Period | Panel | Before | After | Δ | Δ % |
|---|---|---:|---:|---:|---:|
| FY 2027 | Consolidated | 6.083537 | 6.083537 | +0.000000 | +0.0000% |
| FY 2027 | Broking | 1.871544 | 1.871544 | +0.000000 | +0.0000% |
| FY 2027 | MTF | 4.211993 | 4.211993 | +0.000000 | +0.0000% |
| FY 2027 | F&O | 1.871544 | 1.871544 | +0.000000 | +0.0000% |
| FY 2027 | Cash | 0.000000 | 0.000000 | +0.000000 |  |
| FY 2027 | Commodities | 0.000000 | 0.000000 | +0.000000 |  |
| Q2 FY 2027 | Consolidated | 8.967060 | 8.967060 | +0.000000 | +0.0000% |
| Q2 FY 2027 | Broking | 4.247980 | 4.247980 | +0.000000 | +0.0000% |
| Q2 FY 2027 | MTF | 4.719079 | 4.719079 | +0.000000 | +0.0000% |
| Q2 FY 2027 | F&O | 1.694618 | 1.694618 | +0.000000 | +0.0000% |
| Q2 FY 2027 | Cash | 2.031303 | 2.031303 | +0.000000 | +0.0000% |
| Q2 FY 2027 | Commodities | 0.522060 | 0.522060 | +0.000000 | +0.0000% |
| Q1 FY 2027 | Consolidated | 8.197926 | 8.197926 | +0.000000 | +0.0000% |
| Q1 FY 2027 | Broking | 4.544588 | 4.544588 | +0.000000 | +0.0000% |
| Q1 FY 2027 | MTF | 3.653339 | 3.653339 | +0.000000 | +0.0000% |
| Q1 FY 2027 | F&O | 1.963321 | 1.963321 | +0.000000 | +0.0000% |
| Q1 FY 2027 | Cash | 2.060675 | 2.060675 | +0.000000 | +0.0000% |
| Q1 FY 2027 | Commodities | 0.520592 | 0.520592 | +0.000000 | +0.0000% |
| FY 2027 October | Consolidated | 2.332592 | 2.332592 | +0.000000 | +0.0000% |
| FY 2027 October | Broking | 2.332592 | 2.332592 | +0.000000 | +0.0000% |
| FY 2027 October | MTF | 0.000000 | 0.000000 | +0.000000 |  |
| FY 2027 October | F&O | 2.332592 | 2.332592 | +0.000000 | +0.0000% |
| FY 2027 October | Cash | 0.000000 | 0.000000 | +0.000000 |  |
| FY 2027 October | Commodities | 0.000000 | 0.000000 | +0.000000 |  |
| FY 2026 | Consolidated | 7.642700 | 7.642700 | +0.000000 | +0.0000% |
| FY 2026 | Broking | 4.329293 | 4.329293 | +0.000000 | +0.0000% |
| FY 2026 | MTF | 3.313407 | 3.313407 | +0.000000 | +0.0000% |
| FY 2026 | F&O | 1.849289 | 1.849289 | +0.000000 | +0.0000% |
| FY 2026 | Cash | 1.880952 | 1.880952 | +0.000000 | +0.0000% |
| FY 2026 | Commodities | 0.599053 | 0.599053 | +0.000000 | +0.0000% |
| FY 2027 September | Consolidated | 9.230728 | 9.237757 | +0.007029 | +0.0761% |
| FY 2027 September | Broking | 4.290353 | 4.297382 | +0.007029 | +0.1638% |
| FY 2027 September | MTF | 4.940375 | 4.940375 | +0.000000 | +0.0000% |
| FY 2027 September | F&O | 1.704934 | 1.704934 | +0.000000 | +0.0000% |
| FY 2027 September | Cash | 1.977761 | 1.984791 | +0.007029 | +0.3554% |
| FY 2027 September | Commodities | 0.607658 | 0.607658 | +0.000000 | +0.0000% |
| FY 2027 August | Consolidated | 8.695724 | 8.729330 | +0.033606 | +0.3865% |
| FY 2027 August | Broking | 3.983725 | 4.017331 | +0.033606 | +0.8436% |
| FY 2027 August | MTF | 4.711999 | 4.711999 | +0.000000 | +0.0000% |
| FY 2027 August | F&O | 1.456093 | 1.456093 | +0.000000 | +0.0000% |
| FY 2027 August | Cash | 2.019779 | 2.053385 | +0.033606 | +1.6639% |
| FY 2027 August | Commodities | 0.507852 | 0.507852 | +0.000000 | +0.0000% |
| FY 2026 September | Consolidated | 7.806113 | 7.843211 | +0.037098 | +0.4752% |
| FY 2026 September | Broking | 4.072312 | 4.109410 | +0.037098 | +0.9110% |
| FY 2026 September | MTF | 3.733801 | 3.733801 | +0.000000 | +0.0000% |
| FY 2026 September | F&O | 1.852181 | 1.852181 | +0.000000 | +0.0000% |
| FY 2026 September | Cash | 1.699012 | 1.736110 | +0.037098 | +2.1835% |
| FY 2026 September | Commodities | 0.521119 | 0.521119 | +0.000000 | +0.0000% |

Parameters that moved:

| Segment | Quantity | Quarter | Before | After | Δ % |
|---|---|---|---:|---:|---:|
| Cash | 'delivery ratio' H | Q1 FY 2026 | 2.5730 | 2.5759 | +0.111% |
| Cash | 'delivery ratio' H | Q2 FY 2026 | 2.6548 | 2.6448 | -0.378% |
| Cash | 'delivery ratio' H | Q3 FY 2026 | 2.6610 | 2.6644 | +0.131% |
| Cash | 'delivery ratio' H | Q4 FY 2026 | 2.8959 | 2.9222 | +0.907% |
| Cash | 'delivery ratio' H | Q1 FY 2027 | 2.7783 | 2.7840 | +0.205% |
| Cash | 'delivery ratio' H | Q2 FY 2027 | 2.7618 | 2.7503 | -0.415% |
| Cash | 'delivery ratio' H | Q3 FY 2027 | 2.8120 | 2.8188 | +0.243% |
| Cash | model gross brokerage Rs Cr | Q3 FY 2027 | 233.81 | 221.24 | -5.377% |
| F&O | gross Rs per contract | Q1 FY 2025 | 0.7498 | 0.7382 | -1.544% |

Week / weekday tables (as of the last date) that changed: 75 rows over all panels; the Consolidated panel:

| Panel | Table | Row | Before | After |
|---|---|---|---:|---:|
| Consolidated | Week | Last 5 trading days | 9.774980 | 10.021311 |
| Consolidated | Week | Last 5 trading days | vs 45D | 9.774980 | 10.021311 |
| Consolidated | Week | Previous 5 trading days | 9.998240 | 9.977988 |
| Consolidated | Week | Last 45 trading days | 9.189508 | 9.219741 |
| Consolidated | Week | Last 20 trading days | 9.699266 | 9.696069 |
| Consolidated | Weekday | Monday | 10.577803 | 10.175587 |
| Consolidated | Weekday | Monday | vs 10 | 10.577803 | 10.175587 |
| Consolidated | Weekday | Average of last 3 Mondays | 9.257750 | 9.094611 |
| Consolidated | Weekday | Average of last 10 Mondays | 8.641918 | 8.622832 |
| Consolidated | Weekday | Tuesday | 10.274615 | 11.169574 |
| Consolidated | Weekday | Tuesday | vs 10 | 10.274615 | 11.169574 |
| Consolidated | Weekday | Average of last 3 Tuesdays | 10.293089 | 10.434849 |
| Consolidated | Weekday | Average of last 10 Tuesdays | 9.605023 | 9.666502 |
| Consolidated | Weekday | Wednesday | 8.856868 | 9.304549 |
| Consolidated | Weekday | Wednesday | vs 10 | 8.856868 | 9.304549 |
| Consolidated | Weekday | Average of last 3 Wednesdays | 9.281215 | 9.455375 |
| Consolidated | Weekday | Average of last 10 Wednesdays | 8.649845 | 8.739168 |
| Consolidated | Weekday | Thursday | 11.580231 | 11.927126 |
| Consolidated | Weekday | Thursday | vs 10 | 11.580231 | 11.927126 |
| Consolidated | Weekday | Average of last 3 Thursdays | 12.007931 | 12.012284 |
| Consolidated | Weekday | Average of last 10 Thursdays | 10.476552 | 10.502288 |
| Consolidated | Weekday | Friday | 9.058258 | 9.002591 |
| Consolidated | Weekday | Friday | vs 10 | 9.058258 | 9.002591 |
| Consolidated | Weekday | Average of last 3 Fridays | 8.495864 | 8.630176 |
| Consolidated | Weekday | Average of last 10 Fridays | 8.120077 | 8.083274 |

Daily revenue rows that changed:

| Segment | Days before | Days after | Changed | First | Last | Ratio min | Ratio max | Added | Dropped |
|---|---:|---:|---:|---|---|---:|---:|---:|---:|
| F&O | 757 | 758 | 385 | 2024-04-01 | 2026-10-21 | 0.984555296 | 1.000000000 | 1 | 0 |
| Cash | 634 | 634 | 372 | 2025-04-01 | 2026-09-30 | 0.186454599 | 4.306998593 | 0 | 0 |
| Commodities | 653 | 653 | 0 |  |  |  |  | 0 | 0 |
| MTF | 495 | 495 | 0 |  |  |  |  | 0 | 0 |
