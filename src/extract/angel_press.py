"""Parse Angel One's quarterly press release (NSE 'Press Release', "Qn FYyy Business Performance Highlights").

Usage: python3 angel_press.py <pdf>   -> JSON facts on stdout
Needs `pdftotext` (poppler). Reads two things, as staged by hand for Q2 FY27 (facts in the 478–655 catch-up):
  - the 'No. of Orders' table, first (current-quarter) column: orders_fo, orders_cash, orders_comm (Mn);
    'Total' is read for the sum check only (the monthly update carries the unrounded quarterly total)
  - Total Gross Revenues, Consolidated -> total_income, Standalone -> total_income_standalone (Rs Mn)
Automatic check: F&O + Cash + Commodity vs Total (the release prints whole millions, so allow 2 Mn of rounding).
"""
import json, re, subprocess, sys

QTOK = r"Q([1-4])\s*[’‘'`]\s*(\d\d)"
ORDER_ROWS = (('Total', 'orders_total'), ('F&O', 'orders_fo'), ('Cash', 'orders_cash'), ('Commodity', 'orders_comm'))


def qkey(q, yy):
    return f'Q{q} FY 20{yy}'


def page_texts(pdf):
    npages = int(re.search(r'Pages:\s+(\d+)', subprocess.run(['pdfinfo', pdf], capture_output=True, text=True).stdout).group(1))
    return [subprocess.run(['pdftotext', '-f', str(p), '-l', str(p), '-layout', pdf, '-'], capture_output=True,
                           text=True).stdout for p in range(1, npages + 1)]


def num(tok):
    return float(tok.replace(',', ''))


def parse_pages(pages):
    facts, checks, orders = [], [], {}
    for p, text in enumerate(pages, start=1):
        lines = [l.strip() for l in text.splitlines()]
        for i, line in enumerate(lines):
            # 'No. of Orders' table: header "Particulars (Mn)  Q2 ’27  Q1 ’27  Q2 ’26"
            if line.startswith('Particulars (Mn)') and not orders:
                m = re.search(QTOK, line)
                if not m:
                    continue
                pk = qkey(*m.groups())
                for row in lines[i + 1:i + 8]:
                    for label, metric in ORDER_ROWS:
                        mm = re.match(re.escape(label) + r'\s+([\d,]+(?:\.\d+)?)\b', row)
                        if mm and metric not in orders:
                            orders[metric] = (num(mm.group(1)), pk, p, row)
                continue
            # table form: "Total Gross Revenues   ₹ 14,007 Mn   ₹ 14,315 Mn" under "Qn ‘yy  Standalone  Consolidated"
            if line.startswith('Total Gross Revenues'):
                vals = re.findall(r'₹\s*([\d,]+(?:\.\d+)?)\s*Mn', line, re.I)
                head = next((l for l in reversed(lines[max(0, i - 4):i]) if 'Standalone' in l and 'Consolidated' in l), '')
                m = re.search(QTOK, head)
                if len(vals) == 2 and m and head.index('Standalone') < head.index('Consolidated'):
                    pk = qkey(*m.groups())
                    for metric, v, col in (('total_income_standalone', vals[0], 'Standalone'),
                                           ('total_income', vals[1], 'Consolidated')):
                        facts.append(dict(period_type='Q', period_key=pk, metric=metric, value=num(v), unit='Rs Mn',
                                          page=str(p), column='current',
                                          table_label=f'Business Performance: Total Gross Revenues, {col}'))
            # bullet form: "Consolidated Total Gross Revenues" then "₹ 13,377 mn in Q3 ‘26 vs ..."
            elif re.search(r'Consolidated Total Gross Revenues\s*$', line) and i + 1 < len(lines):
                m = re.match(r'₹\s*([\d,]+(?:\.\d+)?)\s*mn in ' + QTOK, lines[i + 1], re.I)
                if m:
                    facts.append(dict(period_type='Q', period_key=qkey(m.group(2), m.group(3)), metric='total_income',
                                      value=num(m.group(1)), unit='Rs Mn', page=str(p), column='current',
                                      table_label='Highlights: Consolidated Total Gross Revenues'))
    for metric, (v, pk, p, row) in orders.items():
        facts.append(dict(period_type='Q', period_key=pk, metric=metric, value=v, unit='Mn', page=str(p),
                          column='check_only' if metric == 'orders_total' else 'current',
                          table_label=f"No. of Orders table, {pk}"))
    seg = [orders[k][0] for k in ('orders_fo', 'orders_cash', 'orders_comm') if k in orders]
    if len(seg) == 3 and 'orders_total' in orders:
        tot = orders['orders_total'][0]
        checks.append(dict(check=f"F&O + Cash + Commodity vs Total orders ({orders['orders_total'][1]})",
                           expected=tot, computed=sum(seg), ok=abs(sum(seg) - tot) <= 2))
    return facts, checks


def parse(pdf):
    return parse_pages(page_texts(pdf))


if __name__ == '__main__':
    f, c = parse(sys.argv[1])
    json.dump({'pdf': sys.argv[1], 'facts': f, 'checks': c}, sys.stdout, indent=1, ensure_ascii=False)
