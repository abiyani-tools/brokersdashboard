# MOSL switch m-g (FY24 quarters Q2-Q4 FY24): independent recompute

Script: `out/checks/mosl_switch_g_check.py` (stdlib json/math/csv/re; openpyxl only for the data-book re-reads; run from the worktree root, `--md` prints the tables below). Items: `out/checks/mosl_switch_g_items.csv`. Inputs: `docs/MOSL_ADR_Methodology.md` s3-s4, `docs/MOSL_LIVE_SPEC.md` (m-g), `out/bridges/mosl_g.md` (claims), `snapshot/mosl_facts_fy24_candidates_2026-11-03.json`, `snapshot/mosl_facts_reviewed_2026-11-02.json`, `snapshot/mosl_lake_2026-11-03.json` (F&O and cash keys), `snapshot/db_snapshot_2026-11-03.json` (calendar, MCX), and the Q4 FY26 data book. Nothing under `src/engine/` or `src/live/` was read; no database was touched. The data book is not in the worktree; the script finds it in the main repo's `data/raw/disclosures/mosl/` (it walks up from the worktree).

**Result: 478 of 478 items with a bridge value or an identity to test agree, plus 152 new-cell values recomputed (the bridge prints no value for them, see section 2).** Agreement rule: relative diff <= 1e-6, or the bridge's print precision where it prints 4-6 digits (largest relative diff of a printed value 4e-5, which is a 4-digit print: F&O Q3 FY24 rate 0.9419).

| Item kind | n | agree |
|---|---:|---:|
| data-book cell re-reads (all 116 FY24 facts) | 116 | 116 |
| segment table (share, key, rate, net/gross, gross, net revenue, days, ADR; 9 rows x 8) | 72 | 72 |
| ties (sum of daily net = net-brokerage fact; sum of daily gross = gross fact; Broking net = cash+F&O+comm net) | 21 | 21 |
| bridge arithmetic lines (K = share x key, H, contracts, take, ADR numerators, ADTO) | 24 | 24 |
| Broking table | 12 | 12 |
| parameters that moved (Q2-Q4 FY24 rows) | 48 | 48 |
| inputs replaced by facts (live value, fact ids, workbook dash) | 90 | 90 |
| June 2023 / Q1 FY24 / FY 2024 / MTF absence, first revenue day | 9 | 9 |
| daily rows added, days after, first day | 12 | 12 |
| FY25+ ADR table: after value from FY25+ facts alone, before = after | 50 | 50 |
| new-cell set (38 rows x 4 panels = 152) and panel tie | 4 + 19 | 23 |
| new-cell values recomputed | 152 | n/a |

## 1. Segment x quarter (Rs crore)

Rules rebuilt from the data: F&O key = NSE index-option + BSE contracts (lake), cash key = NSE + BSE turnover (lake), commodity key = MCX contracts. Gross = fact / 10, net/gross = net fact / gross fact. Rate = gross / (share x key): F&O Rs per contract (Cr / Cr contracts), commodities gross x 10 / (share x Mn contracts); cash is reported as J = gross / ADTO, as the bridge does. Daily gross = gross x key_d / key_q (the share cancels; cash goes through H and J and gives the same), daily net = ratio x daily gross. ADR = mean of daily net over days that are not special sessions (Muhurat 12 Nov 2023, 20 Jan and 2 Mar 2024). All 72 values agree. Examples:

