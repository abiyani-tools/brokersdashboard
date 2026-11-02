"""Build the Motilal Oswal (MOSL) snapshot and fixtures from the workbook (the MOSL counterpart of build_groww.py).

    python seed/build_mosl.py "<workbook>.xlsx" snapshot [--tag 2026-10-23] [--inputs out/mosl/workbook_inputs.json]

Needs openpyxl (not an engine dependency): use a scratch venv. Reads the workbook twice: cached values
(data_only=True) for the numbers, formulas (data_only=False) to assert that every fact is a typed constant.

Writes, in the engine's snapshot format (rows carry broker_id = 'MOSL'; source_ref = 'excel:<sheet>!<cell>'):
  <out>/mosl_snapshot_<tag>.json   facts, assumptions, pins (the typed inputs the MOSL chain reads) and the
                                   exchange series the shared snapshot lacks (`market_daily`, same shape):
                                     nse_fo/index_opt_contracts       backtesting F&O!P  (NSE index options, raw count)
                                     bse_fo/opt_contracts_live        backtesting F&O!R  (BSE contracts, NOT the frozen U)
                                     nse_fo/index_opt_adto, bse_fo/opt_adto   backtesting F&O!J, M (Rs Cr; the cancelling G term)
                                     nse_cash/turnover_cr_xl, bse_cash/turnover_cr_xl   backtesting cash!I, J as the
                                       workbook uses them (two rows out of date alignment from 9 Jun 2025, issue #5)
  <out>/mosl_fixtures_<tag>.json   the cached daily feeder columns (backtesting F&O!AG / AF, backtesting cash!AB / AA,
                                   Commodities!O / L, MTF data (2)!X / W), the quarterly parameters they read, and the
                                   264 cells of SUMMARY - Motilal Oswal.

MCX contracts (Commodities!F) and the industry MTF book (MTF data (2)!I) are NOT repeated: they equal the series
already in the shared snapshot (db_snapshot_*.json: mcx/contracts, mtf_industry/book_cr), and the build asserts it.
Nothing is read from an Angel One or Groww cell.
"""
import datetime as dt
import json
import os
import sys

import openpyxl

B = 'MOSL'
AS, WS = 'Motilal Oswal assumptions', 'Working Sheet - MOSL'
SRC_NEEDED_NII = ('[SOURCE NEEDED: typed NII yield; not a line in the MOSL data book and equal to no data-book cell '
                  '(docs/MOSL_ADR_Methodology.md section 2b)]')

Q = ['Q1 FY 2025', 'Q2 FY 2025', 'Q3 FY 2025', 'Q4 FY 2025', 'Q1 FY 2026', 'Q2 FY 2026', 'Q3 FY 2026', 'Q4 FY 2026',
     'Q1 FY 2027']
RATIO_COL = dict(zip(Q, ['G', 'H', 'I', 'J', 'L', 'M', 'N', 'O', 'Q']))          # assumptions rows 111-114
WS_COL = dict(zip(Q[:8], ['J', 'K', 'L', 'M', 'O', 'P', 'Q', 'R']))              # Working Sheet - MOSL rows 53, 73

# (sheet, cell, metric, period_key, unit, read_by_model, note)
FACTS = []


def _add(sheet, cells, metric, unit, read=True, note=None):
    for cell, q in cells:
        FACTS.append((sheet, cell, metric, q, unit, read, note))


_add(AS, [(f'C{r}', Q[r - 6]) for r in range(6, 15)], 'mtf_book_closing', 'Rs Cr')
_add(AS, [(f'F{r}', Q[r - 6]) for r in range(6, 15)], 'mtf_nii_yield', 'fraction', note=SRC_NEEDED_NII)
_add(AS, [(f'C{r}', Q[r - 27]) for r in range(29, 36)], 'gross_fo_cr', 'Rs Cr')
_add(AS, [(f'I{r}', Q[r - 27]) for r in range(27, 35)], 'share_fo', 'fraction',
     note='F&O premium-turnover share; cancels in a calibrated quarter')
