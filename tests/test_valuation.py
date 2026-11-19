"""Valuation (src/engine/valuation.py) against the 09.11 workbook: fed the workbook's own daily ADR and prices
(tests/fixtures/valuation_wb_0911.json, from '<broker> Revenue'!B/M/Q), the engine must reproduce the regression,
ratio and P/E band cells of `Angel One - ADR model (A+B)` and `Groww - ADR Model` and the weighted net value."""
import json
import unittest
from pathlib import Path

from src.engine import valuation as V

FIX = json.load(open(Path(__file__).parent / 'fixtures/valuation_wb_0911.json'))
W = dict(regression=0.2, ratio=0.3, adr=0.5)


def wb(broker):
    b = FIX['brokers'][broker]
    adr = [(r['date'], r['adr']) for r in b['daily']]
    prices = [dict(trade_date=r['date'], close=r['price']) for r in b['daily'] if r['price']]
    c = {k: v for k, (v, _) in b['cells'].items()}
    return b, adr, prices, c


class TestAgainstWorkbook(unittest.TestCase):
    def check(self, broker):
        b, adr, prices, c = wb(broker)
        rows = V.build_daily(adr, prices, 45)
        # the 45-day average, ratio and regression-implied price, day by day ('<broker> Revenue'!N, R, AK)
        for mine, theirs in zip(rows, b['daily']):
            if theirs['dma45'] is None:
                self.assertIsNone(mine['dma'], mine['date'])
                continue
            self.assertAlmostEqual(mine['dma'], theirs['dma45'], places=9, msg=mine['date'])
            self.assertAlmostEqual(mine['ratio'], theirs['ratio'], places=9, msg=mine['date'])
        reg = V.regression(rows, c['adr_now'], c['band'])
        self.assertAlmostEqual(reg['slope'], c['slope'], places=9)
        self.assertAlmostEqual(reg['intercept'], c['intercept'], places=7)
        self.assertAlmostEqual(reg['r2'], c['r2'], places=9)
        for s in V.SCENARIOS:
            self.assertAlmostEqual(reg['values'][s], c[f'reg_{s}'], places=7, msg=s)
        for mine, theirs in zip(rows, b['daily']):
            if theirs['implied'] not in (None, ''):
                self.assertAlmostEqual(reg['slope'] * mine['dma'] + reg['intercept'], theirs['implied'], places=7)
        rat = V.ratio(rows, c['adr_now'])
        self.assertAlmostEqual(rat['mean'], c['ratio_mean'], places=9)
        self.assertAlmostEqual(rat['sd'], b['ratio_sd'][0], places=9)
        for s, k in zip(V.SCENARIOS, ('ratio_lo', 'ratio_mean', 'ratio_hi')):
            self.assertAlmostEqual(rat['values'][s] / c['adr_now'], c[k], places=9)
        return reg, rat, c

    def test_angel(self):
        reg, rat, c = self.check('ANGELONE')
        # AB, 9 Nov (point 2): the ratio leg is a current value (Ratio × Q3 FY27 ADR, D50:F50), as the summary takes it
        for s in V.SCENARIOS:
            self.assertAlmostEqual(rat['values'][s], c[f'ratio_{s}'], places=7)
        # AB, 9 Nov (point 1): 20 / 30 / 50 weights; the sheet's plain AVERAGE is replaced.
        # Base: 0.2 × 316.527 + 0.3 × 354.053 + 0.5 × 349.774 = 344.408
        vals = dict(regression=reg['values'], ratio=rat['values'], adr={s: c[f'adr_{s}'] for s in V.SCENARIOS})
        net = V.triangulate(vals, W)
        self.assertAlmostEqual(net['base'], 0.2 * 316.5268994920784 + 0.3 * 354.053233403514 + 0.5 * 349.77358306406893, places=9)
        self.assertAlmostEqual(net['base'], 344.408, places=3)
        self.assertEqual((c['w_reg'], c['w_ratio'], c['w_adr']), (0.2, 0.3, 0.5))

    def test_groww(self):
        reg, rat, c = self.check('GROWW')
        vals = dict(regression=reg['values'], ratio=rat['values'], adr={s: c[f'adr_{s}'] for s in V.SCENARIOS})
        net = V.triangulate(vals, W)
        for s in V.SCENARIOS:   # Groww - ADR Model!E74:G74 (SUMPRODUCT with H71:H73)
            self.assertAlmostEqual(rat['values'][s], c[f'ratio_{s}'], places=7)
            self.assertAlmostEqual(net[s], c[f'avg_{s}'], places=7, msg=s)

    def test_pe_bands(self):
        """The band statistics of the vendor P/E column ('Angel One Ltd.1'!K) as the sheet takes them: 3 years and
        since 1 Apr 2025, STDEV.S."""
        pe = FIX['brokers']['ANGELONE']['pe']
        c = {k: v for k, (v, _) in pe['cells'].items()}
        series = sorted(({'date': r['date'], 'pe': r['cons_ttm_pe']} for r in pe['rows']), key=lambda r: r['date'])
        three = V.pe_bands(series, '2023-11-03')
        self.assertAlmostEqual(three['mean'], c['mean3y'], places=9)
        self.assertAlmostEqual(three['sd'], c['sd3y'], places=9)
        apr = V.pe_bands(series, '2025-04-01')
        self.assertAlmostEqual(apr['mean'], c['mean_apr25'], places=9)
        self.assertAlmostEqual(apr['sd'], c['sd_apr25'], places=9)
        self.assertAlmostEqual(apr['current'], c['current'], places=9)

    def test_weights_must_add_up(self):
        with self.assertRaises(V.ValuationInputMissing):
            V.triangulate({m: {s: 1.0 for s in V.SCENARIOS} for m in V.METHODS}, dict(regression=0.2, ratio=0.3, adr=0.4))


