"""Motilal Oswal's consolidated book value by quarter, from AB's ACE Equity export, as database rows for the P/B bands
(src/engine/valuation.py build_pb; AB, 19 Nov 2026). Nothing is written to the database here.

    python3 seed/build_mosl_pb.py "../MOSL pb.xlsx"     # writes out/mosl/pb_book_ace.json and out/mosl/pb_facts.sql

Source: ACE Equity Nxt (Accord Fintech) "Motilal Oswal Financial Services Ltd. - Share Price-NSE-Daily-Adjusted", one row per
trading day with Close, Market Cap (Rs Cr) and Cons P/BV(x). AB supplied it and chose to match ACE: a quarter's book value
is in force from the day ACE switches to it (the quarter end, or the first trading day after it), not from the results date.

Per day:  consolidated net worth = Market Cap ÷ Cons P/BV;  shares (Cr) = Market Cap ÷ Close (bonus-adjusted, as the close).
A new book starts where the net worth moves by more than NW_STEP; small share-count moves inside a quarter (ESOP allotments)
change ACE's BVPS slightly but not its net worth, and are not steps (the engine divides by the share count of the step day).
Each step is labelled with the quarter that ended on or just before its first day.

out/mosl/pb_facts.sql (NOT APPLIED until AB approves): per quarter, sb_disclosure_facts net_worth (Rs Cr) and
shares_period_end_cr (Cr shares, on the step day, today's bonus-adjusted basis), consolidated, extracted_by 'claude', status
'reviewed', insert-only: a quarter that already has a (non-rejected) row of the metric is skipped, whatever its source, since
the MOSL ADR run's FactIndex refuses two facts with one (metric, period, segment); a later export adds only new quarters (to
replace a figure, reject the old row first). And the sb_assumptions row
MOSL / val_pb_dates ("Q2 FY 2027=2026-09-30; …"), upserted.
"""
import datetime as dt
import hashlib
import json
import os
import sys

import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'out', 'mosl')
FROM = '2023-06-01'      # the 3-year window from Nov 2026 starts on 2023-11-18, inside Q2 FY24's book (from 2023-10-03)
NW_STEP = 0.001
PB_DATES_NOTE = ("Day each quarter's consolidated book value comes into the P/B series (AB, 19 Nov 2026: match ACE, the "
                 "quarter end or the first trading day after it). A new quarter: add it here and its net_worth / "
                 "shares_period_end_cr facts.")
SHEET_COLS = ('Date', 'Close (Unit Curr)', 'Market Cap', 'Cons P/BV(x)')


