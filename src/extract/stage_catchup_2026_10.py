"""Build the staged documents + facts for the Oct-2026 catch-up (Jun–Sep 2026 monthly updates, Q1/Q2 FY27,
Q3 FY26 correction, Q2 FY27 deck revenue mix). Output: catchup_payload.json for the loader.

Every fact carries doc_id + page + table label; status = 'staged' until AB approves it on the review page.
"""
import json, glob, uuid, datetime as dt

NOW = dt.datetime.now(dt.timezone.utc).isoformat()
B = 'ANGELONE'
BASE = 'https://nsearchives.nseindia.com/corporate/'
sha = dict(reversed(l.split()) for l in open('data/raw_sha256.txt'))

DOCS = {  # file -> (doc_type, period_key, published_at IST, title)
    'ANGEL8896_03072026073737_July032026_Intimation_of_Business_Update.pdf': ('monthly_update', 'FY 2027 June', '2026-07-03T07:37:49+05:30', 'Monthly business update — June 2026 & Q1 FY27'),
    'ANGEL8896_05082026080431_IntimationBU.pdf': ('monthly_update', 'FY 2027 July', '2026-08-05T08:05:45+05:30', 'Monthly business update — July 2026'),
    'ANGEL8896_04092026073149_September042026__Intimation_of_Business_Update.pdf': ('monthly_update', 'FY 2027 August', '2026-09-04T07:32:06+05:30', 'Monthly business update — August 2026'),
    'ANGEL8896_06102026073616_October062026_Intimation_of_Business_updates.pdf': ('monthly_update', 'FY 2027 September', '2026-10-06T07:36:59+05:30', 'Monthly business update — September 2026 & Q2 FY27'),
    'ANGEL8896_15102026175127_CoveringPressRelease.pdf': ('press_release', 'Q2 FY 2027', '2026-10-15T17:52:26+05:30', 'Press release — Q2 FY27 business performance'),
    'ANGEL8896_15102026174556_CoveringInvestorsPresentation.pdf': ('investor_presentation', 'Q2 FY 2027', '2026-10-15T17:46:16+05:30', 'Investor presentation — Q2 FY27'),
    'ANGEL8896_15102026171541_Outcome.pdf': ('financial_results', 'Q2 FY 2027', '2026-10-15T17:18:58+05:30', 'Outcome of board meeting — Q2 FY27 financial results (pp. 3–15 scanned)'),
    'ANGEL8896_15072026175453_15072026Press_Release_AOL.pdf': ('press_release', 'Q1 FY 2027', '2026-07-15T17:55:11+05:30', 'Press release — Q1 FY27'),
    'ANGEL8896_15072026180330_15072026InvestorPresentationAOL.pdf': ('investor_presentation', 'Q1 FY 2027', '2026-07-15T18:03:45+05:30', 'Investor presentation — Q1 FY27 (original; superseded 18:49)'),
    'ANGEL8896_15072026184909_15072026InvestorPresentationAOLupdate.pdf': ('investor_presentation', 'Q1 FY 2027', '2026-07-15T18:49:26+05:30', 'Investor presentation — Q1 FY27 (updated version)'),
    'Q3FY26_Press_release_final_1768485161540.pdf': ('press_release', 'Q3 FY 2026', '2026-01-15T00:00:00+05:30', 'Press release — Q3 FY26 (Angel One website copy)'),
}
docs, doc_id = [], {}
for fn, (t, pk, pub, title) in DOCS.items():
    i = str(uuid.uuid4()); doc_id[fn] = i
    url = ('https://w3assets.angelone.in/wp-content/uploads/pdf/1768485161540-Press-release-final.pdf'
           if fn.startswith('Q3FY26') else BASE + fn)
    docs.append(dict(doc_id=i, broker_id=B, doc_type=t, period_key=pk, title=title, url=url,
                     file_path='broker_db/data/raw/disclosures/angelone/' + fn, sha256=sha[fn], published_at=pub,
                     fetched_at=NOW, note=None))