_add(AS, [(f'E{r}', Q[r - 44]) for r in range(46, 53)], 'share_cash', 'fraction')
_add(AS, [(f'G{r}', Q[r - 44]) for r in range(46, 53)], 'adto_cash_mosl', 'Rs Cr/day')
_add(AS, [(f'I{r}', Q[r - 44]) for r in range(46, 52)], 'gross_cash_cr', 'Rs Cr')
_add(AS, [('I52', 'Q1 FY 2027')], 'gross_cash_cr', 'Rs Cr', read=False,
     note='typed 228 is NOT used: J52 = J51 (the Q4 FY26 take rate is carried; issue #7)')
_add(AS, [('K60', 'Q1 FY 2027')], 'gross_comm_cr', 'Rs Cr')
_add(AS, [('K62', 'Q1 FY 2027')], 'share_comm', 'fraction')
_add(WS, [(f'{c}53', q) for q, c in WS_COL.items()], 'gross_comm_cr', 'Rs Cr',
     note='Working Sheet - MOSL: typed copy of the data book (Consol row 53)')
_add(WS, [(f'{c}73', q) for q, c in WS_COL.items()], 'share_comm', 'fraction',
     note='Working Sheet - MOSL: typed copy of the data book (Consol row 67)')
for _row, _seg in ((112, 'cash'), (113, 'fo'), (114, 'comm')):
    _add(AS, [(f'{RATIO_COL[q]}{_row}', q) for q in Q], f'net_gross_{_seg}', 'fraction',
         note='net / gross brokerage (data book Consol rows 56-60 / 50-54)')
# present in the sheet but never read by SUMMARY - Motilal Oswal
_add(AS, [('D6', 'Q1 FY 2025'), ('D7', 'Q2 FY 2025')], 'mtf_industry_book_close', 'Rs Cr', read=False,
     note='[SOURCE NEEDED: industry book before 1 Oct 2024]')


def sheetval(wb, sheet, cell):
    v = wb[sheet][cell].value
    return v.date().isoformat() if isinstance(v, dt.datetime) else v


