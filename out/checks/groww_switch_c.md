# Groww switch g-c: independent recompute

Script: `out/checks/groww_switch_c_check.py` (stdlib json/math/csv). Inputs: db snapshot, Groww fixtures/snapshot, reviewed facts, Angel calibration read from `parity_expected`. No engine code read.

**Result: 50/50 items agree** (50 to 1e-6 relative; 0 agree only to the bridge print precision).

| Item kind | Checked | Agree | Agree at 1e-6 |
|---|---:|---:|---:|
| ADR | 30 | 30 | 30 |
| daily | 4 | 4 | 4 |
| lake | 16 | 16 | 16 |

## ADR, Rs crore per trading day (consolidated and panels)

| Period | Panel | My before | Bridge before | My after | Bridge after | Max rel diff | Verdict |
|---|---|---:|---:|---:|---:|---:|---|
| FY 2027 | Consolidated | 19.468553 | 19.468553 | 20.112171 | 20.112171 | 1.8e-08 | agree |
| FY 2027 | Broking | 17.139643 | 17.139643 | 17.783261 | 17.783261 | 1.1e-08 | agree |
| FY 2027 | MTF | 2.328909 | 2.328909 | 2.328909 | 2.328909 | 2.1e-07 | agree |
| FY 2027 | F&O | 11.955493 | 11.955493 | 12.599111 | 12.599111 | 4.8e-09 | agree |
| FY 2027 | Cash | 4.162446 | 4.162446 | 4.162446 | 4.162446 | 4.2e-08 | agree |
| FY 2027 | Commodities | 1.021704 | 1.021704 | 1.021704 | 1.021704 | 3.0e-07 | agree |
| Q2 FY 2027 | Consolidated | 18.682593 | 18.682593 | 18.775865 | 18.775865 | 2.6e-08 | agree |
| Q2 FY 2027 | Broking | 16.200229 | 16.200229 | 16.293502 | 16.293502 | 1.9e-08 | agree |
| Q2 FY 2027 | MTF | 2.482364 | 2.482364 | 2.482364 | 2.482364 | 8.6e-08 | agree |
| Q2 FY 2027 | F&O | 10.981340 | 10.981340 | 11.074613 | 11.074613 | 1.5e-08 | agree |
| Q2 FY 2027 | Cash | 4.099037 | 4.099037 | 4.099037 | 4.099037 | 5.5e-08 | agree |
| Q2 FY 2027 | Commodities | 1.119852 | 1.119852 | 1.119852 | 1.119852 | 7.8e-08 | agree |
| FY 2027 October | Consolidated | 17.505687 | 17.505687 | 23.871576 | 23.871576 | 2.8e-08 | agree |
| FY 2027 October | Broking | 14.608014 | 14.608014 | 20.973902 | 20.973902 | 1.8e-08 | agree |
| FY 2027 October | MTF | 2.897674 | 2.897674 | 2.897674 | 2.897674 | 1.1e-07 | agree |
| FY 2027 October | F&O | 8.714887 | 8.714887 | 15.080776 | 15.080776 | 2.3e-08 | agree |
| FY 2027 October | Cash | 4.511097 | 4.511097 | 4.511097 | 4.511097 | 4.7e-08 | agree |
| FY 2027 October | Commodities | 1.382030 | 1.382030 | 1.382030 | 1.382030 | 3.5e-07 | agree |
| FY 2026 | Consolidated | 15.906563 | 15.906563 | 15.906563 | 15.906563 | 5.4e-10 | agree |
| FY 2026 | Broking | 14.899155 | 14.899155 | 14.899155 | 14.899155 | 1.4e-08 | agree |
| FY 2026 | MTF | 1.007408 | 1.007408 | 1.007408 | 1.007408 | 2.1e-07 | agree |
| FY 2026 | F&O | 10.772896 | 10.772896 | 10.772896 | 10.772896 | 1.0e-09 | agree |
| FY 2026 | Cash | 3.325009 | 3.325009 | 3.325009 | 3.325009 | 1.4e-07 | agree |
| FY 2026 | Commodities | 0.801250 | 0.801250 | 0.801250 | 0.801250 | 3.1e-07 | agree |
| FY 2026 October | Consolidated | 16.556092 | 16.556092 | 16.556092 | 16.556092 | 2.3e-08 | agree |
| FY 2026 October | Broking | 15.468204 | 15.468204 | 15.468204 | 15.468204 | 1.9e-10 | agree |
| FY 2026 October | MTF | 1.087888 | 1.087888 | 1.087888 | 1.087888 | 3.5e-07 | agree |
| FY 2026 October | F&O | 11.350532 | 11.350532 | 11.350532 | 11.350532 | 2.5e-09 | agree |
| FY 2026 October | Cash | 3.402207 | 3.402207 | 3.402207 | 3.402207 | 1.4e-07 | agree |
| FY 2026 October | Commodities | 0.715465 | 0.715465 | 0.715465 | 0.715465 | 6.0e-07 | agree |

