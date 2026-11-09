"""Groww quarterly consolidated P&L lines from its results filings (board outcome PDFs) → staged facts.

    python3 -m src.extract.pl_groww > out/pat/facts_groww_pl.json

Reads the "Statement of the ... consolidated financial results" table of each filing (pdftotext -layout),
takes the three quarter columns (current, previous, same quarter last year) and records each line as filed
(unit Rs Mn up to the Q4 FY26 filing, Rs Cr from Q1 FY27). Overlapping quarters across filings are
cross-checked. Shares outstanding = paid-up equity capital ÷ face value (INR 2), from the latest filing that
prints it. Every fact carries the file, its sha256 and the page.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

DIR = Path('data/raw/disclosures/groww')
# file stem → (quarter keys of the three quarter columns, filing date)
FILES = {
    'BILLIONBRAINS_14012026123241_OutcomeSigned': (('Q3 FY 2026', 'Q2 FY 2026', 'Q3 FY 2025'), '2026-01-14'),
    'BILLIONBRAINS_20042026130140_Boardoutcomesigned': (('Q4 FY 2026', 'Q3 FY 2026', 'Q4 FY 2025'), '2026-04-20'),
    'BILLIONBRAINS_15072026112913_outcomefinal': (('Q1 FY 2027', 'Q4 FY 2026', 'Q1 FY 2026'), '2026-07-15'),
    'BILLIONBRAINS_14102026124408_outcomefinalsigned': (('Q2 FY 2027', 'Q1 FY 2027', 'Q2 FY 2026'), '2026-10-14'),
}
# metric → label regex (start of line, inside the consolidated statement)
LINES = [
    ('pl_revenue_ops', r'Revenue from operations\b'),
    ('pl_other_income', r'Other income\b'),
    ('pl_total_income', r'Total income\b'),
    ('pl_employee', r'Employee benefits? expenses?\b'),
    ('pl_finance_cost', r'Finance costs?\b'),
    ('pl_depreciation', r'Depreciation and amortisation expense\b'),
    ('pl_other_expenses', r'Other expenses\b'),
    ('pl_total_expenses', r'Total expenses\b'),
    ('pl_pbt', r'Profit before (income )?tax for the (period|year|period/year)\b'),
    ('pl_tax', r'Total tax expense\b'),
    ('pl_pat', r'Profit for the (period|year|period/year)\b'),
]
NUM = r'\(?-?[\d,]+\.\d+\)?|-(?=\s|$)'


def _num(s):
    if s == '-':
        return 0.0
    neg = s.startswith('(')
    v = float(s.strip('()').replace(',', ''))
    return -v if neg else v


def statement(path):
    txt = subprocess.run(['pdftotext', '-layout', str(path), '-'], capture_output=True, text=True, check=True).stdout
    pages = txt.split('\f')
    for i, p in enumerate(pages, 1):
        m = re.search(r'Statement of the (un)?audited consolidated financial results', p)
        if m:
            unit = 'Rs Cr' if re.search(r'INR Crores', p) else 'Rs Mn' if re.search(r'INR (Million|Mn)', p) else None
            return i, p[m.start():], unit
    raise ValueError(f'{path.name}: no consolidated statement found')


def extract(stem, quarters, filed):
    path = DIR / f'{stem}.pdf'
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    page, text, unit = statement(path)
    if unit is None:
        raise ValueError(f'{stem}: unit not stated on the statement page')
    facts, seen = [], set()
    for metric, rx in LINES:
        for line in text.splitlines():
            s = line.strip()
            if metric in seen or not re.match(rx, s):
                continue
            nums = re.findall(NUM, s[re.match(rx, s).end():])
            if len(nums) < 3:
                continue
            seen.add(metric)
            for q, v in zip(quarters, nums[:3]):
                facts.append(dict(broker_id='GROWW', period_type='Q', period_key=q, metric=metric, segment='consolidated',
                                  value=_num(v), unit=unit, doc_id=sha, page=str(page),
                                  table_label=f'Statement of consolidated financial results: {s[:60].strip()}',
                                  source_ref=f'results_outcome:{path.name}#page={page}', filing_date=filed))
    missing = [m for m, _ in LINES if m not in seen]
    if missing:
        raise ValueError(f'{stem}: lines not found: {missing}')
    cap = re.search(r'Paid up equity share capital \(Face Value : INR (\d+)/- per share\)\s+(' + NUM + r')', text)
    return facts, (cap and dict(face_value=float(cap.group(1)), capital=_num(cap.group(2)), unit=unit, page=page,
                                source_ref=f'results_outcome:{path.name}#page={page}', doc_id=sha, filed=filed))


def to_cr(f):
    return f['value'] / 10 if f['unit'] == 'Rs Mn' else f['value']


def main():
    allf, caps = [], []
    for stem, (qs, filed) in FILES.items():
        f, cap = extract(stem, qs, filed)
        allf += f
        if cap:
            caps.append(cap)
    # one fact per (quarter, metric): the latest filing wins; earlier ones must agree within rounding
    best, conflicts = {}, []
    for f in sorted(allf, key=lambda x: x['filing_date']):
        k = (f['period_key'], f['metric'])
        if k in best and abs(to_cr(best[k]) - to_cr(f)) > 0.06:
            conflicts.append(dict(key=k, earlier=(to_cr(best[k]), best[k]['source_ref']), later=(to_cr(f), f['source_ref'])))
        best[k] = f
    facts = sorted(best.values(), key=lambda x: (x['period_key'], x['metric']))
    cap = max(caps, key=lambda c: c['filed'])
    shares = dict(broker_id='GROWW', period_type='Q', period_key=None, metric='shares_outstanding_cr', segment='consolidated',
                  value=round((cap['capital'] / 10 if cap['unit'] == 'Rs Mn' else cap['capital']) / cap['face_value'], 4),
                  unit='crore shares', doc_id=cap['doc_id'], page=str(cap['page']), source_ref=cap['source_ref'],
                  table_label=f"Paid up equity share capital {cap['capital']} {cap['unit']} ÷ face value INR {cap['face_value']:g}",
                  filing_date=cap['filed'])
    json.dump(dict(facts=facts, shares=shares, conflicts=conflicts), sys.stdout, indent=1)


if __name__ == '__main__':
    main()
