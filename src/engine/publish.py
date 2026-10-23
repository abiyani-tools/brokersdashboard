"""Turn an engine run into rows for sb_runs / sb_calibration / sb_daily_revenue / sb_summary_cells."""
import datetime as dt
from .summary import PARITY_LABELS, WEEKDAYS

BROKER = 'ANGELONE'


def calibration_rows(run_id, calib):
    rows = []
    def add(seg, pt, pk, param, value, regime, rule=None, src=None):
        if value is None:
            return
        rows.append(dict(run_id=run_id, broker_id=BROKER, segment=seg, period_type=pt, period_key=pk,
                         param=param, value=float(value), regime=regime, rule=rule, source_periods=src))
    for q, r in calib['take_rates'].items():
        for s in ('fo', 'cash', 'comm'):
            add(s, 'Q', q, 'take_rate', r.get(f'take_rate_{s}'), 'actual', 'rev mix x total income / orders')
        add('fo', 'Q', q, 'fo_pct', r.get('fo_pct'), 'actual', 'fo / (fo+cash+comm)')
        add('comm', 'Q', q, 'comm_pct', r.get('comm_pct'), 'actual', 'comm orders / sum of monthly orders')
    for m, r in calib['fo_month'].items():
        add('fo', 'M', m, 'cpo', r['cpo'], r['regime'], r['rule'])
        add('fo', 'M', m, 'share', r['share'], 'actual' if r['share_rule'] == 'actual' else 'projected', r['share_rule'])
        add('fo', 'M', m, 'fo_pct', r['fo_pct'], 'actual' if r['fo_pct_rule'] == 'actual' else 'projected', r['fo_pct_rule'])
        add('fo', 'M', m, 'mkt_contracts', r.get('mkt_contracts'), 'actual', 'sum of NSE + BSE F&O contracts')
        add('fo', 'M', m, 'fo_orders_mn', r.get('fo_orders'), 'actual', 'total orders x F&O %')
    for q, (v, rule) in calib['fo_take_rate'].items():
        add('fo', 'Q', q, 'take_rate_used', v, 'actual' if rule == 'actual' else 'projected', rule)
    for q, r in calib['cash_quarter'].items():
        for p, name in (('tpo', 'tpo'), ('share', 'share'), ('take_rate', 'take_rate_used'), ('mkt_trades_mn', 'mkt_trades_mn')):
            add('cash', 'Q', q, name, r.get(p), r['regime'], r['rule'])
    for m, r in calib['comm_month'].items():
        add('comm', 'M', m, 'cpo', r['cpo'], r['regime'], r['rule'])
        add('comm', 'M', m, 'share', r['share'], 'actual' if r['share_rule'].startswith('actual') else 'projected', r['share_rule'])
        add('comm', 'M', m, 'mcx_contracts', r.get('mcx_contracts'), 'actual', 'sum of MCX contracts')
        add('comm', 'M', m, 'comm_orders_mn', r.get('comm_orders'), 'actual', 'total orders x commodity %')
    tr, q = calib['comm_take_rate']
    add('comm', 'Q', q, 'take_rate_used', tr, 'actual', 'fixed quarter (Commodities!AI11), applied to all dates')
    for q, r in calib['mtf_quarter'].items():
        add('mtf', 'Q', q, 'share', r.get('share'), r['regime'], r['rule'])
        add('mtf', 'Q', q, 'industry_avg_cr', r.get('industry_avg_cr'), r['regime'])
        add('mtf', 'Q', q, 'angel_book_cr', r.get('angel_book_cr'), r['regime'])
    return rows


def daily_rows(run_id, daily):
    rows = []
    for seg, key in (('fo', 'rev_mn'), ('cash', 'rev_mn'), ('comm', 'rev_mn')):
        for d, r in daily[seg].items():
            rows.append(dict(run_id=run_id, broker_id=BROKER, trade_date=d, segment=seg,
                             orders_mn=r['orders_mn'], revenue_cr=r[key] / 10, regime=r['regime']))
    for d, r in daily['mtf'].items():
        for seg, k in (('mtf_gross', 'gross_cr'), ('mtf_net', 'net_cr')):
            rows.append(dict(run_id=run_id, broker_id=BROKER, trade_date=d, segment=seg,
                             orders_mn=None, revenue_cr=r[k], regime=r['regime']))
    return rows


def summary_rows(run_id, stats, as_of):
    """Parity grid rows. period_type/period_key name the selection each table was built for (E3 columns)."""
    rows = []
    TYPE = {'Financial Year': 'FY', 'Quarter': 'Q', 'Month': 'M', 'Week': 'asof', 'Weekday': 'asof'}
    def add(panel, tbl, label, value, cmp_name=None, cmp_val=None):
        key = {'FY': lab['fy'][0], 'Q': lab['q'][0], 'M': lab['m'][0], 'asof': str(as_of)}[TYPE[tbl]]
        rows.append(dict(run_id=run_id, broker_id=BROKER, panel=panel, period_type=TYPE[tbl], period_key=key,
                         table_name=tbl, row_label=label, value=value, comparison=cmp_name, comp_value=cmp_val,
                         note=None))
    def ratio(a, b):
        return a / b - 1 if b else None
    for panel, st in stats.items():
        lab = PARITY_LABELS.get(panel, PARITY_LABELS['default'])
        fy, q, m, w = st['fy'], st['q'], st['m'], st['w']
        add(panel, 'Financial Year', lab['fy'][0], fy[0], 'YoY', ratio(fy[0], fy[1]))
        add(panel, 'Financial Year', lab['fy'][1], fy[1])
        add(panel, 'Quarter', lab['q'][0], q[0], 'QoQ', ratio(q[0], q[1]))
        add(panel, 'Quarter', lab['q'][0] + ' | YoY', q[0], 'YoY', ratio(q[0], q[2]))
        add(panel, 'Quarter', lab['q'][1], q[1]); add(panel, 'Quarter', lab['q'][2], q[2])
        add(panel, 'Month', lab['m'][0], m[0], 'MoM', ratio(m[0], m[1]))
        add(panel, 'Month', lab['m'][0] + ' | vs 6M', m[0], 'Mo 6M', ratio(m[0], m[2]))
        add(panel, 'Month', lab['m'][1], m[1]); add(panel, 'Month', 'Avg of last 6 months', m[2])
        add(panel, 'Week', 'Last 5 trading days', w[0], 'WoW', ratio(w[0], w[1]))
        add(panel, 'Week', 'Last 5 trading days | vs 45D', w[0], 'vs last 45 days', ratio(w[0], w[2]))
        add(panel, 'Week', 'Previous 5 trading days', w[1]); add(panel, 'Week', 'Last 45 trading days', w[2])
        add(panel, 'Week', 'Last 20 trading days', w[3])
        for k, (latest, a3, a10) in enumerate(st['wd']):
            d = WEEKDAYS[k]
            add(panel, 'Weekday', d, latest, 'vs avg of last 3', ratio(latest, a3))
            add(panel, 'Weekday', d + ' | vs 10', latest, 'vs avg of last 10', ratio(latest, a10))
            add(panel, 'Weekday', f'Average of last 3 {d}s', a3)
            add(panel, 'Weekday', f'Average of last 10 {d}s', a10)
    return rows


def period_summary_rows(run_id, rows):
    """Live E3 rows (summary_periods.period_rows) for sb_summary_cells. value is NULL when note says why."""
    return [dict(run_id=run_id, broker_id=BROKER, **r) for r in rows]
