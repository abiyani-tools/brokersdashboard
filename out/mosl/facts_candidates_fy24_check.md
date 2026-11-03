# MOSL FY24 candidate facts: cross-vintage check

Prepared 2026-11-03. Output: `out/mosl/facts_candidates_fy24.json` (116 facts). Nothing written to any database.

Source rule: each value comes from the latest data-book vintage that still carries the quarter for that row. FY24 quarterly columns (Q1FY24-Q4FY24) exist only in the Q1 FY25 ... Q4 FY26 books (8 vintages); the Q1 FY27 and Q2 FY27 books start at Q1FY25. All 116 values therefore come from `MOSL_DataBook_q4fy26-data-book.xlsx` (sheets Consol, WM, PWM, Capital Market). Extractor validated by re-reading the 290 existing facts from the Q2 FY27 book with the same label-matching code: 290 of 290 values and cells reproduced exactly.

Columns: value is in output unit (Rs Cr x10 = Rs Mn etc.). "Max abs diff" is in the output unit, "max rel diff" is vs the staged value, across the other vintages carrying that quarter and row. Flag = restatement above 0.5%.


## adto_cash  (ADTO (in Rs. Cr): Cash; Rs Mn/day)

| Quarter | Value | Unit | source_ref | Vintages compared (n) | Max abs diff | Max rel diff | Flag |
|---|---|---|---|---|---|---|---|
| Q1FY24 | 16024.478 | Rs Mn/day | `q4fy26-data-book.xlsx#Consol!E44` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 7531.9059 | 47.003% | RESTATED >0.5%: 23556.384 @ Q1FY25; 15279.054 @ Q2FY25; 16024.478 @ Q2FY26 |
| Q2FY24 | 24088.209 | Rs Mn/day | `q4fy26-data-book.xlsx#Consol!F44` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 9451.2017 | 39.236% | RESTATED >0.5%: 33539.411 @ Q1FY25; 23430.831 @ Q2FY25; 24088.209 @ Q2FY26 |
| Q3FY24 | 27969.824 | Rs Mn/day | `q4fy26-data-book.xlsx#Consol!G44` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 4776.5036 | 17.077% | RESTATED >0.5%: 32746.328 @ Q1FY25; 27203.661 @ Q2FY25; 27969.824 @ Q2FY26 |
| Q4FY24 | 40597.634 | Rs Mn/day | `q4fy26-data-book.xlsx#Consol!H44` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 11069.287 | 27.266% | RESTATED >0.5%: 51666.921 @ Q1FY25; 39777.113 @ Q2FY25; 40597.634 @ Q2FY26 |

## adto_notional_fo  (ADTO (in Rs. Cr): F&O (notional); Rs Mn/day)

| Quarter | Value | Unit | source_ref | Vintages compared (n) | Max abs diff | Max rel diff | Flag |
|---|---|---|---|---|---|---|---|
| Q1FY24 | 3965624.5 | Rs Mn/day | `q4fy26-data-book.xlsx#Consol!E45` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 134867.59 | 3.401% | RESTATED >0.5%: 4100492 @ Q1FY25; 3965624.5 @ Q2FY25 |
| Q2FY24 | 5123913.4 | Rs Mn/day | `q4fy26-data-book.xlsx#Consol!F45` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 94910.096 | 1.852% | RESTATED >0.5%: 5218823.5 @ Q1FY25; 5123913.4 @ Q2FY25 |
| Q3FY24 | 5546141 | Rs Mn/day | `q4fy26-data-book.xlsx#Consol!G45` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 63989.138 | 1.154% | RESTATED >0.5%: 5610130.2 @ Q1FY25; 5546141 @ Q2FY25 |
| Q4FY24 | 6982181.2 | Rs Mn/day | `q4fy26-data-book.xlsx#Consol!H45` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 122065.4 | 1.748% | RESTATED >0.5%: 7104246.6 @ Q1FY25; 6982181.2 @ Q2FY25 |

## adto_premium_fo  (ADTO (in Rs. Cr): F&O premium; Rs Mn/day)

| Quarter | Value | Unit | source_ref | Vintages compared (n) | Max abs diff | Max rel diff | Flag |
|---|---|---|---|---|---|---|---|
| Q1FY24 | 36673.058 | Rs Mn/day | `q4fy26-data-book.xlsx#Consol!E46` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 1527.682 | 4.166% | RESTATED >0.5%: 35145.376 @ Q1FY25; 36320 @ Q1FY26; 36673.058 @ Q2FY26 |
| Q2FY24 | 44373.577 | Rs Mn/day | `q4fy26-data-book.xlsx#Consol!F46` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 614.68794 | 1.385% | RESTATED >0.5%: 43758.889 @ Q1FY25; 44373.577 @ Q2FY26 |
| Q3FY24 | 48580.035 | Rs Mn/day | `q4fy26-data-book.xlsx#Consol!G46` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 1136.4214 | 2.339% | RESTATED >0.5%: 47443.613 @ Q1FY25; 48580.035 @ Q2FY26 |
| Q4FY24 | 66816.341 | Rs Mn/day | `q4fy26-data-book.xlsx#Consol!H46` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 767.81599 | 1.149% | RESTATED >0.5%: 66048.525 @ Q1FY25; 66816.341 @ Q2FY26 |

## adto_comm  (ADTO (in Rs. Cr): Commodity; Rs Mn/day)

| Quarter | Value | Unit | source_ref | Vintages compared (n) | Max abs diff | Max rel diff | Flag |
|---|---|---|---|---|---|---|---|
| Q1FY24 | 27293.758 | Rs Mn/day | `q4fy26-data-book.xlsx#Consol!E47` | Q2FY25..Q4FY26 (7); row absent in Q1FY25; book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q2FY24 | 33671.485 | Rs Mn/day | `q4fy26-data-book.xlsx#Consol!F47` | Q2FY25..Q4FY26 (7); row absent in Q1FY25; book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q3FY24 | 45778.545 | Rs Mn/day | `q4fy26-data-book.xlsx#Consol!G47` | Q2FY25..Q4FY26 (7); row absent in Q1FY25; book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q4FY24 | 54683.339 | Rs Mn/day | `q4fy26-data-book.xlsx#Consol!H47` | Q2FY25..Q4FY26 (7); row absent in Q1FY25; book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |

## adto_currency  (ADTO (in Rs. Cr): Currency; Rs Mn/day)

