"""Build the Groww snapshot and fixtures from the workbook (the Groww counterpart of build_fixtures.py).

    python seed/build_groww.py "<workbook>.xlsx" snapshot [--tag 2026-10-23]

Needs openpyxl (not an engine dependency): use a scratch venv. Reads cached values only (data_only=True).

Writes, in the engine's snapshot format (rows carry broker_id = 'GROWW'; source_ref = 'excel:<sheet>!<cell>'):
  <out>/groww_snapshot_<tag>.json   facts, assumptions, pins   (the 41 Groww inputs + the Groww assumptions)
  <out>/groww_fixtures_<tag>.json   expected daily values of the four feeder columns
                                    (backtesting F&O!AD, backtesting cash!V, Commodities!K, MTF data (2)!L)
                                    the quarterly parameters they read (take rates, shares, orders per contract/trade),
                                    and the 262 numeric + 2 dash cells of SUMMARY - Groww

Exchange data, the industry MTF book and Angel's calibration inputs are NOT repeated here: Groww reads them
from the Angel snapshot (db_snapshot_*.json), exactly as the workbook shares those cells.
"""
import datetime as dt
import json
import os
import sys

import openpyxl

SRC_NEEDED = ('[SOURCE NEEDED: workbook names no source; presumably Groww quarterly results / '
              'investor presentation]')
B = 'GROWW'
WG, MT = 'Working sheet - Groww', 'MTF data'
Q = {'G': 'Q1 FY 2026', 'H': 'Q2 FY 2026', 'I': 'Q3 FY 2026', 'J': 'Q4 FY 2026', 'L': 'Q1 FY 2027'}

# (sheet, cell, metric, period_key, unit, read_by_model, note)
FACTS = []
# revenue mix: the cells SUMMARY - Groww reads, then the ones that are in the sheet but not read
for _cells, _read in ((('H7', 'I7', 'J7', 'H8', 'I8', 'J8', 'L8', 'I9'), True),
                      (('G7', 'L7', 'G8', 'J9', 'L9'), False)):
    for _cell in _cells:
        FACTS.append((WG, _cell, {7: 'revmix_fo', 8: 'revmix_cash', 9: 'revmix_comm'}[int(_cell[1:])],
                      Q[_cell[0]], 'fraction', _read, None))
for _c in 'HI':
    FACTS.append((WG, f'{_c}103', 'revenue_from_ops', Q[_c], 'Rs Mn', True, None))
    FACTS.append((WG, f'{_c}104', 'other_income', Q[_c], 'Rs Mn', True, None))
    FACTS.append((WG, f'{_c}105', 'total_income', Q[_c], 'Rs Mn', True, 'DERIVED'))
for _c in 'JL':
    FACTS.append((WG, f'{_c}120', 'total_income_ex_fisdom_amc', Q[_c], 'Rs Mn', True,
                  'base for the Q4 FY26 / Q1 FY27 revenue-mix cells J17, L18'))
FACTS += [(WG, f'{c}55', 'share_fo_adto_q', Q[c], 'fraction', c != 'L',
           'Groww F&O market share by ADTO; Angel share_fo_q is a share of orders') for c in 'HIJL']
FACTS += [(WG, f'{c}56', 'share_cash_adto_q', Q[c], 'fraction', True,
           'Groww cash market share by ADTO; Angel share_cash_q is a share of orders') for c in 'HIJL']
FACTS += [(WG, 'G103', 'revenue_from_ops', Q['G'], 'Rs Mn', False, 'G103 hard-coded (K103 - sum(H103:J103) = 9043.98)'),
          (WG, 'G104', 'other_income', Q['G'], 'Rs Mn', False, None)]
for _r, _q in {51: 'Q3 FY 2025', 52: 'Q4 FY 2025', 53: 'Q1 FY 2026', 54: 'Q2 FY 2026', 55: 'Q3 FY 2026',
               56: 'Q4 FY 2026', 57: 'Q1 FY 2027'}.items():
    FACTS.append((MT, f'H{_r}', 'mtf_revenue', _q, 'Rs Cr', True, 'hard-coded copy of Working sheet - Groww row 22 / 10'))