| Segment | Quarter | Share | Key | Rate | Net/gross | Gross | Net (every day) | Days | ADR |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| F&O | Q2 FY24 | 0.076257 | 2,502.80 | 1.35788 | 0.587624 | 259.1596 | 152.2885 | 63 | 2.417278 |
| F&O | Q3 FY24 | 0.083105 | 2,959.11 | 0.94186 | 0.578157 | 231.6191 | 133.9122 | 60 | 2.228444 |
| F&O | Q4 FY24 | 0.087714 | 3,486.35 | 0.87019 | 0.570816 | 266.1069 | 151.8982 | 60 | 2.507006 |
| Cash | Q2 FY24 | 0.072539 | 5,254,831.41 | J 0.082145 | 0.514606 | 197.8727 | 101.8264 | 63 | 1.616292 |
| Cash | Q3 FY24 | 0.076871 | 5,311,212.39 | J 0.079038 | 0.534623 | 221.0688 | 118.1884 | 60 | 1.963964 |
| Cash | Q4 FY24 | 0.083239 | 7,415,163.67 | J 0.078071 | 0.525047 | 316.9479 | 166.4125 | 60 | 2.736416 |
| Commodities | Q2 FY24 | 0.065298 | 117.46 | 30.9396 | 0.623593 | 23.7305 | 14.7982 | 62 | 0.238680 |
| Commodities | Q3 FY24 | 0.079353 | 130.51 | 25.2313 | 0.606744 | 26.1304 | 15.8545 | 60 | 0.264241 |
| Commodities | Q4 FY24 | 0.090716 | 150.59 | 21.9487 | 0.615156 | 29.9835 | 18.4445 | 61 | 0.302369 |

Net revenue ties to the net-brokerage fact for all 9 segment-quarters to 1e-12 (and the gross likewise). Broking ADR = F&O + Cash + Commodities: 4.272250 / 4.456649 / 5.545791 (agree).

Absences (all agree): no revenue row before 2023-07-03 in any segment (the 21 calendar days of June 2023 get none); first revenue day 2023-07-03 for F&O, cash and commodities; my model has no Q1 FY24 and no FY 2024; the industry MTF book starts 2024-10-01, so Consolidated FY24 has no MTF base. Daily rows added: F&O 186 (63+61+62), cash 186, commodities 183 (62+60+61), as the bridge says.

### Two things in the bridge text worth fixing (numbers are right)

1. **Commodities Q4 FY24 has 61 days because MCX 22 Jan 2024 is in the MCX series but not in `sb_calendar`** (NSE/BSE were shut; MCX traded the evening session, 1.55 Mn contracts, net Rs 0.19 Cr). The model counts it, which matches the bridge (key 150.5882 Mn, ADR 0.302369 = 18.4445 / 61). If the day were dropped the ADR would be 0.307409 (60 days, +1.7%). The Q4 total still ties to the reported net, so it is the right treatment for the key; just note that the calendar row is missing.
2. **Cash arithmetic lines say "quarter key = X Rs Cr over 60 days" for Q3 and Q4 FY24.** X includes the special-session days (Q3: 61 days with Muhurat; Q4: 62 days with the two Saturday sessions). 60 is the ADR day count (specials out). The averaging inside H and the J / D split use all days (61, 62): only that choice makes the daily rows sum to the reported gross, and H agrees to 4 digits with it. Wording only.

## 2. FY25+ cells