| Quarter | Value | Unit | source_ref | Vintages compared (n) | Max abs diff | Max rel diff | Flag |
|---|---|---|---|---|---|---|---|
| Q1FY24 | 93318.758 | Rs Mn/day | `q4fy26-data-book.xlsx#Consol!E48` | Q2FY25..Q4FY26 (7); row absent in Q1FY25; book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q2FY24 | 98954.279 | Rs Mn/day | `q4fy26-data-book.xlsx#Consol!F48` | Q2FY25..Q4FY26 (7); row absent in Q1FY25; book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q3FY24 | 67400.796 | Rs Mn/day | `q4fy26-data-book.xlsx#Consol!G48` | Q2FY25..Q4FY26 (7); row absent in Q1FY25; book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q4FY24 | 60524.39 | Rs Mn/day | `q4fy26-data-book.xlsx#Consol!H48` | Q2FY25..Q4FY26 (7); row absent in Q1FY25; book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |

## gross_brokerage_total  (Gross Brokerage (Rs Cr): total; Rs Mn)

| Quarter | Value | Unit | source_ref | Vintages compared (n) | Max abs diff | Max rel diff | Flag |
|---|---|---|---|---|---|---|---|
| Q1FY24 | 4062.9309 | Rs Mn | `q4fy26-data-book.xlsx#Consol!E50` | Q2FY25..Q4FY26 (7); row absent in Q1FY25; book has no FY24 columns: Q1FY27..Q2FY27 | 274.63303 | 6.759% | RESTATED >0.5%: 3788.2979 @ Q2FY25; 4062.9309 @ Q2FY26 |
| Q2FY24 | 5075.8353 | Rs Mn | `q4fy26-data-book.xlsx#Consol!F50` | Q2FY25..Q4FY26 (7); row absent in Q1FY25; book has no FY24 columns: Q1FY27..Q2FY27 | 31.260412 | 0.616% | RESTATED >0.5%: 5044.5749 @ Q2FY25; 5075.8353 @ Q2FY26 |
| Q3FY24 | 4959.7317 | Rs Mn | `q4fy26-data-book.xlsx#Consol!G50` | Q2FY25..Q4FY26 (7); row absent in Q1FY25; book has no FY24 columns: Q1FY27..Q2FY27 | 95.012854 | 1.916% | RESTATED >0.5%: 4864.7189 @ Q2FY25; 4959.7317 @ Q2FY26 |
| Q4FY24 | 6319.877 | Rs Mn | `q4fy26-data-book.xlsx#Consol!H50` | Q2FY25..Q4FY26 (7); row absent in Q1FY25; book has no FY24 columns: Q1FY27..Q2FY27 | 92.120566 | 1.458% | RESTATED >0.5%: 6227.7564 @ Q2FY25; 6319.877 @ Q2FY26 |

## gross_brokerage_cash  (Gross Brokerage (Rs Cr): Cash; Rs Mn)

| Quarter | Value | Unit | source_ref | Vintages compared (n) | Max abs diff | Max rel diff | Flag |
|---|---|---|---|---|---|---|---|
| Q1FY24 | 1509.6156 | Rs Mn | `q4fy26-data-book.xlsx#Consol!E51` | Q2FY25..Q4FY26 (7); row absent in Q1FY25; book has no FY24 columns: Q1FY27..Q2FY27 | 271.20359 | 17.965% | RESTATED >0.5%: 1238.412 @ Q2FY25; 1509.6156 @ Q2FY26 |
| Q2FY24 | 1978.7272 | Rs Mn | `q4fy26-data-book.xlsx#Consol!F51` | Q2FY25..Q4FY26 (7); row absent in Q1FY25; book has no FY24 columns: Q1FY27..Q2FY27 | 25.983123 | 1.313% | RESTATED >0.5%: 1952.7441 @ Q2FY25; 1978.7272 @ Q2FY26 |
| Q3FY24 | 2210.6881 | Rs Mn | `q4fy26-data-book.xlsx#Consol!G51` | Q2FY25..Q4FY26 (7); row absent in Q1FY25; book has no FY24 columns: Q1FY27..Q2FY27 | 86.43028 | 3.910% | RESTATED >0.5%: 2124.2578 @ Q2FY25; 2210.6881 @ Q2FY26 |
| Q4FY24 | 3169.4787 | Rs Mn | `q4fy26-data-book.xlsx#Consol!H51` | Q2FY25..Q4FY26 (7); row absent in Q1FY25; book has no FY24 columns: Q1FY27..Q2FY27 | 85.04137 | 2.683% | RESTATED >0.5%: 3084.4373 @ Q2FY25; 3169.4787 @ Q2FY26 |

## gross_brokerage_fo  (Gross Brokerage (Rs Cr): F&O; Rs Mn)

| Quarter | Value | Unit | source_ref | Vintages compared (n) | Max abs diff | Max rel diff | Flag |
|---|---|---|---|---|---|---|---|
| Q1FY24 | 2065.2304 | Rs Mn | `q4fy26-data-book.xlsx#Consol!E52` | Q2FY25..Q4FY26 (7); row absent in Q1FY25; book has no FY24 columns: Q1FY27..Q2FY27 | 3.4294368 | 0.166% | restated <=0.5% |
| Q2FY24 | 2591.5957 | Rs Mn | `q4fy26-data-book.xlsx#Consol!F52` | Q2FY25..Q4FY26 (7); row absent in Q1FY25; book has no FY24 columns: Q1FY27..Q2FY27 | 5.277289 | 0.204% | restated <=0.5% |
| Q3FY24 | 2316.191 | Rs Mn | `q4fy26-data-book.xlsx#Consol!G52` | Q2FY25..Q4FY26 (7); row absent in Q1FY25; book has no FY24 columns: Q1FY27..Q2FY27 | 8.582574 | 0.371% | restated <=0.5% |
| Q4FY24 | 2661.0694 | Rs Mn | `q4fy26-data-book.xlsx#Consol!H52` | Q2FY25..Q4FY26 (7); row absent in Q1FY25; book has no FY24 columns: Q1FY27..Q2FY27 | 7.0791966 | 0.266% | restated <=0.5% |

## gross_brokerage_comm  (Gross Brokerage (Rs Cr): Commodity; Rs Mn)

| Quarter | Value | Unit | source_ref | Vintages compared (n) | Max abs diff | Max rel diff | Flag |
|---|---|---|---|---|---|---|---|
| Q1FY24 | 226.7595 | Rs Mn | `q4fy26-data-book.xlsx#Consol!E53` | Q2FY25..Q4FY26 (7); row absent in Q1FY25; book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q2FY24 | 237.30465 | Rs Mn | `q4fy26-data-book.xlsx#Consol!F53` | Q2FY25..Q4FY26 (7); row absent in Q1FY25; book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q3FY24 | 261.30393 | Rs Mn | `q4fy26-data-book.xlsx#Consol!G53` | Q2FY25..Q4FY26 (7); row absent in Q1FY25; book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q4FY24 | 299.83523 | Rs Mn | `q4fy26-data-book.xlsx#Consol!H53` | Q2FY25..Q4FY26 (7); row absent in Q1FY25; book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |

## gross_brokerage_currency  (Gross Brokerage (Rs Cr): Currency; Rs Mn)

| Quarter | Value | Unit | source_ref | Vintages compared (n) | Max abs diff | Max rel diff | Flag |
|---|---|---|---|---|---|---|---|
| Q1FY24 | 261.32542 | Rs Mn | `q4fy26-data-book.xlsx#Consol!E54` | Q2FY25..Q4FY26 (7); row absent in Q1FY25; book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q2FY24 | 268.20773 | Rs Mn | `q4fy26-data-book.xlsx#Consol!F54` | Q2FY25..Q4FY26 (7); row absent in Q1FY25; book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q3FY24 | 171.54869 | Rs Mn | `q4fy26-data-book.xlsx#Consol!G54` | Q2FY25..Q4FY26 (7); row absent in Q1FY25; book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q4FY24 | 189.49368 | Rs Mn | `q4fy26-data-book.xlsx#Consol!H54` | Q2FY25..Q4FY26 (7); row absent in Q1FY25; book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |

## net_brokerage_total  (Net Brokerage (Rs Cr): total; Rs Mn)

| Quarter | Value | Unit | source_ref | Vintages compared (n) | Max abs diff | Max rel diff | Flag |
|---|---|---|---|---|---|---|---|
| Q1FY24 | 2431.2338 | Rs Mn | `q4fy26-data-book.xlsx#Consol!E56` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 601.47862 | 24.740% | RESTATED >0.5%: 1829.7552 @ Q1FY25; 2160.2151 @ Q2FY25; 2431.2338 @ Q2FY26 |
| Q2FY24 | 2875.1105 | Rs Mn | `q4fy26-data-book.xlsx#Consol!F56` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 359.70778 | 12.511% | RESTATED >0.5%: 2515.4027 @ Q1FY25; 2849.3639 @ Q2FY25; 2875.1105 @ Q2FY26 |
| Q3FY24 | 2788.7811 | Rs Mn | `q4fy26-data-book.xlsx#Consol!G56` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 358.55081 | 12.857% | RESTATED >0.5%: 2430.2303 @ Q1FY25; 2698.0057 @ Q2FY25; 2788.7811 @ Q2FY26 |
| Q4FY24 | 3491.2976 | Rs Mn | `q4fy26-data-book.xlsx#Consol!H56` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 387.86072 | 11.109% | RESTATED >0.5%: 3103.4369 @ Q1FY25; 3411.6282 @ Q2FY25; 3491.2976 @ Q2FY26 |

## net_brokerage_cash  (Net Brokerage (Rs Cr): Cash; Rs Mn)

| Quarter | Value | Unit | source_ref | Vintages compared (n) | Max abs diff | Max rel diff | Flag |
|---|---|---|---|---|---|---|---|
| Q1FY24 | 904.15964 | Rs Mn | `q4fy26-data-book.xlsx#Consol!E57` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 267.74164 | 29.612% | RESTATED >0.5%: 636.418 @ Q1FY25; 904.15964 @ Q2FY26 |
| Q2FY24 | 1018.2643 | Rs Mn | `q4fy26-data-book.xlsx#Consol!F57` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 20.61753 | 2.025% | RESTATED >0.5%: 997.64673 @ Q1FY25; 1018.2643 @ Q2FY26 |
| Q3FY24 | 1181.8841 | Rs Mn | `q4fy26-data-book.xlsx#Consol!G57` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 82.344385 | 6.967% | RESTATED >0.5%: 1099.5397 @ Q1FY25; 1181.8841 @ Q2FY26 |
| Q4FY24 | 1664.1245 | Rs Mn | `q4fy26-data-book.xlsx#Consol!H57` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 72.752412 | 4.372% | RESTATED >0.5%: 1591.3721 @ Q1FY25; 1664.1245 @ Q2FY26 |

## net_brokerage_fo  (Net Brokerage (Rs Cr): F&O; Rs Mn)

| Quarter | Value | Unit | source_ref | Vintages compared (n) | Max abs diff | Max rel diff | Flag |
|---|---|---|---|---|---|---|---|
| Q1FY24 | 1196.6142 | Rs Mn | `q4fy26-data-book.xlsx#Consol!E58` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 3.2770472 | 0.274% | restated <=0.5% |
| Q2FY24 | 1522.885 | Rs Mn | `q4fy26-data-book.xlsx#Consol!F58` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 5.1290602 | 0.337% | restated <=0.5% |
| Q3FY24 | 1339.1216 | Rs Mn | `q4fy26-data-book.xlsx#Consol!G58` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 8.4310095 | 0.630% | RESTATED >0.5%: 1330.6906 @ Q1FY25; 1339.1216 @ Q2FY26 |
| Q4FY24 | 1518.9817 | Rs Mn | `q4fy26-data-book.xlsx#Consol!H58` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 6.9169667 | 0.455% | restated <=0.5% |

## net_brokerage_comm  (Net Brokerage (Rs Cr): Commodity; Rs Mn)

| Quarter | Value | Unit | source_ref | Vintages compared (n) | Max abs diff | Max rel diff | Flag |
|---|---|---|---|---|---|---|---|
| Q1FY24 | 140.53011 | Rs Mn | `q4fy26-data-book.xlsx#Consol!E59` | Q2FY25..Q4FY26 (7); row absent in Q1FY25; book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q2FY24 | 147.98154 | Rs Mn | `q4fy26-data-book.xlsx#Consol!F59` | Q2FY25..Q4FY26 (7); row absent in Q1FY25; book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q3FY24 | 158.54466 | Rs Mn | `q4fy26-data-book.xlsx#Consol!G59` | Q2FY25..Q4FY26 (7); row absent in Q1FY25; book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q4FY24 | 184.44533 | Rs Mn | `q4fy26-data-book.xlsx#Consol!H59` | Q2FY25..Q4FY26 (7); row absent in Q1FY25; book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |

## net_brokerage_currency  (Net Brokerage (Rs Cr): Currency; Rs Mn)

