# Groww switch g-a: independent recompute

Script: `out/checks/groww_switch_a_check.py` (stdlib json/math/csv). Inputs: db snapshot, Groww fixtures/snapshot, reviewed facts, Angel calibration read from `parity_expected`. No engine code read.

**Result: 112/112 items agree** (69 to 1e-6 relative; 43 agree only to the bridge print precision).

| Item kind | Checked | Agree | Agree at 1e-6 |
|---|---:|---:|---:|
| ADR | 30 | 30 | 30 |
| param | 46 | 46 | 8 |
| input | 24 | 24 | 19 |
| daily | 4 | 4 | 4 |
| tie | 8 | 8 | 8 |

## ADR, Rs crore per trading day (consolidated and panels)

| Period | Panel | My before | Bridge before | My after | Bridge after | Max rel diff | Verdict |
|---|---|---:|---:|---:|---:|---:|---|
| FY 2027 | Consolidated | 19.063286 | 19.063286 | 19.468553 | 19.468553 | 1.7e-08 | agree |
| FY 2027 | Broking | 16.776562 | 16.776562 | 17.139643 | 17.139643 | 1.1e-08 | agree |
| FY 2027 | MTF | 2.286724 | 2.286724 | 2.328909 | 2.328909 | 2.1e-07 | agree |
| FY 2027 | F&O | 11.474513 | 11.474513 | 11.955493 | 11.955493 | 3.7e-08 | agree |
| FY 2027 | Cash | 4.134387 | 4.134387 | 4.162446 | 4.162446 | 7.9e-08 | agree |
| FY 2027 | Commodities | 1.167662 | 1.167662 | 1.021704 | 1.021704 | 3.0e-07 | agree |
| Q2 FY 2027 | Consolidated | 18.449855 | 18.449855 | 18.682593 | 18.682593 | 2.5e-08 | agree |
| Q2 FY 2027 | Broking | 15.967491 | 15.967491 | 16.200229 | 16.200229 | 1.5e-08 | agree |
| Q2 FY 2027 | MTF | 2.482364 | 2.482364 | 2.482364 | 2.482364 | 8.6e-08 | agree |
| Q2 FY 2027 | F&O | 10.539552 | 10.539552 | 10.981340 | 10.981340 | 4.7e-08 | agree |
| Q2 FY 2027 | Cash | 4.148108 | 4.148108 | 4.099037 | 4.099037 | 7.0e-08 | agree |
| Q2 FY 2027 | Commodities | 1.279831 | 1.279831 | 1.119852 | 1.119852 | 7.8e-08 | agree |
| FY 2027 October | Consolidated | 17.406517 | 17.406517 | 17.505687 | 17.505687 | 2.8e-08 | agree |
| FY 2027 October | Broking | 14.508844 | 14.508844 | 14.608014 | 14.608014 | 1.5e-08 | agree |
| FY 2027 October | MTF | 2.897674 | 2.897674 | 2.897674 | 2.897674 | 1.1e-07 | agree |
| FY 2027 October | F&O | 8.364280 | 8.364280 | 8.714887 | 8.714887 | 2.7e-08 | agree |
| FY 2027 October | Cash | 4.565102 | 4.565102 | 4.511097 | 4.511097 | 6.5e-08 | agree |
| FY 2027 October | Commodities | 1.579462 | 1.579462 | 1.382030 | 1.382030 | 3.5e-07 | agree |
| FY 2026 | Consolidated | 13.040054 | 13.040054 | 12.996051 | 12.996051 | 2.3e-08 | agree |
| FY 2026 | Broking | 12.054900 | 12.054900 | 11.988643 | 11.988643 | 2.1e-08 | agree |
| FY 2026 | MTF | 0.985154 | 0.985154 | 1.007408 | 1.007408 | 3.1e-07 | agree |
| FY 2026 | F&O | 8.445306 | 8.445306 | 8.603497 | 8.603497 | 5.2e-08 | agree |
| FY 2026 | Cash | 2.693880 | 2.693880 | 2.583896 | 2.583896 | 1.7e-07 | agree |
| FY 2026 | Commodities | 0.915715 | 0.915715 | 0.801250 | 0.801250 | 4.7e-07 | agree |
| FY 2026 October | Consolidated | 16.939220 | 16.939220 | 16.556092 | 16.556092 | 2.3e-08 | agree |
| FY 2026 October | Broking | 15.773625 | 15.773625 | 15.468204 | 15.468204 | 4.9e-09 | agree |
| FY 2026 October | MTF | 1.165595 | 1.165595 | 1.087888 | 1.087888 | 3.5e-07 | agree |
| FY 2026 October | F&O | 11.244452 | 11.244452 | 11.350532 | 11.350532 | 2.1e-08 | agree |
| FY 2026 October | Cash | 3.711499 | 3.711499 | 3.402207 | 3.402207 | 1.4e-07 | agree |
| FY 2026 October | Commodities | 0.817674 | 0.817674 | 0.715465 | 0.715465 | 6.0e-07 | agree |