def build_snapshot(wbv, wbf, tag, databook, series):
    facts, seen = [], set()
    for i, (sheet, cell, metric, pk, unit, read, note) in enumerate(FACTS, 1):
        v = sheetval(wbv, sheet, cell)
        assert isinstance(v, (int, float)) and not isinstance(v, bool), (sheet, cell, v)
        f = wbf[sheet][cell].value
        assert not (isinstance(f, str) and f.startswith('=')), f'{sheet}!{cell} is a formula, not a typed input'
        assert (metric, pk) not in seen, (metric, pk)
        seen.add((metric, pk))
        db = databook.get((sheet, cell))
        notes = [note, None if not db else f'data book {db["databook_ref"]} ({db["databook_match"]})',
                 None if read else 'present in the sheet, not read by SUMMARY - Motilal Oswal']
        facts.append(dict(fact_id=i, broker_id=B, period_type='Q', period_key=pk, metric=metric, segment='',
                          value=v, unit=unit, source_ref=f'excel:{sheet}!{cell}', table_label=sheet,
                          status='staged', read_by_model=read, note='; '.join(n for n in notes if n)))
    A = lambda key, value, unit, ref, note=None, text=None: dict(
        broker_id=B, key=key, value=value, value_text=text, unit=unit, source_ref=ref, note=note)
    assumptions = [
        A('mtf_day_basis', 247, 'days', 'excel:MTF data (2)!X12 (literal in =W12*NII/247)',
          'FY26 had 247 trading days; the workbook applies it to every quarter'),
        A('cash_key_alignment', None, None, 'excel:backtesting cash!I:K',
          'NSE + BSE turnover as the workbook uses it: two rows out of date alignment from 2025-06-09 '
          '(docs/MOSL_ADR_Methodology.md issue #5); kept in parity mode',
          text='workbook_as_used'),
        A('rule_fo_share', None, None, 'excel:Motilal Oswal assumptions!I35:I37',
          'Q1 FY27 = mean of the last two typed shares, then carried (cancels in the output)',
          text='avg_last_2_quarters; carry'),
        A('rule_fo_rate', None, None, 'excel:Motilal Oswal assumptions!L36:L37', 'Q1 FY27 rate carried',
          text='carry_last_calibrated_quarter'),
        A('rule_cash_take_rate', None, None, 'excel:Motilal Oswal assumptions!J52:J54',
          'Q1 FY27 = Q4 FY26 (typed 228 ignored), then carried; per quarter, not per day',
          text='carry_prior_quarter_ignoring_Q1FY27_reported'),
        A('rule_cash_delivery_ratio', None, None, 'excel:Motilal Oswal assumptions!H53:H54',
          'trailing 3 quarters (Q3 FY27 includes the Q2 estimate)', text='avg_last_3_quarters'),
        A('rule_cash_share', None, None, 'excel:Motilal Oswal assumptions!E53:E54', 'Q1 FY27 share carried',
          text='carry_last_typed_quarter'),
        A('rule_comm_share', None, None, 'excel:Motilal Oswal assumptions!L62', 'mean of the last four quarters',
          text='avg_last_4_quarters'),
        A('rule_comm_take_rate', None, None, 'excel:Motilal Oswal assumptions!L74', 'Q1 FY27 carried',
          text='carry_last_calibrated_quarter'),
        A('rule_net_gross', None, None, 'excel:Motilal Oswal assumptions!R112:S114',
          'Q2 FY27 = mean(Q4 FY26, Q1 FY27); F&O Q3 FY27 = Q2 FY27; cash and commodities have no Q3 FY27 ratio',
          text='avg_Q4FY26_Q1FY27; fo_carry_to_Q3FY27'),
        A('rule_mtf', None, None, 'excel:Motilal Oswal assumptions!E15:F15', 'share and NII carried from Q1 FY27',
          text='carry_last_actual_quarter'),
        # live switch m-f: the typed Q1 FY27 yield as a labelled assumption, carried to later quarters
        A('mtf_nii_yield_carry', next(f['value'] for f in facts if f['metric'] == 'mtf_nii_yield' and f['period_key'] == 'Q1 FY 2027'),
          'fraction', 'excel:Motilal Oswal assumptions!F14 (typed Q1 FY27 yield; the workbook carries it to Q2 FY27 as F15 = F14)',
          "[SOURCE NEEDED: MOSL does not publish an MTF yield] The workbook's typed 12.94% (unrounded), carried to every quarter "
          'after the last typed yield (MOSL data book has no MTF NII or yield line; docs/MOSL_ADR_Methodology.md section 2b). '
          'Read by live switch m-f.'),
    ]
    pins = []
    P = lambda key, period, text, cell, note=None: pins.append(dict(
        broker_id=B, key=key, period_key=period, value=None, value_text=text, excel_cell=cell, note=note))
    P('fo_table_first_quarter', '', 'Q1 FY 2025', 'Motilal Oswal assumptions!B27',
      'quarters before it have no table row: #N/A (VLOOKUP miss)')
    P('fo_zero_quarters', '', 'Q1 FY 2025,Q2 FY 2025', 'Motilal Oswal assumptions!L27:L28',
      'rate cell blank: the VLOOKUP returns 0, so the daily rows are numeric 0')
    P('fo_last_actual_quarter', '', 'Q1 FY 2027', 'Motilal Oswal assumptions!C35')
    P('cash_table_first_quarter', '', 'Q3 FY 2025', 'Motilal Oswal assumptions!B46',
      'backtesting cash!AB is blank before 2024-10-01 (first formula row 252)')
    P('cash_last_actual_quarter', '', 'Q1 FY 2027', 'Motilal Oswal assumptions!E52')
    P('cash_net_ratio_last_quarter', '', 'Q2 FY 2027', 'Motilal Oswal assumptions!R112',
      'HLOOKUP range $C$111:$R$112 ends at Q2 FY27: Q3 FY27 net cash is #N/A')
    P('comm_table_last_quarter', '', 'Q2 FY 2027', 'Motilal Oswal assumptions!L59',
      'Commodities!L is #N/A for Q3 FY27 (no column in B59:L74)')
    P('comm_last_actual_quarter', '', 'Q1 FY 2027', 'Motilal Oswal assumptions!K60')
    P('comm_o_blank_from_date', '', series['comm_o_blank_from'], 'Commodities!O655',
      'Commodities!O is #N/A for the Q3 FY27 rows before this date and blank (formula not extended) from it')
    P('mtf_last_actual_quarter', '', 'Q1 FY 2027', 'Motilal Oswal assumptions!C14')
    P('mtf_last_formula_date', '', series['mtf_last_date'], 'MTF data (2)!X506',
      'V:X have no formulas after this date; the industry book (I) runs on')
    return dict(broker_id=B, tag=tag, source_workbook=os.path.basename(WORKBOOK[0]), facts=facts,
                assumptions=assumptions, pins=pins, market_daily=series['market_daily'],
                market_daily_sources=series['sources'])


