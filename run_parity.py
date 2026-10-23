import json, sys
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