## Parameters that moved

| Segment | Quantity | Quarter | My before | Bridge before | My after | Bridge after | My d% | Bridge d% | Verdict |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| Cash | revenue Rs Mn | Q2 FY 2026 | 2034.51 | 2,034.51 | 1906.02 | 1,906.02 | -6.31579 | -6.316% | agree |
| Cash | revenue Rs Mn | Q3 FY 2026 | 2269.93 | 2,269.93 | 2080.77 | 2,080.77 | -8.33333 | -8.333% | agree |
| Cash | revenue Rs Mn | Q4 FY 2026 | 2349.44 | 2,349.44 | 2395.43 | 2,395.43 | 1.95768 | +1.958% | agree |
| Cash | revenue Rs Mn | Q1 FY 2027 | 2415.72 | 2,415.72 | 2493.36 | 2,493.36 | 3.21389 | +3.214% | agree |
| Cash | take rate Rs/order | Q2 FY 2026 | 20.2004 | 20.2004 | 18.9246 | 18.9246 | -6.31579 | -6.316% | agree |
| Cash | take rate Rs/order | Q3 FY 2026 | 21.211 | 21.2110 | 19.4435 | 19.4435 | -8.33333 | -8.333% | agree |
| Cash | take rate Rs/order | Q4 FY 2026 | 19.2083 | 19.2083 | 19.5843 | 19.5843 | 1.95768 | +1.958% | agree |
| Cash | take rate Rs/order | Q1 FY 2027 | 20.7737 | 20.7737 | 21.4414 | 21.4414 | 3.21389 | +3.214% | agree |
| Cash | take rate Rs/order | Q2 FY 2027 | 20.3977 | 20.3977 | 20.1564 | 20.1564 | -1.18299 | -1.183% | agree |
| Cash | take rate Rs/order | Q3 FY 2027 | 20.3977 | 20.3977 | 20.1564 | 20.1564 | -1.18299 | -1.183% | agree |
| Commodities | revenue Rs Mn | Q3 FY 2026 | 504.429 | 504.43 | 441.375 | 441.38 | -12.5 | -12.500% | agree |
| Commodities | share of Angel market orders | Q3 FY 2026 | 0.332399 | 0.3324 | 0.290849 | 0.2908 | -12.5 | -12.500% | agree |
| Commodities | share of Angel market orders | Q4 FY 2026 | 0.332399 | 0.3324 | 0.290849 | 0.2908 | -12.5 | -12.500% | agree |
| Commodities | share of Angel market orders | Q1 FY 2027 | 0.332399 | 0.3324 | 0.290849 | 0.2908 | -12.5 | -12.500% | agree |
| Commodities | share of Angel market orders | Q2 FY 2027 | 0.332399 | 0.3324 | 0.290849 | 0.2908 | -12.5 | -12.500% | agree |
| Commodities | share of Angel market orders | Q3 FY 2027 | 0.332399 | 0.3324 | 0.290849 | 0.2908 | -12.5 | -12.500% | agree |
| F&O | revenue Rs Mn | Q2 FY 2026 | 6103.54 | 6,103.54 | 6092.83 | 6,092.83 | -0.175439 | -0.175% | agree |
| F&O | revenue Rs Mn | Q3 FY 2026 | 6683.68 | 6,683.68 | 6746.74 | 6,746.74 | 0.943396 | +0.943% | agree |
| F&O | revenue Rs Mn | Q4 FY 2026 | 8076.2 | 8,076.20 | 8414.73 | 8,414.73 | 4.19172 | +4.192% | agree |
| F&O | take rate Rs/order | Q2 FY 2026 | 29.6325 | 29.6325 | 29.5805 | 29.5805 | -0.175439 | -0.175% | agree |
| F&O | take rate Rs/order | Q3 FY 2026 | 28.9769 | 28.9769 | 29.2503 | 29.2503 | 0.943396 | +0.943% | agree |
| F&O | take rate Rs/order | Q4 FY 2026 | 26.3781 | 26.3781 | 27.4838 | 27.4838 | 4.19172 | +4.192% | agree |
| F&O | take rate Rs/order | Q1 FY 2027 | 26.3781 | 26.3781 | 27.4838 | 27.4838 | 4.19172 | +4.192% | agree |
| F&O | take rate Rs/order | Q2 FY 2027 | 26.3781 | 26.3781 | 27.4838 | 27.4838 | 4.19172 | +4.192% | agree |
| F&O | take rate Rs/order | Q3 FY 2027 | 26.3781 | 26.3781 | 27.4838 | 27.4838 | 4.19172 | +4.192% | agree |
| MTF | Groww average book Rs Cr | Q3 FY 2025 | 537.793 | 537.79 | 537.497 | 537.50 | -0.0550249 | -0.055% | agree |
| MTF | Groww average book Rs Cr | Q4 FY 2025 | 1137.12 | 1,137.12 | 454.62 | 454.62 | -60.0201 | -60.020% | agree |
| MTF | Groww average book Rs Cr | Q1 FY 2026 | 1268.9 | 1,268.90 | 761.315 | 761.31 | -40.0018 | -40.002% | agree |
| MTF | Groww average book Rs Cr | Q2 FY 2026 | 1432.5 | 1,432.50 | 1346.55 | 1,346.55 | -6 | -6.000% | agree |
| MTF | Groww average book Rs Cr | Q3 FY 2026 | 2024.46 | 2,024.46 | 1889.5 | 1,889.50 | -6.66667 | -6.667% | agree |
| MTF | Groww average book Rs Cr | Q4 FY 2026 | 1964.41 | 1,964.41 | 2834.83 | 2,834.83 | 44.3093 | +44.309% | agree |
| MTF | Groww average book Rs Cr | Q1 FY 2027 | 3157.19 | 3,157.19 | 3314.88 | 3,314.88 | 4.99458 | +4.995% | agree |
| MTF | revenue Rs Cr | Q3 FY 2025 | 20.1 | 20.1000 | 20.0889 | 20.0889 | -0.0550249 | -0.055% | agree |
| MTF | revenue Rs Cr | Q4 FY 2025 | 42.5 | 42.5000 | 16.9914 | 16.9914 | -60.0201 | -60.020% | agree |
| MTF | revenue Rs Cr | Q1 FY 2026 | 47.425 | 47.4250 | 28.4541 | 28.4541 | -40.0018 | -40.002% | agree |
| MTF | revenue Rs Cr | Q2 FY 2026 | 53.5399 | 53.5399 | 50.3275 | 50.3275 | -6 | -6.000% | agree |
| MTF | revenue Rs Cr | Q3 FY 2026 | 75.6643 | 75.6643 | 70.62 | 70.6200 | -6.66667 | -6.667% | agree |
| MTF | revenue Rs Cr | Q4 FY 2026 | 73.42 | 73.4200 | 105.952 | 105.95 | 44.3093 | +44.309% | agree |
| MTF | revenue Rs Cr | Q1 FY 2027 | 118 | 118.00 | 123.894 | 123.89 | 4.99458 | +4.995% | agree |
| MTF | share of industry book | Q3 FY 2025 | 0.00606533 | 0.0061 | 0.00606199 | 0.0061 | -0.0550249 | -0.055% | agree |
| MTF | share of industry book | Q4 FY 2025 | 0.0145785 | 0.0146 | 0.00582847 | 0.0058 | -60.0201 | -60.020% | agree |
| MTF | share of industry book | Q1 FY 2026 | 0.0161987 | 0.0162 | 0.00971891 | 0.0097 | -40.0018 | -40.002% | agree |
| MTF | share of industry book | Q2 FY 2026 | 0.0147681 | 0.0148 | 0.013882 | 0.0139 | -6 | -6.000% | agree |
| MTF | share of industry book | Q3 FY 2026 | 0.0177067 | 0.0177 | 0.0165262 | 0.0165 | -6.66667 | -6.667% | agree |
| MTF | share of industry book | Q4 FY 2026 | 0.0171315 | 0.0171 | 0.0247224 | 0.0247 | 44.3093 | +44.309% | agree |
| MTF | share of industry book | Q1 FY 2027 | 0.026531 | 0.0265 | 0.0278561 | 0.0279 | 4.99458 | +4.995% | agree |

