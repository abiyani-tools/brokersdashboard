"""Compare a Groww engine run with the workbook's cached values (groww_fixtures_*.json)."""
import json
import os

from . import groww, summary

TOL = 1e-9
SNAP_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'snapshot')
ANGEL_SNAPSHOT = os.path.join(SNAP_DIR, 'db_snapshot_2026-10-23.json')
GROWW_SNAPSHOT = os.path.join(SNAP_DIR, 'groww_snapshot_2026-10-23.json')
GROWW_FIXTURES = os.path.join(SNAP_DIR, 'groww_fixtures_2026-10-23.json')

# feeder column -> (daily segment, field)
FEEDERS = {'backtesting F&O!AD': ('fo', 'rev_mn'), 'backtesting cash!V': ('cash', 'rev_mn'),
           'Commodities!K': ('comm', 'rev_mn'), 'MTF data (2)!L': ('mtf', 'gross_cr')}


def run_all(angel_snapshot=ANGEL_SNAPSHOT, groww_snapshot=GROWW_SNAPSHOT):
    I, G = groww.load(angel_snapshot, groww_snapshot)
    res = groww.run(I, G)
    cells, stats = summary.build(res['daily'], 'GROWW')
    return I, G, res, cells


def compare_daily(res, fixtures, tol=TOL):
    """Per feeder column: {'days', 'max_abs_diff', 'mismatches'}. Expected '#N/A' <-> engine None; a date that is
    blank in the sheet must be absent from the engine's rows."""
    out = {}
    for col, (seg, field) in FEEDERS.items():
        exp, got = fixtures['daily'][col], res['daily'][seg]
        worst, bad = 0.0, []
        for d in sorted(set(exp) | set(got)):
            if d not in exp:                                   # blank in the sheet: the engine must have no row
                bad.append((d, None, got[d][field]))
                continue
            e, g = exp[d], (got[d][field] if d in got else 'ABSENT')
            if e == '#N/A':                                    # a row whose value is not numeric
                if g is not None:
                    bad.append((d, e, g))
            elif g is None or g == 'ABSENT':
                bad.append((d, e, g))
            else:
                worst = max(worst, abs(e - g))
                if abs(e - g) > tol:
                    bad.append((d, e, g))
        out[col] = {'days': len(exp), 'max_abs_diff': worst, 'mismatches': bad}
    return out


def compare_summary(cells, fixtures, tol=TOL):
    """Rows {cell, panel, label, header, expected, got, ok}; '-' cells must be None (division by 0)."""
    rows = []
    for e in fixtures['summary']:
        g = cells[e['cell']][2]
        rows.append(dict(e, expected=e['value'], got=g, ok=g is not None and abs(g - e['value']) <= tol))
    for e in fixtures['summary_dash']:
        g = cells[e['cell']][2]
        rows.append(dict(e, expected='-', got=g, ok=g is None))
    return rows


def compare_calibration(res, fixtures, rel=1e-9):
    """Quarterly parameters against the workbook's cached cells: [(what, expected, got, ok)]."""
    c, fx, rows = res['calib'], fixtures['calib'], []

    def chk(what, e, g):
        rows.append((what, e, g, g is not None and abs(e - g) <= rel * max(1.0, abs(e))))
    for q, r in fx['fo'].items():
        p = c['fo_quarter'][q]
        chk(f'fo take_rate|{q}', r['take_rate'], p['take_rate'])
        chk(f'fo share|{q}', r['share'], p['share'])
        if 'cpo_q' in p:                                  # row 55 is read by the take-rate step of Q2-Q4 FY26 only
            chk(f'fo cpo_q|{q}', r['cpo_q'], p['cpo_q'])
    for q, r in fx['cash'].items():
        p = c['cash_quarter'][q]
        for k in ('tpo', 'take_rate', 'share'):
            chk(f'cash {k}|{q}', r[k], p[k])
    for k, e in fx['comm'].items():
        chk(f'comm {k}', e, {'rev_mn': c['comm']['rev_mn'], 'take_rate': c['comm']['take_rate'],
                             'orders_mn': c['comm']['orders_mn'], 'mkt_orders_mn': c['comm']['mkt_orders_mn'],
                             'share0': c['comm']['share0'], 'growth': c['comm']['growth']}[k])
    for q, r in fx['mtf'].items():
        if q in c['mtf_quarter']:
            chk(f'mtf share|{q}', r['share'], c['mtf_quarter'][q]['share'])
    return rows


def main(angel_snapshot=ANGEL_SNAPSHOT, groww_snapshot=GROWW_SNAPSHOT, fixtures_path=GROWW_FIXTURES):
    fixtures = json.load(open(fixtures_path))
    I, G, res, cells = run_all(angel_snapshot, groww_snapshot)
    daily = compare_daily(res, fixtures)
    calib = compare_calibration(res, fixtures)
    rows = compare_summary(cells, fixtures)
    n_ok, n_all = sum(r['ok'] for r in rows), len(rows)
    n_num = len(fixtures['summary'])
    num_ok = sum(r['ok'] for r in rows[:n_num])
    print(f'GROWW PARITY summary {num_ok}/{n_num} cells exact (tol {TOL:g}); '
          f'{sum(r["ok"] for r in rows[n_num:])}/{n_all - n_num} dash cells')
    for col, r in daily.items():
        print(f'  daily {col:22s} {r["days"] - len(r["mismatches"]):4d}/{r["days"]:<4d} days  '
              f'max abs diff {r["max_abs_diff"]:.3g}')
    print(f'  quarterly parameters {sum(r[3] for r in calib)}/{len(calib)}')
    for r in rows:
        if not r['ok']:
            print('  MISS', r['cell'], r['panel'], r['label'], r['header'], r['expected'], r['got'])
    for r in calib:
        if not r[3]:
            print('  MISS calib', r[:3])
    return rows, daily, calib