class TestTtmPe(unittest.TestCase):
    def test_quarter_counts_from_results_date(self):
        q = [('2025-01-15', 'Q3 FY 2025', 100.0), ('2025-04-15', 'Q4 FY 2025', 100.0),
             ('2025-07-15', 'Q1 FY 2026', 100.0), ('2025-10-15', 'Q2 FY 2026', 100.0), ('2026-01-15', 'Q3 FY 2026', 200.0)]
        px = [dict(trade_date='2025-10-14', close=10.0), dict(trade_date='2025-10-15', close=10.0),
              dict(trade_date='2026-01-15', close=10.0)]
        s = V.ttm_pe(px, q, 100.0)
        self.assertEqual([r['date'] for r in s], ['2025-10-15', '2026-01-15'])
        self.assertAlmostEqual(s[0]['pe'], 10 * 100 / 400)
        self.assertAlmostEqual(s[1]['pe'], 10 * 100 / 500)


    def test_pe_quarters_reads_results_dates_and_period_end_shares(self):
        from src.engine.pat import Assume
        A = Assume([dict(broker_id='ANGELONE', key='val_results_dates', value=None,
                         value_text='Q1 FY 2026=2025-07-16;Q2 FY 2026=2025-10-15')], 'ANGELONE')
        facts = [dict(period_type='Q', period_key='Q1 FY 2026', metric='pl_pat', segment='consolidated', value=1144.68, unit='Rs Mn'),
                 dict(period_type='Q', period_key='Q2 FY 2026', metric='pl_pat', segment='consolidated', value=211.73, unit='Rs Cr'),
                 dict(period_type='Q', period_key='Q3 FY 2026', metric='pl_pat', segment='consolidated', value=268.7, unit='Rs Cr'),
                 dict(period_type='Q', period_key='Q2 FY 2026', metric='shares_period_end_cr', segment='consolidated', value=90.717, unit='crore shares'),
                 dict(period_type='Q', period_key='Q2 FY 2027', metric='shares_outstanding_cr', segment='consolidated', value=91.459, unit='crore shares')]
        q = V.pe_quarters(facts, A)
        self.assertEqual(q, [('2025-07-16', 'Q1 FY 2026', 114.468, None), ('2025-10-15', 'Q2 FY 2026', 211.73, 90.717)])
        self.assertEqual(V.pe_quarters(facts, Assume([], 'GROWW')), [])


