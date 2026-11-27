"""g-j evidence: backtest of the cash trades-per-order (tpo) projection, 25 Nov 2026.

    python3 -m src.engine.groww_tpo_backtest

Inputs are the live run's cash calibration (sb_calibration, runs of 24 Nov 2026, data to 23 Nov): Angel One's quarterly
tpo and market trades, Groww's reported cash revenue (Rs Mn) and cash share. A. Angel's tpo projection rules out of
sample. B. Whether Angel's tpo helps predict Groww's revenue per share-weighted market trade (y = rev / (N x share);
share set to its actual value so only the tpo adjustment is tested). Conclusion in docs/GROWW_LIVE_SPEC.md (g-j).
"""
from statistics import mean
Q = ['Q3 FY25','Q4 FY25','Q1 FY26','Q2 FY26','Q3 FY26','Q4 FY26','Q1 FY27','Q2 FY27']
tpo = dict(zip(Q, [4.91792,5.99215,5.62978,5.7792,5.69722,6.16541,6.58808,6.85224]))
N   = dict(zip(Q, [2515.49014,2568.06249,2345.74086,2256.0512,2116.99801,2401.64344,2536.78877,2691.95336]))
GQ = Q[2:]
grev  = dict(zip(GQ, [1830.54903,1906.01866,2080.7688,2395.4346,2493.3587,2680.5396]))
gshare= dict(zip(GQ, [0.236,0.258,0.288,0.314,0.302,0.308]))

print('A. Angel trades-per-order: projection rules vs actual (out of sample)')
rules = {
 'avg last 3 (model)': lambda h: mean(h[-3:]),
 'avg last 2':         lambda h: mean(h[-2:]),
 'carry last':         lambda h: h[-1],
 'last x QoQ trend':   lambda h: h[-1] * h[-1] / h[-2],
}
errs = {k: [] for k in rules}
print(f"{'quarter':9} {'actual':>7} {'chg':>6} " + ' '.join(f'{k:>20}' for k in rules))
for i in range(3, len(Q)):
    h = [tpo[q] for q in Q[:i]]; a = tpo[Q[i]]
    row = []
    for k, f in rules.items():
        e = f(h) / a - 1; errs[k].append(e); row.append(f'{f(h):6.3f} ({e*100:+5.1f}%)')
    print(f'{Q[i]:9} {a:7.3f} {(a/h[-1]-1)*100:+5.1f}% ' + ' '.join(f'{r:>20}' for r in row))
print('mean abs error ', ' '.join(f"{k}: {mean(abs(e) for e in v)*100:.1f}%" for k, v in errs.items()))
print('mean (bias)    ', ' '.join(f"{k}: {mean(v)*100:+.1f}%" for k, v in errs.items()))
# the revenue effect: revenue ~ 1/tpo, so tpo too low => revenue too high
print('\nImplied revenue effect of the tpo step (last actual / projected - 1) vs what actually happened:')
for i in range(3, len(Q)):
    h = [tpo[q] for q in Q[:i]]
    print(f"  {Q[i]}: model step {h[-1]/mean(h[-3:])*100-100:+5.1f}%   actual {h[-1]/tpo[Q[i]]*100-100:+5.1f}%")
print(f"  Q3 FY27: model step {tpo['Q2 FY27']/mean([tpo[q] for q in Q[-3:]])*100-100:+5.1f}%   actual: not reported yet")

print('\nB. Groww: does borrowing Angel\'s tpo help predict Groww cash revenue? (share = actual, so only tpo is tested)')
y = {q: grev[q] / (N[q] * gshare[q]) for q in GQ}   # Groww revenue per share-weighted market trade
vari = {
 'no tpo adjustment':        lambda q, p, i: 1.0,
 'Angel actual tpo (hindsight)': lambda q, p, i: tpo[p] / tpo[q],
 'Angel projected tpo (model)':  lambda q, p, i: tpo[p] / mean([tpo[x] for x in Q[Q.index(q)-3:Q.index(q)]]),
}
e2 = {k: [] for k in vari}
for i in range(1, len(GQ)):
    q, p = GQ[i], GQ[i-1]
    line = f'  {q}: y {y[p]:.3f}->{y[q]:.3f} ({(y[q]/y[p]-1)*100:+5.1f}%)'
    for k, f in vari.items():
        e = y[p] * f(q, p, i) / y[q] - 1; e2[k].append(e); line += f' | {k}: {e*100:+5.1f}%'
    print(line)
for k, v in e2.items():
    print(f'  {k:30} mean abs error {mean(abs(x) for x in v)*100:.1f}%  bias {mean(v)*100:+.1f}%')
