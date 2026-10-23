# 2.4 Back-sourcing the Q3 / Q4 FY25 revenue-mix differences (23 Oct 2026)

The four Excel values that differ from the Q2 FY27 deck (slide 30, PDF p.31) are each the product of two
whole-number percentages on the deck published that quarter: segment share of gross broking revenue
× gross broking share of gross revenue. They are rounding differences, not restatements.

| Excel cell | Seed fact | Excel | Deck of the quarter | Product | Q2 FY27 deck (reviewed fact) |
|---|---|---|---|---|---|
| Working sheet F15 (Q3 FY25 F&O) | 28 | 0.5265 | Q3 FY25 deck p.25: F&O 81% of broking, broking 65% | 0.5265 | 0.525 (606) |
| Working sheet F17 (Q3 FY25 commodity) | 42 | 0.0455 | same slide: commodity 7% of broking | 0.0455 | 0.044 (608) |
| Working sheet G15 (Q4 FY25 F&O) | 29 | 0.462 | Q4 FY25 deck p.24: F&O 77% of broking, broking 60% | 0.462 | 0.463 (612) |
| Working sheet G17 (Q4 FY25 commodity) | 43 | 0.054 | same slide: commodity 9% of broking | 0.054 | 0.052 (614) |

Cash ties the same way and matches the Q2 FY27 deck: F16 = 12% × 65% = 0.078 (607), G16 = 14% × 60% = 0.084 (613).

Decks (slide "Segmental Revenue Break Up", panels "Gross Revenue Mix" and "Gross Broking Revenue Mix"):
- Q3 FY25: https://nsearchives.nseindia.com/corporate/ANGEL8896_13012025191051_Investor_Presentation_Q3_FY2025-2026_F.pdf (PDF p.25)
- Q4 FY25: https://nsearchives.nseindia.com/corporate/ANGEL8896_16042025211536_16042025CoveringInvestorsPresentation.pdf (PDF p.24)

Live mode already uses the one-decimal deck values (switch b), so nothing changes in the engine.
