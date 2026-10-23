"""PLAN 4.2 filing watcher: NSE announcements -> sb_documents + staged facts, with fakes for NSE and the DB."""
import datetime as dt
import hashlib
import json
import shutil
from pathlib import Path

import pytest

from src.extract import angel_monthly, angel_press, watch_filings as W

FIX = Path(__file__).parent / 'fixtures'
ROOT = Path(__file__).resolve().parents[2]
BASE = 'https://nsearchives.nseindia.com/corporate/'
SEP = 'ANGEL8896_06102026073616_October062026_Intimation_of_Business_updates.pdf'
NOV = 'ANGEL8896_06112026073500_November062026_Intimation_of_Business_Update.pdf'   # synthetic, the exit test
PR = 'ANGEL8896_15102026175127_CoveringPressRelease.pdf'


def ann(an_dt, desc, fn, text='', seq='1'):
    return dict(an_dt=an_dt, desc=desc, attchmntFile=BASE + fn, attchmntText=text, seq_id=seq, symbol='ANGELONE')


ANNS = [
    ann('06-Nov-2026 07:35:12', 'Monthly Business Updates', NOV,
        'Angel One Limited has informed the Exchange regarding Monthly Business Updates for the month of October 2026',
        '200'),
    ann('15-Oct-2026 17:52:26', 'Press Release', PR, 'press release Q2 FY27', '101'),
    ann('15-Oct-2026 17:27:39', 'Record Date', 'ANGEL8896_15102026172717_OutcomeoftheBoardmeeting15102026.pdf'),
    ann('06-Oct-2026 07:36:59', 'Monthly Business Updates', SEP,
        'regarding Monthly Business Updates for the month of September 2026', '99'),
    ann('21-Oct-2026 12:29:50', 'Analysts/Institutional Investor Meet/Con. Call Updates', 'ANGEL8896_x_transcript.pdf'),
]


def pdf_bytes(name):
    return b'%PDF-1.6\n% test file ' + name.encode() + b'\n%%EOF\n'


class Resp:
    def __init__(self, status=200, body=None, content=b''):
        self.status_code, self._body, self.content = status, body, content
        self.text = json.dumps(body) if body is not None else content.decode('latin-1')

    def json(self):
        if self._body is None:
            raise ValueError('no JSON')
        return self._body


class FakeNSE:
    def __init__(self, anns=ANNS, api_status=200, pdfs=None):
        self.anns, self.api_status, self.calls = anns, api_status, []
        self.pdfs = pdfs or {}

    def get(self, url, params=None, headers=None, timeout=None):
        self.calls.append(url)
        if url == W.NSE_API:
            return Resp(self.api_status, self.anns if self.api_status == 200 else None,
                        b'' if self.api_status == 200 else b'<html>Access Denied</html>')
        fn = url.rsplit('/', 1)[1]
        return Resp(200, content=self.pdfs.get(fn, pdf_bytes(fn)))


class FakeReader:
    def __init__(self, docs, facts=()):
        self.docs, self.facts = list(docs), list(facts)

    def table(self, name, **eq):
        rows = self.docs if name == 'sb_documents' else self.facts
        return [r for r in rows if all(str(r.get(k)) == str(v) for k, v in eq.items())]


class FakeWriter:
    def __init__(self, start=700):
        self.calls, self.next_id = [], start

    def insert(self, table, rows, returning=False):
        self.calls.append(('insert', table, rows))
        if not returning:
            return len(rows)
        out = []
        for r in rows:
            out.append(dict(r, fact_id=self.next_id))
            self.next_id += 1
        return out

    def update(self, table, values, **eq):
        self.calls.append(('update', table, values, eq))


def sha(b):
    return hashlib.sha256(b).hexdigest()


def known_rows():
    return [dict(doc_id='6f5e746b-79c0-4684-b857-7f821a8009b9', broker_id='ANGELONE', url=BASE + SEP,
                 sha256=sha(pdf_bytes(SEP)), note=None),
            dict(doc_id='b3bcbddb-ba85-4f59-8f7e-fbdce7c1f4c3', broker_id='ANGELONE', url=BASE + PR,
                 sha256=sha(pdf_bytes(PR)), note=None)]


