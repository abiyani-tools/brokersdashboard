# Fresh workbook audit (unaudited areas)

Workbook: `20260714_brokers dashboard v2.xlsx`, read-only copy. Cached values read with openpyxl and formulas read separately.
Every impact below was recomputed in Python from the cached cell values. The base case reproduces the sheet exactly: `PAT!E16` = 208.368.
Not repeated: Angel/Groww ADR feeder sheets, `SUMMARY - Groww`, `Groww - ADR Model`, and the issue lists in the two methodology docs.
No DB writes, no commits, no workbook edits.

Audit chain for Angel One: ADR (`SUMMARY - Brokers`) -> `PAT` -> `PAT predictor Q1FY27` / `Q2FY27` -> `Angel One - ADR model` / `Angel One - Final`.
The dashboard's Angel PAT Predictor reproduces `PAT!E5:E19`, so H1 to H4 flow straight into it.

Counts: High 10, Med 15, Low 12.

---

## HIGH

### H1. `PAT!D4` reads the FY2027 row but is labelled Fy'26 (Angel block); Groww `J4` has the same fault
- Cells and formulas:
  - `PAT!D4 ='SUMMARY - Brokers'!C63`, `PAT!J4 ='SUMMARY - Brokers'!M63`.
  - Headers: `PAT!D3` = Fy'26, `PAT!J3` = Fy'26.
- Evidence:
  - `SUMMARY - Brokers!B63` = "FY 2027", `B64` = "FY 2026". The same holds for `L63` / `L64`.
  - `C63` = 12.887 is the FY27 YTD ADR. The FY26 ADR is `C64` = 12.367.
  - The CDSL block is right: `W63` = "FY 2026", so `P4 = X63` is fine. The row 63 offset was copied across blocks.
  - Check against actuals: `PAT predictor Q2FY27!G4` FY26 broking revenue = 3,098. 12.367 x 247 = 3,055 (-1.4%). 12.887 x 249 = 3,209 (+3.6%).
- Impact, Angel (recomputed):
  - `D9` FY26 PAT estimate: 900.6 -> 877.4 (-2.6%).
  - `D12` EPS: 9.90 -> 9.64. `D13` trailing PE: 28.2x -> 28.9x.
  - `F9` FY27 PAT growth: 10.4% -> 13.3%. `F4` revenue/day growth: -10.5% -> -6.7%.
  - `D23` variance vs actual 915: +1.6% -> +4.3%.
  - The FY27 target (`E16` = 208.37) is unaffected.
