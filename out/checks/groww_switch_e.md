# Groww switch g-e: independent recompute

Script: `out/checks/groww_switch_e_check.py` (stdlib json/math/csv). Inputs: db snapshot, Groww fixtures/snapshot, reviewed facts, Angel calibration read from `parity_expected`. No engine code read.

**Result: 39/39 items agree** (35 to 1e-6 relative; 4 agree only to the bridge print precision).

| Item kind | Checked | Agree | Agree at 1e-6 |
|---|---:|---:|---:|
| ADR | 30 | 30 | 30 |
| param | 5 | 5 | 1 |
| daily | 4 | 4 | 4 |

## ADR, Rs crore per trading day (consolidated and panels)

| Period | Panel | My before | Bridge before | My after | Bridge after | Max rel diff | Verdict |
|---|---|---:|---:|---:|---:|---:|---|
| FY 2027 | Consolidated | 20.143031 | 20.143031 | 19.985235 | 19.985235 | 2.1e-08 | agree |
| FY 2027 | Broking | 17.814122 | 17.814122 | 17.728318 | 17.728318 | 2.4e-08 | agree |
| FY 2027 | MTF | 2.328909 | 2.328909 | 2.256917 | 2.256917 | 2.1e-07 | agree |
| FY 2027 | F&O | 12.255779 | 12.255779 | 12.187676 | 12.187676 | 1.7e-08 | agree |
| FY 2027 | Cash | 4.185758 | 4.185758 | 4.176738 | 4.176738 | 1.1e-07 | agree |
| FY 2027 | Commodities | 1.372585 | 1.372585 | 1.363903 | 1.363903 | 2.2e-07 | agree |
| Q2 FY 2027 | Consolidated | 18.671320 | 18.671320 | 18.589965 | 18.589965 | 2.6e-08 | agree |
| Q2 FY 2027 | Broking | 16.188957 | 16.188957 | 16.188957 | 16.188957 | 1.8e-08 | agree |
| Q2 FY 2027 | MTF | 2.482364 | 2.482364 | 2.401008 | 2.401008 | 9.6e-08 | agree |
| Q2 FY 2027 | F&O | 10.617876 | 10.617876 | 10.617876 | 10.617876 | 2.9e-08 | agree |
| Q2 FY 2027 | Cash | 4.123907 | 4.123907 | 4.123907 | 4.123907 | 1.9e-08 | agree |
| Q2 FY 2027 | Commodities | 1.447174 | 1.447174 | 1.447174 | 1.447174 | 4.2e-08 | agree |
| FY 2027 October | Consolidated | 24.588926 | 24.588926 | 23.305704 | 23.305704 | 1.3e-08 | agree |
| FY 2027 October | Broking | 21.691252 | 21.691252 | 20.783268 | 20.783268 | 6.7e-09 | agree |
| FY 2027 October | MTF | 2.897674 | 2.897674 | 2.522436 | 2.522436 | 1.2e-07 | agree |
| FY 2027 October | F&O | 15.181758 | 15.181758 | 14.458817 | 14.458817 | 5.4e-09 | agree |
| FY 2027 October | Cash | 4.634212 | 4.634212 | 4.538468 | 4.538468 | 8.1e-08 | agree |
| FY 2027 October | Commodities | 1.875282 | 1.875282 | 1.785983 | 1.785983 | 2.3e-07 | agree |
| FY 2026 | Consolidated | 15.989974 | 15.989974 | 15.989974 | 15.989974 | 2.1e-08 | agree |
| FY 2026 | Broking | 14.982565 | 14.982565 | 14.982565 | 14.982565 | 3.0e-08 | agree |
| FY 2026 | MTF | 1.007408 | 1.007408 | 1.007408 | 1.007408 | 2.1e-07 | agree |
| FY 2026 | F&O | 10.772896 | 10.772896 | 10.772896 | 10.772896 | 1.0e-09 | agree |
| FY 2026 | Cash | 3.325009 | 3.325009 | 3.325009 | 3.325009 | 1.4e-07 | agree |
| FY 2026 | Commodities | 0.884661 | 0.884661 | 0.884661 | 0.884661 | 1.1e-07 | agree |
| FY 2026 October | Consolidated | 16.522023 | 16.522023 | 16.522023 | 16.522023 | 2.2e-08 | agree |
| FY 2026 October | Broking | 15.434134 | 15.434134 | 15.434134 | 15.434134 | 1.7e-08 | agree |
| FY 2026 October | MTF | 1.087888 | 1.087888 | 1.087888 | 1.087888 | 3.5e-07 | agree |
| FY 2026 October | F&O | 11.350532 | 11.350532 | 11.350532 | 11.350532 | 2.5e-09 | agree |
| FY 2026 October | Cash | 3.402207 | 3.402207 | 3.402207 | 3.402207 | 1.4e-07 | agree |
| FY 2026 October | Commodities | 0.681395 | 0.681395 | 0.681395 | 0.681395 | 2.5e-07 | agree |

