# Bridge — MOSL switch (m-g)

FY24 quarters: F&O, cash and commodities calibrate Q2 - Q4 FY24 from reviewed data-book facts; MTF still starts Q3 FY25.

Before: switches abcdef · after: abcdefg · series read to 2026-10-21

Consolidated ADR, Rs crore per trading day (net brokerage + MTF NII):

| Period | Before | After | Δ % |
|---|---:|---:|---:|
| FY 2027 | 8.718295 | 8.718295 | +0.0000% |
| Q2 FY 2027 | 8.967060 | 8.967060 | +0.0000% |
| Q1 FY 2027 | 8.197926 | 8.197926 | +0.0000% |
| FY 2027 October | 9.876513 | 9.876513 | +0.0000% |
| FY 2026 | 7.662290 | 7.662290 | +0.0000% |

Inputs replaced by reviewed data-book facts: 30 change the workbook's value, 0 already equal it (source confirmed, not listed). Each fact is converted from its unit (Rs Mn, Rs Mn per day) to the input's (Rs Cr, Rs Cr per day); net / gross = net brokerage / gross brokerage of the same quarter.

| Input | Period | Workbook | Live | Facts | Basis |
|---|---|---:|---:|---|---|
| adto_cash_mosl | Q2 FY 2024 | — | 2,408.82 | 20292 | 24,088.2093 Rs Mn/day / 10 |
| adto_cash_mosl | Q3 FY 2024 | — | 2,796.98 | 20293 | 27,969.8239 Rs Mn/day / 10 |
| adto_cash_mosl | Q4 FY 2024 | — | 4,059.76 | 20294 | 40,597.6338 Rs Mn/day / 10 |
| gross_cash_cr | Q2 FY 2024 | — | 197.87 | 20316 | 1,978.7272 Rs Mn / 10 |
| gross_cash_cr | Q3 FY 2024 | — | 221.07 | 20317 | 2,210.6881 Rs Mn / 10 |
| gross_cash_cr | Q4 FY 2024 | — | 316.95 | 20318 | 3,169.4787 Rs Mn / 10 |
| gross_comm_cr | Q2 FY 2024 | — | 23.7305 | 20324 | 237.3047 Rs Mn / 10 |
| gross_comm_cr | Q3 FY 2024 | — | 26.1304 | 20325 | 261.3039 Rs Mn / 10 |
| gross_comm_cr | Q4 FY 2024 | — | 29.9835 | 20326 | 299.8352 Rs Mn / 10 |
| gross_fo_cr | Q2 FY 2024 | — | 259.16 | 20320 | 2,591.5957 Rs Mn / 10 |
| gross_fo_cr | Q3 FY 2024 | — | 231.62 | 20321 | 2,316.1910 Rs Mn / 10 |
| gross_fo_cr | Q4 FY 2024 | — | 266.11 | 20322 | 2,661.0694 Rs Mn / 10 |
| net_gross_cash | Q2 FY 2024 | — | 0.5146 | 20336, 20316 | 1,018.26 / 1,978.73 Rs Mn |
| net_gross_cash | Q3 FY 2024 | — | 0.5346 | 20337, 20317 | 1,181.88 / 2,210.69 Rs Mn |
| net_gross_cash | Q4 FY 2024 | — | 0.5250 | 20338, 20318 | 1,664.12 / 3,169.48 Rs Mn |
| net_gross_comm | Q2 FY 2024 | — | 0.6236 | 20344, 20324 | 147.98 / 237.30 Rs Mn |
| net_gross_comm | Q3 FY 2024 | — | 0.6067 | 20345, 20325 | 158.54 / 261.30 Rs Mn |
| net_gross_comm | Q4 FY 2024 | — | 0.6152 | 20346, 20326 | 184.45 / 299.84 Rs Mn |
| net_gross_fo | Q2 FY 2024 | — | 0.5876 | 20340, 20320 | 1,522.89 / 2,591.60 Rs Mn |
| net_gross_fo | Q3 FY 2024 | — | 0.5782 | 20341, 20321 | 1,339.12 / 2,316.19 Rs Mn |
| net_gross_fo | Q4 FY 2024 | — | 0.5708 | 20342, 20322 | 1,518.98 / 2,661.07 Rs Mn |
| share_cash | Q2 FY 2024 | — | 0.0725 | 20356 | 0.0725 fraction |
| share_cash | Q3 FY 2024 | — | 0.0769 | 20357 | 0.0769 fraction |
| share_cash | Q4 FY 2024 | — | 0.0832 | 20358 | 0.0832 fraction |
| share_comm | Q2 FY 2024 | — | 0.0653 | 20364 | 0.0653 fraction |
| share_comm | Q3 FY 2024 | — | 0.0794 | 20365 | 0.0794 fraction |
| share_comm | Q4 FY 2024 | — | 0.0907 | 20366 | 0.0907 fraction |
| share_fo | Q2 FY 2024 | — | 0.0763 | 20360 | 0.0763 fraction |
| share_fo | Q3 FY 2024 | — | 0.0831 | 20361 | 0.0831 fraction |
| share_fo | Q4 FY 2024 | — | 0.0877 | 20362 | 0.0877 fraction |

