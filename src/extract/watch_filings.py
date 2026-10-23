"""Filing watcher (PLAN 4.2): NSE corporate announcements -> new PDFs -> sb_documents + staged sb_disclosure_facts.

1. GET the NSE corporate-announcements API for ANGELONE (browser user agent; a first GET to nseindia.com sets the
   cookie when NSE asks for one) and keep the announcements whose `desc` is in DOC_TYPES. The file name is not used.
2. Skip any filing whose URL, or whose PDF's sha256, is already in sb_documents.
3. Download the PDF to data/raw/disclosures/angelone/, sha256 it, build the sb_documents row.
4. Parse it (monthly update -> angel_monthly; press release -> angel_press; decks and results have no parser yet,
   so the document is registered and the summary asks for the filing-extractor) and stage the facts with
   status 'staged', doc_id, page, table_label and source_ref '<doc_type>:<file>#page=N' (the 478–661 format).
5. Write out/filings/<date>/summary.md (+ payload.json, stage.sql) and the GitHub job summary, so AB knows what
   is waiting on the review page. Staged facts never reach the engine until AB marks them reviewed.

Nothing is written to the DB without --write. A failure after the document row is in leaves the row marked
PENDING_MARK; the next run sees the mark and stages the facts against the same doc_id.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import time
import uuid
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

BROKER = 'ANGELONE'
NSE_HOME = 'https://www.nseindia.com/'
NSE_API = 'https://www.nseindia.com/api/corporate-announcements'
NSE_REFERER = 'https://www.nseindia.com/companies-listing/corporate-filings-announcements'
UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
      'Chrome/124.0 Safari/537.36')
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
RAW_DIR = Path('data/raw/disclosures/angelone')
FILE_PATH_PREFIX = 'broker_db/data/raw/disclosures/angelone/'      # as in the rows staged so far
PENDING_MARK = 'watcher: FACTS NOT STAGED'
RETRY_WAIT = 2                                                      # seconds; x1, x2, x3 between API attempts

# NSE announcement `desc` -> sb_documents.doc_type
DOC_TYPES = {
    'Monthly Business Updates': 'monthly_update',
    'Press Release': 'press_release',
    'Investor Presentation': 'investor_presentation',
    'Outcome of Board Meeting': 'financial_results',
}
QALIAS = {'adto_premium_fo_q': 'adto_fo'}                           # quarterly names aligned with the seeded metrics
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
          'November', 'December']


class SourceBlocked(RuntimeError):
    """NSE answered with something other than the announcements JSON (block page, 401/403, captcha)."""


# ---------------------------------------------------------------- NSE

def nse_session():
    import requests
    s = requests.Session()
    s.headers.update({'User-Agent': UA, 'Accept-Language': 'en-US,en;q=0.9'})
    try:                                    # sets nsit / nseappid cookies when NSE wants them; a 403 here is normal
        s.get(NSE_HOME, timeout=20)
    except Exception:
        pass
    return s


def fetch_announcements(session, since: dt.date, until: dt.date, symbol: str = BROKER) -> List[dict]:
    params = {'index': 'equities', 'symbol': symbol,
              'from_date': since.strftime('%d-%m-%Y'), 'to_date': until.strftime('%d-%m-%Y')}
    headers = {'Accept': 'application/json', 'Referer': NSE_REFERER}
    last = ''
    for attempt in range(3):
        try:
            r = session.get(NSE_API, params=params, headers=headers, timeout=30)
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, dict):
                    data = data.get('data', [])
                if isinstance(data, list):
                    return data
            last = f'HTTP {r.status_code}: {r.text[:200]!r}'
        except ValueError as e:
            last = f'not JSON: {e}'
        except Exception as e:              # network errors: retry, then report as blocked
            last = f'{type(e).__name__}: {e}'
        time.sleep(RETRY_WAIT * (attempt + 1))
    raise SourceBlocked(f'NSE corporate-announcements API for {symbol}: {last}')


def doc_type_for(a: dict) -> Optional[str]:
    t = DOC_TYPES.get((a.get('desc') or '').strip())
    if t == 'financial_results' and 'financial result' not in (a.get('attchmntText') or '').lower():
        return 'other'                      # a board-meeting outcome that is not the results (fund raise etc.)
    return t


def select(anns: List[dict]) -> List[dict]:
    """Announcements we watch, one per attachment URL, oldest first."""
    out, seen = [], set()
    for a in sorted(anns, key=lambda a: published_at(a)):
        url = (a.get('attchmntFile') or '').strip()
        if doc_type_for(a) and url.lower().endswith('.pdf') and url not in seen:
            seen.add(url)
            out.append(a)
    return out


def published_at(a: dict) -> str:
    return dt.datetime.strptime(a['an_dt'], '%d-%b-%Y %H:%M:%S').replace(tzinfo=IST).isoformat()


# ---------------------------------------------------------------- periods

def quarter_key(year: int, month: int) -> str:
    """Indian FY quarter of a calendar month: Jun 2026 -> 'Q1 FY 2027'."""
    q = {4: 1, 5: 1, 6: 1, 7: 2, 8: 2, 9: 2, 10: 3, 11: 3, 12: 3, 1: 4, 2: 4, 3: 4}[month]
    return f'Q{q} FY {year + 1 if month >= 4 else year}'


def quarter_before(d: dt.date) -> str:
    """The last quarter that ended before d (results, decks and press releases report it)."""
    first = dt.date(d.year, d.month, 1)
    while first.month not in (1, 4, 7, 10):
        first = (first - dt.timedelta(days=1)).replace(day=1)
    end = first - dt.timedelta(days=1)
    return quarter_key(end.year, end.month)


def month_key(year: int, month: int) -> str:
    return f'FY {year + 1 if month >= 4 else year} {MONTHS[month - 1]}'


def month_from_text(text: str) -> Optional[str]:
    m = re.search(r'month of (' + '|'.join(MONTHS) + r'),?\s+(\d{4})', text or '', re.I)
    if not m:
        return None
    return month_key(int(m.group(2)), MONTHS.index(m.group(1).capitalize()) + 1)


def short_q(pk: str) -> str:
    m = re.match(r'Q(\d) FY 20(\d\d)', pk or '')
    return f'Q{m.group(1)} FY{m.group(2)}' if m else (pk or '')


def month_label(pk: str) -> str:
    m = re.match(r'FY (\d{4}) (\w+)', pk or '')
    if not m:
        return pk or ''
    fy, mon = int(m.group(1)), m.group(2)
    return f'{mon} {fy - 1 if MONTHS.index(mon) >= 3 else fy}'


# ---------------------------------------------------------------- download

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def download(session, url: str, dest_dir: Path) -> Tuple[Path, str]:
    dest_dir.mkdir(parents=True, exist_ok=True)
    path = dest_dir / url.rsplit('/', 1)[1]
    if not path.exists():
        r = session.get(url, headers={'Referer': NSE_REFERER}, timeout=120)
        if r.status_code != 200 or not r.content.startswith(b'%PDF'):
            raise SourceBlocked(f'download {url}: HTTP {r.status_code}, {len(r.content)} bytes, not a PDF')
        tmp = path.with_suffix('.part')
        tmp.write_bytes(r.content)
        tmp.rename(path)
    return path, sha256_file(path)


# ---------------------------------------------------------------- what is already in the DB

def known_documents(reader) -> Dict[str, dict]:
    """url -> row and sha256 -> row for every sb_documents row of the broker, plus rows left PENDING_MARK."""
    rows = reader.table('sb_documents', broker_id=BROKER)
    return {
        'url': {r['url']: r for r in rows if r.get('url')},
        'sha': {r['sha256']: r for r in rows if r.get('sha256')},
        'pending': {r['url']: r for r in rows if r.get('url') and (r.get('note') or '').startswith(PENDING_MARK)},
    }


def reviewed_facts(reader) -> Dict[Tuple[str, str, str], dict]:
    rows = reader.table('sb_disclosure_facts', broker_id=BROKER, status='reviewed')
    return {(r['metric'], r['period_key'], r.get('segment') or ''): r for r in rows}


# ---------------------------------------------------------------- parse

def _monthly_normalise(f: dict) -> Tuple[str, float, str]:
    m = QALIAS.get(f['metric'], f['metric']) if f['period_type'] == 'Q' else f['metric']
    v, u = f['value'], f['unit']
    if m == 'avg_funding_book' and f['period_type'] == 'Q':
        v, u = v * 1000, 'Rs Mn'                                        # seeded quarterly book is in Rs Mn
    return m, round(v, 6), u


def parse_monthly(pdf: Path):
    from src.extract import angel_monthly
    raw, checks = angel_monthly.parse(str(pdf))
    staged, compare = [], []
    for f in raw:
        m, v, u = _monthly_normalise(f)
        row = dict(period_type=f['period_type'], period_key=f['period_key'], metric=m, value=v, unit=u,
                   page=f['page'], table_label=f['table_label'], column=f['column'])
        (staged if f['column'] == 'current' else compare).append(row)
    return staged, compare, checks


def parse_press(pdf: Path):
    from src.extract import angel_press
    raw, checks = angel_press.parse(str(pdf))
    staged = [dict(f, value=round(f['value'], 6)) for f in raw if f['column'] == 'current']
    return staged, [], checks


PARSERS: Dict[str, Callable] = {'monthly_update': parse_monthly, 'press_release': parse_press}
NO_PARSER = {
    'investor_presentation': 'deck: revenue-mix slide is a chart (read by the filing-extractor, extracted_by claude)',
    'financial_results': 'results PDF is mostly scanned (PLAN 2.5); no facts needed for the ADR',
    'other': 'board-meeting outcome other than results; registered only',
}


def compare_columns(compare: List[dict], reviewed: Dict[Tuple[str, str, str], dict]) -> List[dict]:
    """Prior-period columns of a new update vs the reviewed facts: a difference means a restatement (or a misread)."""
    out = []
    for f in compare:
        r = reviewed.get((f['metric'], f['period_key'], ''))
        if r is None or r.get('value') is None:
            continue
        old = float(r['value'])
        if abs(f['value'] - old) > 1e-9 * max(1.0, abs(old)):
            out.append(dict(metric=f['metric'], period_key=f['period_key'], column=f['column'], new=f['value'],
                            reviewed=old, fact_id=r.get('fact_id'), page=f['page']))
    return out


# ---------------------------------------------------------------- plan

def plan(anns: List[dict], known: Dict[str, dict], session, reviewed: Dict, raw_dir: Optional[Path] = None,
         force: Tuple[str, ...] = (), now: Optional[str] = None) -> List[dict]:
    """One item per watched announcement that is not in sb_documents yet (or was left pending)."""
    now = now or dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')
    items = []
    for a in select(anns):
        url = a['attchmntFile'].strip()
        pending = known['pending'].get(url)
        if url in known['url'] and not pending and url not in force:
            continue
        doc_type = doc_type_for(a)
        item = dict(announcement={k: a.get(k) for k in ('an_dt', 'desc', 'attchmntText', 'seq_id', 'attchmntFile')},
                    doc_type=doc_type, doc=None, facts=[], checks=[], restated=[], problems=[], skipped=None)
        items.append(item)
        try:
            path, sha = download(session, url, raw_dir or RAW_DIR)
        except SourceBlocked as e:
            item['problems'].append(str(e))
            continue
        same = known['sha'].get(sha)
        if same and not pending and url not in force:
            item['skipped'] = f"same file (sha256) as sb_documents {same['doc_id']} ({same.get('url')})"
            continue
        fn = path.name
        staged, compare, checks = [], [], []
        parser = PARSERS.get(doc_type)
        if parser:
            try:
                staged, compare, checks = parser(path)
            except Exception as e:
                item['problems'].append(f'parser failed: {type(e).__name__}: {e}')
            if not staged and not item['problems']:
                item['problems'].append('parser found no table: read this PDF by hand (filing-extractor)')
        else:
            item['problems'].append(f'no parser: {NO_PARSER[doc_type]}')
        pub = published_at(a)
        pub_date = dt.date.fromisoformat(pub[:10])
        if doc_type == 'monthly_update':
            pk = next((f['period_key'] for f in staged if f['period_type'] == 'M'), None) \
                 or month_from_text(a.get('attchmntText'))
            has_q = any(f['period_type'] == 'Q' for f in staged)
            qk = next((f['period_key'] for f in staged if f['period_type'] == 'Q'), '')
            title = f'Monthly business update — {month_label(pk)}' + (f' & {short_q(qk)}' if has_q else '')
        else:
            pk = next((f['period_key'] for f in staged), None) or quarter_before(pub_date)
            title = {'press_release': f'Press release — {short_q(pk)} business performance',
                     'investor_presentation': f'Investor presentation — {short_q(pk)}',
                     'financial_results': f'Outcome of board meeting — {short_q(pk)} financial results',
                     }.get(doc_type, (a.get('attchmntText') or a.get('desc') or '')[:160])
        doc_id = pending['doc_id'] if pending else str(uuid.uuid4())
        item['pending_doc'] = bool(pending)
        item['doc'] = dict(doc_id=doc_id, broker_id=BROKER, doc_type=doc_type, period_key=pk, title=title, url=url,
                           file_path=FILE_PATH_PREFIX + fn, sha256=sha, published_at=pub, fetched_at=now,
                           note=f"watcher: NSE '{a.get('desc')}' seq_id {a.get('seq_id')}")
        bad = [c for c in checks if not c.get('ok')]
        for f in staged:
            note = '; '.join(f"auto-check failed: {c['check']} (printed {c['expected']}, computed {c['computed']})"
                             for c in bad) or None
            item['facts'].append(dict(broker_id=BROKER, period_type=f['period_type'], period_key=f['period_key'],
                                      metric=f['metric'], segment='', value=f['value'], unit=f['unit'],
                                      doc_id=doc_id, page=str(f['page']), table_label=f['table_label'],
                                      source_ref=f"{doc_type}:{fn}#page={f['page']}", extracted_by='parser',
                                      status='staged', note=note))
        item['checks'] = checks
        item['restated'] = compare_columns(compare, reviewed)
    return items


# ---------------------------------------------------------------- output

def _q(v) -> str:
    if v is None:
        return 'null'
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


DOC_COLS = ('doc_id', 'broker_id', 'doc_type', 'period_key', 'title', 'url', 'file_path', 'sha256', 'published_at',
            'fetched_at', 'note')
FACT_COLS = ('broker_id', 'period_type', 'period_key', 'metric', 'segment', 'value', 'unit', 'doc_id', 'page',
             'table_label', 'source_ref', 'extracted_by', 'status', 'note')


def to_sql(items: List[dict], end: str = 'commit') -> str:
    out = ['begin;']
    for it in items:
        if not it['doc']:
            continue
        d = it['doc']
        if it.get('pending_doc'):
            out.append(f"update sb_documents set note={_q(d['note'])} where doc_id={_q(d['doc_id'])};")
        else:
            out.append(f"insert into sb_documents ({', '.join(DOC_COLS)}) values "
                       f"({', '.join(_q(d[c]) for c in DOC_COLS)});")
        for f in it['facts']:
            out.append(f"insert into sb_disclosure_facts ({', '.join(FACT_COLS)}) values "
                       f"({', '.join(_q(f[c]) for c in FACT_COLS)});")
    out.append(f'{end};')
    return '\n'.join(out) + '\n'


def write_db(items: List[dict], writer) -> None:
    """Document row first (PENDING_MARK on its note), then the facts, then the final note."""
    for it in items:
        d = it['doc']
        if not d:
            continue
        final_note = d['note']
        if not it.get('pending_doc'):
            writer.insert('sb_documents', [dict(d, note=f'{PENDING_MARK} — {final_note}')])
        ids = writer.insert('sb_disclosure_facts', it['facts'], returning=True) if it['facts'] else []
        it['fact_ids'] = sorted(r['fact_id'] for r in ids)
        writer.update('sb_documents', dict(note=final_note), doc_id=d['doc_id'])


def _ids(ids: List[int]) -> str:
    if not ids:
        return ''
    return f'{ids[0]}–{ids[-1]}' if ids == list(range(ids[0], ids[-1] + 1)) else ', '.join(map(str, ids))


def summary_md(items: List[dict], meta: dict) -> str:
    new = [it for it in items if it['doc']]
    nfacts = sum(len(it['facts']) for it in new)
    head = (f"# Filing watcher — {meta['run_date']}\n\n"
            f"NSE announcements for {BROKER} {meta['since']} → {meta['until']}: {meta['n_announcements']} in all, "
            f"{meta['n_watched']} of the watched types. Mode: **{meta['mode']}**.\n\n")
    if not items:
        return head + 'No new filings. Nothing staged.\n'
    lines = [head, f"**{len(new)} new document(s), {nfacts} fact(s) "
                   f"{'staged — waiting for review' if meta['mode'] == 'write' else 'ready to stage (dry run)'}.**\n"]
    for it in items:
        a = it['announcement']
        lines.append(f"\n## {a['an_dt']} · {a['desc']}\n")
        lines.append(f"- File: {a['attchmntFile']}")
        if it['skipped']:
            lines.append(f"- Skipped: {it['skipped']}")
        if it['doc']:
            d = it['doc']
            lines.append(f"- Document: {d['title']} (`{d['doc_type']}`, {d['period_key']}), doc_id `{d['doc_id']}`, "
                         f"sha256 `{d['sha256'][:12]}…`")
            ids = it.get('fact_ids')
            lines.append(f"- Facts: {len(it['facts'])}" + (f" (fact_id {_ids(ids)})" if ids else ''))
            by_period: Dict[str, List[str]] = {}
            for f in it['facts']:
                by_period.setdefault(f['period_key'], []).append(f"{f['metric']} {f['value']:g} {f['unit']} (p.{f['page']})")
            for pk, fs in by_period.items():
                lines.append(f"  - {pk}: " + '; '.join(fs))
        for c in it['checks']:
            lines.append(f"- Check {'ok' if c['ok'] else '**FAILED**'}: {c['check']} — printed {c['expected']}, "
                         f"computed {c['computed']}")
        for r in it['restated']:
            lines.append(f"- **Differs from reviewed fact {r['fact_id']}**: {r['metric']} {r['period_key']} "
                         f"({r['column']} column, p.{r['page']}) {r['new']:g} vs reviewed {r['reviewed']:g}")
        for p in it['problems']:
            lines.append(f"- Needs attention: {p}")
    lines.append('\nNext: review the staged figures (review page, then `apply_review.py`). '
                 'Staged facts do not change the engine until they are marked reviewed.\n')
    return '\n'.join(lines)


def notify(summary: str, out_dir: Path, items: List[dict]) -> None:
    (out_dir / 'summary.md').write_text(summary)
    step = os.environ.get('GITHUB_STEP_SUMMARY')
    if step:
        with open(step, 'a') as fh:
            fh.write(summary + '\n')
    nfacts = sum(len(it['facts']) for it in items if it['doc'])
    if os.environ.get('WATCH_MAC_NOTIFY') and any(it['doc'] for it in items):
        import subprocess
        msg = f'{nfacts} Angel One figure(s) staged for review' if nfacts else 'New Angel One filing registered'
        subprocess.run(['osascript', '-e', f'display notification "{msg}" with title "Filing watcher"'], check=False)


# ---------------------------------------------------------------- CLI

def main(argv: Optional[List[str]] = None, session=None, reader=None, writer=None, today: Optional[dt.date] = None) -> int:
    import argparse
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    p.add_argument('--since', help='first announcement date, YYYY-MM-DD (default: 45 days back)')
    p.add_argument('--until', help='last announcement date, YYYY-MM-DD (default: today, IST)')
    p.add_argument('--write', action='store_true', help='insert into sb_documents / sb_disclosure_facts')
    p.add_argument('--force', action='append', default=[], help='treat this URL as new (replay; refused with --write)')
    p.add_argument('--from-json', help='use a saved announcements JSON instead of the NSE API')
    p.add_argument('--db-snapshot', help='read sb_documents / sb_disclosure_facts from a JSON file (no key needed; '
                                         'dry runs only)')
    p.add_argument('--out', default='out/filings', help='folder for summary.md / payload.json / stage.sql')
    a = p.parse_args(argv)
    if a.write and (a.force or a.db_snapshot):
        p.error('--force and --db-snapshot are for dry runs only')
    today = today or dt.datetime.now(IST).date()
    until = dt.date.fromisoformat(a.until) if a.until else today
    since = dt.date.fromisoformat(a.since) if a.since else until - dt.timedelta(days=45)

    if reader is None:
        from src.live.db import SnapshotReader, SupabaseReader
        reader = SnapshotReader(a.db_snapshot) if a.db_snapshot else SupabaseReader()
    if session is None:
        session = nse_session()
    try:
        anns = json.loads(Path(a.from_json).read_text()) if a.from_json else fetch_announcements(session, since, until)
    except SourceBlocked as e:
        print(f'BLOCKED: {e}')
        return 2
    known = known_documents(reader)
    items = plan(anns, known, session, reviewed_facts(reader), force=tuple(a.force))

    if a.write and any(it['doc'] for it in items):
        if writer is None:
            from src.live.db import SupabaseWriter
            writer = SupabaseWriter()
        write_db(items, writer)
    out_dir = Path(a.out) / today.isoformat()
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = dict(run_date=today.isoformat(), since=since.isoformat(), until=until.isoformat(),
                n_announcements=len(anns), n_watched=len(select(anns)), mode='write' if a.write else 'dry run')
    if items:
        (out_dir / 'payload.json').write_text(json.dumps(
            {'meta': meta, 'items': items,
             'sb_documents': [it['doc'] for it in items if it['doc']],
             'sb_disclosure_facts': [f for it in items for f in it['facts']]}, indent=1, ensure_ascii=False))
        (out_dir / 'stage.sql').write_text(to_sql(items))
    summary = summary_md(items, meta)
    notify(summary, out_dir, items)
    print(summary)
    return 1 if any(p.startswith('download') for it in items for p in it['problems']) else 0