- Impact, Groww (recomputed):
  - `J13 = J14/J12` (trailing PE) feeds `K13 = J13`, then `K14 = K13*K12`, then `K16`.
  - With `M64` (FY26 12.055): `J9` 2,010.8 -> 1,528.8, `J13` 55.7x -> 73.3x, `K16` 162.04 -> 213.14 (+31.5%).
  - Caveat: `M64` is itself distorted by the known zero-filled Q1 FY26 (Groww doc #1). This is not a clean correction. The point is that the Groww target is driven by a mislabelled row.

### H2. `PAT!E7` and `PAT!E10` read the stale Q1FY27 predictor, not Q2FY27
- Cells: `PAT!E7 ='PAT predictor Q1FY27'!J8+J10+J12`, `PAT!E10 ='PAT predictor Q1FY27'!J16`.
- Evidence:
  - The Q1FY27 predictor still projects Q1 FY27 (`H3` = "Q1 FY27 E") although Q1 actuals exist.
  - `PAT predictor Q2FY27` is the live roll. Its FY27E "other" revenue is `J8+J10+J12` = 2,353.0 vs 2,266.3. Its PAT margin `J16` = 18.18% vs 19.35%.
- Impact (recomputed): `E9` FY27 PAT 994.4 -> 949.8 (-4.5%). `E16` target 208.37 -> 199.02 (-4.5%).

### H3. `PAT!D7` and `PAT!E7` omit depository income, but the margin is on total revenue including depository
- Evidence:
  - `D7 = G8+G10+G12` (distribution + MTF + other interest). Depository `G6` = 191.4 (FY26) and `J6` = 258.1 (FY27E) are left out.
  - `D10 = 'PAT predictor Q1FY27'!G16 = G15/G14`, where `G14` includes depository.
  - `PAT!D8` = 5,035 vs predictor `G14` = 5,116.
- Impact (recomputed):
  - FY27 base including depository: PAT 994.4 -> 1,044.4 (+5.0%). Target 208.37 -> 218.83.
  - H2 and H3 together (Q2FY27 predictor plus depository): PAT 985.9 (-0.9%), target 206.58. The two errors partly offset, so the shown 208.37 is close by luck.

### H4. Q2 FY27 trading days typed as 66; the quarter had 65
- Cells and formulas:
  - `PAT predictor Q2FY27!D25` = 22 (typed). `D27` = 66.
  - `F30:L30 = F27*($D$27/$E$27)` scales a completed quarter up by 66/65.
  - `I93` = 66.
  - `Angel One - Final!D11` = 66, `D12` = 65. `D33 = D14*(D11-D12)` adds a phantom day of ADR.
- Evidence:
  - `backtesting F&O` has 21 September 2026 rows (14 Sep absent; `PAT predictor Q2FY27!E25` = 21).
  - Q2 FY27 = 23 + 21 + 21 = 65 rows.
  - `Angel One - Final!D35` = 797.53 vs `D32` accrued 785.53 for the full quarter.
- Impact (recomputed):
  - Q2 broking revenue `I30` 797.6 -> 785.5 (+1.54% overstated).
  - Q2 PAT `I53` 287.4 -> about 280.4 (-2.4%).
  - Because `J42 = K42 = I42`, three quarters carry the error. FY27 PAT `L53` 1,055.1 -> about 1,034.2 (-1.98%).

### H5. `Angel One Charts` stops at row 495 (25 Sep 2026); the data runs to 21 Oct; the valuation sheets read different rows
- Evidence:
  - `Angel One Charts!B495` = 2026-09-25 (`=B494+1`). `backtesting F&O` runs to row 761 (21 Oct).
  - Rows read for the "latest" ADR windows:
    - `Angel One - ADR model` and `(A+B)`: row 495.
    - `Angel One - ADR model(Treasury)`: row 494.
    - `Angel One - Final!D57:D59` (annual predictor): row 494. `D14:D16` (quarterly predictor): row 480 (3 Sep).
  - 45-day broking ADR by row: 12.003 (row 480), 11.874 (row 494), 11.595 (row 495). Same label, three values.
  - `Angel One Charts!V494:V495` (MTF ADR) = `V493`: frozen, although `MTF data (2)` has 4.7646 and 4.7601 for 24 and 25 Sep.
- Impact (recomputed):
  - Final annual: using row 495 instead of 494 changes `E111` PAT by -21.3 (-2.1%), and the target with it.
  - ADR model `C14` (20-day, to 25 Sep) = 14.184. On `SUMMARY - Brokers` 20-day figures to 21 Oct (broking 11.364 + net MTF 2.133 = 13.497), `C22` PAT 865.2 -> 737.9 (-14.7%) and `D28` 200.4 -> 170.9.
  - Caveat: the 21 Oct numbers include the known frozen-BSE problem (Angel doc #1). The staleness effect is real; its size is overlapped.

### H6. `Angel One - Final` FY26 "Historical performance" PAT is 1,066, not 915; the revenue-mix block uses a fixed denominator
- Cells:
  - `Final!J410` = 1,066.2 (`J408 - J409`). `J402` total opex 3,603.5. `J392` revenue 5,151.4.
  - `Final!F417:J422 = F386/$E$392` (anchored to FY21 revenue).
- Evidence:
  - `PAT predictor Q2FY27!G15` = 915 (114 + 212 + 269 + 320). The model's own computed `G72` = 916.7.
  - Predictor FY26 costs `G67` = 3,880.3 vs `Final!J402` + D&A `J407` = 3,728.5. About 152 of costs are missing.
  - `Final!K410` shows YoY -9.2%; on 915 vs `I410` 1,174.5 it is -22.1%.
  - Mix: `J417` MTF = 64.8% (should be 841.8 / 5,151.4 = 16.3%). `J419` treasury = 62.4% (should be 15.7%). The column J mix (J416:J422) sums to 208%.
- Impact: display only (nothing downstream reads it), but the FY26 PAT, the margin and the YoY printed on the visible sheet are wrong by 16.5%, with similar errors in the mix.

### H7. `SUMMARY - Brokers` MOSL panel does not tie to `SUMMARY - Motilal Oswal`
- Evidence:
  - `SUMMARY - Brokers!AH63` (FY27 broking) = 3.599 vs `SUMMARY - Motilal Oswal!M7` = 1.805.
  - Q1 FY27: `Brokers!AH67` = 3.808 vs `MOSL!M12` = 4.521 vs reported 275 Cr / 60 days = 4.583 (`PAT predictor Q1FY27!N30:Q30`). That is -16.9% against reported.
  - Causes:
    1. The Brokers panel uses gross F&O (`backtesting F&O!AF`) and gross cash (`backtesting cash!AA`). The MOSL sheet uses net (`AG`, `AB`).
    2. The Brokers panel divides cash `AA` by 10. `AA` is already in Cr: `PAT predictor Q1FY27!O29` = 0.5418 x `O27` (no /10) = 121.9 vs reported cash 118.
    3. Commodities `Brokers!AH145` is typed 0.
  - In the MOSL sheet, `M64` (FY27 cash) = 0 because `backtesting cash!AB760` is `#N/A` (HLOOKUP past the table) and `IFERROR` turns it into 0. This is a silent zero.
  - The FY26 YoY on `MOSL!N7` (-58%) compares FY26 cash 1.88 with FY27 cash 0.
- Impact: MOSL ADR is wrong by about 17% in the hidden Brokers panel. The FY27 figure on its own sheet omits cash (about 0.24 net).

### H8. `SUMMARY - Brokers` Angel "Consolidated ADR" uses net MTF; `SUMMARY - Angel One` uses gross
- Cells:
  - `Brokers!C35 = AVERAGEIFS('MTF data (2)'!P...)` (net = 45% of gross).
  - `Angel One!C35 = AVERAGEIFS(...O...)` (gross).
  - `Brokers (A+B)!C35` uses O and ties to `Angel One`.
- Impact (read from the sheets): FY27 consolidated `C7` is 14.782 in `Brokers` vs 17.097 in `Angel One` (-13.5%). MTF is 1.894 vs 4.209. Same label, same period. This extends Angel doc #2 from the weekday tables to the whole hidden sheet.

### H9. `Angel One - Final` FY28 price double-discounts at 13.5% and ignores its own 18%
- Cells: `Final!D150:F150 =D148/(1+$I$118)` and `D151:F151 =D150/(1+$I$151)`. `I118` = 0.135, `I151` = 0.135. `I150` = 0.18, labelled "Discounting rate" next to row 150, and referenced by nothing.
- Impact (recomputed): `E151` 240.30 -> 231.14 (-3.8%) if `I150` is used in row 150.
- Related: the FY27 discount rate differs by sheet for the same stock.
  - `Final!E118` (13.5%) = 216.36.
  - `PAT!E16` (18%) = 208.37.
  - `ADR model!D28` (18%) = 200.42.
  - The headline "triangulated" `Final!E6` = 216.36.

### H10. `Angel One - ADR model` and `(A+B)`: FY28 growth is applied to a different base than FY27
- Evidence:
  - FY27 `C14 = E9` is the 20-day ADR (14.184). FY28 `C33 = (1+C32)*C8` uses the 45-day broking ADR and `D33 = (1+D32)*D8` the 45-day MTF ADR.
  - The resulting FY28 ADR is 17.160. That is +21.0% over FY27 `C14`, not the labelled +25% / +30%.
  - In `(A+B)`, `C33` uses `C9` (20-day).
- Impact (recomputed): growing off the 20-day base (12.0745 x 1.25 + 2.1098 x 1.30 = 17.836) lifts FY28 PAT 1,231.6 -> 1,356.8 (+10.2%) and the discounted FY28 price 261.7 -> 288.4.
- Confidence: moderate. If the 45-day base is deliberate, the label and the FY27 base should say so.

---

## MED

### M1. `Angel One - Final` MTF block: ranges end before the data and drop three days
- Cells:
  - `Final!D94 = SUMIFS('MTF data (2)'!O12:O498,...)` (to 18 Sep).
  - `D91 = COUNTIFS(B12:B501)` = 119.
  - `D87:D89` use `O457:O501`, `O482:O501`, `O497:O501` (to 23 Sep).
- Evidence:
  - `MTF data (2)` runs to row 518 (19 Oct) = 136 FY27 days.
  - Days 21, 22 and 23 Sep are neither accrued nor projected: 3 x 4.676 = 14.0 Cr (1.3% of `E102`).
- Impact (recomputed): accrued to 19 Oct (136 days) plus 20-day ADR (4.739) x 110 balance days gives 1,093.8 vs 1,071.5 (+2.08%). `E111` PAT +16.7 (+1.7%).

### M2. `Angel One - ADR model` `K6` / `I6`: MTF definition changes across columns
- Evidence:
  - `I6 = (C118-C119)/C114` is revenue minus the actual finance cost.
  - `J6:K6` use `'MTF data (2)'!P` (45% of gross).
  - The predictor's own `E120` (FY26, same finance-cost definition as `I6`) = 1.640 vs `K6` = 1.403.
- Impact: `K7` total ADR 13.866 -> 14.103 (+1.7%). The FY24-26 MTF CAGR `M6` shows 54.1% vs 66.6% on one definition.

### M3. `ADR model!K5` uses typed FY26 broking 3,078.4
- Evidence: `PAT predictor Q2FY27!E116` = 3,078.4 vs computed `G42` = 3,098.1. ADR 12.463 vs 12.543 (+0.64%).

### M4. EPS uses 91 shares; live count is 91.459 Cr
- Evidence:
  - `PAT!E12 = E9/91` and `PAT predictor C18:L18 /91`.
  - `Final!D3`, `ADR model!D2` = 91.45948.
- Impact: PAT-sheet target 208.37 -> 207.32 (-0.50%). The same stock has different EPS across sheets.

### M5. `Treasury!P16` = 59 days for Q1 FY27; the quarter had 60
- Evidence:
  - `backtesting F&O` and `Working sheet - Angel One!M4` = 60.
  - `Q16 = O16/P16` = 4.364, carried to Q2 by `Q17`, then to every Q2 date. 257.47 / 60 = 4.291 (+1.7% overstated).
  - The series ends 22 Sep (row 741).
- Impact (recomputed): in `Angel One - ADR model(Treasury)`, `C21` PAT 852.6 is overstated by 13.5 (+1.6%).

### M6. `PAT predictor Q2FY27` FY27 PAT row 53 vs row 72
- Evidence: `L72` = 1,067.45 (25% of annual PBT) vs `L53 = SUM(H53:K53)` = 1,055.08.
- The gap is 12.4 (+1.2%). `H71` is the actual Q1 tax 93.3 = 28.8% of PBT, while `I71:K71` use 25%. `PAT!E7/E10`, `Final` and the dashboard read `L53`.

### M7. Depository income assumed at 40% of cash broking (Q2 sheet) and 50% (Q1 sheet)
- Evidence:
  - `Q2FY27!G33` = 0.4. The Q1FY27 sheet `I32 = 50%*G29` gives 64.5 vs actual 43.0.
  - Q1 FY27 actual depository / cash = 43.011 / 129.033 = 33.3%.
  - `J44 = K44 = I44` carries the Q2 figure of 51.9 to Q3 and Q4.
- Impact (recomputed): at 33.3%, FY27 depository 198.7 -> 172.7 and FY27 PAT 1,055.1 -> about 1,035.6 (-1.8%).

### M8. Wrong day counts in `PAT predictor Q2FY27!C93:F93` and `C102`
- Evidence: Q3 FY26 = 61 (calendar 62), Q4 FY26 = 57 (calendar 60), Q4 FY25 = 61 (62). Calendar counts are from `backtesting F&O` dates.
- Impact: Q4 FY26 finance ADC 2.343 vs 2.226 (+5.3%); other ADC 15.68 vs 14.93. These feed `Angel One Charts!Z/AB`, the Angel ADP, and the ADP sheet.

### M9. `SUMMARY - Brokers ADP!W4` = `MAX('Angel One Charts'!B3:B480)`
- Evidence: `W4` = 3 Sep 2026. The Charts data runs to row 495 (25 Sep), so the range is truncated and 15 rows are missed. "Last complete month" shows Aug, so September is absent from the month panels and the 6-month average.
- Angel ADP is near zero or negative (`C8` -0.405, `H7` -2.96), so small shifts change its sign.

### M10. `Matrix!C39` mixes dates
- Evidence:
  - Groww 12,126,921 = Dec-25 (`Monthly Market share!Y5` 12.13M).
  - Total 44,814,230 = Feb-26 (`AA23`). Angel 6,758,500 = Feb-26 (`AA7`).
- Impact: Groww client share `D4` 27.06% vs 28.43% on Feb-26 (`AA27`), -4.8% relative.

### M11. `SUMMARY NSE Revenue` vs `NSE Segment Revenue`: same inputs, different discount
- Evidence: `SUMMARY NSE Revenue!T5` = 0 and `NSE Segment Revenue!S5` = 0.04 on identical PAT, EPS and P/E.
- Impact: base "Exp Dis Price Today" 1,968.8 vs 1,893.1 (-3.8%).
- Also in `SUMMARY NSE Revenue`:
  - FY26 revenue is 17,685 (`E5`) vs 18,434 (`O40`), +4.2%.
  - PAT is 10,828 (`E6`) / 11,892 (`E8`) vs 11,716 (`O41`).

### M12. External-link breakage: Options, Futures, Cash, NSE Segment Revenue, SUMMARY NSE Revenue
- Evidence:
  - Options, Futures, Cash, NSE Segment Revenue, SUMMARY NSE Revenue and `cash market` carry 57, 57, 31, 36, 15 and 66 external-link formulas respectively. Examples: `Options!AI11 ='[9]MCX Segment Revenue'!I17` -> `#REF!`; `NSE Segment Revenue!C5 ='[7]NSE BSE CDSL NSDL'!J41`.
  - Headline totals are errors:
    - `Options!C7`, `D7`, `H19:J19` -> `#VALUE!` / `#REF!`.
    - `SUMMARY NSE Revenue!D13:F24` -> `#VALUE!`.
    - `NSE Segment Revenue!N14` (cash block, labelled "ANGEL ONE - MCX") -> `#REF!`.
  - The data that does exist stops at Feb 2026.

### M13. `backtesting MCX` is dead
- Evidence: 1,524 `#REF!` cells and 382 external formulas (`=SUMIF([3]!Table5[Date],...)`).
- It still feeds `PE chart - Angel One!I499:I695` (163 `#REF!`) and `NSE Segment Revenue!N14`.

### M14. `MTF data!D64` / `L64` typed 64 days; Q2 FY27 has 65
- Evidence:
  - `E64`, `M64` scale the executed total down to 64 days, so `E66` / `M66` balance days = -2.48 / -4.50.
  - `M64` = 288.08 feeds `Angel One - Final!D43`, while the predictor's own `I10` = 275.98 and `M65` = 292.58.
- Impact: Q2 MTF revenue -1.5% (4.5 Cr); Q2 PAT effect -0.9 (0.3%). Two Q2 MTF estimates (288.08 vs 275.98) sit in the same sheet.

### M15. `PAT predictor Q2FY27!I77 = F53`
- Evidence: Q2's "previous quarter PAT" is Q4 FY26 (320), not Q1 FY27 (`H53` = 231). `H77 = F53` is right for Q1; `J77 = I53` for Q3.
- Impact (recomputed): the Q2 finance charge is understated by 1.5 and flows to Q3 and Q4. FY27 PAT overstated by about 3.4 (0.3%).

---

## LOW

- L1. `PAT!C4:C13` (Fy'25) is identical in the Angel, Groww and CDSL blocks: revenue/day 5.84, revenue 3,212, PAT 1,322, 40.7 shares, P/E 42. It is not Angel's: `Final!I392` revenue 5,247.7, `I410` PAT 1,174.5. It feeds `C10`, `C12`, `C14` only.
- L2. `PAT!P9`, `Q9 = P8*0.41` (CDSL) ignore `P10` / `Q10` = 0.486. PAT 466.8 -> 553.3 and trailing PE 53.5 -> 45.1. The target (1,331.9) is unchanged because the same margin applies to both years. `K9 = K8*0.43` is also typed (equals `K10`).
- L3. `PAT!P14` CDSL CMP typed 1,192 vs live `Q18` 1,188.5 (0.3%).
- L4. `PAT!J12` Groww shares 617 vs live 621.0962 (0.66%). Only the trailing PE moves; the target is unchanged.
- L5. `PAT!C5:E5` = 249 days for every year. FY26 had 247 (`ADR model!K3`) and FY27 about 246. At 247, `E9` -0.45% (at 246, -0.67%). Day bases also differ between sheets: `Final!D52` 247 vs `J126` 246, `PAT predictor Q2FY27!F114` 246, `ADR model!C15` 247.
- L6. `PAT predictor` `G45` / `G44` (Q2 / Q1 sheets) `= G44/$F$51` shows 13.16% depository share vs 3.74%. `G17` FY vs Q4 shows +185.9%.
- L7. `Angel One - Final!E19` ("June 2026") `=N23` (May); `F19` ("May") `=N23`. The June figure (`N24`) is 0.221 vs 0.224 shown.
- L8. Labels in `Final`: `C11` "Q1 2027 Trading Days" (it is Q2) and `E437` "Q1 2027 Est" for 30 Sep. Orphans: `ADR model (A+B)!J34:J36` and `Final!H65`.
- L9. `ADR model` Bear / Base / Bull: `C14 = E9`, `D14 = C14`, `E14 = D14`, so the scenarios differ only by P/E.
- L10. `Groww - comparables`: the Revolut text says GBP 790m profit on GBP 3.1bn (26%). The USD table row 22 shows revenue 3,100 and PAT 1,400 (45%). Currency and PBT/PAT are mixed. Other figures are uncited approximations; Schwab P/E is blank in the table.
- L11. `Monthly Market share`: the title says "Feb 2024 - Jan 2026" but columns run to Apr-26. The note says all but Mar-24 and Mar-25 are interpolated. Arithmetic checks out: broker sums equal the NSE totals and shares sum to 1.0 in all 27 months.
- L12. `SUMMARY - Brokers` panels were not rolled: MOSL `AG68` and `AG69` are both "Q4 FY 2026"; the Groww F&O panel `L95:L97` is stale (known). `PE chart - Angel One`: ADR / 45 DMA series end 26 May 2026 (row 243) and TTM PE ends 29 Jul 2026 (row 287). `cash market!D68:D72` is an `#N/A` scratch block on 29 Sep 2023.

## Checked, no issue found
- `SUMMARY - Brokers` Angel block `B63:J81` ties to `SUMMARY - Angel One!M8:U26` (0 mismatches over 171 cells).
- The Groww block ties to `SUMMARY - Groww` except hand-rolled labels and the values that follow them.
- `SUMMARY - Brokers (A+B)` ties to `SUMMARY - Angel One` (consolidated 17.0967).
- `Matrix` period alignment for orders, take rates and market shares: Q3 FY26 throughout.
- `Summary MTF` and `Sheet3` / `Sheet4` are empty.