## Parameters that moved

| Segment | Quantity | Quarter | My before | Bridge before | My after | Bridge after | My d% | Bridge d% | Verdict |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| Cash | take rate Rs/order | Q3 FY 2027 | 20.3031 | 20.3031 | 19.8836 | 19.8836 | -2.06603 | -2.066% | agree |
| Commodities | share of Angel market orders | Q3 FY 2027 | 0.444172 | 0.4442 | 0.423021 | 0.4230 | -4.7619 | -4.762% | agree |
| F&O | share (ADTO, legacy basis) | Q3 FY 2027 | 0.231 | 0.2310 | 0.22 | 0.2200 | -4.7619 | -4.762% | agree |
| MTF | share of industry book | Q2 FY 2027 | 0.0288 | 0.0288 | 0.0278561 | 0.0279 | -3.27734 | -3.277% | agree |
| MTF | share of industry book | Q3 FY 2027 | 0.032 | 0.0320 | 0.0278561 | 0.0279 | -12.9496 | -12.950% | agree |

## Inputs replaced (reviewed facts)

| Input | Period | My workbook | Bridge workbook | My live | Bridge live | Fact ids ok | Vintage ok | Verdict |
|---|---|---:|---:|---:|---:|---|---|---|

## Daily revenue rows that changed

| Segment | Days | Changed (mine / bridge) | First | Last | Ratio min (mine / bridge) | Ratio max (mine / bridge) | Verdict |
|---|---:|---|---|---|---|---|---|
| F&O | 573 | 13 / 13 | 2026-10-01 | 2026-10-21 | 0.952380952 / 0.952380952 | 0.952380952 / 0.952380952 | agree |
| Cash | 573 | 13 / 13 | 2026-10-01 | 2026-10-21 | 0.979339713 / 0.979339713 | 0.979339713 / 0.979339713 | agree |
| Commodities | 272 | 14 / 14 | 2026-10-01 | 2026-10-21 | 0.952380952 / 0.952380952 | 0.952380952 / 0.952380952 | agree |
| MTF | 507 | 77 / 77 | 2026-07-01 | 2026-10-19 | 0.870503921 / 0.870503921 | 0.967226578 / 0.967226578 | agree |

## Notes

Estimate rule recomputed: for Q3 FY27 (no disclosure) F&O share, F&O take rate, cash share, cash take rate, commodity share and commodity take rate all carry the Q2 FY27 actual (no 1.05 growth, no trailing mean). MTF share for Q2/Q3 FY27 carries the Q1 FY27 actual share (0.027856) until g-f supplies Q2 FY27 revenue; the typed 0.0288/0.032/0.036 are dropped.
Spec vs switch: as the spec says. The spec's 'overrides go in sb_assumptions with a note' cannot be recomputed from the bridge (no override is exercised).
The carried parameters still sit on Angel's estimated contracts-per-order for Oct 2026 (carried May value 14.35172 for F&O, 13.0244 for commodities); that is outside this switch.
