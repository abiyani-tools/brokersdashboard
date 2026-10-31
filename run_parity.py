import json, sys
if '--broker' in sys.argv:                              # python3 run_parity.py --broker GROWW
    broker = sys.argv[sys.argv.index('--broker') + 1].upper()
    if broker != 'GROWW':
        sys.exit(f'--broker {broker}: only GROWW has a separate parity run (Angel One is the default)')
    from src.engine import parity_groww
    rows, daily, calib = parity_groww.main()
    bad = (sum(not r['ok'] for r in rows) + sum(bool(r['mismatches']) for r in daily.values())
           + sum(not r[3] for r in calib))
    sys.exit(1 if bad else 0)
from src.engine.inputs import load_snapshot
from src.engine import daily, summary, parity
snap = sys.argv[1] if len(sys.argv) > 1 else 'snapshot/db_snapshot_2026-10-23.json'
I = load_snapshot(snap)
res = daily.run(I)
cells, stats = summary.build(res['daily'])
rows = parity.compare(res, cells, I.snap['parity_expected'])
rep = parity.report(rows)
tot = sum(v[0] for v in rep.values()); ok = sum(v[1] for v in rep.values()); oos = sum(v[2] for v in rep.values())
print(f'PARITY {ok}/{tot} exact; {oos} out of scope; {tot-ok-oos} unexplained')
for k, (n, good, miss) in sorted(rep.items()):
    flag = '' if good == n else '  <--'
    print(f'{k:32s} {good:5d}/{n:<5d} out-of-scope {miss}{"" if good+miss==n else "  <-- UNEXPLAINED"}')
json.dump(rows, open('parity_rows.json', 'w'), default=str)