class TestWindows(unittest.TestCase):
    def test_months_back_and_cover(self):
        self.assertEqual(V.months_back('2026-11-06', 3), '2026-08-06')
        self.assertEqual(V.months_back('2026-05-31', 3), '2026-02-28')      # month end clipped
        self.assertEqual(V.months_back('2026-11-06', 36), '2023-11-06')
        self.assertTrue(V.covered('2025-04-10', '2025-04-01'))              # within the 10-day slack
        self.assertFalse(V.covered('2025-04-12', '2025-04-01'))

    def test_build_fits_each_window_over_its_own_days(self):
        """build() on the workbook's Angel series: 'All' is the workbook fit, a window's fit is the fit over its days,
        windows the data start after are not published, and the ADR leg is the same in every window."""
        from src.engine.pat import Assume
        b, adr, prices, c = wb('ANGELONE')
        daily = [dict(trade_date=d, segment=s, revenue_cr=(v if s == 'fo' else 0.0)) for d, v in adr
                 for s in ('fo', 'cash', 'comm', 'mtf_gross')]
        A = Assume(json.load(open(Path(__file__).parents[1] / 'seed/valuation_assumptions.json'))['assumptions'], 'ANGELONE')
        targets = {s: c[f'adr_{s}'] for s in V.SCENARIOS}
        m = V.build('ANGELONE', daily, prices, targets, A)
        self.assertAlmostEqual(m['windows']['all']['regression']['slope'], c['slope'], places=9)
        self.assertAlmostEqual(m['windows']['all']['ratio']['mean'], c['ratio_mean'], places=9)
        self.assertEqual(set(m['windows']), {'all', '3m', '6m', '1y', 'apr25'})   # ADR from 2025-01-01: no 2y / 3y
        rows = [r for r in V.build_daily(adr, prices) if r['date'] >= V.months_back(m['as_of'], 6)]
        self.assertAlmostEqual(m['windows']['6m']['regression']['slope'], V.regression(rows, m['adr_now'], 0.1)['slope'], places=9)
        self.assertEqual(m['windows']['3m']['values']['adr'], targets)
        net = m['windows']['3m']['net']['base']
        w = m['windows']['3m']['values']
        self.assertAlmostEqual(net, 0.2 * w['regression']['base'] + 0.3 * w['ratio']['base'] + 0.5 * w['adr']['base'], places=9)
        keys = {(r['section'], r['period_key'], r['line'], r['scenario']) for r in V.lines(m, 'run')}
        self.assertEqual(len(keys), len(V.lines(m, 'run')))                  # the table's primary key holds

    def test_groww_pe_from_its_results_dates(self):
        """Groww's TTM P/E: the pre-listing quarters count from the listing day, each later quarter from its results
        date, so the series starts on 21 Nov 2025 (Q2 FY26 results); the whole series is the 'all' band."""
        from src.engine.pat import Assume
        A = Assume(json.load(open(Path(__file__).parents[1] / 'seed/valuation_assumptions.json'))['assumptions'], 'GROWW')
        pat = {'Q3 FY 2025': (7571.1, 'Rs Mn'), 'Q4 FY 2025': (3090.89, 'Rs Mn'), 'Q1 FY 2026': (378.35, 'Rs Cr'),
               'Q2 FY 2026': (471.34, 'Rs Cr'), 'Q3 FY 2026': (5469.33, 'Rs Mn'), 'Q4 FY 2026': (686.36, 'Rs Cr')}
        facts = [dict(period_type='Q', period_key=q, metric='pl_pat', segment='consolidated', value=v, unit=u)
                 for q, (v, u) in pat.items()]
        q = V.pe_quarters(facts, A)
        self.assertEqual([x[0] for x in q], ['2025-11-12'] * 3 + ['2025-11-21', '2026-01-14', '2026-04-20'])
        px = [dict(trade_date=d, close=c) for d, c in (('2025-11-12', 131.33), ('2025-11-20', 150.0), ('2025-11-21', 155.0),
                                                       ('2026-01-13', 160.0), ('2026-01-14', 161.0), ('2026-04-20', 170.0))]
        s = V.ttm_pe(px, q, 623.905)
        self.assertEqual([r['date'] for r in s], ['2025-11-21', '2026-01-13', '2026-01-14', '2026-04-20'])
        self.assertAlmostEqual(s[0]['ttm_pat'], 757.11 + 309.089 + 378.35 + 471.34, places=6)      # Q3 FY25 .. Q2 FY26
        self.assertAlmostEqual(s[2]['ttm_pat'], 309.089 + 378.35 + 471.34 + 546.933, places=6)     # Q4 FY25 .. Q3 FY26
        self.assertAlmostEqual(s[0]['pe'], 155.0 * 623.905 / s[0]['ttm_pat'])
        self.assertEqual(V.pe_bands(s, s[0]['date'])['n'], 4)


if __name__ == '__main__':
    unittest.main()