**0 FY25+ values change.** I rebuilt FY25+ from the FY25+ facts only (FY24 facts and days are not used by any FY25+ quarter) and compared with the bridge's 30-line ADR table (FY 2027, Q2 and Q1 FY27, Oct 2026, FY 2026; Broking, F&O, Cash, Commodities, and Consolidated = my Broking + the bridge's MTF, which g does not touch). All 50 agree, and before = after in all 30 rows. The open quarter follows m-e (last reported quarter's net per unit of key).

**152 cells.** From the rules (a FY25 comparison needs its base to be a complete FY24 period; June 2023 is incomplete, so Apr-Jun YoY and Q1 FY25 YoY / FY 2025 YoY stay out) I derived the list of rows: 30 month rows + 8 quarter rows = 38 rows x 4 panels (Broking, F&O, Cash, Commodities) = 152. My set equals the bridge's table exactly (no row on one side only). Definitions: YoY / QoQ / MoM = current / base - 1; "vs 6M" = current / (net revenue over the 6 calendar months ending at the month / trading days, special sessions out, per segment; Broking = sum of the three) - 1 (LIVE_SPEC E3 decision Q2). The bridge prints no value for these cells, so there is nothing to agree with; all 152 recomputed values are numbers and Broking = F&O + Cash + Commodities on every "value" row (19 rows, 1e-12). Values (ADR in Rs Cr/day for "value" rows, ratios for comparisons):

| Period | Row | Field | Broking | F&O | Cash | Commodities |
|---|---|---|---:|---:|---:|---:|
| FY 2025 April | Avg of last 6 months | value | 5.133430 | 2.379314 | 2.468844 | 0.285272 |
| FY 2025 April | FY 2024 March | value | 5.322453 | 2.509866 | 2.515883 | 0.296704 |
| FY 2025 April | FY 2025 April | comparison | -11.05% | -14.54% | -7.86% | -8.61% |
| FY 2025 April | FY 2025 April / vs 6M | comparison | -7.78% | -9.85% | -6.11% | -4.95% |
| FY 2025 August | Avg of last 6 months | value | 5.590146 | 2.446819 | 2.831871 | 0.311456 |
| FY 2025 August | FY 2024 August | value | 4.343368 | 2.476973 | 1.616989 | 0.249406 |
| FY 2025 August | FY 2025 August / YoY | comparison | +33.00% | -0.29% | +82.43% | +43.09% |
| FY 2025 August | FY 2025 August / vs 6M | comparison | +3.34% | +0.94% | +4.17% | +14.59% |
| FY 2025 December | FY 2024 December | value | 5.297887 | 2.473907 | 2.529544 | 0.294436 |
| FY 2025 December | FY 2025 December / YoY | comparison | -24.92% | -38.53% | -18.54% | +34.51% |
| FY 2025 February | FY 2024 February | value | 5.676691 | 2.524986 | 2.862698 | 0.289007 |
| FY 2025 February | FY 2025 February / YoY | comparison | -43.44% | -44.09% | -51.07% | +37.89% |
| FY 2025 January | FY 2024 January | value | 5.605495 | 2.486574 | 2.799161 | 0.319760 |
| FY 2025 January | FY 2025 January / YoY | comparison | -30.03% | -18.52% | -46.89% | +28.13% |
| FY 2025 July | Avg of last 6 months | value | 5.573342 | 2.456380 | 2.816730 | 0.300232 |
| FY 2025 July | FY 2024 July | value | 3.711838 | 2.003194 | 1.498610 | 0.210035 |
| FY 2025 July | FY 2025 July / YoY | comparison | +56.31% | +12.46% | +117.54% | +37.66% |
| FY 2025 July | FY 2025 July / vs 6M | comparison | +4.10% | -8.29% | +15.74% | -3.69% |
| FY 2025 June | Avg of last 6 months | value | 5.537026 | 2.498985 | 2.732374 | 0.305666 |
| FY 2025 June | FY 2025 June / vs 6M | comparison | +15.89% | +8.84% | +23.06% | +9.43% |
| FY 2025 March | FY 2024 March | value | 5.322453 | 2.509866 | 2.515883 | 0.296704 |
| FY 2025 March | FY 2025 March / YoY | comparison | -31.93% | -31.22% | -39.49% | +26.10% |
| FY 2025 May | Avg of last 6 months | value | 5.359372 | 2.460164 | 2.599902 | 0.299306 |
| FY 2025 May | FY 2025 May / vs 6M | comparison | +2.27% | +6.23% | -2.10% | +7.69% |
| FY 2025 November | FY 2024 November | value | 4.131604 | 2.135917 | 1.756205 | 0.239482 |
| FY 2025 November | FY 2025 November / YoY | comparison | +20.05% | +15.29% | +18.67% | +72.60% |
| FY 2025 October | FY 2024 October | value | 3.940456 | 2.075508 | 1.606142 | 0.258805 |
| FY 2025 October | FY 2025 October / YoY | comparison | +31.27% | +28.33% | +32.41% | +47.78% |
| FY 2025 September | FY 2024 September | value | 4.783415 | 2.786401 | 1.739094 | 0.257920 |
| FY 2025 September | FY 2025 September / YoY | comparison | +21.64% | -8.85% | +63.22% | +70.73% |
| Q1 FY 2025 | Q1 FY 2025 | comparison | -0.32% | -0.64% | -0.30% | +2.11% |
| Q1 FY 2025 | Q4 FY 2024 | value | 5.545791 | 2.507006 | 2.736416 | 0.302369 |
| Q2 FY 2025 | Q2 FY 2024 | value | 4.272250 | 2.417278 | 1.616292 | 0.238680 |
| Q2 FY 2025 | Q2 FY 2025 / YoY | comparison | +35.72% | +0.04% | +86.85% | +50.78% |
| Q3 FY 2025 | Q3 FY 2024 | value | 4.456649 | 2.228444 | 1.963964 | 0.264241 |
| Q3 FY 2025 | Q3 FY 2025 / YoY | comparison | +5.44% | -0.79% | +6.49% | +50.16% |
| Q4 FY 2025 | Q4 FY 2024 | value | 5.545791 | 2.507006 | 2.736416 | 0.302369 |
| Q4 FY 2025 | Q4 FY 2025 / YoY | comparison | -34.96% | -30.54% | -46.24% | +30.49% |

Reading: FY25 months look weak against FY24 in F&O and cash from Dec 2024 to Mar 2025 (Broking -25% to -43% YoY) against FY24 months that were strong (cause not examined here); commodities are up 26-73% YoY throughout. These are the model's values, not reviewed numbers.

## 3. Sanity of the F&O rate (Rs per contract 1.36 / 0.94 / 0.87 vs 0.74 in Q1 FY25)

The inputs explain it; the rate is a ratio of a flat numerator to a fast-growing denominator.

| Quarter | Gross Rs Cr | Premium share | Key, Cr contracts | NSE index options | BSE | BSE % of key | Rate | Rate, NSE-only key |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Q2 FY24 | 259.16 | 0.0763 | 2,502.8 | 2,373.8 | 129.1 | 5.2% | 1.3579 | 1.4317 |
| Q3 FY24 | 231.62 | 0.0831 | 2,959.1 | 2,547.3 | 411.8 | 13.9% | 0.9419 | 1.0941 |
| Q4 FY24 | 266.11 | 0.0877 | 3,486.3 | 2,900.5 | 585.8 | 16.8% | 0.8702 | 1.0459 |
| Q1 FY25 | 262.71 | 0.0966 | 3,682.6 | 2,911.8 | 770.8 | 20.9% | 0.7382 | 0.9336 |
| Q2 FY25 | 268.80 | 0.0912 | 4,462.4 | 3,485.9 | 976.4 | 21.9% | 0.6606 | 0.8457 |

Gross brokerage is flat (259 to 263 Rs Cr) while the key rose 47% (2,503 to 3,683 Cr contracts) and the premium share rose 27% (0.0763 to 0.0966). Rate = gross / (share x key), so it falls by 46% (log 0.609). Split of that log fall, Q2 FY24 to Q1 FY25: BSE contracts entering the key 30% (BSE went from 5.2% to 20.9% of the key), NSE index-option contracts 34% (+23%), the rising share 39%, gross -2%. So the BSE contract share explains about a third; it is not the whole story: with an NSE-only key the rate still falls 35% (1.43 to 0.93). (Q1 FY25 here is 0.7382, with 31 May 2024 included; the m-a figure 0.7498 left that day out.) Caveat on the method: the share is a premium-turnover share applied to a contract count, so when contracts per rupee of premium rise (BSE Sensex weekly options, cheaper far-from-the-money contracts) the implied Rs per contract falls even if MOSL's business did not change. Per-day gross brokerage (4.11 / 3.80 / 4.29 / 4.31 Rs Cr) is steady, and the daily-revenue shape is unaffected because each quarter calibrates to its own reported gross. The rate is not comparable across quarters as a "price per contract"; Q4 FY25 shows the regime break (key 1,330 Cr contracts, BSE 39%, rate 1.68).

## Disagreements

None. Two wording notes in section 1.