| Quarter | Value | Unit | source_ref | Vintages compared (n) | Max abs diff | Max rel diff | Flag |
|---|---|---|---|---|---|---|---|
| Q1FY24 | 189.92982 | Rs Mn | `q4fy26-data-book.xlsx#Consol!E60` | Q2FY25..Q4FY26 (7); row absent in Q1FY25; book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q2FY24 | 185.97964 | Rs Mn | `q4fy26-data-book.xlsx#Consol!F60` | Q2FY25..Q4FY26 (7); row absent in Q1FY25; book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q3FY24 | 109.23076 | Rs Mn | `q4fy26-data-book.xlsx#Consol!G60` | Q2FY25..Q4FY26 (7); row absent in Q1FY25; book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q4FY24 | 123.74601 | Rs Mn | `q4fy26-data-book.xlsx#Consol!H60` | Q2FY25..Q4FY26 (7); row absent in Q1FY25; book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |

## share_overall  (Market share: Overall (Cash + F&O + Commodity); fraction)

| Quarter | Value | Unit | source_ref | Vintages compared (n) | Max abs diff | Max rel diff | Flag |
|---|---|---|---|---|---|---|---|
| Q1FY24 | 0.067778741 | fraction | `q4fy26-data-book.xlsx#Consol!E63` | Q4FY26 (1); row absent in Q1FY25..Q3FY26; book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q2FY24 | 0.071440764 | fraction | `q4fy26-data-book.xlsx#Consol!F63` | Q4FY26 (1); row absent in Q1FY25..Q3FY26; book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q3FY24 | 0.080198817 | fraction | `q4fy26-data-book.xlsx#Consol!G63` | Q4FY26 (1); row absent in Q1FY25..Q3FY26; book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q4FY24 | 0.087512468 | fraction | `q4fy26-data-book.xlsx#Consol!H63` | Q4FY26 (1); row absent in Q1FY25..Q3FY26; book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |

## share_cash  (Market share: Cash; fraction)

| Quarter | Value | Unit | source_ref | Vintages compared (n) | Max abs diff | Max rel diff | Flag |
|---|---|---|---|---|---|---|---|
| Q1FY24 | 0.064659927 | fraction | `q4fy26-data-book.xlsx#Consol!E64` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 0.0069194501 | 10.701% | RESTATED >0.5%: 0.057740476 @ Q1FY25; 0.061797036 @ Q2FY25; 0.061797034 @ Q1FY26; 0.064659927 @ Q2FY26 |
| Q2FY24 | 0.072539401 | fraction | `q4fy26-data-book.xlsx#Consol!F64` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 0.0093281495 | 12.859% | RESTATED >0.5%: 0.063211251 @ Q1FY25; 0.070559767 @ Q2FY25; 0.072539401 @ Q2FY26 |
| Q3FY24 | 0.076870966 | fraction | `q4fy26-data-book.xlsx#Consol!G64` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 0.013659715 | 17.770% | RESTATED >0.5%: 0.063211251 @ Q1FY25; 0.07476528 @ Q2FY25; 0.076870966 @ Q2FY26 |
| Q4FY24 | 0.08323862 | fraction | `q4fy26-data-book.xlsx#Consol!H64` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 0.0016823407 | 2.021% | RESTATED >0.5%: 0.081556279 @ Q1FY25; 0.08155628 @ Q2FY25; 0.08323862 @ Q2FY26 |

## share_fo_premium  (Market share: F&O premium; fraction)

| Quarter | Value | Unit | source_ref | Vintages compared (n) | Max abs diff | Max rel diff | Flag |
|---|---|---|---|---|---|---|---|
| Q1FY24 | 0.073190892 | fraction | `q4fy26-data-book.xlsx#Consol!E66` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 0.0030429479 | 4.158% | RESTATED >0.5%: 0.070147944 @ Q1FY25; 0.072486209 @ Q2FY25; 0.073190892 @ Q2FY26 |
| Q2FY24 | 0.076256995 | fraction | `q4fy26-data-book.xlsx#Consol!F66` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 0.0010563647 | 1.385% | RESTATED >0.5%: 0.075200631 @ Q1FY25; 0.076256995 @ Q2FY26 |
| Q3FY24 | 0.083104633 | fraction | `q4fy26-data-book.xlsx#Consol!G66` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 0.0019463355 | 2.342% | RESTATED >0.5%: 0.081158297 @ Q1FY25; 0.083104633 @ Q2FY26 |
| Q4FY24 | 0.087714069 | fraction | `q4fy26-data-book.xlsx#Consol!H66` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 0.001008981 | 1.150% | RESTATED >0.5%: 0.086705088 @ Q1FY25; 0.087714069 @ Q2FY26 |

## share_comm  (Market share: Commodity; fraction)

| Quarter | Value | Unit | source_ref | Vintages compared (n) | Max abs diff | Max rel diff | Flag |
|---|---|---|---|---|---|---|---|
| Q1FY24 | 0.063279814 | fraction | `q4fy26-data-book.xlsx#Consol!E67` | Q4FY26 (1); row absent in Q1FY25..Q3FY26; book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q2FY24 | 0.065298359 | fraction | `q4fy26-data-book.xlsx#Consol!F67` | Q4FY26 (1); row absent in Q1FY25..Q3FY26; book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q3FY24 | 0.079353206 | fraction | `q4fy26-data-book.xlsx#Consol!G67` | Q4FY26 (1); row absent in Q1FY25..Q3FY26; book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q4FY24 | 0.090715684 | fraction | `q4fy26-data-book.xlsx#Consol!H67` | Q4FY26 (1); row absent in Q1FY25..Q3FY26; book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |

## mtf_book  (MTF Book (in Rs Cr); Rs Mn)

| Quarter | Value | Unit | source_ref | Vintages compared (n) | Max abs diff | Max rel diff | Flag |
|---|---|---|---|---|---|---|---|
| Q1FY24 | 14670 | Rs Mn | `q4fy26-data-book.xlsx#Consol!E70` | Q4FY26 (1); row absent in Q1FY25..Q3FY26; book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q2FY24 | 19700 | Rs Mn | `q4fy26-data-book.xlsx#Consol!F70` | Q4FY26 (1); row absent in Q1FY25..Q3FY26; book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q3FY24 | 28270 | Rs Mn | `q4fy26-data-book.xlsx#Consol!G70` | Q4FY26 (1); row absent in Q1FY25..Q3FY26; book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q4FY24 | 34940 | Rs Mn | `q4fy26-data-book.xlsx#Consol!H70` | Q4FY26 (1); row absent in Q1FY25..Q3FY26; book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |

## nse_active_clients  (NSE Active clients (in Lacs.); Mn)

| Quarter | Value | Unit | source_ref | Vintages compared (n) | Max abs diff | Max rel diff | Flag |
|---|---|---|---|---|---|---|---|
| Q1FY24 | 0.761297 | Mn | `q4fy26-data-book.xlsx#Consol!E69` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q2FY24 | 0.798085 | Mn | `q4fy26-data-book.xlsx#Consol!F69` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q3FY24 | 0.822398 | Mn | `q4fy26-data-book.xlsx#Consol!G69` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q4FY24 | 0.879629 | Mn | `q4fy26-data-book.xlsx#Consol!H69` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |

## broking_arpu  (Broking ARPU in Rs. (on Gross brokerage); Rs)

| Quarter | Value | Unit | source_ref | Vintages compared (n) | Max abs diff | Max rel diff | Flag |
|---|---|---|---|---|---|---|---|
| Q1FY24 | 18246.159 | Rs | `q4fy26-data-book.xlsx#Consol!E72` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q2FY24 | 19322.204 | Rs | `q4fy26-data-book.xlsx#Consol!F72` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q3FY24 | 20228.812 | Rs | `q4fy26-data-book.xlsx#Consol!G72` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q4FY24 | 23653.718 | Rs | `q4fy26-data-book.xlsx#Consol!H72` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |

## wm_nii  (Wealth Management: Net Interest Income (Rs Cr); Rs Mn)

| Quarter | Value | Unit | source_ref | Vintages compared (n) | Max abs diff | Max rel diff | Flag |
|---|---|---|---|---|---|---|---|
| Q1FY24 | 1279.3035 | Rs Mn | `q4fy26-data-book.xlsx#WM!E8` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 10 | 0.782% | RESTATED >0.5%: 1269.3035 @ Q1FY25; 1279.3035 @ Q4FY25 |
| Q2FY24 | 1437.976 | Rs Mn | `q4fy26-data-book.xlsx#WM!F8` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q3FY24 | 1536.3256 | Rs Mn | `q4fy26-data-book.xlsx#WM!G8` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q4FY24 | 1854.4285 | Rs Mn | `q4fy26-data-book.xlsx#WM!H8` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 20 | 1.078% | RESTATED >0.5%: 1834.4285 @ Q1FY25; 1854.4285 @ Q4FY25 |

## wm_brokerage_net  (Wealth Management: Brokerage Income (Rs Cr), net of commission sharing; Rs Mn)

| Quarter | Value | Unit | source_ref | Vintages compared (n) | Max abs diff | Max rel diff | Flag |
|---|---|---|---|---|---|---|---|
| Q1FY24 | 1638.7385 | Rs Mn | `q4fy26-data-book.xlsx#WM!E9` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q2FY24 | 2151.5377 | Rs Mn | `q4fy26-data-book.xlsx#WM!F9` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q3FY24 | 2049.9497 | Rs Mn | `q4fy26-data-book.xlsx#WM!G9` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q4FY24 | 2658.2023 | Rs Mn | `q4fy26-data-book.xlsx#WM!H9` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |

## wm_distribution  (Wealth Management: Distribution Income (Rs Cr); Rs Mn)

| Quarter | Value | Unit | source_ref | Vintages compared (n) | Max abs diff | Max rel diff | Flag |
|---|---|---|---|---|---|---|---|
| Q1FY24 | 277.2308 | Rs Mn | `q4fy26-data-book.xlsx#WM!E7` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 37.960178 | 13.693% | RESTATED >0.5%: 315.19097 @ Q1FY25; 277.2308 @ Q4FY26 |
| Q2FY24 | 364.99699 | Rs Mn | `q4fy26-data-book.xlsx#WM!F7` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 48.374275 | 13.253% | RESTATED >0.5%: 413.37127 @ Q1FY25; 364.99699 @ Q4FY26 |
| Q3FY24 | 507.53629 | Rs Mn | `q4fy26-data-book.xlsx#WM!G7` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 44.078325 | 8.685% | RESTATED >0.5%: 551.61461 @ Q1FY25; 507.53629 @ Q4FY26 |
| Q4FY24 | 710.34949 | Rs Mn | `q4fy26-data-book.xlsx#WM!H7` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 67.175595 | 9.457% | RESTATED >0.5%: 777.52508 @ Q1FY25; 710.34949 @ Q4FY26 |

## wm_lending_book_close  (Wealth Management: Lending Book, closing (Rs Cr); Rs Mn)

| Quarter | Value | Unit | source_ref | Vintages compared (n) | Max abs diff | Max rel diff | Flag |
|---|---|---|---|---|---|---|---|
| Q1FY24 | 42324.14 | Rs Mn | `q4fy26-data-book.xlsx#WM!E18` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q2FY24 | 46080 | Rs Mn | `q4fy26-data-book.xlsx#WM!F18` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q3FY24 | 47660 | Rs Mn | `q4fy26-data-book.xlsx#WM!G18` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q4FY24 | 49880 | Rs Mn | `q4fy26-data-book.xlsx#WM!H18` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |

## wm_lending_assets_avg  (Wealth Management: Lending Assets, average (Rs Cr); Rs Mn)

| Quarter | Value | Unit | source_ref | Vintages compared (n) | Max abs diff | Max rel diff | Flag |
|---|---|---|---|---|---|---|---|
| Q1FY24 | 33147.07 | Rs Mn | `q4fy26-data-book.xlsx#WM!E46` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q2FY24 | 44202.07 | Rs Mn | `q4fy26-data-book.xlsx#WM!F46` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q3FY24 | 46870 | Rs Mn | `q4fy26-data-book.xlsx#WM!G46` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q4FY24 | 48770 | Rs Mn | `q4fy26-data-book.xlsx#WM!H46` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |

## pwm_brokerage_net  (Private Wealth Management: Brokerage Income (Rs Cr), net; Rs Mn)

| Quarter | Value | Unit | source_ref | Vintages compared (n) | Max abs diff | Max rel diff | Flag |
|---|---|---|---|---|---|---|---|
| Q1FY24 | 501.04496 | Rs Mn | `q4fy26-data-book.xlsx#PWM!E8` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 10 | 1.996% | RESTATED >0.5%: 511.04496 @ Q1FY25; 501.04496 @ Q4FY25 |
| Q2FY24 | 676.54828 | Rs Mn | `q4fy26-data-book.xlsx#PWM!F8` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q3FY24 | 630.33408 | Rs Mn | `q4fy26-data-book.xlsx#PWM!G8` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q4FY24 | 734.41825 | Rs Mn | `q4fy26-data-book.xlsx#PWM!H8` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |

## capmkt_net_brokerage_allied  (Capital Market: Net Brokerage & other allied income (Rs Cr); institutional; Rs Mn)