def sep_as_october():
    """The September update's parsed table, relabelled one month on: what the October update will look like."""
    d = json.loads((FIX / 'monthly_2026-09.json').read_text())
    shift = {'FY 2027 September': 'FY 2027 October', 'FY 2027 August': 'FY 2027 September',
             'FY 2026 September': 'FY 2026 October'}
    facts = [dict(f, period_key=shift.get(f['period_key'], f['period_key'])) for f in d['facts'] if f['period_type'] == 'M']
    return facts, d['checks'][:1]


@pytest.fixture
def raw(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(W, 'RAW_DIR', tmp_path / 'raw')
    monkeypatch.setattr(angel_monthly, 'parse', lambda pdf: sep_as_october())
    return tmp_path


# ------------------------------------------------------------------ pieces

def test_select_filters_by_desc_not_file_name():
    sel = W.select(ANNS)
    assert [a['attchmntFile'].rsplit('/', 1)[1] for a in sel] == [SEP, PR, NOV]   # oldest first
    # 'Record Date' is skipped although its file is called ...OutcomeoftheBoardmeeting...
    assert all(a['desc'] != 'Record Date' for a in sel)


def test_board_meeting_outcome_is_results_only_when_it_says_so():
    a = ann('15-Oct-2026 17:18:58', 'Outcome of Board Meeting', 'x.pdf',
            'Angel One Limited has submitted to the Exchange, the financial results for the period ended September 30, 2026.')
    assert W.doc_type_for(a) == 'financial_results'
    assert W.doc_type_for(dict(a, attchmntText='approved raising funds by NCDs')) == 'other'


@pytest.mark.parametrize('d, q', [(dt.date(2026, 10, 15), 'Q2 FY 2027'), (dt.date(2026, 7, 15), 'Q1 FY 2027'),
                                  (dt.date(2027, 1, 20), 'Q3 FY 2027'), (dt.date(2026, 4, 30), 'Q4 FY 2026')])
def test_quarter_before(d, q):
    assert W.quarter_before(d) == q


def test_periods_and_labels():
    assert W.month_from_text('Monthly Business Updates for the month of October 2026') == 'FY 2027 October'
    assert W.month_from_text('for the month of January 2027') == 'FY 2027 January'
    assert W.month_label('FY 2027 October') == 'October 2026'
    assert W.month_label('FY 2027 February') == 'February 2027'
    assert W.published_at(ANNS[0]) == '2026-11-06T07:35:12+05:30'


def test_blocked_api_raises(monkeypatch):
    monkeypatch.setattr(W, 'RETRY_WAIT', 0)
    with pytest.raises(W.SourceBlocked, match='HTTP 403'):
        W.fetch_announcements(FakeNSE(api_status=403), dt.date(2026, 10, 1), dt.date(2026, 11, 6))


def test_html_instead_of_pdf_is_a_problem_not_a_document(raw):
    nse = FakeNSE(pdfs={NOV: b'<html>Access Denied</html>'})
    items = W.plan(ANNS, W.known_documents(FakeReader(known_rows())), nse, {})
    assert len(items) == 1 and items[0]['doc'] is None
    assert 'not a PDF' in items[0]['problems'][0]


# ------------------------------------------------------------------ the exit test: a new monthly update is staged

def test_new_monthly_update_is_staged(raw, capsys):
    reader, writer, nse = FakeReader(known_rows()), FakeWriter(), FakeNSE()
    rc = W.main(['--write'], session=nse, reader=reader, writer=writer, today=dt.date(2026, 11, 6))
    assert rc == 0
    # only the new filing is downloaded; the two known ones are matched on URL
    assert [u for u in nse.calls if u != W.NSE_API] == [BASE + NOV]
    ins = [c for c in writer.calls if c[0] == 'insert']
    assert [c[1] for c in ins] == ['sb_documents', 'sb_disclosure_facts']
    doc = ins[0][2][0]
    assert doc['doc_type'] == 'monthly_update' and doc['period_key'] == 'FY 2027 October'
    assert doc['title'] == 'Monthly business update — October 2026'
    assert doc['url'] == BASE + NOV and doc['file_path'] == 'broker_db/data/raw/disclosures/angelone/' + NOV
    assert doc['sha256'] == sha(pdf_bytes(NOV)) and doc['published_at'] == '2026-11-06T07:35:12+05:30'
    assert doc['note'].startswith(W.PENDING_MARK)                      # until the facts are in
    facts = ins[1][2]
    assert len(facts) == 17 and {f['status'] for f in facts} == {'staged'}
    assert {f['extracted_by'] for f in facts} == {'parser'} and {f['doc_id'] for f in facts} == {doc['doc_id']}
    td = next(f for f in facts if f['metric'] == 'trading_days')
    assert (td['period_key'], td['value'], td['page'], td['source_ref']) == \
        ('FY 2027 October', 21.0, '1', f'monthly_update:{NOV}#page=1')
    assert next(f for f in facts if f['metric'] == 'share_comm')['value'] == 0.417          # no float noise
    # final note replaces the pending mark
    upd = writer.calls[-1]
    assert upd[0] == 'update' and upd[3] == {'doc_id': doc['doc_id']} and not upd[2]['note'].startswith(W.PENDING_MARK)
    s = (raw / 'out/filings/2026-11-06/summary.md').read_text()
    assert '1 new document(s), 17 fact(s) staged' in s and 'fact_id 700–716' in s
    assert (raw / 'raw' / NOV).exists()


def test_dry_run_writes_nothing_but_sql_and_summary(raw):
    writer = FakeWriter()
    rc = W.main([], session=FakeNSE(), reader=FakeReader(known_rows()), writer=writer, today=dt.date(2026, 11, 6))
    assert rc == 0 and writer.calls == []
    sql = (raw / 'out/filings/2026-11-06/stage.sql').read_text()
    assert sql.startswith('begin;\ninsert into sb_documents') and sql.rstrip().endswith('commit;')
    assert sql.count('insert into sb_disclosure_facts') == 17
    payload = json.loads((raw / 'out/filings/2026-11-06/payload.json').read_text())
    assert len(payload['sb_documents']) == 1 and len(payload['sb_disclosure_facts']) == 17


def test_nothing_new_is_quiet(raw):
    rows = known_rows() + [dict(doc_id='n', broker_id='ANGELONE', url=BASE + NOV, sha256='x', note='watcher: ...')]
    writer = FakeWriter()
    assert W.main(['--write'], session=FakeNSE(), reader=FakeReader(rows), writer=writer,
                  today=dt.date(2026, 11, 6)) == 0
    assert writer.calls == []
    assert 'No new filings' in (raw / 'out/filings/2026-11-06/summary.md').read_text()


def test_same_file_under_a_new_url_is_skipped_by_sha(raw):
    rows = known_rows()
    rows[0]['sha256'] = sha(pdf_bytes(NOV))                  # the Nov PDF is byte-identical to a known document
    items = W.plan(ANNS, W.known_documents(FakeReader(rows)), FakeNSE(), {})
    assert len(items) == 1 and items[0]['doc'] is None and 'same file (sha256)' in items[0]['skipped']


def test_pending_document_gets_its_facts_on_the_next_run(raw):
    rows = known_rows() + [dict(doc_id='11111111-2222-3333-4444-555555555555', broker_id='ANGELONE', url=BASE + NOV,
                                sha256=sha(pdf_bytes(NOV)), note=W.PENDING_MARK + " — watcher: NSE 'x'")]
    writer = FakeWriter()
    W.main(['--write'], session=FakeNSE(), reader=FakeReader(rows), writer=writer, today=dt.date(2026, 11, 6))
    assert [c[1] for c in writer.calls if c[0] == 'insert'] == ['sb_disclosure_facts']          # no second doc row
    assert {f['doc_id'] for f in writer.calls[0][2]} == {'11111111-2222-3333-4444-555555555555'}


def test_prior_columns_are_checked_against_reviewed_facts(raw):
    facts, checks = sep_as_october()
    # the 'previous' column (now FY 2027 September) disagrees with a reviewed Sep fact -> reported, not staged
    reviewed = [dict(fact_id=547, broker_id='ANGELONE', metric='client_base', period_key='FY 2027 September',
                     segment='', value='39.90', status='reviewed')]
    prev = next(f for f in facts if f['metric'] == 'client_base' and f['column'] == 'previous')
    items = W.plan(ANNS, W.known_documents(FakeReader(known_rows())), FakeNSE(),
                   W.reviewed_facts(FakeReader([], reviewed)))
    r = items[0]['restated']
    assert r == [dict(metric='client_base', period_key='FY 2027 September', column='previous', new=prev['value'],
                      reviewed=39.9, fact_id=547, page='1')]
    assert 'Differs from reviewed fact 547' in W.summary_md(items, dict(run_date='d', since='s', until='u',
                                                                        n_announcements=5, n_watched=3, mode='dry run'))


def test_deck_is_registered_without_facts_and_flagged(raw):
    deck = ann('15-Jan-2027 17:46:16', 'Investor Presentation', 'ANGEL8896_15012027174556_InvestorPresentation.pdf',
               'Angel One Limited has informed the Exchange about Investor Presentation')
    items = W.plan([deck], W.known_documents(FakeReader([])), FakeNSE(), {})
    d = items[0]['doc']
    assert d['doc_type'] == 'investor_presentation' and d['period_key'] == 'Q3 FY 2027'
    assert d['title'] == 'Investor presentation — Q3 FY27' and items[0]['facts'] == []
    assert 'filing-extractor' in items[0]['problems'][0]


def test_blocked_nse_exits_2(raw, monkeypatch):
    monkeypatch.setattr(W, 'RETRY_WAIT', 0)
    assert W.main([], session=FakeNSE(api_status=403), reader=FakeReader([]), today=dt.date(2026, 11, 6)) == 2


@pytest.mark.parametrize('extra', [['--force', BASE + SEP], ['--db-snapshot', 'x.json']])
def test_replay_options_are_refused_with_write(extra):
    with pytest.raises(SystemExit):
        W.main(['--write'] + extra, session=FakeNSE(), reader=FakeReader([]))


def test_writer_returning_gives_the_stored_rows(monkeypatch):
    from src.live.db import KEY_ENV, SupabaseWriter

    class S:
        def __init__(self):
            self.headers = None

        def post(self, url, data, headers, timeout):
            self.headers = headers
            r = Resp(201, [dict(r, fact_id=i) for i, r in enumerate(json.loads(data), start=800)])
            return r

    monkeypatch.setenv(KEY_ENV, 'sb_secret_TEST_ONLY_not_a_real_key')
    s = S()
    w = SupabaseWriter(url='https://example.invalid', session=s)
    assert w.insert('sb_disclosure_facts', [dict(metric='a'), dict(metric='b')], returning=True) == \
        [dict(metric='a', fact_id=800), dict(metric='b', fact_id=801)]
    assert s.headers['Prefer'] == 'return=representation'
    assert w.insert('sb_disclosure_facts', [dict(metric='a')]) == 1 and s.headers['Prefer'] == 'return=minimal'


def test_sql_quotes_text():
    items = [dict(doc=dict(doc_id='d', broker_id='ANGELONE', doc_type='other', period_key=None,
                           title="Angel's outcome", url='u', file_path='f', sha256='s', published_at='p',
                           fetched_at='t', note=None), facts=[], pending_doc=False)]
    sql = W.to_sql(items, end='rollback')
    assert "'Angel''s outcome'" in sql and 'null' in sql and sql.rstrip().endswith('rollback;')


# ------------------------------------------------------------------ press release parser

def test_press_release_parser_matches_the_hand_staged_q2_fy27_values():
    facts, checks = angel_press.parse_pages(['page 1', (FIX / 'press_q2fy27_p2.txt').read_text()])
    got = {(f['metric'], f['period_key']): f['value'] for f in facts if f['column'] == 'current'}
    assert got == {('orders_fo', 'Q2 FY 2027'): 256, ('orders_cash', 'Q2 FY 2027'): 66,
                   ('orders_comm', 'Q2 FY 2027'): 45, ('total_income', 'Q2 FY 2027'): 14315,
                   ('total_income_standalone', 'Q2 FY 2027'): 14007}           # facts staged 23 Oct (478–655)
    assert {f['page'] for f in facts} == {'2'}
    assert checks == [dict(check='F&O + Cash + Commodity vs Total orders (Q2 FY 2027)', expected=366, computed=367,
                           ok=True)]


RAWPDF = ROOT / 'data/raw/disclosures/angelone' / SEP


@pytest.mark.skipif(not (shutil.which('pdftotext') and RAWPDF.exists()), reason='needs pdftotext and the raw PDF')
def test_real_monthly_pdf_parses_to_the_reviewed_figures():
    staged, compare, checks = W.parse_monthly(RAWPDF)
    got = {(f['metric'], f['period_key']): f['value'] for f in staged}
    assert len(staged) == 34 and all(c['ok'] for c in checks)
    assert got[('avg_funding_book', 'Q2 FY 2027')] == 74530.0 and got[('adto_fo', 'Q2 FY 2027')] == 123.0
    assert got[('share_comm', 'FY 2027 September')] == 0.417                # fact 562
