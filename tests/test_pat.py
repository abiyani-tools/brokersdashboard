"""PAT model (src/engine/pat.py): filed quarters reconcile, rules match the workbook where they are unchanged,
and the projected P&L adds up. Inputs: the staged P&L extracts (out/pat/facts_*_pl.json), snapshot facts,
seed/pat_assumptions.json and a synthetic daily ADR series (so the test needs no network)."""
import datetime as dt
import json
import unittest
from pathlib import Path

from src.engine import pat as P

ROOT = Path(__file__).resolve().parents[1]
HAVE_EXTRACTS = (ROOT / 'out/pat/facts_angel_pl.json').exists() and (ROOT / 'out/pat/facts_groww_pl.json').exists()


def synthetic_daily(start='2026-04-01', end='2026-11-03', broking=15.0, cash=2.0, mtf=4.7):
    rows, d = [], dt.date.fromisoformat(start)
    while d <= dt.date.fromisoformat(end):
        if d.weekday() < 5:
            iso = d.isoformat()
            rows += [dict(trade_date=iso, segment='fo', revenue_cr=broking - cash - 1.0, regime='actual'),
                     dict(trade_date=iso, segment='cash', revenue_cr=cash, regime='actual'),
                     dict(trade_date=iso, segment='comm', revenue_cr=1.0, regime='actual'),
                     dict(trade_date=iso, segment='mtf_gross', revenue_cr=mtf, regime='actual')]
        d += dt.timedelta(days=1)
    return rows


