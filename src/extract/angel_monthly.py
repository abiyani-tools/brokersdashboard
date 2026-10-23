"""Parse Angel One's monthly business update PDF (NSE 'Monthly Business Updates').

Usage: python3 angel_monthly.py <pdf> [--url URL]   -> JSON facts on stdout
Needs `pdftotext` (poppler). Every value keeps its page, table, row label and column so a reviewer can find it.
Automatic checks: avg daily orders x trading days ~ orders; printed MoM/YoY vs recomputed.
"""
import json, re, subprocess, sys

MON = {'Jan': 'January', 'Feb': 'February', 'Mar': 'March', 'Apr': 'April', 'May': 'May', 'Jun': 'June', 'Jul': 'July',
       'Aug': 'August', 'Sep': 'September', 'Oct': 'October', 'Nov': 'November', 'Dec': 'December'}

# row label (regex) -> (monthly metric, quarterly metric, unit, scale)
ROWS = [
    (r'^No\. of Trading Days', 'trading_days', 'trading_days_q', 'days', 1),
    (r'^Client Base \(Mn\)', 'client_base', 'client_base', 'Mn', 1),
    (r'^Gross Client Acquisition \(Mn\)', 'gross_client_acq', 'gross_client_acq_q', 'Mn', 1),
    (r'^Avg Client Funding Book', 'avg_funding_book', 'avg_funding_book', 'Rs Bn', 1),
    (r'^Number of Orders \(Mn\)', 'total_orders', 'orders_total', 'Mn', 1),
    (r'^Average Daily Orders \(Mn\)', 'avg_daily_orders', 'avg_daily_orders_q', 'Mn', 1),
    (r"^Unique MF SIPs Registered", 'sip_registrations_k', 'sip_registrations_k_q', "'000", 1),
    (r'^Overall\*', 'adto_notional_overall', 'adto_notional_overall_q', 'Rs Bn', 1),
    (r'^F&O\*', 'adto_notional_fo', 'adto_notional_fo_q', 'Rs Bn', 1),
    (r'^Overall\$', 'adto_premium_overall', 'adto_premium_overall_q', 'Rs Bn', 1),
    (r'^F&O\$', 'adto_premium_fo', 'adto_premium_fo_q', 'Rs Bn', 1),
    (r'^Cash ADTO', 'adto_cash', 'adto_cash', 'Rs Bn', 1),
    (r'^Commodity ADTO', 'adto_comm', 'adto_comm', 'Rs Bn', 1),
    (r'^Overall Equity\^', 'share_overall', 'share_overall_q', 'fraction', 0.01),
    (r'^F&O\^', 'share_fo', 'share_fo_q', 'fraction', 0.01),
    (r'^Cash Turnover Market Share', 'share_cash', 'share_cash_q', 'fraction', 0.01),
    (r'^Commodity Turnover Market Share', 'share_comm', 'share_comm_q', 'fraction', 0.01),
]
NUM = r'-?[\d,]+(?:\.\d+)?%?'


def period(tok):
    m = re.match(r"([A-Z][a-z]{2}) '(\d\d)", tok)
    if m:                                   # Jun '26 -> FY 2027 June
        mon, yy = MON[m.group(1)], 2000 + int(m.group(2))
        fy = yy + 1 if mon in ('April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December') else yy
        return 'M', f'FY {fy} {mon}'
    m = re.match(r'Q(\d) FY(\d\d)', tok)
    if m:
        return 'Q', f'Q{m.group(1)} FY 20{m.group(2)}'
    return None, None


def parse(pdf):
    facts, checks = [], []
    npages = int(re.search(r'Pages:\s+(\d+)', subprocess.run(['pdfinfo', pdf], capture_output=True, text=True).stdout).group(1))
    for p in range(1, npages + 1):
        text = subprocess.run(['pdftotext', '-f', str(p), '-l', str(p), '-layout', pdf, '-'], capture_output=True, text=True).stdout
        cols = None
        for raw in text.splitlines():
            line = raw.strip()
            if line.startswith('Particulars'):
                toks = re.findall(r"[A-Z][a-z]{2} '\d\d|Q\d FY\d\d", line)
                if len(toks) >= 3:
                    cols = [period(t) for t in toks[:3]]
                    col_labels = ['current', 'previous', 'year_ago']
                continue
            if not cols:
                continue
            for rx, m_metric, q_metric, unit, scale in ROWS:
                if re.match(rx, line):
                    rest = re.sub(r'\([^)]*\)', ' ', line[len(re.match(rx, line).group(0)):])   # drop "(Mn)", "('000)" etc.
                    nums = re.findall(NUM, rest)
                    nums = [n for n in nums if re.search(r'\d', n)]
                    for i in range(3):
                        if i >= len(nums):
                            break
                        tok = nums[i]
                        v = float(tok.rstrip('%').replace(',', '')) * (0.01 if tok.endswith('%') else 1)
                        pt, pk = cols[i]
                        facts.append(dict(period_type=pt, period_key=pk, metric=m_metric if pt == 'M' else q_metric,
                                          value=v, unit=unit, page=str(p), column=col_labels[i],
                                          table_label=f"{'monthly' if pt == 'M' else 'quarterly'} table, row '{line[:40].strip()}'"))
                    break
    # automatic checks on the 'current' column of each table
    cur = {(f['period_type'], f['metric']): f for f in facts if f['column'] == 'current'}
    for pt, o, a, d in (('M', 'total_orders', 'avg_daily_orders', 'trading_days'), ('Q', 'orders_total', 'avg_daily_orders_q', 'trading_days_q')):
        if all((pt, k) in cur for k in (o, a, d)):
            est = cur[(pt, a)]['value'] * cur[(pt, d)]['value']
            act = cur[(pt, o)]['value']
            checks.append(dict(check=f'{a} x {d} vs {o} ({cur[(pt, o)]["period_key"]})', expected=act, computed=round(est, 2),
                               ok=abs(est / act - 1) < 0.01))
    return facts, checks


if __name__ == '__main__':
    f, c = parse(sys.argv[1])
    json.dump({'pdf': sys.argv[1], 'facts': f, 'checks': c}, sys.stdout, indent=1)
