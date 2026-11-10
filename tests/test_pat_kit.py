"""PAT predictor recompute kit (src/engine/pat_kit.py): from the published rows alone it reproduces build() / rows()
at the defaults and at other QoQ growth rates, the top block adds up to total income, and the start rule takes the
current quarter's QTD ADR (the previous full quarter under 5 engine days). Inputs as tests/test_pat.py, with a
daily series that moves from day to day so the quarter-to-date and the 45-day figures differ."""
import datetime as dt
import json
import math
import unittest
from pathlib import Path

from src.engine import pat as P
from src.engine import pat_kit as K

ROOT = Path(__file__).resolve().parents[1]
HAVE_EXTRACTS = (ROOT / 'out/pat/facts_angel_pl.json').exists() and (ROOT / 'out/pat/facts_groww_pl.json').exists()
TOL = 1e-6


def moving_daily(start='2026-04-01', end='2026-11-03'):
    rows, d, i = [], dt.date.fromisoformat(start), 0
    while d <= dt.date.fromisoformat(end):
        if d.weekday() < 5:
            iso, w = d.isoformat(), 1 + 0.15 * math.sin(i / 7) + 0.002 * i
            rows += [dict(trade_date=iso, segment='fo', revenue_cr=12.0 * w, regime='actual'),
                     dict(trade_date=iso, segment='cash', revenue_cr=2.0 * w ** 0.5, regime='actual'),
                     dict(trade_date=iso, segment='comm', revenue_cr=1.0, regime='actual'),
                     dict(trade_date=iso, segment='mtf_gross', revenue_cr=4.7 + 0.01 * i, regime='actual')]
            i += 1
        d += dt.timedelta(days=1)
    return rows


def key(r):
    return (r['period_key'], r['line'], r['scenario'])


def model_lines(rows):
    """The published lines the page recomputes or shows (not the inputs / kit rows)."""
    return {key(r): r['value'] for r in rows if r['period_key'] != 'inputs' and not r['line'].startswith(('k_', 'in_'))}


