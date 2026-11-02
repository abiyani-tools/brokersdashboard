# Bridge — MOSL switch (m-c)

No silent zeros: missing, non-ok and zero key days and error rows are excluded, not averaged as 0.

Before: switches ab · after: abc · series read to 2026-10-21

Consolidated ADR, Rs crore per trading day (net brokerage + MTF NII):

| Period | Before | After | Δ % |
|---|---:|---:|---:|
| FY 2027 | 6.083537 | 8.650276 | +42.1916% |
| Q2 FY 2027 | 8.967060 | 8.967060 | +0.0000% |
| Q1 FY 2027 | 8.197926 | 8.197926 | +0.0000% |
| FY 2027 October | 2.332592 | 2.332592 | +0.0000% |
| FY 2026 | 7.642700 | 7.642700 | +0.0000% |

F&O: 124 day(s) have no row after m-c (error rows the workbook shows as #N/A / #VALUE! or blank, or a missing / non-ok / zero key): 2023-09-29 .. 2024-03-28

Cash: 13 day(s) have no row after m-c (error rows the workbook shows as #N/A / #VALUE! or blank, or a missing / non-ok / zero key): 2026-10-01 .. 2026-10-21

Commodities: 7 day(s) have no row after m-c (error rows the workbook shows as #N/A / #VALUE! or blank, or a missing / non-ok / zero key): 2026-10-01 .. 2026-10-12

Before m-c an FY / quarter / month statistic that contained one error day was the workbook's IFERROR 0 (Methodology issue 1). After it the error days are left out and the average runs over the days that have a value; a period with no value at all is flagged insufficient in the live rows. The ADR tables below are the unguarded statistics (a segment with no value in a month adds 0 to the sum, as FY 2027 October does for cash and commodities until m-e); the live rows flag such a period as insufficient instead.

Periods flagged insufficient in the live rows after this switch: 28.

- Consolidated FY 2025: insufficient data: MTF FY 2025: MTF series starts 2024-10-01, after FY 2025 began
- Consolidated Q1 FY 2025: insufficient data: MTF Q1 FY 2025: MTF series starts 2024-10-01, after Q1 FY 2025 began
- Consolidated Q2 FY 2025: insufficient data: MTF Q2 FY 2025: MTF series starts 2024-10-01, after Q2 FY 2025 began
- Consolidated Q3 FY 2027: insufficient data: Cash Q3 FY 2027: no trading days
- Consolidated FY 2025 April: insufficient data: MTF FY 2025 April: MTF series starts 2024-10-01, after FY 2025 April began
- Consolidated FY 2025 May: insufficient data: MTF FY 2025 May: MTF series starts 2024-10-01, after FY 2025 May began
- Consolidated FY 2025 June: insufficient data: MTF FY 2025 June: MTF series starts 2024-10-01, after FY 2025 June began
- Consolidated FY 2025 July: insufficient data: MTF FY 2025 July: MTF series starts 2024-10-01, after FY 2025 July began

ADR, Rs crore per trading day (net brokerage + MTF NII):

| Period | Panel | Before | After | Δ | Δ % |
|---|---|---:|---:|---:|---:|
| FY 2027 | Consolidated | 6.083537 | 8.650276 | +2.566739 | +42.1916% |
| FY 2027 | Broking | 1.871544 | 4.438283 | +2.566739 | +137.1455% |
| FY 2027 | MTF | 4.211993 | 4.211993 | +0.000000 | +0.0000% |
| FY 2027 | F&O | 1.871544 | 1.871544 | +0.000000 | +0.0000% |
| FY 2027 | Cash | 0.000000 | 2.045402 | +2.045402 |  |
| FY 2027 | Commodities | 0.000000 | 0.521337 | +0.521337 |  |
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

Parameters that moved:

| Segment | Quantity | Quarter | Before | After | Δ % |
|---|---|---|---:|---:|---:|
| Cash | model gross brokerage Rs Cr | Q3 FY 2027 | 221.24 | — |  |
| Cash | model net brokerage Rs Cr | Q3 FY 2027 | 0.0000 | — |  |

Daily revenue rows that changed:

| Segment | Days before | Days after | Changed | First | Last | Ratio min | Ratio max | Added | Dropped |
|---|---:|---:|---:|---|---|---:|---:|---:|---:|
| F&O | 758 | 634 | 0 |  |  |  |  | 0 | 124 |
| Cash | 634 | 621 | 0 |  |  |  |  | 0 | 13 |
| Commodities | 653 | 646 | 0 |  |  |  |  | 0 | 7 |
| MTF | 495 | 495 | 0 |  |  |  |  | 0 | 0 |