## Inputs replaced (reviewed facts)

| Input | Period | My workbook | Bridge workbook | My live | Bridge live | Fact ids ok | Vintage ok | Verdict |
|---|---|---:|---:|---:|---:|---|---|---|
| mtf_revenue | Q3 FY 2025 | 20.1 | 20.1000 | 20.0889 | 20.0889 | yes | yes | agree |
| mtf_revenue | Q4 FY 2025 | 42.5 | 42.5000 | 16.9914 | 16.9914 | yes | yes | agree |
| mtf_revenue | Q1 FY 2026 | 47.425 | 47.4250 | 28.4541 | 28.4541 | yes | yes | agree |
| mtf_revenue | Q2 FY 2026 | 53.5399 | 53.5399 | 50.3275 | 50.3275 | yes | yes | agree |
| mtf_revenue | Q3 FY 2026 | 75.6643 | 75.6643 | 70.62 | 70.6200 | yes | yes | agree |
| mtf_revenue | Q4 FY 2026 | 73.42 | 73.4200 | 105.952 | 105.95 | yes | yes | agree |
| mtf_revenue | Q1 FY 2027 | 118 | 118.00 | 123.894 | 123.89 | yes | yes | agree |
| revmix_cash | Q2 FY 2026 | 0.19 | 0.1900 | 0.178 | 0.1780 | yes | yes | agree |
| revmix_cash | Q3 FY 2026 | 0.18 | 0.1800 | 0.165 | 0.1650 | yes | yes | agree |
| revmix_cash | Q4 FY 2026 | 0.16 | 0.1600 | 0.156 | 0.1560 | yes | yes | agree |
| revmix_cash | Q1 FY 2027 | 0.164 | 0.1640 | 0.161 | 0.1610 | yes | yes | agree |
| revmix_comm | Q3 FY 2026 | 0.04 | 0.0400 | 0.035 | 0.0350 | yes | yes | agree |
| revmix_fo | Q2 FY 2026 | 0.57 | 0.5700 | 0.569 | 0.5690 | yes | yes | agree |
| revmix_fo | Q3 FY 2026 | 0.53 | 0.5300 | 0.535 | 0.5350 | yes | yes | agree |
| revmix_fo | Q4 FY 2026 | 0.55 | 0.5500 | 0.548 | 0.5480 | yes | yes | agree |
| share_cash_adto_q | Q2 FY 2026 | 0.258 | 0.2580 | 0.258 | 0.2580 | yes | yes | agree |
| share_cash_adto_q | Q3 FY 2026 | 0.288 | 0.2880 | 0.288 | 0.2880 | yes | yes | agree |
| share_cash_adto_q | Q4 FY 2026 | 0.314 | 0.3140 | 0.314 | 0.3140 | yes | yes | agree |
| share_cash_adto_q | Q1 FY 2027 | 0.302 | 0.3020 | 0.302 | 0.3020 | yes | yes | agree |
| share_fo_adto_q | Q2 FY 2026 | 0.173 | 0.1730 | 0.173 | 0.1730 | yes | yes | agree |
| share_fo_adto_q | Q3 FY 2026 | 0.181 | 0.1810 | 0.181 | 0.1810 | yes | yes | agree |
| share_fo_adto_q | Q4 FY 2026 | 0.212 | 0.2120 | 0.212 | 0.2120 | yes | yes | agree |
| total_income | Q4 FY 2026 | — | — | 15355.4 | 15,355.35 | yes | yes | agree |
| total_income | Q1 FY 2027 | — | — | 15486.7 | 15,486.70 | yes | yes | agree |