WORKBOOK = ['']


# ── exchange series the shared snapshot lacks ──
def _rows(ws, r0, r1, dcol):
    for r in range(r0, r1 + 1):
        d = ws[f'{dcol}{r}'].value
        if isinstance(d, dt.datetime):
            yield r, d.date().isoformat()


def exchange_series(wbv):
    """market_daily rows (shared-snapshot shape) from backtesting F&O (rows 4-761) and backtesting cash (rows 3-760),
    the workbook's columns as they stand. A row whose value is text (backtesting F&O!P169 = ' ') is kept with
    value None and status 'text'. The date 2024-02-01 occurs twice in backtesting F&O (Q4 FY24, outside every
    Summary period): the two rows must agree."""
    fo, ca = wbv['backtesting F&O'], wbv['backtesting cash']
    spec = [(fo, 4, 761, 'nse_fo', 'index_opt_contracts', 'P', 'count', 'backtesting F&O!P'),
            (fo, 4, 761, 'bse_fo', 'opt_contracts_live', 'R', 'count', 'backtesting F&O!R'),
            (fo, 4, 761, 'nse_fo', 'index_opt_adto', 'J', 'Rs Cr', 'backtesting F&O!J'),
            (fo, 4, 761, 'bse_fo', 'opt_adto', 'M', 'Rs Cr', 'backtesting F&O!M'),
            (ca, 3, 760, 'nse_cash', 'turnover_cr_xl', 'I', 'Rs Cr', 'backtesting cash!I'),
            (ca, 3, 760, 'bse_cash', 'turnover_cr_xl', 'J', 'Rs Cr', 'backtesting cash!J')]
    out, sources, dup = [], {}, []
    for ws, r0, r1, dataset, metric, col, unit, src in spec:
        seen = {}
        for r, d in _rows(ws, r0, r1, 'B'):
            v = ws[f'{col}{r}'].value
            if isinstance(v, bool) or not (v is None or isinstance(v, (int, float, str))):
                raise ValueError((src, r, v))
            val, status = (v, 'ok') if isinstance(v, (int, float)) else (None, 'text')
            if d in seen:
                assert seen[d] == (val, status), (src, d, seen[d], val)
                dup.append((src, d))
                continue
            seen[d] = (val, status)
            out.append(dict(trade_date=d, dataset=dataset, metric=metric, value=val, status=status, unit=unit))
        sources[f'{dataset}/{metric}'] = f'excel:{src}{r0}:{col}{r1} (cached values; {len(seen)} dates)'
    return dict(market_daily=out, sources=sources, duplicates=sorted(set(dup)))