facts = []
def add(fn, pt, pk, metric, value, unit, page, label, by='parser', note=None, segment=''):
    facts.append(dict(fact_id=None, broker_id=B, period_type=pt, period_key=pk, metric=metric, segment=segment,
                      value=value, unit=unit, doc_id=doc_id[fn], page=str(page), table_label=label,
                      source_ref=f'{DOCS[fn][0]}:{fn}#page={page}', extracted_by=by, status='staged',
                      reviewed_at=None, supersedes=None, note=note, created_at=NOW))

# (a) monthly-update tables: 'current' column of every table; quarterly names aligned with the seeded metrics
QALIAS = {'adto_premium_fo_q': 'adto_fo'}
for fn in sorted(glob.glob('data/extracted/*.json')):
    d = json.load(open(fn)); pdf = d['pdf'].split('/')[-1]
    for f in d['facts']:
        if f['column'] != 'current':
            continue
        m = QALIAS.get(f['metric'], f['metric']) if f['period_type'] == 'Q' else f['metric']
        v, u = f['value'], f['unit']
        if m == 'avg_funding_book' and f['period_type'] == 'Q':
            v, u = round(v * 1000, 6), 'Rs Mn'                     # seeded quarterly book is in Rs Mn
        add(pdf, f['period_type'], f['period_key'], m, v, u, f['page'], f['table_label'])

# (b) corrections found by back-sourcing the comparison columns (Excel used rounded / averaged values)
BU_Q1 = 'ANGEL8896_03072026073737_July032026_Intimation_of_Business_Update.pdf'
BU_Q2 = 'ANGEL8896_06102026073616_October062026_Intimation_of_Business_updates.pdf'
for fn, pk, m, v, u, excel in [
    (BU_Q1, 'Q4 FY 2026', 'avg_funding_book', 58490.0, 'Rs Mn', 'K31 = 58000'),
    (BU_Q1, 'Q1 FY 2026', 'avg_funding_book', 42060.0, 'Rs Mn', 'H31 = 42083.33 (avg of monthly)'),
    (BU_Q2, 'Q2 FY 2026', 'avg_funding_book', 53050.0, 'Rs Mn', 'I31 = 53076.67 (avg of monthly)'),
    (BU_Q1, 'Q1 FY 2026', 'orders_total', 343.11, 'Mn', 'C178 = 343'),
    (BU_Q2, 'Q2 FY 2026', 'orders_total', 360.43, 'Mn', 'C179 = 360'),
    (BU_Q1, 'Q4 FY 2026', 'client_base', 37.39, 'Mn', 'J181 = 37.4'),
    (BU_Q1, 'Q1 FY 2026', 'client_base', 32.47, 'Mn', 'J178 = 32.5'),
    (BU_Q2, 'Q2 FY 2026', 'client_base', 34.08, 'Mn', 'J179 = 34.1'),
    (BU_Q1, 'Q4 FY 2026', 'gross_client_acq_q', 1.82, 'Mn', 'K181 = 1.8'),
    (BU_Q1, 'Q1 FY 2026', 'gross_client_acq_q', 1.55, 'Mn', 'K178 = 1.5'),
    (BU_Q2, 'Q2 FY 2026', 'gross_client_acq_q', 1.74, 'Mn', 'K179 = 1.7'),
]:
    col = 'previous' if pk == 'Q4 FY 2026' else 'year_ago'
    add(fn, 'Q', pk, m, v, u, 2, f'quarterly table, {col} column',
        note=f'Back-sourcing correction: Excel Working sheet {excel}')

# (c) Q2 FY27 press release (orders by segment; consolidated gross revenues = the Excel's "total income")
PR = 'ANGEL8896_15102026175127_CoveringPressRelease.pdf'
for m, v in (('orders_fo', 256), ('orders_cash', 66), ('orders_comm', 45)):
    add(PR, 'Q', 'Q2 FY 2027', m, v, 'Mn', 2, "No. of Orders table, Q2 '27")
add(PR, 'Q', 'Q2 FY 2027', 'total_income', 14315, 'Rs Mn', 2, 'Business Performance: Total Gross Revenues, Consolidated')
add(PR, 'Q', 'Q2 FY 2027', 'total_income_standalone', 14007, 'Rs Mn', 2, 'Business Performance: Total Gross Revenues, Standalone')