## m-g: FY24 quarters

MOSL's quarters now start at Q2 FY24 (Jul 2023). F&O, cash and commodities calibrate Q2 - Q4 FY24 exactly as m-a does for FY25+: rate = reported gross brokerage / (share x the quarter's key), revenue = rate x share x the day's key x net / gross. The facts are the 116 FY24 facts (AB approved them with the switch on 3 Nov 2026); the FY24 gross and net brokerage Rs Mn are divided by 10 to Rs Cr. Market data from 1 June 2023 (db_snapshot_2026-11-03.json, mosl_lake_2026-11-03.json; read only from ExchangesDash's public JSON). No revenue row exists before Q2 FY24 (the 21 calendar days from 2023-06-01 to 2023-06-30 have none). First revenue day per segment: F&O 2023-07-03; Cash 2023-07-03; Commodities 2023-07-03. MTF is unchanged: NII still starts Q3 FY25 (no industry book before Oct 2024), so Consolidated FY24 stays insufficient.

Per segment and quarter (Rs crore; ADR = net revenue / trading days with a row, special sessions left out by m-d: net revenue below counts every day, ADR does not):

| Segment | Quarter | Share | Quarter key | Rate | Net / gross | Gross Rs Cr | Net revenue Rs Cr | Days | ADR |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| F&O | Q2 FY 2024 | 0.076257 | 2,502.80 (Cr contracts (NSE index options + BSE)) | 1.3579 | 0.587624 | 259.1596 | 152.2885 | 63 | 2.417278 |
| F&O | Q3 FY 2024 | 0.083105 | 2,959.11 (Cr contracts (NSE index options + BSE)) | 0.9419 | 0.578157 | 231.6191 | 133.9122 | 60 | 2.228444 |
| F&O | Q4 FY 2024 | 0.087714 | 3,486.35 (Cr contracts (NSE index options + BSE)) | 0.8702 | 0.570816 | 266.1069 | 151.8982 | 60 | 2.507006 |
| Cash | Q2 FY 2024 | 0.072539 | 5,254,831.41 (Rs Cr turnover (NSE + BSE)) | 0.082145 | 0.514606 | 197.8727 | 101.8264 | 63 | 1.616292 |
| Cash | Q3 FY 2024 | 0.076871 | 5,311,212.39 (Rs Cr turnover (NSE + BSE)) | 0.079038 | 0.534623 | 221.0688 | 118.1884 | 60 | 1.963964 |
| Cash | Q4 FY 2024 | 0.083239 | 7,415,163.67 (Rs Cr turnover (NSE + BSE)) | 0.078071 | 0.525047 | 316.9479 | 166.4125 | 60 | 2.736416 |
| Commodities | Q2 FY 2024 | 0.065298 | 117.46 (Mn contracts (MCX)) | 30.9396 | 0.623593 | 23.7305 | 14.7982 | 62 | 0.238680 |
| Commodities | Q3 FY 2024 | 0.079353 | 130.51 (Mn contracts (MCX)) | 25.2313 | 0.606744 | 26.1304 | 15.8545 | 60 | 0.264241 |
| Commodities | Q4 FY 2024 | 0.090716 | 150.59 (Mn contracts (MCX)) | 21.9487 | 0.615156 | 29.9835 | 18.4445 | 61 | 0.302369 |

Rate: F&O and commodities in Rs per contract (gross / (share x key)); cash is gross per Rs of the data book's ADTO (J). Arithmetic:

- F&O Q2 FY 2024: K = share x key = 0.076257 x 2,502.8038 = 190.8563 Cr contracts; rate = gross / K = 259.1596 / 190.8563 = 1.3579 Rs per contract; net = 0.587624 x 259.1596 = 152.2885 Rs Cr; ADR = 152.2885 / 63 days = 2.417278
- F&O Q3 FY 2024: K = share x key = 0.083105 x 2,959.1130 = 245.9160 Cr contracts; rate = gross / K = 231.6191 / 245.9160 = 0.9419 Rs per contract; net = 0.578157 x 231.6191 = 133.9122 Rs Cr; ADR = 133.7066 / 60 days = 2.228444
- F&O Q4 FY 2024: K = share x key = 0.087714 x 3,486.3494 = 305.8019 Cr contracts; rate = gross / K = 266.1069 / 305.8019 = 0.8702 Rs per contract; net = 0.570816 x 266.1069 = 151.8982 Rs Cr; ADR = 150.4204 / 60 days = 2.507006
- Cash Q2 FY 2024: gross per Rs of reported ADTO J = gross / ADTO = 197.8727 / 2,408.8209 = 0.082145; day gross = share x (key_d / H) x (J x ADTO / days) with H = share x avg key / ADTO = 2.5118; quarter key = 5,254,831.41 Rs Cr over 63 days; net = 0.514606 x 197.8727 = 101.8264; ADR = 101.8264 / 63 days = 1.616292
- Cash Q3 FY 2024: gross per Rs of reported ADTO J = gross / ADTO = 221.0688 / 2,796.9824 = 0.079038; day gross = share x (key_d / H) x (J x ADTO / days) with H = share x avg key / ADTO = 2.3930; quarter key = 5,311,212.39 Rs Cr over 60 days; net = 0.534623 x 221.0688 = 118.1884; ADR = 117.8378 / 60 days = 1.963964
- Cash Q4 FY 2024: gross per Rs of reported ADTO J = gross / ADTO = 316.9479 / 4,059.7634 = 0.078071; day gross = share x (key_d / H) x (J x ADTO / days) with H = share x avg key / ADTO = 2.4522; quarter key = 7,415,163.67 Rs Cr over 60 days; net = 0.525047 x 316.9479 = 166.4125; ADR = 164.1849 / 60 days = 2.736416
- Commodities Q2 FY 2024: take = gross x 10 / (share x contracts) = 23.7305 x 10 / (0.065298 x 117.4599) = 30.9396 Rs per contract; net = 0.623593 x 23.7305 = 14.7982; ADR = 14.7982 / 62 days = 0.238680
- Commodities Q3 FY 2024: take = gross x 10 / (share x contracts) = 26.1304 x 10 / (0.079353 x 130.5092) = 25.2313 Rs per contract; net = 0.606744 x 26.1304 = 15.8545; ADR = 15.8545 / 60 days = 0.264241
- Commodities Q4 FY 2024: take = gross x 10 / (share x contracts) = 29.9835 x 10 / (0.090716 x 150.5882) = 21.9487 Rs per contract; net = 0.615156 x 29.9835 = 18.4445; ADR = 18.4445 / 61 days = 0.302369

Broking ADR (F&O + Cash + Commodities, Rs crore per trading day):

| Quarter | F&O | Cash | Commodities | Broking |
|---|---:|---:|---:|---:|
| Q2 FY 2024 | 2.417278 | 1.616292 | 0.238680 | 4.272250 |
| Q3 FY 2024 | 2.228444 | 1.963964 | 0.264241 | 4.456649 |
| Q4 FY 2024 | 2.507006 | 2.736416 | 0.302369 | 5.545791 |

Still "insufficient data" after m-g (live rows):

