"""Units: contracts and trades are raw counts (same as the excel_seed rows).

Build parity fixtures (Excel outputs) and data-lake market rows for the brokers-dashboard DB.

Inputs: cached-value dump of the workbook (f.pkl: {sheet: {cell: value}}), ExchangesDash JSON
exports, Octo-MCX mcx_commodity_daily dump. Output: two JSON lists ready for sb_tmp_load2.
"""
import json, pickle, re, sys, datetime as dt
from collections import defaultdict

W = sys.argv[1]          # dir with f.pkl
EXD = sys.argv[2]        # ExchangesDash repo dir
MCX = sys.argv[3]        # mcx_commodity_daily.json
OUT = sys.argv[4]

F, V = pickle.load(open(f'{W}/f.pkl', 'rb'))
B = 'ANGELONE'
num = lambda x: isinstance(x, (int, float)) and not isinstance(x, bool)
iso = lambda d: d.date().isoformat() if hasattr(d, 'date') else None

exp = {}
def add(kind, key, value, ref, note=None):
    if not num(value):
        return
    k = (kind, key)
    if k in exp:            # duplicate date rows in Excel (e.g. 2024-02-01): keep first, note it
        return
    exp[k] = dict(broker_id=B, kind=kind, key=key, value=float(value), excel_ref=ref, note=note)

# ── daily outputs ──
def daily(sheet, date_col, cols, r0, r1):
    v = V[sheet]
    for r in range(r0, r1 + 1):
        d = iso(v.get(f'{date_col}{r}'))
        if not d:
            continue
        for col, name in cols:
            add('daily', f'{name}|{d}', v.get(f'{col}{r}'), f"{sheet}!{col}{r}")

daily('backtesting F&O', 'B', [('Z', 'fo_orders_mn'), ('AA', 'fo_rev_mn'), ('W', 'fo_cpo'), ('Y', 'fo_share')], 4, 761)
daily('backtesting cash', 'B', [('R', 'cash_orders_mn'), ('S', 'cash_rev_mn'), ('P', 'cash_tpo'), ('Q', 'cash_share')], 3, 760)
daily('Commodities', 'B', [('H', 'comm_orders_mn'), ('I', 'comm_rev_mn'), ('N', 'comm_cpo')], 2, 661)
daily('MTF data (2)', 'B', [('M', 'mtf_share'), ('N', 'mtf_angel_book_cr'), ('O', 'mtf_gross_cr'), ('P', 'mtf_net_cr')], 12, 518)

# ── calibration outputs ──
fm = V[' F&O market']
for r in range(4, 29):
    add('calib', f'fo_share_m|{fm.get(f"E{r}")}', fm.get(f'N{r}'), f"' F&O market'!N{r}")
    add('calib', f'fo_mkt_contracts_m|{fm.get(f"E{r}")}', fm.get(f'J{r}'), f"' F&O market'!J{r}")
for r in range(32, 57):
    m = fm.get(f'B{r}')
    for c, n in [('C', 'total_orders_m'), ('E', 'fo_pct_m'), ('F', 'fo_orders_m'), ('G', 'angel_contracts_mn'), ('H', 'fo_cpo_m')]:
        add('calib', f'{n}|{m}', fm.get(f'{c}{r}'), f"' F&O market'!{c}{r}")
bf = V['backtesting F&O']
for c in ['AJ', 'AK', 'AL', 'AM', 'AN', 'AO', 'AP', 'AQ', 'AR']:
    q = bf.get(f'{c}48')
    add('calib', f'fo_take_rate_q|{q}', bf.get(f'{c}51'), f'backtesting F&O!{c}51')
cm = V['cash market']
for r in range(35, 44):
    q = cm.get(f'F{r}')
    for c, n in [('G', 'cash_tpo_q'), ('H', 'cash_mkt_trades_q'), ('I', 'cash_take_rate_q'), ('J', 'cash_share_q')]:
        add('calib', f'{n}|{q}', cm.get(f'{c}{r}'), f'cash market!{c}{r}')
co = V['Commodities']
for r in range(14, 45):
    m = co.get(f'U{r}')
    for c, n in [('W', 'mcx_contracts_m'), ('X', 'comm_mkt_orders_m'), ('Y', 'comm_orders_m'), ('Z', 'comm_cpo_m'), ('AA', 'comm_share_m'), ('AB', 'comm_take_rate_m')]:
        add('calib', f'{n}|{m}', co.get(f'{c}{r}'), f'Commodities!{c}{r}')
add('calib', 'comm_take_rate_fixed', co.get('AI11'), 'Commodities!AI11')
md = V['MTF data']
for r in range(49, 61):
    q = (md.get(f'C{r}') or '').strip()
    for c, n in [('D', 'mtf_industry_avg_q'), ('P', 'mtf_angel_book_q'), ('Q', 'mtf_share_q')]:
        add('calib', f'{n}|{q}', md.get(f'{c}{r}'), f'MTF data!{c}{r}')
ws = V['Working sheet - Angel One']
def qlab(s):  # 'Q3FY25' -> 'Q3 FY 2025'
    m = re.match(r'Q(\d)FY(\d\d)', s or '')
    return f'Q{m.group(1)} FY 20{m.group(2)}' if m else None
for c in 'DEFGHIJKM':
    q = qlab(ws.get(f'{c}2'))
    if not q:
        continue
    for r, n in [(10, 'fo_pct_q'), (61, 'fo_rev_q_mn'), (62, 'cash_rev_q_mn'), (63, 'comm_rev_q_mn'),
                 (76, 'take_rate_fo_q'), (77, 'take_rate_cash_q'), (78, 'take_rate_comm_q'), (99, 'total_income_q')]:
        add('calib', f'{n}|{q}', ws.get(f'{c}{r}'), f'Working sheet - Angel One!{c}{r}')