class TestPriceToBook(unittest.TestCase):
    """Consolidated P/B (AB, 19 Nov 2026): close ÷ (net worth ÷ shares) of the latest quarter whose results are out."""
    FACTS = [
        dict(period_type='Q', segment='consolidated', metric='net_worth', period_key='Q4 FY 2026', value=12888.1, unit='Rs Cr'),
        dict(period_type='Q', segment='consolidated', metric='shares_period_end_cr', period_key='Q4 FY 2026', value=60.0, unit='crore shares'),
        dict(period_type='Q', segment='consolidated', metric='net_worth', period_key='Q1 FY 2027', value=140000.0, unit='Rs Mn'),
        dict(period_type='Q', segment='consolidated', metric='shares_period_end_cr', period_key='Q1 FY 2027', value=60.5, unit='crore shares'),
        # no results date: left out
        dict(period_type='Q', segment='consolidated', metric='net_worth', period_key='Q2 FY 2027', value=15000.0, unit='Rs Cr'),
        dict(period_type='Q', segment='consolidated', metric='shares_period_end_cr', period_key='Q2 FY 2027', value=61.0, unit='crore shares'),
        # no share count: left out
        dict(period_type='Q', segment='consolidated', metric='net_worth', period_key='Q3 FY 2026', value=13631.7, unit='Rs Cr'),
        # standalone: ignored
        dict(period_type='Q', segment='standalone', metric='net_worth', period_key='Q4 FY 2025', value=1.0, unit='Rs Cr'),
    ]

    @staticmethod
    def A(d):
        return lambda k, default=None: d.get(k, default)

    def test_quarters(self):
        A = self.A(dict(val_results_dates='Q3 FY 2026=2026-01-28; Q4 FY 2026=2026-04-29;Q1 FY 2027=2026-07-28;Q4 FY 2025=2025-04-29'))
        self.assertEqual(V.pb_quarters(self.FACTS, A), [
            ('2026-04-29', 'Q4 FY 2026', 12888.1, 60.0), ('2026-07-28', 'Q1 FY 2027', 14000.0, 60.5)])
        self.assertEqual(V.pb_quarters(self.FACTS, self.A({})), [])

    def test_series_steps_on_results_dates(self):
        qs = [('2026-04-29', 'Q4 FY 2026', 12000.0, 60.0), ('2026-07-28', 'Q1 FY 2027', 14000.0, 70.0)]
        prices = [dict(trade_date=d, close=c) for d, c in
                  (('2026-04-28', 900.0), ('2026-04-29', 1000.0), ('2026-07-27', 1100.0), ('2026-07-28', 1200.0), ('2026-07-29', None))]
        s = V.pb_series(prices, qs)
        self.assertEqual([r['date'] for r in s], ['2026-04-29', '2026-07-27', '2026-07-28'])   # none before the first results
        self.assertAlmostEqual(s[0]['bvps'], 200.0)                      # 12,000 ÷ 60
        self.assertAlmostEqual(s[0]['pb'], 5.0)                          # 1,000 ÷ 200
        self.assertEqual(s[1]['quarter'], 'Q4 FY 2026')                  # the day before Q1 FY27's results
        self.assertAlmostEqual(s[2]['pb'], 1200.0 / 200.0)               # 14,000 ÷ 70 = 200
        self.assertEqual(s[2]['quarter'], 'Q1 FY 2027')

    def test_bands_per_window_and_lines(self):
        import datetime as dt
        d0 = dt.date(2023, 1, 2)
        days = [(d0 + dt.timedelta(days=i)).isoformat() for i in range(0, 1400, 1)]
        prices = [dict(trade_date=d, close=100.0 + (i % 37)) for i, d in enumerate(days)]
        qs = [('2023-01-02', 'Q2 FY 2023', 5000.0, 50.0)]
        A = self.A(dict(val_pe_since='2025-04-01'))
        m = V.build_pb('MOSL', prices, qs, A)
        self.assertEqual(set(m['windows']), {'3m', '6m', '1y', '2y', '3y', 'apr25'})   # no 'all'
        last = m['series'][-1]['date']
        for k, n in (('1y', 12), ('3y', 36)):
            xs = [r['pb'] for r in m['series'] if r['date'] >= V.months_back(last, n)]
            self.assertAlmostEqual(m['windows'][k]['mean'], V.mean(xs))
            self.assertAlmostEqual(m['windows'][k]['sd'], V.stdev_s(xs))
        self.assertEqual(m['windows']['apr25']['since'], '2025-04-01')
        rows = V.pb_lines(m, 'run-1')
        self.assertEqual(len({(r['section'], r['period_key'], r['line'], r['scenario']) for r in rows}), len(rows))
        self.assertEqual(sum(r['section'] == 'pb' and r['line'] == 'pb' for r in rows), len(m['series']))
        self.assertEqual([r['line'] for r in rows if r['section'] == 'pb_book'], ['net_worth', 'shares', 'bvps'])
        self.assertAlmostEqual(next(r['value'] for r in rows if r['line'] == 'bvps' and r['section'] == 'pb_book'), 100.0)
        # a series that starts after a window's start leaves that window out
        late = V.build_pb('MOSL', prices[-200:], qs, A)
        self.assertNotIn('1y', late['windows'])
        self.assertIn('6m', late['windows'])
        self.assertIsNone(V.build_pb('MOSL', prices, [], A))

    def test_pb_dates_win_over_results_dates(self):
        A = self.A({'val_pb_dates': 'Q4 FY 2026=2026-04-01', 'val_results_dates': 'Q4 FY 2026=2026-04-29'})
        self.assertEqual(V.pb_quarters(self.FACTS, A)[0][0], '2026-04-01')