| Quarter | Value | Unit | source_ref | Vintages compared (n) | Max abs diff | Max rel diff | Flag |
|---|---|---|---|---|---|---|---|
| Q1FY24 | 730.4015 | Rs Mn | `q4fy26-data-book.xlsx#Capital Market!E7` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q2FY24 | 763.52142 | Rs Mn | `q4fy26-data-book.xlsx#Capital Market!F7` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q3FY24 | 498.55744 | Rs Mn | `q4fy26-data-book.xlsx#Capital Market!G7` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |
| Q4FY24 | 649.24365 | Rs Mn | `q4fy26-data-book.xlsx#Capital Market!H7` | Q1FY25..Q4FY26 (8); book has no FY24 columns: Q1FY27..Q2FY27 | 0 | 0.000% |  |

## Restatements above 0.5% (summary)

| Metric | Quarter | Staged (Q4FY26 book, output unit) | Max rel diff | Vintage values (output unit, change points) |
|---|---|---|---|---|
| adto_cash | Q1FY24 | 16024.478 | 47.00% | 23556.384 @ Q1FY25; 15279.054 @ Q2FY25; 16024.478 @ Q2FY26 |
| adto_cash | Q2FY24 | 24088.209 | 39.24% | 33539.411 @ Q1FY25; 23430.831 @ Q2FY25; 24088.209 @ Q2FY26 |
| adto_cash | Q3FY24 | 27969.824 | 17.08% | 32746.328 @ Q1FY25; 27203.661 @ Q2FY25; 27969.824 @ Q2FY26 |
| adto_cash | Q4FY24 | 40597.634 | 27.27% | 51666.921 @ Q1FY25; 39777.113 @ Q2FY25; 40597.634 @ Q2FY26 |
| adto_notional_fo | Q1FY24 | 3965624.5 | 3.40% | 4100492 @ Q1FY25; 3965624.5 @ Q2FY25 |
| adto_notional_fo | Q2FY24 | 5123913.4 | 1.85% | 5218823.5 @ Q1FY25; 5123913.4 @ Q2FY25 |
| adto_notional_fo | Q3FY24 | 5546141 | 1.15% | 5610130.2 @ Q1FY25; 5546141 @ Q2FY25 |
| adto_notional_fo | Q4FY24 | 6982181.2 | 1.75% | 7104246.6 @ Q1FY25; 6982181.2 @ Q2FY25 |
| adto_premium_fo | Q1FY24 | 36673.058 | 4.17% | 35145.376 @ Q1FY25; 36320 @ Q1FY26; 36673.058 @ Q2FY26 |
| adto_premium_fo | Q2FY24 | 44373.577 | 1.39% | 43758.889 @ Q1FY25; 44373.577 @ Q2FY26 |
| adto_premium_fo | Q3FY24 | 48580.035 | 2.34% | 47443.613 @ Q1FY25; 48580.035 @ Q2FY26 |
| adto_premium_fo | Q4FY24 | 66816.341 | 1.15% | 66048.525 @ Q1FY25; 66816.341 @ Q2FY26 |
| gross_brokerage_total | Q1FY24 | 4062.9309 | 6.76% | 3788.2979 @ Q2FY25; 4062.9309 @ Q2FY26 |
| gross_brokerage_total | Q2FY24 | 5075.8353 | 0.62% | 5044.5749 @ Q2FY25; 5075.8353 @ Q2FY26 |
| gross_brokerage_total | Q3FY24 | 4959.7317 | 1.92% | 4864.7189 @ Q2FY25; 4959.7317 @ Q2FY26 |
| gross_brokerage_total | Q4FY24 | 6319.877 | 1.46% | 6227.7564 @ Q2FY25; 6319.877 @ Q2FY26 |
| gross_brokerage_cash | Q1FY24 | 1509.6156 | 17.97% | 1238.412 @ Q2FY25; 1509.6156 @ Q2FY26 |
| gross_brokerage_cash | Q2FY24 | 1978.7272 | 1.31% | 1952.7441 @ Q2FY25; 1978.7272 @ Q2FY26 |
| gross_brokerage_cash | Q3FY24 | 2210.6881 | 3.91% | 2124.2578 @ Q2FY25; 2210.6881 @ Q2FY26 |
| gross_brokerage_cash | Q4FY24 | 3169.4787 | 2.68% | 3084.4373 @ Q2FY25; 3169.4787 @ Q2FY26 |
| net_brokerage_total | Q1FY24 | 2431.2338 | 24.74% | 1829.7552 @ Q1FY25; 2160.2151 @ Q2FY25; 2431.2338 @ Q2FY26 |
| net_brokerage_total | Q2FY24 | 2875.1105 | 12.51% | 2515.4027 @ Q1FY25; 2849.3639 @ Q2FY25; 2875.1105 @ Q2FY26 |
| net_brokerage_total | Q3FY24 | 2788.7811 | 12.86% | 2430.2303 @ Q1FY25; 2698.0057 @ Q2FY25; 2788.7811 @ Q2FY26 |
| net_brokerage_total | Q4FY24 | 3491.2976 | 11.11% | 3103.4369 @ Q1FY25; 3411.6282 @ Q2FY25; 3491.2976 @ Q2FY26 |
| net_brokerage_cash | Q1FY24 | 904.15964 | 29.61% | 636.418 @ Q1FY25; 904.15964 @ Q2FY26 |
| net_brokerage_cash | Q2FY24 | 1018.2643 | 2.02% | 997.64673 @ Q1FY25; 1018.2643 @ Q2FY26 |
| net_brokerage_cash | Q3FY24 | 1181.8841 | 6.97% | 1099.5397 @ Q1FY25; 1181.8841 @ Q2FY26 |
| net_brokerage_cash | Q4FY24 | 1664.1245 | 4.37% | 1591.3721 @ Q1FY25; 1664.1245 @ Q2FY26 |
| net_brokerage_fo | Q3FY24 | 1339.1216 | 0.63% | 1330.6906 @ Q1FY25; 1339.1216 @ Q2FY26 |
| share_cash | Q1FY24 | 0.064659927 | 10.70% | 0.057740476 @ Q1FY25; 0.061797036 @ Q2FY25; 0.061797034 @ Q1FY26; 0.064659927 @ Q2FY26 |
| share_cash | Q2FY24 | 0.072539401 | 12.86% | 0.063211251 @ Q1FY25; 0.070559767 @ Q2FY25; 0.072539401 @ Q2FY26 |
| share_cash | Q3FY24 | 0.076870966 | 17.77% | 0.063211251 @ Q1FY25; 0.07476528 @ Q2FY25; 0.076870966 @ Q2FY26 |
| share_cash | Q4FY24 | 0.08323862 | 2.02% | 0.081556279 @ Q1FY25; 0.08155628 @ Q2FY25; 0.08323862 @ Q2FY26 |
| share_fo_premium | Q1FY24 | 0.073190892 | 4.16% | 0.070147944 @ Q1FY25; 0.072486209 @ Q2FY25; 0.073190892 @ Q2FY26 |
| share_fo_premium | Q2FY24 | 0.076256995 | 1.39% | 0.075200631 @ Q1FY25; 0.076256995 @ Q2FY26 |
| share_fo_premium | Q3FY24 | 0.083104633 | 2.34% | 0.081158297 @ Q1FY25; 0.083104633 @ Q2FY26 |
| share_fo_premium | Q4FY24 | 0.087714069 | 1.15% | 0.086705088 @ Q1FY25; 0.087714069 @ Q2FY26 |
| wm_nii | Q1FY24 | 1279.3035 | 0.78% | 1269.3035 @ Q1FY25; 1279.3035 @ Q4FY25 |
| wm_nii | Q4FY24 | 1854.4285 | 1.08% | 1834.4285 @ Q1FY25; 1854.4285 @ Q4FY25 |
| wm_distribution | Q1FY24 | 277.2308 | 13.69% | 315.19097 @ Q1FY25; 277.2308 @ Q4FY26 |
| wm_distribution | Q2FY24 | 364.99699 | 13.25% | 413.37127 @ Q1FY25; 364.99699 @ Q4FY26 |
| wm_distribution | Q3FY24 | 507.53629 | 8.68% | 551.61461 @ Q1FY25; 507.53629 @ Q4FY26 |
| wm_distribution | Q4FY24 | 710.34949 | 9.46% | 777.52508 @ Q1FY25; 710.34949 @ Q4FY26 |
| pwm_brokerage_net | Q1FY24 | 501.04496 | 2.00% | 511.04496 @ Q1FY25; 501.04496 @ Q4FY25 |