## Daily revenue rows that changed

| Segment | Days | Changed (mine / bridge) | First | Last | Ratio min (mine / bridge) | Ratio max (mine / bridge) | Verdict |
|---|---:|---|---|---|---|---|---|
| F&O | 573 | 324 / 324 | 2025-07-01 | 2026-10-21 | 0.998245614 / 0.998245614 | 1.041917214 / 1.041917214 | agree |
| Cash | 573 | 324 / 324 | 2025-07-01 | 2026-10-21 | 0.916666667 / 0.916666667 | 1.032138948 / 1.032138948 | agree |
| Commodities | 272 | 272 / 272 | 2025-10-01 | 2026-10-21 | 0.875000000 / 0.875000000 | 0.875000000 / 0.875000000 | agree |
| MTF | 507 | 430 / 430 | 2024-10-01 | 2026-06-30 | 0.399798588 / 0.399798588 | 1.443093367 / 1.443093367 | agree |

## Tie-out of newly calibrated quarters (self-consistency, not in the bridge)

| Segment | Quarter | Reported revenue | Sum of daily revenue | Rel diff | Tolerance | Verdict |
|---|---|---:|---:|---:|---:|---|
| fo | Q2 FY 2026 | 6092.8349 | 6097.1216 | 7.04e-04 | 5e-03 | agree |
| fo | Q3 FY 2026 | 6746.7352 | 6740.7945 | 8.81e-04 | 5e-03 | agree |
| fo | Q4 FY 2026 | 8414.7318 | 8412.7221 | 2.39e-04 | 5e-03 | agree |
| cash | Q2 FY 2026 | 1906.0187 | 1906.0187 | 4.44e-16 | 1e-09 | agree |
| cash | Q3 FY 2026 | 2080.7688 | 2080.7688 | 2.22e-16 | 1e-09 | agree |
| cash | Q4 FY 2026 | 2395.4346 | 2395.4346 | 2.22e-16 | 1e-09 | agree |
| cash | Q1 FY 2027 | 2493.3587 | 2493.3587 | 2.22e-16 | 1e-09 | agree |
| comm | Q3 FY 2026 | 441.3752 | 463.4440 | 6.66e-16 | 1e-09 | agree |