# (d) Q3 FY26 press release — resolves Working sheet J8 typo (36)
PR3 = 'Q3FY26_Press_release_final_1768485161540.pdf'
add(PR3, 'Q', 'Q3 FY 2026', 'orders_comm', 35, 'Mn', 2, "No. of Orders table, Q3 '26",
    note='Correction: Excel Working sheet J8 = 36 (typo); rows 174-182 use 35')
for m, v in (('orders_fo', 277), ('orders_cash', 68), ('orders_total', 380)):
    add(PR3, 'Q', 'Q3 FY 2026', m, v, 'Mn', 2, "No. of Orders table, Q3 '26", note='Confirms the seeded value')

# (e) Q2 FY27 deck, slide 30 (PDF page 31): revenue mix to one decimal, 9 quarters — read visually, sum-checked
DECK = 'ANGEL8896_15102026174556_CoveringInvestorsPresentation.pdf'
Q = ['Q2 FY 2025', 'Q3 FY 2025', 'Q4 FY 2025', 'Q1 FY 2026', 'Q2 FY 2026', 'Q3 FY 2026', 'Q4 FY 2026', 'Q1 FY 2027', 'Q2 FY 2027']
FO = [50.2, 52.5, 46.3, 45.2, 45.7, 44.3, 46.9, 45.1, 38.7]
CA = [7.8, 7.8, 8.4, 9.7, 8.4, 7.7, 7.3, 8.6, 8.7]
CO = [3.7, 4.4, 5.2, 5.5, 5.6, 6.1, 6.5, 6.4, 7.1]
GB = [61.7, 64.7, 59.9, 60.4, 59.7, 58.1, 60.7, 60.1, 54.5]
INT = [23.7, 27.6, 31.9, 31.2, 31.5, 33.0, 31.0, 32.6, 35.6]
DIS = [1.7, 2.4, 3.0, 3.1, 3.7, 4.3, 3.7, 3.0, 4.8]
for i, q in enumerate(Q):
    s = round(FO[i] + CA[i] + CO[i], 1)
    chk = f'F&O+Cash+Commodity = {s}% vs gross broking {GB[i]}% on the same slide: {"tie" if abs(s - GB[i]) < 0.05 else "DIFF"}'
    for m, v in (('revmix_fo', FO[i]), ('revmix_cash', CA[i]), ('revmix_comm', CO[i])):
        add(DECK, 'Q', q, m, round(v / 100, 4), 'fraction', 31, 'Slide 30: Composition of broking revenue in total gross revenues (%)',
            by='claude', note=chk)
    add(DECK, 'Q', q, 'revmix_broking', round(GB[i] / 100, 4), 'fraction', 31, 'Slide 30: Gross broking contribution (%)', by='claude')
    add(DECK, 'Q', q, 'revmix_int', round(INT[i] / 100, 4), 'fraction', 31, 'Slide 30: Contribution of interest income (%)', by='claude')
    add(DECK, 'Q', q, 'revmix_dist', round(DIS[i] / 100, 4), 'fraction', 31, 'Slide 30: Share of distribution revenue (%)', by='claude')
# slide 24 (page 25) pie, whole percent: depository and other income (not on slide 30)
add(DECK, 'Q', 'Q2 FY 2027', 'revmix_dep', 0.04, 'fraction', 25, 'Slide 24: Total gross income split (pie, whole %)', by='claude')
add(DECK, 'Q', 'Q2 FY 2027', 'revmix_other', 0.01, 'fraction', 25, 'Slide 24: Total gross income split (pie, whole %)', by='claude')

json.dump({'sb_documents': docs, 'sb_disclosure_facts': facts}, open('catchup_payload.json', 'w'), indent=0)
from collections import Counter
print('documents', len(docs), 'facts', len(facts))
print(Counter((f['extracted_by'], f['period_key']) for f in facts).most_common(40))
bad = [f['note'] for f in facts if f['note'] and 'DIFF' in f['note']]
print('sum-check failures:', bad)