def shared_agree(wbv, shared_path):
    """The Commodities!F and MTF data (2)!I columns equal the shared snapshot's mcx / mtf_industry series."""
    shared = json.load(open(shared_path))
    ref = {}
    for m in shared['market_daily']:
        ref.setdefault((m['dataset'], m['metric']), {})[m['trade_date']] = m['value']
    for sheet, vcol, key in (('Commodities', 'F', ('mcx', 'contracts')), ('MTF data (2)', 'I', ('mtf_industry', 'book_cr'))):
        ws, n = wbv[sheet], 0
        for r in range(2, 1001):
            d = ws[f'B{r}'].value
            v = ws[f'{vcol}{r}'].value
            if isinstance(d, dt.datetime) and isinstance(v, (int, float)):
                assert ref[key][d.date().isoformat()] == v, (sheet, r, d, v)
                n += 1
        assert n == len(ref[key]), (sheet, n, len(ref[key]))
    return True


# ── feeder columns ──
FEEDERS = {
    'backtesting F&O!AG': ('backtesting F&O', 4, 761, 'AG'), 'backtesting F&O!AF': ('backtesting F&O', 4, 761, 'AF'),
    'backtesting cash!AB': ('backtesting cash', 3, 760, 'AB'), 'backtesting cash!AA': ('backtesting cash', 3, 760, 'AA'),
    'Commodities!O': ('Commodities', 2, 661, 'O'), 'Commodities!L': ('Commodities', 2, 661, 'L'),
    'MTF data (2)!X': ('MTF data (2)', 12, 518, 'X'), 'MTF data (2)!W': ('MTF data (2)', 12, 518, 'W'),
}


def feeder_column(wbv, sheet, r0, r1, vcol):
    """{date: number | '#N/A' | '#VALUE!'}; a blank cell is left out. Rows sharing a date must agree."""
    ws, out = wbv[sheet], {}
    for r, d in _rows(ws, r0, r1, 'B'):
        v = ws[f'{vcol}{r}'].value
        if v is None:
            continue
        v = v if isinstance(v, (int, float)) else str(v)
        assert out.get(d, v) == v, (sheet, vcol, d)
        out[d] = v
    return out


def blank_from(wbv, sheet, r0, r1, vcol):
    """First date whose cell is blank after the last non-blank one (Commodities!O655)."""
    ws, last, first_blank = wbv[sheet], None, None
    for r, d in _rows(ws, r0, r1, 'B'):
        if ws[f'{vcol}{r}'].value is not None:
            last, first_blank = d, None
        elif first_blank is None:
            first_blank = d
    return first_blank


def last_date_with(wbv, sheet, r0, r1, vcol):
    ws, last = wbv[sheet], None
    for r, d in _rows(ws, r0, r1, 'B'):
        if ws[f'{vcol}{r}'].value is not None:
            last = d
    return last


def calibration(wbv):
    """Cached quarterly parameters the daily columns read (assumptions sheet), by quarter."""
    a = wbv[AS]
    qrow = {q: r for q, r in zip(Q + ['Q2 FY 2027', 'Q3 FY 2027'], range(27, 38))}
    out = {'fo': {}, 'cash': {}, 'comm': {}, 'mtf': {}, 'ratio': {}}
    for q, r in qrow.items():
        p = dict(share=a[f'I{r}'].value, rate=a[f'L{r}'].value)
        if q in Q[2:9]:
            p.update(F=a[f'F{r}'].value, G=a[f'G{r}'].value, H=a[f'H{r}'].value, J=a[f'J{r}'].value,
                     K=a[f'K{r}'].value)
        out['fo'][q] = p
    for q, r in zip(Q[2:] + ['Q2 FY 2027', 'Q3 FY 2027'], range(46, 55)):
        assert a[f'B{r}'].value == q, (a[f'B{r}'].value, q)
        out['cash'][q] = dict(days=a[f'D{r}'].value, share=a[f'E{r}'].value, H=a[f'H{r}'].value, J=a[f'J{r}'].value)
    for q, c in zip(Q + ['Q2 FY 2027'], 'CDEFGHIJKL'):
        assert a[f'{c}59'].value == q, (a[f'{c}59'].value, q)
        out['comm'][q] = dict(share=a[f'{c}62'].value, take=a[f'{c}74'].value, contracts_mn=a[f'{c}65'].value)
    for q, r in zip(Q[2:] + ['Q2 FY 2027'], range(8, 16)):
        assert a[f'B{r}'].value == q, (a[f'B{r}'].value, q)
        p = dict(share=a[f'E{r}'].value, nii=a[f'F{r}'].value)
        if r < 15:
            p['industry_close'] = a[f'D{r}'].value
        out['mtf'][q] = p
    for q in Q + ['Q2 FY 2027', 'Q3 FY 2027']:
        col = dict(RATIO_COL, **{'Q2 FY 2027': 'R', 'Q3 FY 2027': 'S'})[q]
        assert a[f'{col}111'].value == q, (a[f'{col}111'].value, q)
        out['ratio'][q] = dict(cash=a[f'{col}112'].value, fo=a[f'{col}113'].value, comm=a[f'{col}114'].value)
    return out