def quarter_ended_by(d):
    """The quarter that ended on or before d: 2026-09-30 → Q2 FY 2027, 2026-10-01 → Q2 FY 2027, 2026-04-01 → Q4 FY 2026."""
    qe = dt.date(d.year, (d.month - 1) // 3 * 3 + 1, 1) - dt.timedelta(days=1)   # the last quarter end before d's quarter
    if d.month in (3, 6, 9, 12) and (d + dt.timedelta(days=1)).day == 1:
        qe = d                                                                       # d is itself a quarter end
    fy = qe.year + 1 if qe.month >= 4 else qe.year
    return f'Q{(qe.month - 4) % 12 // 3 + 1} FY {fy}', qe


def read(path):
    ws = openpyxl.load_workbook(path, data_only=True, read_only=True).worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    hdr_i = next(i for i, r in enumerate(rows) if r and r[0] == 'Date')
    hdr = list(rows[hdr_i])
    col = {c: hdr.index(c) for c in SHEET_COLS}
    out = []
    for i, r in enumerate(rows[hdr_i + 1:], start=hdr_i + 2):
        if not r or not isinstance(r[0], dt.datetime):
            continue
        c, mc, pb = r[col['Close (Unit Curr)']], r[col['Market Cap']], r[col['Cons P/BV(x)']]
        out.append(dict(date=r[0].date(), row=i, close=c, mcap=mc, pb=pb))
    return sorted(out, key=lambda x: x['date']), ws.title


def steps(days):
    """[{quarter, quarter_end, from, row, net_worth, shares, bvps, close, pb}]: the first day of each book."""
    out, prev = [], None
    for x in days:
        nw = x['mcap'] / x['pb']
        if prev is None or abs(nw / prev - 1) > NW_STEP:
            q, qe = quarter_ended_by(x['date'])
            if out and out[-1]['quarter'] == q:
                # ACE revised the quarter's book inside the quarter (Q4 FY24 on 2024-06-10, the bonus ex-date): the revised
                # figure is kept from the quarter's first day, so the P/B differs from ACE's by the revision until then
                o = out[-1]
                o['revised'] = dict(on=x['date'].isoformat(), row=x['row'], first_net_worth=o['net_worth'], first_shares=o['shares'])
                o.update(net_worth=round(nw, 2), shares=round(x['mcap'] / x['close'], 4))
                o['bvps'] = round(o['net_worth'] / o['shares'], 4)
                prev = nw
                continue
            out.append(dict(quarter=q, quarter_end=qe.isoformat(), **{'from': x['date'].isoformat()}, row=x['row'],
                            net_worth=round(nw, 2), shares=round(x['mcap'] / x['close'], 4),
                            bvps=round(x['close'] / x['pb'], 4), close=x['close'], pb=x['pb']))
        prev = nw
    return out


def sql_str(s):
    return "'" + str(s).replace("'", "''") + "'"


def main(path):
    days, sheet = read(path)
    sha = hashlib.sha256(open(path, 'rb').read()).hexdigest()
    book = [s for s in steps(days) if s['from'] >= FROM]
    qs = [s['quarter'] for s in book]
    if len(set(qs)) != len(qs):
        raise SystemExit(f'two books in one quarter: {qs}')
    fname = os.path.basename(path)
    os.makedirs(OUT, exist_ok=True)
    json.dump(dict(source=fname, sha256=sha, sheet=sheet, first_day=days[0]['date'].isoformat(),
                   last_day=days[-1]['date'].isoformat(), book=book), open(os.path.join(OUT, 'pb_book_ace.json'), 'w'), indent=1)
    lines = ['-- Motilal Oswal consolidated book value by quarter for the P/B bands (seed/build_mosl_pb.py). NOT APPLIED until AB approves.',
             f'-- Source: {fname} (ACE Equity Nxt, Accord Fintech), sha256 {sha}', 'begin;']
    for s in book:
        ref = f"ACE Equity Nxt export {fname}, sheet '{sheet}', row {s['row']} ({s['from']})"
        for metric, value, unit, label, note in (
                ('net_worth', s['net_worth'], 'Rs Cr', 'Market Cap ÷ Cons P/BV(x)',
                 f"{s['quarter']} consolidated net worth as ACE uses it from {s['from']}: market cap ÷ Cons P/BV "
                 f"(close {s['close']} ÷ {s['pb']:.4f} = BVPS {s['bvps']:.2f}). AB's choice: match ACE (book from the quarter end)."
                 + (f" ACE revised it on {s['revised']['on']} (row {s['revised']['row']}) from {s['revised']['first_net_worth']:,.1f}; "
                    f"the revised figure is used from {s['from']}." if s.get('revised') else '')),
                ('shares_period_end_cr', s['shares'], 'crore shares', 'Market Cap ÷ Close',
                 f"Equity shares on {s['from']} (bonus-adjusted, as the close), from ACE's market cap ÷ close; ACE's own share "
                 f"count moves a little inside a quarter with ESOP allotments.")):
            lines.append(
                'insert into sb_disclosure_facts (broker_id, period_type, period_key, metric, segment, value, unit, page, table_label, '
                'source_ref, extracted_by, status, reviewed_at, note)\n'
                f"select 'MOSL', 'Q', {sql_str(s['quarter'])}, '{metric}', 'consolidated', {value}, '{unit}', {sql_str('row ' + str(s['row']))}, "
                f"{sql_str(label)}, {sql_str(ref)}, 'claude', 'reviewed', now(), {sql_str(note)}\n"
                f"where not exists (select 1 from sb_disclosure_facts where broker_id = 'MOSL' and metric = '{metric}' "
                f"and period_key = {sql_str(s['quarter'])} and segment = 'consolidated' and status <> 'rejected');")
    dates = ';'.join(f"{s['quarter']}={s['from']}" for s in book)
    lines.append(
        'insert into sb_assumptions (broker_id, key, value, value_text, unit, source_ref, note) values '
        f"('MOSL', 'val_pb_dates', null, {sql_str(dates)}, 'date', "
        f"{sql_str(f'ACE Equity Nxt export {fname}: the first day each Cons P/BV book is in force')}, "
        f"{sql_str(PB_DATES_NOTE)})\n"
        'on conflict (broker_id, key) do update set value_text = excluded.value_text, source_ref = excluded.source_ref, note = excluded.note;')
    lines.append('commit;')
    open(os.path.join(OUT, 'pb_facts.sql'), 'w').write('\n'.join(lines) + '\n')
    for s in book:
        print(f"{s['quarter']:11} from {s['from']}  NW {s['net_worth']:10,.1f}  shares {s['shares']:7.4f}  BVPS {s['bvps']:7.2f}"
              + (f"  (revised by ACE on {s['revised']['on']} from {s['revised']['first_net_worth']:,.1f})" if s.get('revised') else ''))
    print(f'{len(book)} quarters; out/mosl/pb_book_ace.json, out/mosl/pb_facts.sql')


if __name__ == '__main__':
    main(sys.argv[1])