## Identity checks (gross/net total = cash + F&O + commodity + currency, Rs Cr as printed)

Staged vintage (Q4FY26 book): 

| Kind | Quarter | Total | Sum of 4 | Diff | Diff % | Result |
|---|---|---|---|---|---|---|
| gross | Q1FY24 | 406.29309 | 406.29309 | 1.14e-13 | 0.0000% | pass |
| gross | Q2FY24 | 507.58353 | 507.58353 | 0.00e+00 | 0.0000% | pass |
| gross | Q3FY24 | 495.97317 | 495.97317 | 0.00e+00 | 0.0000% | pass |
| gross | Q4FY24 | 631.9877 | 631.9877 | 0.00e+00 | 0.0000% | pass |
| net | Q1FY24 | 243.12338 | 243.12338 | 0.00e+00 | 0.0000% | pass |
| net | Q2FY24 | 287.51105 | 287.51105 | 0.00e+00 | 0.0000% | pass |
| net | Q3FY24 | 278.87811 | 278.87811 | -5.68e-14 | -0.0000% | pass |
| net | Q4FY24 | 349.12976 | 349.12976 | 0.00e+00 | 0.0000% | pass |

All vintages (rows testable only where all four segment rows exist):

| Kind | Quarter | Vintage | Total | Sum of 4 | Diff % | Result |
|---|---|---|---|---|---|---|
| gross | Q1FY24 | Q2FY25 | 378.82979 | 378.82979 | 0.0000% | pass |
| gross | Q1FY24 | Q3FY25 | 378.82979 | 378.82979 | 0.0000% | pass |
| gross | Q1FY24 | Q4FY25 | 378.82979 | 378.82979 | 0.0000% | pass |
| gross | Q1FY24 | Q1FY26 | 378.82979 | 378.82979 | 0.0000% | pass |
| gross | Q1FY24 | Q2FY26 | 406.29309 | 406.29309 | 0.0000% | pass |
| gross | Q1FY24 | Q3FY26 | 406.29309 | 406.29309 | 0.0000% | pass |
| gross | Q1FY24 | Q4FY26 | 406.29309 | 406.29309 | 0.0000% | pass |
| gross | Q2FY24 | Q2FY25 | 504.45749 | 504.45749 | 0.0000% | pass |
| gross | Q2FY24 | Q3FY25 | 504.45749 | 504.45749 | 0.0000% | pass |
| gross | Q2FY24 | Q4FY25 | 504.45749 | 504.45749 | 0.0000% | pass |
| gross | Q2FY24 | Q1FY26 | 504.45749 | 504.45749 | 0.0000% | pass |
| gross | Q2FY24 | Q2FY26 | 507.58353 | 507.58353 | 0.0000% | pass |
| gross | Q2FY24 | Q3FY26 | 507.58353 | 507.58353 | 0.0000% | pass |
| gross | Q2FY24 | Q4FY26 | 507.58353 | 507.58353 | 0.0000% | pass |
| gross | Q3FY24 | Q2FY25 | 486.47189 | 486.47189 | 0.0000% | pass |
| gross | Q3FY24 | Q3FY25 | 486.47189 | 486.47189 | 0.0000% | pass |
| gross | Q3FY24 | Q4FY25 | 486.47189 | 486.47189 | 0.0000% | pass |
| gross | Q3FY24 | Q1FY26 | 486.47189 | 486.47189 | 0.0000% | pass |
| gross | Q3FY24 | Q2FY26 | 495.97317 | 495.97317 | 0.0000% | pass |
| gross | Q3FY24 | Q3FY26 | 495.97317 | 495.97317 | 0.0000% | pass |
| gross | Q3FY24 | Q4FY26 | 495.97317 | 495.97317 | 0.0000% | pass |
| gross | Q4FY24 | Q2FY25 | 622.77564 | 622.77564 | 0.0000% | pass |
| gross | Q4FY24 | Q3FY25 | 622.77564 | 622.77564 | 0.0000% | pass |
| gross | Q4FY24 | Q4FY25 | 622.77564 | 622.77564 | 0.0000% | pass |
| gross | Q4FY24 | Q1FY26 | 622.77564 | 622.77564 | 0.0000% | pass |
| gross | Q4FY24 | Q2FY26 | 631.9877 | 631.9877 | 0.0000% | pass |
| gross | Q4FY24 | Q3FY26 | 631.9877 | 631.9877 | 0.0000% | pass |
| gross | Q4FY24 | Q4FY26 | 631.9877 | 631.9877 | 0.0000% | pass |
| net | Q1FY24 | Q1FY25 | 182.97552 | n/a | n/a | not testable: parts 2 of 4 rows absent; partial sum 182.976 (0.000% of total unexplained) |
| net | Q1FY24 | Q2FY25 | 216.02151 | 216.02151 | 0.0000% | pass |
| net | Q1FY24 | Q3FY25 | 216.02151 | 216.02151 | 0.0000% | pass |
| net | Q1FY24 | Q4FY25 | 216.02151 | 216.02151 | 0.0000% | pass |
| net | Q1FY24 | Q1FY26 | 216.02151 | 216.02151 | 0.0000% | pass |
| net | Q1FY24 | Q2FY26 | 243.12338 | 243.12338 | 0.0000% | pass |
| net | Q1FY24 | Q3FY26 | 243.12338 | 243.12338 | 0.0000% | pass |
| net | Q1FY24 | Q4FY26 | 243.12338 | 243.12338 | 0.0000% | pass |
| net | Q2FY24 | Q1FY25 | 251.54027 | n/a | n/a | not testable: parts 2 of 4 rows absent; partial sum 251.540 (0.000% of total unexplained) |
| net | Q2FY24 | Q2FY25 | 284.93639 | 284.93639 | 0.0000% | pass |
| net | Q2FY24 | Q3FY25 | 284.93639 | 284.93639 | 0.0000% | pass |
| net | Q2FY24 | Q4FY25 | 284.93639 | 284.93639 | 0.0000% | pass |
| net | Q2FY24 | Q1FY26 | 284.93639 | 284.93639 | 0.0000% | pass |
| net | Q2FY24 | Q2FY26 | 287.51105 | 287.51105 | 0.0000% | pass |
| net | Q2FY24 | Q3FY26 | 287.51105 | 287.51105 | 0.0000% | pass |
| net | Q2FY24 | Q4FY26 | 287.51105 | 287.51105 | 0.0000% | pass |
| net | Q3FY24 | Q1FY25 | 243.02303 | n/a | n/a | not testable: parts 2 of 4 rows absent; partial sum 243.023 (0.000% of total unexplained) |
| net | Q3FY24 | Q2FY25 | 269.80057 | 269.80057 | 0.0000% | pass |
| net | Q3FY24 | Q3FY25 | 269.80057 | 269.80057 | 0.0000% | pass |
| net | Q3FY24 | Q4FY25 | 269.80057 | 269.80057 | 0.0000% | pass |
| net | Q3FY24 | Q1FY26 | 269.80057 | 269.80057 | 0.0000% | pass |
| net | Q3FY24 | Q2FY26 | 278.87811 | 278.87811 | -0.0000% | pass |
| net | Q3FY24 | Q3FY26 | 278.87811 | 278.87811 | -0.0000% | pass |
| net | Q3FY24 | Q4FY26 | 278.87811 | 278.87811 | -0.0000% | pass |
| net | Q4FY24 | Q1FY25 | 310.34369 | n/a | n/a | not testable: parts 2 of 4 rows absent; partial sum 310.344 (0.000% of total unexplained) |
| net | Q4FY24 | Q2FY25 | 341.16282 | 341.16282 | 0.0000% | pass |
| net | Q4FY24 | Q3FY25 | 341.16282 | 341.16282 | 0.0000% | pass |
| net | Q4FY24 | Q4FY25 | 341.16282 | 341.16282 | 0.0000% | pass |
| net | Q4FY24 | Q1FY26 | 341.16282 | 341.16282 | 0.0000% | pass |
| net | Q4FY24 | Q2FY26 | 349.12976 | 349.12976 | 0.0000% | pass |
| net | Q4FY24 | Q3FY26 | 349.12976 | 349.12976 | 0.0000% | pass |
| net | Q4FY24 | Q4FY26 | 349.12976 | 349.12976 | 0.0000% | pass |