for _r, _q in {58: 'Q2 FY 2027', 59: 'Q3 FY 2027', 60: 'Q4 FY 2027'}.items():
    FACTS.append((MT, f'J{_r}', 'mtf_share_override', _q, 'fraction', True,
                  'typed assumption: no source, no stated basis'))


def sheetval(wb, sheet, cell):
    v = wb[sheet][cell].value
    return v.date().isoformat() if isinstance(v, dt.datetime) else v


def build_snapshot(wbv, tag):
    facts = []
    for i, (sheet, cell, metric, pk, unit, read, note) in enumerate(FACTS, 1):
        v = sheetval(wbv, sheet, cell)
        assert isinstance(v, (int, float)), (sheet, cell, v)
        derived = note == 'DERIVED'
        notes = [None if derived else note, 'formula (=row 103 + row 104); not hard-coded' if derived else SRC_NEEDED,
                 None if read else 'present in the sheet, not read by SUMMARY - Groww']
        facts.append(dict(fact_id=i, broker_id=B, period_type='Q', period_key=pk, metric=metric, segment='',
                          value=v, unit=unit, source_ref=f'excel:{sheet}!{cell}', table_label=sheet,
                          status='derived' if derived else 'staged', read_by_model=read,
                          note='; '.join(n for n in notes if n)))
    A = lambda key, value, unit, ref, note=None, text=None: dict(
        broker_id=B, key=key, value=value, value_text=text, unit=unit, source_ref=ref, note=note)
    assumptions = [
        A('share_growth_fo', sheetval(wbv, 'backtesting F&O', 'AS57'), 'fraction', 'excel:backtesting F&O!AS57',
          'typed 5%: AP57 = AO57*(1+AS57), AQ57:AR57 carry. [SOURCE NEEDED: basis]'),
        A('share_growth_comm', sheetval(wbv, 'Commodities', 'S9'), 'fraction', 'excel:Commodities!S9',
          'typed 5%, applied to every commodity day incl. the calibration quarter. [SOURCE NEEDED: basis]'),
        A('mtf_yield', 0.1495, 'p.a.', 'excel:MTF data (2)!L12 (literal in =K*(0.1495/246))',
          "Angel One's constant. [SOURCE NEEDED: Groww MTF yield]"),
        A('mtf_day_basis', 246, 'days', 'excel:MTF data (2)!L12 (literal in =K*(0.1495/246))',
          "Angel One's constant; FY26 had 247 trading days"),
        A('mtf_quarter_fraction', 4, 'quarters', 'excel:MTF data!I51 (literal in =H51/(0.1495/4))',
          'Groww average book = quarterly MTF revenue / (yield / 4)'),
        A('first_live_date_fo', None, None, 'excel:backtesting F&O!AD438 (first row that is not zero)',
          'F&O days before this are numeric 0 (Q3 FY25-Q1 FY26) or #N/A (Q2 FY25)', text='2025-07-01'),
        A('first_live_date_cash', None, None, 'excel:backtesting cash!V437 (first row that is not zero)',
          'cash days before this are numeric 0 (Q3 FY25-Q1 FY26) or #N/A (Q2 FY25)', text='2025-07-01'),
        A('first_live_date_comm', None, None, 'excel:Commodities!K390 (first row with a value)',
          'commodity days before this are blank, not 0', text='2025-10-01'),
        A('zero_fill_quarters', None, None, 'excel:backtesting F&O!AB189:AD437; backtesting cash!T188:V436',
          'quarters filled with 0 before first live; earlier quarters are #N/A', text='Q3 FY 2025,Q4 FY 2025,Q1 FY 2026'),
        A('comm_take_rate_basis', None, None, 'excel:Commodities!S5 (=AVERAGE(Angel Working sheet H78:J78))',
          "mean of Angel One's commodity take rate over the listed quarters", text='Q1 FY 2026,Q2 FY 2026,Q3 FY 2026'),
        A('rule_fo_share', None, None, 'excel:backtesting F&O!AP57:AR57', 'Q4 FY26 share x (1 + growth), then carried',
          text='last_actual x (1 + share_growth_fo); carry'),
        A('rule_fo_take_rate', None, None, 'excel:backtesting F&O!AP56:AR56', 'Q4 FY26 take rate carried',
          text='carry_last_actual_quarter'),
        A('rule_cash_take_rate', None, None, 'excel:cash market!K42:K43', 'trailing 3 quarters, then carried',
          text='avg_last_3_quarters; carry'),
        A('rule_cash_share', None, None, 'excel:cash market!L42:L43', 'last reported share carried',
          text='carry_last_actual_quarter'),
    ]
    pins = []
    P = lambda key, period, text, cell, note=None: pins.append(dict(
        broker_id=B, key=key, period_key=period, value=None, value_text=text, excel_cell=cell, note=note))
    P('fo_first_calibrated_quarter', '', 'Q2 FY 2026', 'backtesting F&O!AM56')
    P('fo_last_actual_quarter', '', 'Q4 FY 2026', 'backtesting F&O!AO56',
      'Q1 FY27 F&O is reported (L7, L55) but not fed')
    P('cash_first_calibrated_quarter', '', 'Q2 FY 2026', 'cash market!K38')
    P('cash_last_actual_quarter', '', 'Q1 FY 2027', 'cash market!K41')
    P('comm_calibration_quarter', '', 'Q3 FY 2026', 'Commodities!S3:S8', 'one-off, never refreshed')
    P('mtf_last_actual_quarter', '', 'Q1 FY 2027', 'MTF data!J57')
    for q, text, cell in (('Q2 FY 2026', 'total_income', 'H17'), ('Q3 FY 2026', 'total_income', 'I17'),
                          ('Q4 FY 2026', 'total_income_ex_fisdom_amc', 'J17'),
                          ('Q1 FY 2027', 'total_income_ex_fisdom_amc', 'L18')):
        P('revenue_base', q, text, f'{WG}!{cell}', 'metric used as the base of the revenue mix')
    return dict(broker_id=B, tag=tag, source_workbook=os.path.basename(WORKBOOK[0]), facts=facts,
                assumptions=assumptions, pins=pins)