- Broking FY 2024: insufficient data: F&O FY 2024: calendar starts 2023-06-01, after FY 2024 began
- Cash FY 2024: insufficient data: Cash FY 2024: calendar starts 2023-06-01, after FY 2024 began
- Commodities FY 2024: insufficient data: Commodities FY 2024: calendar starts 2023-06-01, after FY 2024 began
- Consolidated FY 2024: insufficient data: F&O FY 2024: calendar starts 2023-06-01, after FY 2024 began
- F&O FY 2024: insufficient data: F&O FY 2024: calendar starts 2023-06-01, after FY 2024 began
- MTF FY 2024: insufficient data: MTF FY 2024: calendar starts 2023-06-01, after FY 2024 began
- Consolidated Q2 FY 2024: insufficient data: MTF Q2 FY 2024: MTF series starts 2024-10-01, after Q2 FY 2024 began
- MTF Q2 FY 2024: insufficient data: MTF Q2 FY 2024: MTF series starts 2024-10-01, after Q2 FY 2024 began
- Consolidated Q3 FY 2024: insufficient data: MTF Q3 FY 2024: MTF series starts 2024-10-01, after Q3 FY 2024 began
- MTF Q3 FY 2024: insufficient data: MTF Q3 FY 2024: MTF series starts 2024-10-01, after Q3 FY 2024 began
- Consolidated Q4 FY 2024: insufficient data: MTF Q4 FY 2024: MTF series starts 2024-10-01, after Q4 FY 2024 began
- MTF Q4 FY 2024: insufficient data: MTF Q4 FY 2024: MTF series starts 2024-10-01, after Q4 FY 2024 began
- Q1 FY 2024 (the base of Q2 FY24's QoQ): 6 panels, e.g. insufficient data: F&O Q1 FY 2024: calendar starts 2023-06-01, after Q1 FY 2024 began

FY25+ cells (every FY / quarter / month / week row of FY 2025 onward, all panels): 152 change from "insufficient data" to a value, 1414 are unchanged, 0 change a value that was already there (asserted 0).

| Period | Row | Field | Panels (insufficient data -> value) |
|---|---|---|---|
| FY 2025 April | Avg of last 6 months | value | Broking, Cash, Commodities, F&O |
| FY 2025 April | FY 2024 March | value | Broking, Cash, Commodities, F&O |
| FY 2025 April | FY 2025 April | comparison | Broking, Cash, Commodities, F&O |
| FY 2025 April | FY 2025 April / vs 6M | comparison | Broking, Cash, Commodities, F&O |
| FY 2025 August | Avg of last 6 months | value | Broking, Cash, Commodities, F&O |
| FY 2025 August | FY 2024 August | value | Broking, Cash, Commodities, F&O |
| FY 2025 August | FY 2025 August / YoY | comparison | Broking, Cash, Commodities, F&O |
| FY 2025 August | FY 2025 August / vs 6M | comparison | Broking, Cash, Commodities, F&O |
| FY 2025 December | FY 2024 December | value | Broking, Cash, Commodities, F&O |
| FY 2025 December | FY 2025 December / YoY | comparison | Broking, Cash, Commodities, F&O |
| FY 2025 February | FY 2024 February | value | Broking, Cash, Commodities, F&O |
| FY 2025 February | FY 2025 February / YoY | comparison | Broking, Cash, Commodities, F&O |
| FY 2025 January | FY 2024 January | value | Broking, Cash, Commodities, F&O |
| FY 2025 January | FY 2025 January / YoY | comparison | Broking, Cash, Commodities, F&O |
| FY 2025 July | Avg of last 6 months | value | Broking, Cash, Commodities, F&O |
| FY 2025 July | FY 2024 July | value | Broking, Cash, Commodities, F&O |
| FY 2025 July | FY 2025 July / YoY | comparison | Broking, Cash, Commodities, F&O |
| FY 2025 July | FY 2025 July / vs 6M | comparison | Broking, Cash, Commodities, F&O |
| FY 2025 June | Avg of last 6 months | value | Broking, Cash, Commodities, F&O |
| FY 2025 June | FY 2025 June / vs 6M | comparison | Broking, Cash, Commodities, F&O |
| FY 2025 March | FY 2024 March | value | Broking, Cash, Commodities, F&O |
| FY 2025 March | FY 2025 March / YoY | comparison | Broking, Cash, Commodities, F&O |
| FY 2025 May | Avg of last 6 months | value | Broking, Cash, Commodities, F&O |
| FY 2025 May | FY 2025 May / vs 6M | comparison | Broking, Cash, Commodities, F&O |
| FY 2025 November | FY 2024 November | value | Broking, Cash, Commodities, F&O |
| FY 2025 November | FY 2025 November / YoY | comparison | Broking, Cash, Commodities, F&O |
| FY 2025 October | FY 2024 October | value | Broking, Cash, Commodities, F&O |
| FY 2025 October | FY 2025 October / YoY | comparison | Broking, Cash, Commodities, F&O |
| FY 2025 September | FY 2024 September | value | Broking, Cash, Commodities, F&O |
| FY 2025 September | FY 2025 September / YoY | comparison | Broking, Cash, Commodities, F&O |
| Q1 FY 2025 | Q1 FY 2025 | comparison | Broking, Cash, Commodities, F&O |
| Q1 FY 2025 | Q4 FY 2024 | value | Broking, Cash, Commodities, F&O |
| Q2 FY 2025 | Q2 FY 2024 | value | Broking, Cash, Commodities, F&O |
| Q2 FY 2025 | Q2 FY 2025 / YoY | comparison | Broking, Cash, Commodities, F&O |
| Q3 FY 2025 | Q3 FY 2024 | value | Broking, Cash, Commodities, F&O |
| Q3 FY 2025 | Q3 FY 2025 / YoY | comparison | Broking, Cash, Commodities, F&O |
| Q4 FY 2025 | Q4 FY 2024 | value | Broking, Cash, Commodities, F&O |
| Q4 FY 2025 | Q4 FY 2025 / YoY | comparison | Broking, Cash, Commodities, F&O |

A "value" row is the FY24 base of a FY25 comparison (e.g. the "Q2 FY 2024" row inside Q2 FY25); a "comparison" row is the YoY, QoQ, MoM or vs-6M figure itself.

Data effect, not the switch: a-f on these fixtures (market data from 1 Jun 2023, MCX days flagged, owner corrections to two 2025 NSE cash turnover days) against a-f on the 23 Oct / 2 Nov fixtures:

| Period | Panel | a-f, old fixtures | a-f, new fixtures |
|---|---|---:|---:|
| FY 2026 | Consolidated | 7.662290 | 7.662290 |
| FY 2026 | Broking | 4.348883 | 4.348883 |
| FY 2026 | Cash | 1.888062 | 1.888062 |

Periods flagged insufficient in the live rows after this switch: 48 (before: 18).

- Consolidated FY 2024: insufficient data: F&O FY 2024: calendar starts 2023-06-01, after FY 2024 began
- Consolidated FY 2025: insufficient data: MTF FY 2025: MTF series starts 2024-10-01, after FY 2025 began
- Consolidated Q2 FY 2024: insufficient data: MTF Q2 FY 2024: MTF series starts 2024-10-01, after Q2 FY 2024 began
- Consolidated Q3 FY 2024: insufficient data: MTF Q3 FY 2024: MTF series starts 2024-10-01, after Q3 FY 2024 began
- Consolidated Q4 FY 2024: insufficient data: MTF Q4 FY 2024: MTF series starts 2024-10-01, after Q4 FY 2024 began
- Consolidated Q1 FY 2025: insufficient data: MTF Q1 FY 2025: MTF series starts 2024-10-01, after Q1 FY 2025 began
- Consolidated Q2 FY 2025: insufficient data: MTF Q2 FY 2025: MTF series starts 2024-10-01, after Q2 FY 2025 began
- Consolidated FY 2024 July: insufficient data: MTF FY 2024 July: MTF series starts 2024-10-01, after FY 2024 July began

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

Parameters that moved:

| Segment | Quantity | Quarter | Before | After | Δ % |
|---|---|---|---:|---:|---:|
| Cash | 'delivery ratio' H | Q2 FY 2024 | — | 2.5118 |  |
| Cash | 'delivery ratio' H | Q3 FY 2024 | — | 2.3930 |  |
| Cash | 'delivery ratio' H | Q4 FY 2024 | — | 2.4522 |  |
| Cash | gross per Rs of reported ADTO J | Q2 FY 2024 | — | 0.0821 |  |
| Cash | gross per Rs of reported ADTO J | Q3 FY 2024 | — | 0.0790 |  |
| Cash | gross per Rs of reported ADTO J | Q4 FY 2024 | — | 0.0781 |  |
| Cash | model gross brokerage Rs Cr | Q2 FY 2024 | — | 197.87 |  |
| Cash | model gross brokerage Rs Cr | Q3 FY 2024 | — | 221.07 |  |
| Cash | model gross brokerage Rs Cr | Q4 FY 2024 | — | 316.95 |  |
| Cash | model net brokerage Rs Cr | Q2 FY 2024 | — | 101.83 |  |
| Cash | model net brokerage Rs Cr | Q3 FY 2024 | — | 118.19 |  |
| Cash | model net brokerage Rs Cr | Q4 FY 2024 | — | 166.41 |  |
| Cash | net / gross | Q2 FY 2024 | — | 0.5146 |  |
| Cash | net / gross | Q3 FY 2024 | — | 0.5346 |  |
| Cash | net / gross | Q4 FY 2024 | — | 0.5250 |  |
| Cash | share (cancels) | Q2 FY 2024 | — | 0.0725 |  |
| Cash | share (cancels) | Q3 FY 2024 | — | 0.0769 |  |
| Cash | share (cancels) | Q4 FY 2024 | — | 0.0832 |  |
| Commodities | gross Rs per MOSL contract | Q2 FY 2024 | — | 30.9396 |  |
| Commodities | gross Rs per MOSL contract | Q3 FY 2024 | — | 25.2313 |  |
| Commodities | gross Rs per MOSL contract | Q4 FY 2024 | — | 21.9487 |  |
| Commodities | model gross brokerage Rs Cr | Q2 FY 2024 | — | 23.7305 |  |
| Commodities | model gross brokerage Rs Cr | Q3 FY 2024 | — | 26.1304 |  |
| Commodities | model gross brokerage Rs Cr | Q4 FY 2024 | — | 29.9835 |  |
| Commodities | model net brokerage Rs Cr | Q2 FY 2024 | — | 14.7982 |  |
| Commodities | model net brokerage Rs Cr | Q3 FY 2024 | — | 15.8545 |  |
| Commodities | model net brokerage Rs Cr | Q4 FY 2024 | — | 18.4445 |  |
| Commodities | net / gross | Q2 FY 2024 | — | 0.6236 |  |
| Commodities | net / gross | Q3 FY 2024 | — | 0.6067 |  |
| Commodities | net / gross | Q4 FY 2024 | — | 0.6152 |  |
| Commodities | share | Q2 FY 2024 | — | 0.0653 |  |
| Commodities | share | Q3 FY 2024 | — | 0.0794 |  |
| Commodities | share | Q4 FY 2024 | — | 0.0907 |  |
| F&O | gross Rs per contract | Q2 FY 2024 | — | 1.3579 |  |
| F&O | gross Rs per contract | Q3 FY 2024 | — | 0.9419 |  |
| F&O | gross Rs per contract | Q4 FY 2024 | — | 0.8702 |  |
| F&O | model gross brokerage Rs Cr | Q2 FY 2024 | — | 259.16 |  |
| F&O | model gross brokerage Rs Cr | Q3 FY 2024 | — | 231.62 |  |
| F&O | model gross brokerage Rs Cr | Q4 FY 2024 | — | 266.11 |  |
| F&O | model net brokerage Rs Cr | Q2 FY 2024 | — | 152.29 |  |
| F&O | model net brokerage Rs Cr | Q3 FY 2024 | — | 133.91 |  |
| F&O | model net brokerage Rs Cr | Q4 FY 2024 | — | 151.90 |  |
| F&O | net / gross | Q2 FY 2024 | — | 0.5876 |  |
| F&O | net / gross | Q3 FY 2024 | — | 0.5782 |  |
| F&O | net / gross | Q4 FY 2024 | — | 0.5708 |  |
| F&O | premium share (cancels) | Q2 FY 2024 | — | 0.0763 |  |
| F&O | premium share (cancels) | Q3 FY 2024 | — | 0.0831 |  |
| F&O | premium share (cancels) | Q4 FY 2024 | — | 0.0877 |  |

Daily revenue rows that changed:

| Segment | Days before | Days after | Changed | First | Last | Ratio min | Ratio max | Added | Dropped |
|---|---:|---:|---:|---|---|---:|---:|---:|---:|
| F&O | 634 | 820 | 0 |  |  |  |  | 186 | 0 |
| Cash | 634 | 820 | 0 |  |  |  |  | 186 | 0 |
| Commodities | 660 | 843 | 0 |  |  |  |  | 183 | 0 |
| MTF | 507 | 507 | 0 |  |  |  |  | 0 | 0 |