@unittest.skipUnless(HAVE_EXTRACTS, 'run python3 -m src.extract.pl_angel / pl_groww first')
class TestPatKit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import os
        os.chdir(ROOT)
        from run_pat import local_facts
        cls.assume = json.load(open(ROOT / 'seed/pat_assumptions.json'))['assumptions']
        cls.facts = {b: local_facts(b) for b in ('ANGELONE', 'GROWW')}
        cls.m = {b: cls.build(b) for b in cls.facts}

    @classmethod
    def build(cls, b, daily=None, **override):
        facts = cls.facts[b]
        shares = next(f['value'] for f in facts if f['metric'] == 'shares_outstanding_cr')
        assume = cls.assume + [dict(broker_id=b, key=k, value=v, value_text='20,25,30' if k == 'pat_pe' else None)
                               for k, v in override.items()]
        return P.build(b, facts, daily or moving_daily(), assume, dict(price=300.0, date='2026-11-04'), shares)

    def check_same(self, got, rows, msg):
        want = model_lines(rows)
        self.assertEqual(set(got), set(want), msg)
        for k, v in want.items():
            self.assertAlmostEqual(got[k], v, delta=TOL, msg=(msg, k))

    def test_defaults_reproduce_published(self):
        for b, m in self.m.items():
            rows = P.rows(m, 'run-x')
            kit = K.kit_from_rows(rows)
            self.assertEqual(kit['broker'], b)
            d = kit['defaults']
            self.check_same(K.recompute(kit, d['g'], d['pe'], d['disc'], d['today']), rows, b)

    def test_other_growth_equals_rebuild(self):
        for b, m in self.m.items():
            kit = K.kit_from_rows(P.rows(m, 'run-x'))
            d = kit['defaults']
            for dg in (-0.01, 0.01):
                g = d['g'] + dg
                rows = P.rows(self.build(b, pat_adr_qoq_growth=g), 'run-x')
                self.check_same(K.recompute(kit, g, d['pe'], d['disc'], d['today']), rows, (b, g))

    def test_other_pe_and_discounts_equal_rebuild(self):
        for b, m in self.m.items():
            kit = K.kit_from_rows(P.rows(m, 'run-x'))
            rebuilt = self.build(b, pat_discount_fwd=0.15, pat_discount_today=0.08, pat_pe=None)  # P/E 20,25,30
            self.assertEqual(rebuilt['kit']['pe'], [20.0, 25.0, 30.0])
            rows = P.rows(rebuilt, 'run-x')
            self.check_same(K.recompute(kit, kit['defaults']['g'], [20.0, 25.0, 30.0], 0.15, 0.08), rows, b)

    def test_top_block_adds_up(self):
        for b, m in self.m.items():
            v = {key(r): r['value'] for r in P.rows(m, 'run-x')}
            for pk in ('FY 2026', 'FY 2027', 'FY 2028'):
                parts = sum(v[(pk, k, '')] for k in ('op_revenue', 'treasury_rev', 'other_inc'))
                self.assertAlmostEqual(parts, v[(pk, 'total_income', '')], delta=TOL, msg=(b, pk))
                self.assertAlmostEqual(v[(pk, 'op_revenue', '')], v[(pk, 'broking', '')] + v[(pk, 'mtf', '')], delta=TOL)
            self.assertAlmostEqual(v[('FY 2028', 'op_revenue', '')],
                                   v[('FY 2028', 'adr_consol', '')] * v[('FY 2028', 'trading_days', '')], delta=TOL, msg=b)

    def test_start_rule_qtd(self):
        """b0 + m0 = the current quarter's QTD consolidated ADR = the build-up's first quarter (step 0)."""
        daily = moving_daily()
        q3 = [r for r in daily if r['trade_date'] >= '2026-10-01']
        n = len({r['trade_date'] for r in q3})
        want = sum(r['revenue_cr'] for r in q3) / n          # (fo + cash + comm) + mtf_gross, per day
        for b, m in self.m.items():
            v = {key(r): r for r in P.rows(m, 'run-x')}
            self.assertAlmostEqual(v[('Q3 FY 2027', 'adr_consol', '')]['value'], want, delta=TOL)
            self.assertEqual(v[('Q3 FY 2027', 'k_step', '')]['value'], 0)
            self.assertEqual(v[('Q4 FY 2028', 'k_step', '')]['value'], 5)
            self.assertIn('Q3 FY 2027 QTD ADR', v[('inputs', 'k_adr_broking0', '')]['rule'])
            self.assertIn('Q3 FY 2027 QTD ADR', v[('Q3 FY 2027', 'broking', '')]['rule'])
            self.assertTrue(all(r['sort_order'] >= 1000 for r in v.values()
                                if r['line'].startswith(('k_', 'in_')) or r['line'] == 'adr_45dma'))
            self.assertEqual(len(v), len(P.rows(m, 'run-x')))     # the primary key holds

    def test_start_rule_falls_back_under_5_days(self):
        """2 engine days into Q3 FY27 (1-2 Oct 2026): the start is Q2 FY27's full-quarter ADR."""
        daily = moving_daily(end='2026-10-02')
        q2 = [r for r in daily if '2026-07-01' <= r['trade_date'] <= '2026-09-30']
        n = len({r['trade_date'] for r in q2})
        for b in self.facts:
            m = self.build(b, daily=daily)
            self.assertAlmostEqual(m['fy27']['adr_broking'],
                                   sum(r['revenue_cr'] for r in q2 if r['segment'] in ('fo', 'cash', 'comm')) / n, delta=1e-9)
            self.assertAlmostEqual(m['fy27']['adr_mtf'], sum(r['revenue_cr'] for r in q2 if r['segment'] == 'mtf_gross') / n,
                                   delta=1e-9)
            rows = P.rows(m, 'run-x')
            self.assertIn('fewer than 5 engine days', {key(r): r for r in rows}[('inputs', 'k_adr_broking0', '')]['rule'])
            kit = K.kit_from_rows(rows)
            d = kit['defaults']
            self.check_same(K.recompute(kit, d['g'], d['pe'], d['disc'], d['today']), rows, (b, 'fallback'))


if __name__ == '__main__':
    unittest.main()