@unittest.skipUnless(HAVE_EXTRACTS, 'run python3 -m src.extract.pl_angel / pl_groww first')
class TestPat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import os
        os.chdir(ROOT)
        from run_pat import local_facts
        cls.assume = json.load(open(ROOT / 'seed/pat_assumptions.json'))['assumptions']
        cls.m = {}
        for b in ('ANGELONE', 'GROWW'):
            facts = local_facts(b)
            shares = next(f['value'] for f in facts if f['metric'] == 'shares_outstanding_cr')
            cls.m[b] = P.build(b, facts, synthetic_daily(), cls.assume, dict(price=300.0, date='2026-11-04'), shares)

    def test_reported_quarters_add_up(self):
        for b, m in self.m.items():
            for q in ('Q1 FY 2027', 'Q2 FY 2027'):
                L = m['quarters'][q]
                self.assertEqual(L['regime'], 'actual')
                self.assertAlmostEqual(sum(L[k] for k in P.REVENUE_LINES[b]), L['total_income'], delta=0.5, msg=(b, q))
                # filed costs: the model's lines cover total expenses (Angel's employee line includes ESOP)
                self.assertAlmostEqual(sum(L[k] for k in P.COST_LINES[b]), L['total_costs'], delta=0.5, msg=(b, q))
                # Groww's PBT also carries its share of an associate's loss (Rs 0.7 Cr a quarter), not a model line
                self.assertAlmostEqual(L['total_income'] - L['total_costs'], L['pbt'], delta=1.0, msg=(b, q))

    def test_projected_quarters_add_up(self):
        for b, m in self.m.items():
            for q in ('Q3 FY 2027', 'Q4 FY 2027'):
                L = m['quarters'][q]
                self.assertEqual(L['regime'], 'projected')
                self.assertAlmostEqual(L['pat'], 0.75 * L['pbt'], places=6)
                self.assertGreaterEqual(L['finance'], 0.0)
            f27 = m['fy27']
            self.assertAlmostEqual(f27['pat'], sum(m['quarters'][q]['pat'] for q in P.FY27_Q), places=6)

    def test_fy27_trading_days_total_247(self):
        for m in self.m.values():
            done = sum(1 for d in synthetic_daily() if d['segment'] == 'fo')
            proj = sum(m['quarters'][q]['trading_days'] for q in ('Q3 FY 2027', 'Q4 FY 2027'))
            in_q3 = sum(1 for d in synthetic_daily() if d['segment'] == 'fo' and d['trade_date'] >= '2026-10-01')
            self.assertAlmostEqual(done - in_q3 + proj, 247, places=6)

    def test_angel_rules_match_workbook(self):
        """Unchanged rules reproduce 'PAT predictor Q2FY27'!J63:K66 (Rs Cr)."""
        q3, q4 = self.m['ANGELONE']['quarters']['Q3 FY 2027'], self.m['ANGELONE']['quarters']['Q4 FY 2027']
        self.assertAlmostEqual(q3['other_expenses'], 381.78, delta=0.1)     # J66 = E66*(1+10%)
        self.assertAlmostEqual(q4['other_expenses'], 456.44, delta=0.1)     # K66 = F66*(1+10%)
        self.assertAlmostEqual(q3['depreciation'], 35.28, delta=0.05)       # J65 = E65*(1+12%)
        self.assertAlmostEqual(q4['depreciation'], 36.88, delta=0.05)       # K65
        self.assertAlmostEqual(q3['employee'], 285.43, delta=0.1)           # J64 = AVERAGE(C64:F64)*(1+7%)
        self.assertAlmostEqual(q3['impairment'], 0.86, delta=0.01)          # J63 = AVERAGE(C63:F63)*1.1

    def test_groww_employee_depreciation(self):
        """AB, 13 Nov 2026: FY26 quarterly average × (1 + average uplift of Q1, Q2 FY27 filed over it).
        Employee: FY26 136.63, 123.76, 157.049, 173.40 → avg 147.710; Q1 182.00 (+23.2%), Q2 168.89 (+14.3%)
        → × 1.1878 = 175.445. Depreciation: 7.14, 6.80, 9.475, 24.46 → avg 11.969; Q1 17.63 (+47.3%),
        Q2 18.20 (+52.1%) → × 1.4968 = 17.915. With both quarters filed this equals their average."""
        for q in ('Q3 FY 2027', 'Q4 FY 2027'):
            L = self.m['GROWW']['quarters'][q]
            self.assertAlmostEqual(L['employee'], 175.445, delta=0.01)
            self.assertAlmostEqual(L['depreciation'], 17.915, delta=0.01)
        f27 = self.m['GROWW']['fy27']
        self.assertAlmostEqual(self.m['GROWW']['fy28']['employee'], f27['employee'] * 1.15, places=6)

    def test_groww_restated_mix_wins(self):
        """AB, 13 Nov 2026: the October 2026 letter's restated mix (segment '') beats the July letter's rows tagged
        'cls_pre_q2fy27'. Q3 FY26 broking = (F&O 53.5% + cash 16.5% + commodity 3.5%) × 1,261.07 = 926.89 (the July
        cash share 18.2% gave 948.33); other expenses ÷ broking over Q3 FY26..Q2 FY27 = 1,444.73 ÷ 4,259.72 = 33.92%."""
        m = self.m['GROWW']
        t = P.fact_table(__import__('run_pat').local_facts('GROWW'), 'GROWW')
        self.assertAlmostEqual(t[('Q3 FY 2026', 'revmix_cash')], 0.165)
        self.assertAlmostEqual(t[('Q1 FY 2027', 'revmix_cash')], 0.161)
        self.assertAlmostEqual(m['ratios']['other_exp_to_broking'], 0.33916, places=4)

    def test_fact_table_segment_priority(self):
        """An untagged row wins over a segment-tagged one in either order; a tagged row is the fallback."""
        cur = dict(broker_id='GROWW', period_key='Q', metric='revmix_cash', value=0.165, unit='fraction', segment='')
        old = dict(cur, value=0.182, segment='cls_pre_q2fy27')
        only = dict(old, period_key='Q0', value=0.193)
        for rows in ([cur, old, only], [old, cur, only]):
            t = P.fact_table(rows, 'GROWW')
            self.assertEqual(t[('Q', 'revmix_cash')], 0.165)
            self.assertEqual(t[('Q0', 'revmix_cash')], 0.193)

    def test_costs_follow_adr(self):
        """Fees & commission (Angel) and other expenses (Groww) scale with broking revenue; finance cost with MTF."""
        hi = {}
        for b in ('ANGELONE', 'GROWW'):
            from run_pat import local_facts
            facts = local_facts(b)
            shares = next(f['value'] for f in facts if f['metric'] == 'shares_outstanding_cr')
            hi[b] = P.build(b, facts, synthetic_daily(broking=20.0, mtf=6.0), self.assume, dict(price=300.0, date='2026-11-04'), shares)
        a0, a1 = self.m['ANGELONE']['fy28'], hi['ANGELONE']['fy28']
        self.assertAlmostEqual(a1['fees_commission'] / a0['fees_commission'], a1['broking'] / a0['broking'], places=9)
        self.assertGreater(a1['finance'], a0['finance'])
        g0, g1 = self.m['GROWW']['fy28'], hi['GROWW']['fy28']
        self.assertAlmostEqual(g1['other_expenses'] / g0['other_expenses'], g1['broking'] / g0['broking'], places=9)

    def test_quarterly_adr_growth(self):
        """Q4 FY27 broking = days × window ADR × (1 + g); FY28 ADR = window ADR × average of (1 + g)^2..^5."""
        for b, g in (('ANGELONE', 0.03), ('GROWW', 0.04)):   # Groww 4% from the 09.11 workbook (AB, 9 Nov 2026)
            m = self.m[b]
            q4 = m['quarters']['Q4 FY 2027']
            base = m['fy27']['adr_broking']
            self.assertAlmostEqual(q4['broking'], q4['trading_days'] * base * (1 + g), places=6)
            self.assertAlmostEqual(m['fy28']['adr_broking'], base * sum((1 + g) ** k for k in (2, 3, 4, 5)) / 4, places=9)

    def test_new_borrowing(self):
        self.assertEqual(P.new_borrowing(110, 100, 4), 6)
        self.assertEqual(P.new_borrowing(110, 100, 40), 0.0)        # a surplus does not repay interest
        self.assertEqual(P.new_borrowing(90, 100, 40), -10)         # a shrinking book repays borrowing

    def test_rows(self):
        rows = P.rows(self.m['GROWW'], 'run-x')
        keys = {(r['period_key'], r['line'], r['scenario']) for r in rows}
        self.assertEqual(len(keys), len(rows))
        self.assertIn(('FY 2028', 'target_today', 'base'), keys)
        self.assertIn(('FY 2028', 'close', ''), keys)
        self.assertIn(('FY 2027', 'shares', ''), keys)
        self.assertIn(('FY 2026', 'pat', ''), keys)                   # 3-year P&L (10 Nov 2026)
        self.assertIn(('FY 2028', 'adr_consol', ''), keys)
        self.assertIn(('inputs', 'in_pe', 'base'), keys)
        self.assertTrue(all(r['regime'] in ('actual', 'projected') for r in rows))