## Notes

Method. Parity is first rebuilt from raw inputs (exchange volumes, Angel monthly contracts/order, quarterly trades/order, commodity contracts/order, Angel commodity take rates, industry MTF book) and reproduces the 573/573/272/507 daily Groww rows of `groww_fixtures_2026-10-23.json` to 1e-15 relative; this is the 'Before' column of g-a.
Formulas. Segment revenue (Rs Mn) = revenue mix x consolidated total income. F&O take rate = revenue / (sum of NSE+BSE contracts / quarterly mean of the three monthly Angel contracts-per-order x ADTO share). Cash take rate = revenue / (sum of trades / Angel trades-per-order x share). Commodity share = revenue / Angel take rate / sum of market orders over Oct-Dec 2025, times 1.05 (growth kept until g-d). MTF average book = revenue / (0.1495/4), share = book / Angel industry quarterly average. Daily revenue = market orders x share x take rate (MTF: share x daily book x 0.1495/246). Carry rules for unreported quarters are the workbook's (F&O take rate carried, share x1.05 once; cash take rate trailing 3).
Spec vs switch: the spec says 'one classification of the stocks mix'. The switch uses the restated classification (Q2 FY27 letter p6) wherever it exists and the original classification where it does not (Q1 FY26 under g-b; MTF Q3 FY25 to Q1 FY26). The restatement moved cash by about -1.6pp in Q2 FY26 (0.194 to 0.178), so the Q1 FY26 cash mix (0.193) sits on a classification about 8% richer than its neighbours. Disclosed in the bridge vintage column but not 'one classification'.
Spec vs switch: the spec names MTF mixes for Q4 FY25, Q1 FY26 and Q4 FY26 only. The switch also replaces Q3 FY25 (2%), Q2 FY26 (4.7%), Q3 FY26 (5.6%) and Q1 FY27 (8.0%; 118.00 to 123.89 Cr). Values agree with the facts file; the extra quarters are an enlargement of scope, not an error.
MTF Q2 FY27 ADR is unchanged at g-a because its share is still the typed 0.0288 (the share is not re-derived from revenue until g-f).
