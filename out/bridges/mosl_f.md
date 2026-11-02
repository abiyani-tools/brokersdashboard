# Bridge — MOSL switch (m-f)

MTF yield: typed NII yields kept, the last carried as a labelled assumption (MOSL publishes no MTF yield).

Before: switches abcde · after: abcdef · series read to 2026-10-21

Consolidated ADR, Rs crore per trading day (net brokerage + MTF NII):

| Period | Before | After | Δ % |
|---|---:|---:|---:|
| FY 2027 | 8.718295 | 8.718295 | +0.0000% |
| Q2 FY 2027 | 8.967060 | 8.967060 | +0.0000% |
| Q1 FY 2027 | 8.197926 | 8.197926 | +0.0000% |
| FY 2027 October | 9.876513 | 9.876513 | +0.0000% |
| FY 2026 | 7.662290 | 7.662290 | +0.0000% |

The MTF NII yield is the workbook's typed value for each quarter Q1 FY25 - Q1 FY27 (kept; [SOURCE NEEDED: MOSL does not publish an MTF yield]). Quarters after the last typed one carry it from the assumption row `mtf_nii_yield_carry` (12.94%, the workbook's F14). The numbers do not move because the carried value equals the workbook's own carry; what changes is that the yield is now a labelled assumption row in sb_assumptions, which the run refuses without. The day basis (247) is unchanged.

Periods flagged insufficient in the live rows after this switch: 18 (before: 18).

- Consolidated FY 2025: insufficient data: MTF FY 2025: MTF series starts 2024-10-01, after FY 2025 began
- Consolidated Q1 FY 2025: insufficient data: MTF Q1 FY 2025: MTF series starts 2024-10-01, after Q1 FY 2025 began
- Consolidated Q2 FY 2025: insufficient data: MTF Q2 FY 2025: MTF series starts 2024-10-01, after Q2 FY 2025 began
- Consolidated FY 2025 April: insufficient data: MTF FY 2025 April: MTF series starts 2024-10-01, after FY 2025 April began
- Consolidated FY 2025 May: insufficient data: MTF FY 2025 May: MTF series starts 2024-10-01, after FY 2025 May began
- Consolidated FY 2025 June: insufficient data: MTF FY 2025 June: MTF series starts 2024-10-01, after FY 2025 June began
- Consolidated FY 2025 July: insufficient data: MTF FY 2025 July: MTF series starts 2024-10-01, after FY 2025 July began
- Consolidated FY 2025 August: insufficient data: MTF FY 2025 August: MTF series starts 2024-10-01, after FY 2025 August began

ADR, Rs crore per trading day (net brokerage + MTF NII):

| Period | Panel | Before | After | Δ | Δ % |
|---|---|---:|---:|---:|---:|
| FY 2027 | Consolidated | 8.718295 | 8.718295 | +0.000000 | +0.0000% |
| FY 2027 | Broking | 4.440500 | 4.440500 | +0.000000 | +0.0000% |
| FY 2027 | MTF | 4.277794 | 4.277794 | +0.000000 | +0.0000% |
| FY 2027 | F&O | 1.871544 | 1.871544 | +0.000000 | +0.0000% |
| FY 2027 | Cash | 2.035185 | 2.035185 | +0.000000 | +0.0000% |
| FY 2027 | Commodities | 0.533771 | 0.533771 | +0.000000 | +0.0000% |
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
| FY 2027 October | Consolidated | 9.876513 | 9.876513 | +0.000000 | +0.0000% |
| FY 2027 October | Broking | 4.918772 | 4.918772 | +0.000000 | +0.0000% |
| FY 2027 October | MTF | 4.957741 | 4.957741 | +0.000000 | +0.0000% |
| FY 2027 October | F&O | 2.332592 | 2.332592 | +0.000000 | +0.0000% |
| FY 2027 October | Cash | 1.936953 | 1.936953 | +0.000000 | +0.0000% |
| FY 2027 October | Commodities | 0.649226 | 0.649226 | +0.000000 | +0.0000% |
| FY 2026 | Consolidated | 7.662290 | 7.662290 | +0.000000 | +0.0000% |
| FY 2026 | Broking | 4.348883 | 4.348883 | +0.000000 | +0.0000% |
| FY 2026 | MTF | 3.313407 | 3.313407 | +0.000000 | +0.0000% |
| FY 2026 | F&O | 1.857828 | 1.857828 | +0.000000 | +0.0000% |
| FY 2026 | Cash | 1.888062 | 1.888062 | +0.000000 | +0.0000% |
| FY 2026 | Commodities | 0.602993 | 0.602993 | +0.000000 | +0.0000% |

Daily revenue rows that changed:

| Segment | Days before | Days after | Changed | First | Last | Ratio min | Ratio max | Added | Dropped |
|---|---:|---:|---:|---|---|---:|---:|---:|---:|
| F&O | 634 | 634 | 0 |  |  |  |  | 0 | 0 |
| Cash | 634 | 634 | 0 |  |  |  |  | 0 | 0 |
| Commodities | 660 | 660 | 0 |  |  |  |  | 0 | 0 |
| MTF | 507 | 507 | 0 |  |  |  |  | 0 | 0 |