Breaks above 0.1%: 0.


## Missing (metric x quarter)

None: all 29 metrics x 4 quarters (116) are present in the Q4 FY26 book with numeric cells. Checks of the three rows disclosure_map.md says start late:

- Commodity market share (Consol "Commodity" under "Market share"): the map says the first book is Q4 FY26 with history from Q1FY24. Confirmed: Q4FY26 book carries Q1FY24-Q4FY24 = 6.33%, 6.53%, 7.94%, 9.07%; absent in all older books (single vintage, no cross-check possible).
- Overall market share (Cash + F&O + Commodity): same, Q4FY26 book only, Q1FY24-Q4FY24 = 6.78%, 7.14%, 8.02%, 8.75%. Absent in Q1FY25-Q3FY26 books. Single vintage.
- MTF book: Q4FY26 book only (Q1FY24-Q4FY24 = 146.7, 197.0, 282.7, 349.4 Rs Cr, i.e. 1,467 / 1,970 / 2,827 / 3,494 Rs Mn). Single vintage.
- Gross brokerage (total and four segments): not in the Q1 FY25 book; present from the Q2 FY25 book (7 vintages for FY24).
- ADTO commodity / currency and net brokerage commodity / currency: not in the Q1 FY25 book (7 vintages).
- F&O notional market share (Consol row "F&O" under "Market share") is not a staged metric (same as the existing 290 facts).

## Ambiguities worth a reviewer look

- Net brokerage total in the Q1FY25 book excludes commodity and currency (equals cash + F&O only; those rows do not exist there). The Q2FY25+ books restate it to include them (e.g. Q1FY24 182.98 -> 216.02 Rs Cr). That is a definitional change, not a correction; the staged value is the all-segment total.
- Currency in FY24 looks of a different order from FY25+: ADTO currency Q1FY24-Q4FY24 = 9,332 / 9,895 / 6,740 / 6,052 Rs Cr per day and gross currency brokerage 26.1 / 26.8 / 17.2 / 18.9 Rs Cr, against Q1FY25 391 Rs Cr/day and 1.5 Rs Cr (existing facts). Identical in all 7 vintages carrying it, and gross total = sum of four holds, so staged as printed; the step down between Q4FY24 and Q1FY25 may be a basis change or a real collapse and is not explained in any book.
- Capital Market row label: "Net Brokerage" in Q1FY25-Q3FY26 books, "Net Brokerage & other allied income" in the Q4FY26 book (the staged vintage); FY24 values are identical, treated as one series and the label noted in each fact.
- Cash ADTO and cash market share are restated twice (Q2FY25 book, then Q2FY26 book). The Q1FY25 book values (e.g. cash ADTO Q1FY24 2,355.6 vs 1,602.4 Rs Cr/day) are first-reported numbers.
- WM distribution income FY24 was lowered in the Q4FY26 book (e.g. Q1FY24 31.52 -> 27.72 Rs Cr), the staged vintage; WM NII and PWM brokerage have 1.0 Rs Cr single-quarter corrections (Q1FY24 NII 126.93 -> 127.93 in Q4FY25 book; Q4FY24 NII 183.44 -> 185.44; PWM Q1FY24 51.10 -> 50.10).
