# Bridge — Groww switch (g-j)

Cash trades per order: an unreported quarter carries Groww's last reported quarter's value (the one its take rate was calibrated on), not Angel One's projection for the quarter.

Before: switches abcdefg · after: abcdefgj

Consolidated ADR, Rs crore per trading day (MTF gross):

| Period | Before | After | Δ % |
|---|---:|---:|---:|
| FY 2027 | 20.005274 | 20.005274 | +0.0000% |
| Q2 FY 2027 | 18.582719 | 18.582719 | +0.0000% |
| FY 2027 October | 23.298092 | 23.298092 | +0.0000% |
| FY 2026 | 16.075454 | 16.075454 | +0.0000% |

On the parity fixtures above g-j is a no-op: their Q2 FY27 trades per order is itself Angel's projection, equal to Q3's. Where it bites, the live dry run (the CLI's default snapshots, as of 2026-10-21; Angel One's live run, Q2 FY27 reported), switches abcdefg -> abcdefgj:

Cash trades per order: Q2 FY 2027 (reported) 6.852245; Q3 FY 2027 before 6.535245; Q3 FY 2027 after 6.852245

| Period | Panel | Before | After | Δ | Δ % |
|---|---|---:|---:|---:|---:|
| FY 2027 | Consolidated | 20.007085 | 19.986347 | -0.020738 | -0.1037% |
| FY 2027 | Cash | 4.197477 | 4.176738 | -0.020738 | -0.4941% |
| Q2 FY 2027 | Consolidated | 18.528112 | 18.528112 | +0.000000 | +0.0000% |
| Q2 FY 2027 | Cash | 4.123907 | 4.123907 | +0.000000 | +0.0000% |
| Q3 FY 2027 | Consolidated | 23.617623 | 23.397479 | -0.220144 | -0.9321% |
| Q3 FY 2027 | Cash | 4.758611 | 4.538468 | -0.220144 | -4.6262% |
| FY 2027 October | Consolidated | 23.617623 | 23.397479 | -0.220144 | -0.9321% |
| FY 2027 October | Cash | 4.758611 | 4.538468 | -0.220144 | -4.6262% |

The open quarter's cash moves by Q3-before / Q2 = -4.6262%; Consolidated moves by the same rupees; reported quarters do not move.

ADR, Rs crore per trading day (MTF gross):

| Period | Panel | Before | After | Δ | Δ % |
|---|---|---:|---:|---:|---:|
| FY 2027 | Consolidated | 20.005274 | 20.005274 | +0.000000 | +0.0000% |
| FY 2027 | Broking | 17.728318 | 17.728318 | +0.000000 | +0.0000% |
| FY 2027 | MTF | 2.276956 | 2.276956 | +0.000000 | +0.0000% |
| FY 2027 | F&O | 12.187676 | 12.187676 | +0.000000 | +0.0000% |
| FY 2027 | Cash | 4.176738 | 4.176738 | +0.000000 | +0.0000% |
| FY 2027 | Commodities | 1.363903 | 1.363903 | +0.000000 | +0.0000% |
| Q2 FY 2027 | Consolidated | 18.582719 | 18.582719 | +0.000000 | +0.0000% |
| Q2 FY 2027 | Broking | 16.188957 | 16.188957 | +0.000000 | +0.0000% |
| Q2 FY 2027 | MTF | 2.393762 | 2.393762 | +0.000000 | +0.0000% |
| Q2 FY 2027 | F&O | 10.617876 | 10.617876 | +0.000000 | +0.0000% |
| Q2 FY 2027 | Cash | 4.123907 | 4.123907 | +0.000000 | +0.0000% |
| Q2 FY 2027 | Commodities | 1.447174 | 1.447174 | +0.000000 | +0.0000% |
| FY 2027 October | Consolidated | 23.298092 | 23.298092 | +0.000000 | +0.0000% |
| FY 2027 October | Broking | 20.783268 | 20.783268 | +0.000000 | +0.0000% |
| FY 2027 October | MTF | 2.514824 | 2.514824 | +0.000000 | +0.0000% |
| FY 2027 October | F&O | 14.458817 | 14.458817 | +0.000000 | +0.0000% |
| FY 2027 October | Cash | 4.538468 | 4.538468 | +0.000000 | +0.0000% |
| FY 2027 October | Commodities | 1.785983 | 1.785983 | +0.000000 | +0.0000% |
| FY 2026 | Consolidated | 16.075454 | 16.075454 | +0.000000 | +0.0000% |
| FY 2026 | Broking | 15.041634 | 15.041634 | +0.000000 | +0.0000% |
| FY 2026 | MTF | 1.033820 | 1.033820 | +0.000000 | +0.0000% |
| FY 2026 | F&O | 10.813984 | 10.813984 | +0.000000 | +0.0000% |
| FY 2026 | Cash | 3.330972 | 3.330972 | +0.000000 | +0.0000% |
| FY 2026 | Commodities | 0.896679 | 0.896679 | +0.000000 | +0.0000% |
| FY 2026 October | Consolidated | 17.199648 | 17.199648 | +0.000000 | +0.0000% |
| FY 2026 October | Broking | 16.086385 | 16.086385 | +0.000000 | +0.0000% |
| FY 2026 October | MTF | 1.113263 | 1.113263 | +0.000000 | +0.0000% |
| FY 2026 October | F&O | 11.855821 | 11.855821 | +0.000000 | +0.0000% |
| FY 2026 October | Cash | 3.519421 | 3.519421 | +0.000000 | +0.0000% |
| FY 2026 October | Commodities | 0.711143 | 0.711143 | +0.000000 | +0.0000% |

Daily revenue rows that changed:

| Segment | Days | Changed | First | Last | Ratio min | Ratio max |
|---|---:|---:|---|---|---:|---:|
| F&O | 573 | 0 |  |  |  |  |
| Cash | 573 | 0 |  |  |  |  |
| Commodities | 272 | 0 |  |  |  |  |
| MTF | 507 | 0 |  |  |  |  |