if __name__ == '__main__':
    unittest.main()


@unittest.skipUnless(HAVE_EXTRACTS, 'run python3 -m src.extract.pl_angel / pl_groww first')
class TestPatDbInputs(unittest.TestCase):
    """run_pat.db_inputs on an in-memory reader: latest successful run, reviewed facts only, filed P&L preferred."""

    def test_db_inputs(self):
        import os
        os.chdir(ROOT)
        from run_pat import db_inputs, local_facts
        facts = [dict(f, status='reviewed') for f in local_facts('GROWW')]
        facts.append(dict(broker_id='GROWW', period_type='Q', period_key='Q2 FY 2027', metric='pl_pat', segment='',
                          value=1.0, unit='Rs Cr', status='reviewed'))          # an older non-filing row: dropped
        facts.append(dict(broker_id='GROWW', period_type='Q', period_key='Q3 FY 2027', metric='pl_pat',
                          segment='consolidated', value=9.0, unit='Rs Cr', status='staged'))   # not reviewed: dropped
        tables = {
            'sb_runs': [dict(run_id='old', broker_id='GROWW', mode='live', status='success', started_at='2026-11-01T00:00:00'),
                        dict(run_id='new', broker_id='GROWW', mode='live', status='success', started_at='2026-11-05T00:00:00'),
                        dict(run_id='bad', broker_id='GROWW', mode='live', status='failed', started_at='2026-11-06T00:00:00')],
            'sb_daily_revenue': [dict(r, run_id='new') for r in synthetic_daily()],
            'sb_disclosure_facts': facts,
            'sb_assumptions': json.load(open(ROOT / 'seed/pat_assumptions.json'))['assumptions'],
            'sb_share_prices': [dict(broker_id='GROWW', trade_date='2026-11-04', close=207.23)],
        }

        class Reader:
            def table(self, name, **eq):
                return [r for r in tables[name] if all(str(r.get(k)) == str(v) for k, v in eq.items())]

        run, daily, got, assume, prices, shares = db_inputs(Reader(), 'GROWW')
        px = prices[-1]
        self.assertEqual(run['run_id'], 'new')
        self.assertEqual(len(daily), len(tables['sb_daily_revenue']))
        self.assertFalse(any(f['metric'] == 'pl_pat' and f['segment'] == '' for f in got))
        self.assertFalse(any(f['period_key'] == 'Q3 FY 2027' for f in got))
        self.assertTrue(all(a['key'].startswith(('pat_', 'val_')) for a in assume))
        self.assertAlmostEqual(shares, 623.905, places=3)
        m = P.build('GROWW', got, daily, assume, dict(price=px['close'], date=px['trade_date']), shares)
        self.assertGreater(m['fy28']['pat'], 0)