## Parameters that moved

| Segment | Quantity | Quarter | My before | Bridge before | My after | Bridge after | My d% | Bridge d% | Verdict |
|---|---|---|---:|---:|---:|---:|---:|---:|---|

## Inputs replaced (reviewed facts)

| Input | Period | My workbook | Bridge workbook | My live | Bridge live | Fact ids ok | Vintage ok | Verdict |
|---|---|---:|---:|---:|---:|---|---|---|

## Daily revenue rows that changed

| Segment | Days | Changed (mine / bridge) | First | Last | Ratio min (mine / bridge) | Ratio max (mine / bridge) | Verdict |
|---|---:|---|---|---|---|---|---|
| F&O | 573 | 15 / 15 | 2026-09-29 | 2026-10-21 | 0.998659758 / 0.998659758 | 5.390308547 / 5.390308547 | agree |
| Cash | 573 | 0 / 0 |  |  |  /  |  /  | agree |
| Commodities | 272 | 0 / 0 |  |  |  /  |  /  | agree |
| MTF | 507 | 0 / 0 |  |  |  /  |  /  | agree |

## BSE F&O contracts replaced on imputed days

| Date | Imputed (mine / bridge) | Lake (mine / bridge) | Verdict |
|---|---|---|---|
| 2026-09-29 | 18962859 / 18962859 | 27311202 / 27311202 | agree |
| 2026-09-30 | 18962859 / 18962859 | 152837325 / 152837325 | agree |
| 2026-10-01 | 18962859 / 18962859 | 512976127 / 512976127 | agree |
| 2026-10-05 | 18962859 / 18962859 | 26843978 / 26843978 | agree |
| 2026-10-06 | 18962859 / 18962859 | 27015960 / 27015960 | agree |
| 2026-10-07 | 18962859 / 18962859 | 162293562 / 162293562 | agree |
| 2026-10-08 | 18962859 / 18962859 | 459891587 / 459891587 | agree |
| 2026-10-09 | 18962859 / 18962859 | 18761074 / 18761074 | agree |
| 2026-10-12 | 18962859 / 18962859 | 26038276 / 26038276 | agree |
| 2026-10-13 | 18962859 / 18962859 | 40228045 / 40228045 | agree |
| 2026-10-14 | 18962859 / 18962859 | 174459443 / 174459443 | agree |
| 2026-10-15 | 18962859 / 18962859 | 493485755 / 493485755 | agree |
| 2026-10-16 | 18962859 / 18962859 | 24749231 / 24749231 | agree |
| 2026-10-19 | 18962859 / 18962859 | 32609976 / 32609976 | agree |
| 2026-10-21 | 18962859 / 18962859 | 188513714 / 188513714 | agree |
| set | 15 imputed days, 15 lake days | | agree |

## Notes

Only the BSE F&O contracts on the 15 imputed days (29 Sep to 21 Oct 2026) change, to the lake values already used by Angel switch c. Take rates are not recalibrated at this stage (Q2 FY27 is still an estimate quarter), so only the 2 September days in Q2 FY27 and the 13 October days move.
Spec vs switch: as the spec says. Note the effect carries into g-d: once Q2 FY27 is calibrated its sum of contracts includes the lake values for 29-30 Sep.