WORKBOOK = ['']


# ── feeder columns ──
FEEDERS = {
    'backtesting F&O!AD': ('backtesting F&O', 'B', 'AD', 4, 761),
    'backtesting cash!V': ('backtesting cash', 'B', 'V', 3, 760),
    'Commodities!K': ('Commodities', 'B', 'K', 2, 661),
    'MTF data (2)!L': ('MTF data (2)', 'B', 'L', 12, 518),
}


def feeder_column(wbv, sheet, dcol, vcol, r0, r1):
    ws, out = wbv[sheet], {}
    for r in range(r0, r1 + 1):
        d = ws[f'{dcol}{r}'].value
        if not isinstance(d, dt.datetime):
            continue
        v = ws[f'{vcol}{r}'].value
        if v is None:
            continue
        out[d.date().isoformat()] = v if isinstance(v, (int, float)) else str(v)   # '#N/A'
    return out


def calibration(wbv):
    """Cached quarterly parameters the daily columns read: take rates, shares, orders per contract/trade."""
    bf, cm, co, md = wbv['backtesting F&O'], wbv['cash market'], wbv['Commodities'], wbv['MTF data']
    out = {'fo': {}, 'cash': {}, 'mtf': {}, 'comm': {}}
    for c in ('AM', 'AN', 'AO', 'AP', 'AQ', 'AR'):                              # AM48:AR57
        out['fo'][bf[f'{c}48'].value] = dict(cpo_q=bf[f'{c}55'].value, take_rate=bf[f'{c}56'].value,
                                             share=bf[f'{c}57'].value)
    for r in range(38, 44):                                                       # cash market F38:L43
        out['cash'][cm[f'F{r}'].value] = dict(tpo=cm[f'G{r}'].value, take_rate=cm[f'K{r}'].value, share=cm[f'L{r}'].value)
    for r in range(51, 61):                                                       # MTF data C51:J60
        out['mtf'][md[f'C{r}'].value.strip()] = dict(share=md[f'J{r}'].value, groww_book_cr=md[f'I{r}'].value)
    for key, r in (('rev_mn', 3), ('take_rate', 5), ('orders_mn', 6), ('mkt_orders_mn', 7), ('share0', 8), ('growth', 9)):
        out['comm'][key] = co[f'S{r}'].value                                      # Commodities!S3:S9
    return out


