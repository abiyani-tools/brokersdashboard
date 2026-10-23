# Switch (a) independent check
Formulas: take rate = J17*J99/J8 = 0.06*13376.97/J8; F&O share J10=J6/(J6+J7+J8); F&O day Z ∝ E=FO%; E50=AVERAGE(E41:E49)=mean(I10x3,J10x3,K10x3). ADR = mean(daily Rs Mn)/10 over all dates (AVERAGEIFS). Claims with 6dp are compared at 1e-6 rel (6dp rounding can alone cause ~3e-7).

| check | mine | claim | rel diff | verdict |
|---|---|---|---|---|
| take rate before vs parity AI11 | 22.294950000 | 22.294950000 | 0.00e+00 | AGREE |
| take rate after | 22.931948571 | 22.931948000 | 2.49e-08 | AGREE |
| take-rate ratio | 1.028571429 | 1.028571429 | 0.00e+00 | AGREE |
| J10 before 277/381 | 0.727034121 | 0.727034121 | 0.00e+00 | AGREE |
| Q3 ratio 381/380 | 1.002631579 | 1.002631579 | 2.21e-16 | AGREE |
| 9-mo avg ratio | 1.000874473 | 1.000874473 | 1.27e-10 | AGREE |

FY 2027: comm days 144, F&O days 138
| FY 2027 comm before | 1.537138419 | 1.537138000 | 2.73e-07 | AGREE |
| FY 2027 comm after | 1.581056660 | 1.581057000 | 2.15e-07 | AGREE |
| FY 2027 F&O before | 9.285585900 | 9.285586000 | 1.07e-08 | AGREE |
| FY 2027 F&O after | 9.293705893 | 9.293706000 | 1.15e-08 | AGREE |
| FY 2027 Consol delta (F&O+comm) | 0.052038234 | 0.052038000 | 4.49e-06 | AGREE |
  raw: comm 1.537138419->1.581056660; fo 9.285585900->9.293705893; delta 0.052038234

Q2 FY 2027: comm days 66, F&O days 65
| Q2 FY 2027 comm before | 1.596816963 | 1.596817000 | 2.32e-08 | AGREE |
| Q2 FY 2027 comm after | 1.642440305 | 1.642440000 | 1.86e-07 | AGREE |
| Q2 FY 2027 F&O before | 8.498166453 | 8.498166000 | 5.33e-08 | AGREE |
| Q2 FY 2027 F&O after | 8.505597869 | 8.505598000 | 1.54e-08 | AGREE |
| Q2 FY 2027 Consol delta (F&O+comm) | 0.053054758 | 0.053055000 | 4.56e-06 | AGREE |
  raw: comm 1.596816963->1.642440305; fo 8.498166453->8.505597869; delta 0.053054758

Oct FY2027: comm days 14, F&O days 13
| Oct FY2027 comm before | 1.912729487 | 1.912729000 | 2.55e-07 | AGREE |
| Oct FY2027 comm after | 1.967378901 | 1.967379000 | 5.03e-08 | AGREE |
| Oct FY2027 F&O before | 6.744218832 | 6.744219000 | 2.49e-08 | AGREE |
| Oct FY2027 F&O after | 6.750116469 | 6.750116000 | 6.94e-08 | AGREE |
| Oct FY2027 Consol delta (F&O+comm) | 0.060547050 | 0.060547000 | 8.31e-07 | AGREE |
  raw: comm 1.912729487->1.967378901; fo 6.744218832->6.750116469; delta 0.060547050
| F&O changed day count | 200.000000000 | 200.000000000 | 0.00e+00 | AGREE |

n=22 agree=22