for r in range(174, 183):
    q = ws.get(f'B{r}')  # 'FY 2025 Q1'
    m = re.match(r'FY (\d{4}) (Q\d)', q or '')
    if m:
        add('calib', f'comm_pct_q|{m.group(2)} FY {m.group(1)}', ws.get(f'I{r}'), f'Working sheet - Angel One!I{r}')

# ── summary cells ──
sm = V['SUMMARY - Angel One']
bands = [(3, 26, 'Consolidated', 'Broking'), (30, 53, 'MTF', 'F&O'), (56, 79, 'Cash', 'Commodities')]
def colnum(c):
    n = 0
    for ch in c:
        n = n * 26 + ord(ch) - 64
    return n
for cell, val in sm.items():
    if not num(val):
        continue
    col, row = re.match(r'([A-Z]+)(\d+)', cell).groups(); row = int(row); ci = colnum(col)
    band = next((b for b in bands if b[0] <= row <= b[1]), None)
    if not band:
        continue
    left = ci <= colnum('J')
    panel = band[2] if left else band[3]
    # weekday tables: left G-J, right R-U; others: left B-E, right M-P
    if left:
        lab_col = 'G' if ci >= colnum('G') else 'B'
    else:
        lab_col = 'R' if ci >= colnum('R') else 'M'
    label = sm.get(f'{lab_col}{row}')
    if not isinstance(label, str):
        label = str(label)
    # header: nearest string above in the same column within the band
    hdr = None
    for rr in range(row - 1, band[0] - 1, -1):
        h = sm.get(f'{col}{rr}')
        if isinstance(h, str) and not h.startswith('='):
            hdr = h.strip(); break
    add('summary', f'{panel}|{label.strip()}|{hdr}|{cell}', val, f'SUMMARY - Angel One!{cell}')

json.dump(list(exp.values()), open(f'{OUT}/parity_expected.json', 'w'))
print('parity rows', len(exp), {k: sum(1 for x in exp if x[0] == k) for k in ('daily', 'calib', 'summary')})

# ── data-lake market rows ──
lake = []
SRC = 'exchangesdash_json@b2049b5'
NOW = dt.datetime.now(dt.timezone.utc).isoformat()
START = '2023-09-29'
def jl(p):
    return json.load(open(f'{EXD}/dashboard/data/{p}'))
nse = jl('nse_dashboard_data.json'); bse = jl('bse_dashboard_data.json')
def rows(d):
    return d['daily_all'] + d.get('special_sessions', [])
def push(date, ds, metric, value, ref, status='ok', note=None, source=SRC):
    if value is None:
        return
    lake.append(dict(trade_date=date, dataset=ds, metric=metric, source=source, value=float(value),
                     status=status, source_ref=ref, note=note, loaded_at=NOW))
for r in rows(nse):
    d = r['date']
    if d < START:
        continue
    ref = f'dashboard/data/nse_dashboard_data.json[{d}]'
    push(d, 'nse_fo', 'contracts', r['total_contracts'], ref + '.total_contracts')
    for k, m in [('io_contracts', 'io_contracts'), ('so_contracts', 'so_contracts')]:
        if k in r:
            bad = r[k] == 0
            push(d, 'nse_fo', m, r[k], ref + '.' + k, 'suspect' if bad else 'ok',
                 'zero on a trading day' if bad else None)
    push(d, 'nse_fo', 'io_premium_cr', r['io_premium'], ref + '.io_premium')
    push(d, 'nse_fo', 'so_premium_cr', r['so_premium'], ref + '.so_premium')
    push(d, 'nse_fo', 'fut_turnover_cr', r['if_turnover'] + r['sf_turnover'], ref + '.if_turnover+sf_turnover')
    push(d, 'nse_cash', 'turnover_cr', r['cash_traded_value'], ref + '.cash_traded_value')
for r in rows(bse):
    d = r['date']
    if d < START:
        continue
    ref = f'dashboard/data/bse_dashboard_data.json[{d}]'
    zc = r['total_contracts'] == 0
    push(d, 'bse_fo', 'contracts', r['total_contracts'], ref + '.total_contracts',
         'suspect' if zc else 'ok', 'zero contracts on a trading day' if zc else None)
    push(d, 'bse_fo', 'opt_premium_cr', r['options_premium_turnover'], ref + '.options_premium_turnover')
    push(d, 'bse_fo', 'fut_turnover_cr', r['futures_turnover'], ref + '.futures_turnover')
    zt = r['cash_trades'] == 0
    push(d, 'bse_cash', 'trades', r['cash_trades'], ref + '.cash_trades',
         'suspect' if zt else 'ok', 'zero trades on a trading day' if zt else None)
    push(d, 'bse_cash', 'turnover_cr', r['cash_traded_value'], ref + '.cash_traded_value')
mcx = json.load(open(MCX))
agg = defaultdict(float); srcs = defaultdict(set)
for r in mcx:
    if r['trading_date'] < START or r['source'] not in ('mcx_historical', 'dhan_live'):
        continue
    agg[r['trading_date']] += r['contracts'] or 0
    srcs[r['trading_date']].add(r['source'])
for d, v in sorted(agg.items()):
    bad = v == 0
    push(d, 'mcx', 'contracts', v, f'octo_mcx.mcx_commodity_daily sum(contracts) [{d}]',
         'suspect' if bad else 'ok', ('zero contracts; sources ' + ','.join(sorted(srcs[d]))) if bad else None,
         source='octo_mcx@2026-10-22')
json.dump(lake, open(f'{OUT}/lake_market_daily.json', 'w'))
from collections import Counter
print('lake rows', len(lake), Counter((x['dataset'], x['metric'], x['status']) for x in lake))