# ── SUMMARY - Motilal Oswal cells ──
def summary_cells(wbv, expected_path):
    """The 264 numeric cells with their panel / section / label / header, from out/mosl/summary_expected.json,
    each checked against the workbook's cached value."""
    exp = json.load(open(expected_path))
    ws = wbv['SUMMARY - Motilal Oswal']
    for e in exp:
        v = ws[e['cell']].value
        assert isinstance(v, (int, float)) and abs(v - e['value']) <= 1e-12 * max(1.0, abs(v)), (e['cell'], v, e['value'])
    assert len(exp) == 264 and len({e['cell'] for e in exp}) == 264
    return exp


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]

    def opt(name, default):
        if name in sys.argv:
            v = sys.argv[sys.argv.index(name) + 1]
            args.remove(v)
            return v
        return default
    tag = opt('--tag', '2026-10-23')
    inputs_path = opt('--inputs', 'out/mosl/workbook_inputs.json')
    shared_path = opt('--shared', 'snapshot/db_snapshot_2026-10-23.json')
    expected_path = opt('--expected', 'out/mosl/summary_expected.json')
    wb_path, out = args[0], args[1]
    WORKBOOK[0] = wb_path
    wbv = openpyxl.load_workbook(wb_path, data_only=True)
    wbf = openpyxl.load_workbook(wb_path, data_only=False)
    databook = {}
    if os.path.exists(inputs_path):
        databook = {(r['sheet'], r['cell']): r for r in json.load(open(inputs_path)) if r.get('databook_ref')}
    shared_agree(wbv, shared_path)
    series = exchange_series(wbv)
    series['comm_o_blank_from'] = blank_from(wbv, 'Commodities', 2, 661, 'O')
    series['mtf_last_date'] = last_date_with(wbv, 'MTF data (2)', 12, 518, 'X')
    snap = build_snapshot(wbv, wbf, tag, databook, series)
    daily = {k: feeder_column(wbv, *v) for k, v in FEEDERS.items()}
    fixtures = dict(broker_id=B, tag=tag, daily=daily, calib=calibration(wbv),
                    summary=summary_cells(wbv, expected_path))
    json.dump(snap, open(os.path.join(out, f'mosl_snapshot_{tag}.json'), 'w'), indent=1)
    json.dump(fixtures, open(os.path.join(out, f'mosl_fixtures_{tag}.json'), 'w'))
    print('facts', len(snap['facts']), 'assumptions', len(snap['assumptions']), 'pins', len(snap['pins']),
          'market_daily', len(snap['market_daily']), 'duplicate dates', series['duplicates'])
    print('daily rows', {k: len(v) for k, v in daily.items()}, 'summary', len(fixtures['summary']))
    print('comm O blank from', series['comm_o_blank_from'], '; MTF X last date', series['mtf_last_date'])


if __name__ == '__main__':
    main()
