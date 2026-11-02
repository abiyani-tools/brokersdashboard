"""Compare a MOSL engine run with the workbook's cached values (mosl_fixtures_*.json)."""
import json
import os

from . import mosl, summary

TOL = 1e-9
SNAP_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'snapshot')
SHARED_SNAPSHOT = os.path.join(SNAP_DIR, 'db_snapshot_2026-10-23.json')
MOSL_SNAPSHOT = os.path.join(SNAP_DIR, 'mosl_snapshot_2026-10-23.json')
MOSL_FIXTURES = os.path.join(SNAP_DIR, 'mosl_fixtures_2026-10-23.json')

# feeder column -> (daily segment, field). The net columns feed the Summary; the gross ones are the step before.
FEEDERS = {'backtesting F&O!AG': ('fo', 'rev_mn'), 'backtesting cash!AB': ('cash', 'rev_cr'),
           'Commodities!O': ('comm', 'rev_mn'), 'MTF data (2)!X': ('mtf', 'nii_cr')}
GROSS = {'backtesting F&O!AF': ('fo', 'gross_mn'), 'backtesting cash!AA': ('cash', 'gross_cr'),
         'Commodities!L': ('comm', 'gross_mn'), 'MTF data (2)!W': ('mtf', 'book_cr')}


def run_all(shared_snapshot=SHARED_SNAPSHOT, mosl_snapshot=MOSL_SNAPSHOT):
    M = mosl.load(shared_snapshot, mosl_snapshot)
    res = mosl.run(M)
    cells, stats = summary.build(res['daily'], 'MOSL')
    return M, res, cells


def compare_daily(res, fixtures, tol=TOL):
    """Per net feeder column: {'days', 'max_abs_diff', 'mismatches'}. An expected '#N/A' / '#VALUE!' must be an engine
    row with the same `err`; a date that is blank in the sheet must have no engine row."""
    out = {}
    for col, (seg, field) in FEEDERS.items():
        exp, got = fixtures['daily'][col], res['daily'][seg]
        worst, bad = 0.0, []
        for d in sorted(set(exp) | set(got)):
            if d not in exp:
                bad.append((d, None, got[d][field]))
            elif d not in got:
                bad.append((d, exp[d], 'ABSENT'))
            elif isinstance(exp[d], str):
                if got[d].get('err') != exp[d] or got[d][field] is not None:
                    bad.append((d, exp[d], got[d][field]))
            elif got[d].get('err') or got[d][field] is None:
                bad.append((d, exp[d], got[d].get('err')))
            else:
                worst = max(worst, abs(exp[d] - got[d][field]))
                if abs(exp[d] - got[d][field]) > tol:
                    bad.append((d, exp[d], got[d][field]))
        out[col] = {'days': len(exp), 'max_abs_diff': worst, 'mismatches': bad}
    return out


def compare_gross(res, fixtures, tol=TOL):
    """Gross feeder columns (AF, AA, L, W), numeric cells only: the engine must have the same value."""
    out = {}
    for col, (seg, field) in GROSS.items():
        worst, bad, n = 0.0, [], 0
        for d, e in sorted(fixtures['daily'][col].items()):
            if isinstance(e, str):
                continue
            n += 1
            g = res['daily'][seg].get(d, {}).get(field)
            if g is None:
                bad.append((d, e, g))
                continue
            worst = max(worst, abs(e - g) / max(1.0, abs(e)))
            if abs(e - g) > tol * max(1.0, abs(e)):
                bad.append((d, e, g))
        out[col] = {'days': n, 'max_abs_diff': worst, 'mismatches': bad}
    return out


def compare_summary(cells, fixtures, tol=TOL):
    """Rows {cell, panel, label, header, expected, got, ok}."""
    rows = []
    for e in fixtures['summary']:
        c = cells.get(e['cell'])
        g = c[2] if c else None
        rows.append(dict(e, expected=e['value'], got=g, ok=g is not None and abs(g - e['value']) <= tol))
    return rows


def compare_calibration(res, fixtures, rel=1e-9):
    """Quarterly parameters against the workbook's cached assumptions cells: [(what, expected, got, ok)]."""
    c, fx, rows = res['calib'], fixtures['calib'], []

    def chk(what, e, g):
        rows.append((what, e, g, g is not None and abs(e - g) <= rel * max(1.0, abs(e))))
    for q, r in fx['fo'].items():
        chk(f'fo share|{q}', r['share'], c['fo']['share'].get(q))
        if q in c['fo']['rate'] and r['rate'] is not None:
            chk(f'fo rate|{q}', r['rate'], c['fo']['rate'][q])
        for k in ('F', 'G', 'H', 'J', 'K'):
            if k in r:
                chk(f'fo {k}|{q}', r[k], c['fo']['table'][q][k])
    for q, r in fx['cash'].items():
        for k in ('days', 'share', 'H', 'J'):
            chk(f'cash {k}|{q}', r[k], c['cash']['table'][q][k])
    for q, r in fx['comm'].items():
        for k, kk in (('share', 'share'), ('take', 'take'), ('contracts_mn', 'contracts_mn')):
            chk(f'comm {k}|{q}', r[k], c['comm'][kk][q])
    for q, r in fx['mtf'].items():
        chk(f'mtf share|{q}', r['share'], c['mtf']['share'][q])
        chk(f'mtf nii|{q}', r['nii'], c['mtf']['nii'][q])
        if 'industry_close' in r:
            chk(f'mtf industry_close|{q}', r['industry_close'], c['mtf']['industry_close'][q])
    for q, r in fx['ratio'].items():
        for s, e in r.items():
            g = c['ratio'][q][s]
            if g is None:
                continue                                    # the workbook's HLOOKUP range stops before it
            chk(f'net/gross {s}|{q}', e, g)
    return rows


def main(shared_snapshot=SHARED_SNAPSHOT, mosl_snapshot=MOSL_SNAPSHOT, fixtures_path=MOSL_FIXTURES):
    fixtures = json.load(open(fixtures_path))
    M, res, cells = run_all(shared_snapshot, mosl_snapshot)
    daily = compare_daily(res, fixtures)
    gross = compare_gross(res, fixtures)
    calib = compare_calibration(res, fixtures)
    rows = compare_summary(cells, fixtures)
    n_ok, n_all = sum(r['ok'] for r in rows), len(rows)
    print(f'MOSL PARITY summary {n_ok}/{n_all} cells exact (tol {TOL:g})')
    for col, r in {**daily, **gross}.items():
        print(f'  daily {col:22s} {r["days"] - len(r["mismatches"]):4d}/{r["days"]:<4d} days  '
              f'max abs diff {r["max_abs_diff"]:.3g}')
    print(f'  quarterly parameters {sum(r[3] for r in calib)}/{len(calib)}')
    for r in rows:
        if not r['ok']:
            print('  MISS', r['cell'], r['panel'], r['label'], r['header'], r['expected'], r['got'])
    for r in calib:
        if not r[3]:
            print('  MISS calib', r[:3])
    return rows, {**daily, **gross}, calib