# ── SUMMARY - Groww cells ──
def colnum(c):
    n = 0
    for ch in c:
        n = n * 26 + ord(ch) - 64
    return n


BANDS = {(3, 26): ('Consolidated', 'Broking'), (30, 53): ('MTF', 'F&O'), (56, 79): ('Cash', 'Commodities')}
MARK = {'Financial Year': 'Financial Year', 'Quarter>>': 'Quarter', 'Month>>': 'Month', 'Week>>': 'Week'}


def summary_cells(wbv):
    """Numeric cells (and the '-' cells) of the six panels. Left panel B:J, right panel L:T; the stray typed
    zeros in K144:M163 belong to no panel and are left out."""
    V = wbv['SUMMARY - Groww']
    num, dash = [], []
    for row in V.iter_rows():
        for cell in row:
            cv, r, c = cell.value, cell.row, cell.column
            if cv is None or isinstance(cv, bool):
                continue
            isnum = isinstance(cv, (int, float))
            if not (isnum or cv == '-'):
                continue
            panel = None
            for (r1, r2), (lp, rp) in BANDS.items():
                if r1 <= r <= r2:
                    panel = lp if 2 <= c <= 10 else rp if 12 <= c <= 20 else None
            if panel is None:
                continue
            lc = {3: 2, 4: 2, 5: 2, 13: 12, 14: 12, 15: 12, 8: 7, 9: 7, 10: 7, 18: 17, 19: 17, 20: 17}.get(c)
            if lc is None:
                continue
            sec = hdr = None
            for rr in range(r, 0, -1):
                lv = V.cell(rr, lc).value
                if isinstance(lv, str) and lv.strip() == '' and V.cell(rr, c).value in ('Total', 'YoY') and lc == 12:
                    sec, hdr = 'Financial Year', V.cell(rr, c).value
                    break
                if isinstance(lv, str) and lv.strip() in MARK:
                    sec, hdr = (MARK[lv.strip()] if lc in (2, 12) else 'Weekday'), V.cell(rr, c).value
                    break
            lab = V.cell(r, lc).value
            item = dict(cell=cell.coordinate, panel=panel, section=sec,
                        label=lab.strip() if isinstance(lab, str) else lab,
                        header=hdr.strip() if isinstance(hdr, str) else hdr, value=cv)
            (num if isnum else dash).append(item)
    return num, dash


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    tag = sys.argv[sys.argv.index('--tag') + 1] if '--tag' in sys.argv else '2026-10-23'
    if '--tag' in sys.argv:
        args.remove(tag)
    wb_path, out = args[0], args[1]
    WORKBOOK[0] = wb_path
    wbv = openpyxl.load_workbook(wb_path, data_only=True)
    snap = build_snapshot(wbv, tag)
    daily = {k: feeder_column(wbv, *v) for k, v in FEEDERS.items()}
    num, dash = summary_cells(wbv)
    fixtures = dict(broker_id=B, tag=tag, daily=daily, calib=calibration(wbv), summary=num, summary_dash=dash)
    json.dump(snap, open(os.path.join(out, f'groww_snapshot_{tag}.json'), 'w'), indent=1)
    json.dump(fixtures, open(os.path.join(out, f'groww_fixtures_{tag}.json'), 'w'))
    print('facts', len(snap['facts']), 'assumptions', len(snap['assumptions']), 'pins', len(snap['pins']))
    print('daily rows', {k: len(v) for k, v in daily.items()}, 'summary', len(num), 'dash', len(dash))


if __name__ == '__main__':
    main()
