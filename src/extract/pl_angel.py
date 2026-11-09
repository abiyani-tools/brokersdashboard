"""Angel One quarterly consolidated P&L lines from its investor presentations → staged facts.

    python3 -m src.extract.pl_angel > out/pat/facts_angel_pl.json

The board-outcome PDF's results statement is a scanned image, so the source is the presentation's
"Consolidated profit & loss statement" table (Rs Mn), which prints the quarter, the previous quarter, the
same quarter last year, FY26 and FY25. Q3 FY26 is derived as FY26 − Q1 − Q2 − Q4 FY26 (shown in the note).
Overlapping quarters across presentations are cross-checked.

Shares outstanding: the presentation prints no share count. It prints net worth (balance sheet, Rs Mn) and
book value per share, so shares = net worth ÷ book value per share (derived, flagged as such).
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

DIR = Path('data/raw/disclosures/angelone')
# file stem → (column keys of the P&L table, filing date)
FILES = {
    'ANGEL8896_15072026184909_15072026InvestorPresentationAOLupdate':
        (('Q1 FY 2027', 'Q4 FY 2026', 'Q1 FY 2026', 'FY 2026', 'FY 2025'), '2026-07-15'),
    'ANGEL8896_15102026174556_CoveringInvestorsPresentation':
        (('Q2 FY 2027', 'Q1 FY 2027', 'Q2 FY 2026', 'FY 2026', 'FY 2025'), '2026-10-15'),
}
LINES = [
    ('trading_days', r'# of Trading Days'),
    ('pl_interest_income', r'\(a\) Interest Income'),
    ('pl_fees_commission', r'\(b\) Fees and commission income'),
    ('pl_fv_gain', r'\(c\) Net gain on fair value changes'),
    ('pl_revenue_ops', r'Total Revenue from operations'),
    ('pl_other_income', r'\(d\) Other Income'),
    ('pl_total_income', r'Total Income \(I\+II=III\)'),
    ('pl_finance_cost', r'\(a\) Finance costs'),
    ('pl_fee_commission_expense', r'\(b\) Fees and commission expense'),
    ('pl_impairment', r'\(c\) Impairment on financial instruments'),
    ('pl_employee', r'\(d\) Employee benefits expenses'),
    ('pl_esop', r'\(e\) Expense on Employee Stock Option Scheme'),
    ('pl_depreciation', r'\(f\) Depreciation, amortization and impairment'),
    ('pl_other_expenses', r'\(g\) Other expenses'),
    ('pl_total_expenses', r'Total Expenses \(IV\)'),
    ('pl_pbt', r'Profit before tax'),
    ('pl_tax', r'Total Income tax expense'),
    ('pl_pat', r'Profit for the period / year \(VIII-IX=X\)'),
]
NUM = r'-?[\d,]+(?:\.\d+)?'


def pages(path):
    return subprocess.run(['pdftotext', '-layout', str(path), '-'], capture_output=True, text=True, check=True).stdout.split('\f')


def extract(stem, cols, filed):
    path = DIR / f'{stem}.pdf'
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    pg = next((i for i, p in enumerate(pages(path), 1) if 'Consolidated profit & loss statement' in p), None)
    if pg is None:
        raise ValueError(f'{stem}: no consolidated P&L table')
    text = pages(path)[pg - 1]
    text = text[text.index('Consolidated profit & loss statement'):]
    facts, seen = [], set()
    for metric, rx in LINES:
        for line in text.splitlines():
            s = line.strip()
            m = re.match(rx, s)
            if metric in seen or not m:
                continue
            nums = re.findall(NUM, s[m.end():])
            if len(nums) < len(cols):
                continue
            seen.add(metric)
            for k, v in zip(cols, nums[:len(cols)]):
                facts.append(dict(broker_id='ANGELONE', period_type='FY' if k.startswith('FY') else 'Q', period_key=k,
                                  metric=metric, segment='consolidated', value=float(v.replace(',', '')),
                                  unit='days' if metric == 'trading_days' else 'Rs Mn', doc_id=sha, page=str(pg),
                                  table_label=f'Consolidated profit & loss statement: {s[:55].strip()}',
                                  source_ref=f'investor_presentation:{path.name}#page={pg}', filing_date=filed))
    missing = [m for m, _ in LINES if m not in seen]
    if missing:
        raise ValueError(f'{stem}: lines not found: {missing}')
    return facts, sha


def shares(stem):
    """Net worth (Sep '26, Rs Mn) ÷ book value per share → crore shares."""
    path = DIR / f'{stem}.pdf'
    for i, p in enumerate(pages(path), 1):
        if 'Summary of consolidated balance sheet' in p:
            nw = re.search(r'\n\s*Networth\s+(' + NUM + r')', p)
            bv = re.search(r'Book Value: ₹\s*([\d.]+) as on ([A-Za-z]+ \d+, \d{4})', p)
            if nw and bv:
                net, bvps = float(nw.group(1).replace(',', '')), float(bv.group(1))
                return dict(broker_id='ANGELONE', period_type='Q', period_key='Q2 FY 2027', metric='shares_outstanding_cr',
                            segment='consolidated', value=round(net / bvps / 10, 4), unit='crore shares',
                            doc_id=hashlib.sha256(path.read_bytes()).hexdigest(), page=str(i),
                            source_ref=f'investor_presentation:{path.name}#page={i}',
                            table_label=f'Networth {net:,.0f} Rs Mn ÷ book value Rs {bvps} per share ({bv.group(2)})',
                            note='[DERIVED: the filing prints no share count; net worth ÷ book value per share. '
                                 'Replace with the shareholding-pattern count when staged]')
    raise ValueError(f'{stem}: net worth / book value not found')


def main():
    allf = []
    for stem, (cols, filed) in FILES.items():
        allf += extract(stem, cols, filed)[0]
    best, conflicts = {}, []
    for f in sorted(allf, key=lambda x: x['filing_date']):
        k = (f['period_key'], f['metric'])
        if k in best and abs(best[k]['value'] - f['value']) > 1.01:   # the tables print whole Rs Mn
            conflicts.append(dict(key=k, earlier=(best[k]['value'], best[k]['source_ref']), later=(f['value'], f['source_ref'])))
        best[k] = f
    # Q3 FY26 = FY26 − Q1 − Q2 − Q4 FY26 (all four in the two tables)
    for metric, _ in LINES:
        parts = [best.get((q, metric)) for q in ('FY 2026', 'Q1 FY 2026', 'Q2 FY 2026', 'Q4 FY 2026')]
        if all(parts):
            v = parts[0]['value'] - sum(p['value'] for p in parts[1:])
            best[('Q3 FY 2026', metric)] = dict(parts[0], period_type='Q', period_key='Q3 FY 2026', value=v,
                                                table_label=parts[0]['table_label'] + ' (derived)',
                                                source_ref='; '.join(sorted({p['source_ref'] for p in parts})),
                                                note=f'[DERIVED: FY26 {parts[0]["value"]:g} − Q1 {parts[1]["value"]:g} − '
                                                     f'Q2 {parts[2]["value"]:g} − Q4 {parts[3]["value"]:g}]')
    facts = sorted(best.values(), key=lambda x: (x['period_key'], x['metric']))
    json.dump(dict(facts=facts, shares=shares('ANGEL8896_15102026174556_CoveringInvestorsPresentation'),
                   conflicts=conflicts), sys.stdout, indent=1)


if __name__ == '__main__':
    main()
