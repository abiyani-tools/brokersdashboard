"""Weekly Brokers Update for the CIO: Angel One, Groww, MOSL.

Three steps, each re-runnable on its own:
  fetch   GET the dashboard's public broker API views (publishable key server-side) and the ExchangesDash data
          files (MTF book, broker MTF shares, special sessions) into out/weekly/<date>/raw/. Read-only.
  facts   raw/ -> facts.json: every number the note uses, with the engine run ids.
  render  facts.json + commentary.json -> '<YYYYMMDD>_Weekly Brokers Update.html', then PDF with headless Chrome.

Dates are derived from the data, never typed: as-of = the live runs' as_of_date; the current and previous
quarter / month come from the summary view's `open` and `periods`; quarter date ranges follow the Indian FY.

House rules for this note (AB, 28 Nov 2026):
  * Valuation target = 40% ratio analysis + 60% ADR (PAT model) method; the regression method is left out.
  * No revenue-per-order figures: the engine holds the take rate at the last reported level, so they are an
    assumption, not data.
Commentary (takeaways and section bullets) is written each week into commentary.json; render marks any
missing section [COMMENTARY NEEDED] instead of inventing text.
"""
from __future__ import annotations

import datetime as dt
import json
import statistics as st
import subprocess
from pathlib import Path

API = "https://exchangesdash.vercel.app/api/brokers"
RAW = "https://raw.githubusercontent.com/sucaanalytics-max/ExchangesDash/main/dashboard/data/"
BROKERS = ["ANGELONE", "GROWW", "MOSL"]
VIEWS = ["summary", "daily", "pat", "valuation", "prices"]
DATA_FILES = ["mtf_daily.json", "mtf_brokers.json", "nse_dashboard_data.json", "mcx_dashboard_data.json"]
MTF_ID = {"ANGELONE": "angelone", "GROWW": "groww", "MOSL": "motilaloswal"}
WEIGHTS = {"ratio": 0.4, "adr": 0.6}
VAL_WINDOW = "all"                     # Valuation tab window used for the ratio leg
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
TITLE = "Weekly Brokers Update"          # file and document name: "<YYYYMMDD>_Weekly Brokers Update"

NAME = {"ANGELONE": "Angel One", "GROWW": "Groww", "MOSL": "Motilal Oswal"}
COL = {"ANGELONE": "#2a78d6", "GROWW": "#eb6834", "MOSL": "#1baf7a"}
LIGHT = {"ANGELONE": "#9ec5f4", "GROWW": "#f6b99c", "MOSL": "#9fdcc2"}
INK, INK2, MUTED, GRID = "#1f2328", "#57606a", "#8c959f", "#e5e7ea"
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]


# ---------------------------------------------------------------- fetch
def fetch(raw: Path, session=None, tries: int = 3) -> None:
    import requests
    s = session or requests.Session()
    raw.mkdir(parents=True, exist_ok=True)

    def get(url, params, dest):
        for i in range(tries):
            r = s.get(url, params=params, timeout=180)
            try:
                if r.status_code != 200:
                    raise ValueError(f"HTTP {r.status_code}")
                body = r.json()
                dest.write_text(json.dumps(body))
                return
            except ValueError as e:      # truncated or failed body: retry
                err = e
        raise RuntimeError(f"{url} {params}: {err}")

    for b in BROKERS:
        for v in VIEWS:
            get(API, {"broker": b, "view": v}, raw / f"{b}_{v}.json")
    for f in DATA_FILES:
        get(RAW + f, None, raw / f)


# ---------------------------------------------------------------- dates
def q_range(key: str) -> tuple[str, str]:
    """'Q3 FY 2027' -> ('2026-10-01', '2026-12-31')."""
    q, fy = key.split(" FY ")
    q, fy = int(q[1]), int(fy)
    y, m = (fy - 1, 3 * q + 1) if q <= 3 else (fy, 1)
    start = dt.date(y, m, 1)
    end = (dt.date(y + (m + 3 > 12), (m + 3 - 1) % 12 + 1, 1) - dt.timedelta(days=1))
    return start.isoformat(), end.isoformat()


def m_range(key: str) -> tuple[str, str]:
    """'FY 2027 November' -> ('2026-11-01', '2026-11-30')."""
    _, fy, name = key.split(" ")
    m = MONTHS.index(name) + 1
    y = int(fy) - 1 if m >= 4 else int(fy)
    start = dt.date(y, m, 1)
    end = dt.date(y + (m == 12), m % 12 + 1, 1) - dt.timedelta(days=1)
    return start.isoformat(), end.isoformat()


def short_q(key: str) -> str:
    q, fy = key.split(" FY ")
    return f"{q} FY{fy[2:]}"


def short_m(key: str) -> str:
    return key.split(" ")[2][:3]


def last_on_or_before(series: dict, day: str):
    ks = [k for k in series if k <= day]
    return (max(ks), series[max(ks)]) if ks else (None, None)


# ---------------------------------------------------------------- facts
def build_facts(raw: Path) -> dict:
    load = lambda n: json.loads((raw / n).read_text())
    special = set()
    for f in ("nse_dashboard_data.json", "mcx_dashboard_data.json"):
        try:
            special |= {r["date"] for r in load(f).get("special_sessions", [])}
        except FileNotFoundError:
            pass

    out = {"brokers": {}, "special": sorted(special)}
    for b in BROKERS:
        s = load(f"{b}_summary.json")
        cells = s["cells"]
        cur_q, cur_m = s["open"]["Q"]["key"], s["open"]["M"]["key"]
        prev_q, prev_m = s["periods"]["Q"][1], s["periods"]["M"][1]

        def cell(panel, table, pkey, row, comp="any"):
            for c in cells:
                if (c["panel"], c["table_name"], c["period_key"], c["row_label"]) == (panel, table, pkey, row) \
                        and (comp == "any" or c["comparison"] == comp):
                    return c
            return None

        def v(c, k="value"):
            return None if c is None else c[k]

        panels = {}
        for p in s["panels"]:
            q = {}
            for k in s["periods"]["Q"]:
                c = cell(p, "Quarter", k, k)
                if c and c["value"] is not None:
                    q[k] = c["value"]
            wk = {c["row_label"]: c for c in cells if c["panel"] == p and c["table_name"] == "Week"}
            panels[p] = dict(
                quarters=q,
                cur=v(cell(p, "Quarter", cur_q, cur_q, "QoQ")), qoq=v(cell(p, "Quarter", cur_q, cur_q, "QoQ"), "comp_value"),
                yoy=v(cell(p, "Quarter", cur_q, f"{cur_q} | YoY", "YoY"), "comp_value"),
                prev=v(cell(p, "Quarter", cur_q, prev_q)),
                m_prev=v(cell(p, "Month", cur_m, prev_m)), m_cur=v(cell(p, "Month", cur_m, cur_m, "MoM")),
                mom=v(cell(p, "Month", cur_m, cur_m, "MoM"), "comp_value"),
                m_yoy=v(cell(p, "Month", cur_m, f"{cur_m} | YoY", "YoY"), "comp_value"),
                last5=v(wk.get("Last 5 trading days")), wow=v(wk.get("Last 5 trading days"), "comp_value"),
                prev5=v(wk.get("Previous 5 trading days")), last20=v(wk.get("Last 20 trading days")),
                last45=v(wk.get("Last 45 trading days")),
            )

        daily = {}
        for r in load(f"{b}_daily.json")["rows"]:
            daily.setdefault(r["trade_date"], {})[r["segment"]] = [r["revenue_cr"], r["orders_mn"]]

        pat = load(f"{b}_pat.json")
        val = load(f"{b}_valuation.json")
        out["brokers"][b] = dict(
            label=s["broker"]["label"], as_of=s["run"]["as_of_date"], run_id=s["run"]["run_id"], notes=s["run"]["notes"],
            cur_q=cur_q, prev_q=prev_q, cur_m=cur_m, prev_m=prev_m, q_days=s["open"]["Q"]["days"],
            through={k: x["through"] for k, x in s["through"].items()}, panels=panels, daily=daily,
            pat=[{k: r[k] for k in ("period_key", "line", "scenario", "value", "regime")} for r in pat.get("rows", [])
                 if r["line"] in ("pat", "eps", "close")],
            pat_reason=pat.get("reason"),
            val=[{k: r[k] for k in ("section", "period_key", "line", "scenario", "value")} for r in val.get("rows", [])
                 if r["section"] in ("summary", "pe_bands", "pb_bands")],
            prices={r["trade_date"]: r["close"] for r in load(f"{b}_prices.json")["prices"]},
        )

    mb = load("mtf_brokers.json")
    out["mtf_brokers"] = [{"label": q["label"], "end": q["end"], "industry_cr": q["industry_cr"],
                           "shares": {b: q["shares"].get(MTF_ID[b]) for b in BROKERS}} for q in mb["quarters"]]
    out["mtf_nse"] = {r["date"]: r["closing_cr"] for r in load("mtf_daily.json")["nse"]}
    return out


# ---------------------------------------------------------------- formatting
def pct(x, d=0):
    return "–" if x is None else f"{x * 100:+.{d}f}%".replace("-", "−")


def num(x, d=1):
    return "–" if x is None else f"{x:,.{d}f}"


def cls(x):
    return "" if x is None else ("pos" if x > 0.0005 else "neg" if x < -0.0005 else "")


class Report:
    def __init__(self, F: dict, commentary: dict, report_date: str):
        self.F, self.C, self.date = F, commentary, report_date
        self.B = F["brokers"]
        a = self.B["ANGELONE"]
        self.as_of, self.cur_q, self.prev_q, self.cur_m, self.prev_m = a["as_of"], a["cur_q"], a["prev_q"], a["cur_m"], a["prev_m"]
        self.special = set(F["special"])
        self.qs, self.qe = q_range(self.cur_q)
        self.ps, self.pe = q_range(self.prev_q)
        self.px = {}
        for b in BROKERS:
            p = self.B[b]["prices"]
            d, c = last_on_or_before(p, self.as_of)
            wd = (dt.date.fromisoformat(d) - dt.timedelta(days=7)).isoformat()
            _, w = last_on_or_before(p, wd)
            qd = (dt.date.fromisoformat(self.qs) - dt.timedelta(days=1)).isoformat()
            qdd, q = last_on_or_before(p, qd)
            self.px[b] = dict(date=d, c=c, wk=c / w - 1, qtd=c / q - 1, qtd_from=qdd)

    # -- lookups
    def P(self, b, panel):
        return self.B[b]["panels"][panel]

    def val(self, b, sec, line, scen="", key=VAL_WINDOW):
        for r in self.B[b]["val"]:
            if r["section"] == sec and r["line"] == line and (r["scenario"] or "") == scen and (r["period_key"] or "") in (key, ""):
                return r["value"]
        return None

    def target(self, b, scen):
        return sum(w * self.val(b, "summary", m, scen) for m, w in WEIGHTS.items())

    def has_target(self, b):
        return self.val(b, "summary", "adr", "base") is not None

    def pat(self, b, period, line, scen=""):
        for r in self.B[b]["pat"]:
            if r["period_key"] == period and r["line"] == line and (r["scenario"] or "") == scen:
                return r["value"]
        return None

    def orders(self, b, lo, hi):
        rows = [x["fo"] for d, x in self.B[b]["daily"].items() if lo <= d <= hi and "fo" in x and d not in self.special
                and x["fo"][1] is not None]
        return st.mean(r[1] for r in rows) if rows else None

    def bullets(self, key):
        items = self.C.get(key)
        if not items:
            return "<ul><li class='need'>[COMMENTARY NEEDED]</li></ul>"
        return "<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>"

    # -- charts
    def bars_quarter(self, b, w=230, h=170):
        q = self.P(b, "Consolidated")["quarters"]
        keys = sorted(q, key=lambda k: (k.split(" FY ")[1], k.split(" FY ")[0]))[-9:]
        vals = [q[k] for k in keys]
        top = max(vals) * 1.18
        L, R, T, Bm = 26, 6, 18, 30
        iw, ih = w - L - R, h - T - Bm
        bw = iw / len(keys)
        s = [f"<svg viewBox='0 0 {w} {h}' width='{w}' height='{h}' role='img'><title>{NAME[b]} ADR by quarter</title>"]
        step = 5 if top < 30 else 10
        for g in range(0, int(top) + 1, step):
            y = T + ih - g / top * ih
            s.append(f"<line x1='{L}' x2='{w-R}' y1='{y:.1f}' y2='{y:.1f}' stroke='{GRID}'/><text x='{L-4}' y='{y+3:.1f}' text-anchor='end' class='ax'>{g}</text>")
        for i, (k, v) in enumerate(zip(keys, vals)):
            cur = k == self.cur_q
            x = L + i * bw + bw * 0.16
            bh = v / top * ih
            y = T + ih - bh
            s.append(f"<rect x='{x:.1f}' y='{y:.1f}' width='{bw*0.68:.1f}' height='{bh:.1f}' rx='3' fill='{COL[b] if cur else LIGHT[b]}'/>")
            if cur or k == self.prev_q:
                s.append(f"<text x='{x+bw*0.34:.1f}' y='{y-4:.1f}' text-anchor='middle' class='lbl'>{v:.1f}</text>")
            qq, fy = k.split(" FY ")
            s.append(f"<text x='{x+bw*0.34:.1f}' y='{h-17}' text-anchor='middle' class='ax'>{qq}</text>"
                     f"<text x='{x+bw*0.34:.1f}' y='{h-6}' text-anchor='middle' class='ax'>FY{fy[2:]}</text>")
        return "".join(s) + "</svg>"

    def daily_bars(self, b, w=700, h=120):
        D = self.B[b]["daily"]
        start = m_range(self.prev_m)[0]
        days = [d for d in sorted(D) if start <= d <= self.as_of and d not in self.special and "fo" in D[d]]
        vals = [sum(D[d][s][0] for s in ("fo", "cash", "comm") if s in D[d]) for d in days]
        top = max(vals) * 1.12
        L, R, T, Bm = 30, 6, 8, 18
        iw, ih = w - L - R, h - T - Bm
        bw = iw / len(days)
        s = [f"<svg viewBox='0 0 {w} {h}' width='100%' role='img'><title>{NAME[b]} daily broking revenue</title>"]
        step = 5 if top < 25 else 10
        for g in range(0, int(top) + 1, step):
            y = T + ih - g / top * ih
            s.append(f"<line x1='{L}' x2='{w-R}' y1='{y:.1f}' y2='{y:.1f}' stroke='{GRID}'/><text x='{L-4}' y='{y+3:.1f}' text-anchor='end' class='ax'>{g}</text>")
        mx = max(vals)
        for i, (d, v) in enumerate(zip(days, vals)):
            x = L + i * bw + 1
            bh = v / top * ih
            y = T + ih - bh
            s.append(f"<rect x='{x:.1f}' y='{y:.1f}' width='{bw-2:.1f}' height='{bh:.1f}' rx='2' fill='{COL[b]}'/>")
            if v == mx:
                s.append(f"<text x='{x+bw/2:.1f}' y='{y-2:.1f}' text-anchor='middle' class='lbl'>{v:.1f}</text>")
            if i == 0 or days[i - 1][5:7] != d[5:7] or (days[i - 1][8:] < "15" <= d[8:]):
                lab = dt.date.fromisoformat(d).strftime("%-d %b")
                s.append(f"<text x='{x+bw/2:.1f}' y='{h-5}' text-anchor='middle' class='ax'>{lab}</text>")
        return "".join(s) + "</svg>"

    @staticmethod
    def line_chart(series, ymin, ymax, step, fmt="{:.0f}", xlab=None, w=700, h=200, title=""):
        L, R, T, Bm = 44, 112, 10, 22
        iw, ih = w - L - R, h - T - Bm
        xs = sorted({x for _, pts, _ in series for x, _ in pts})
        xi = {x: i for i, x in enumerate(xs)}
        X = lambda x: L + xi[x] / (len(xs) - 1) * iw
        Y = lambda v: T + ih - (v - ymin) / (ymax - ymin) * ih
        s = [f"<svg viewBox='0 0 {w} {h}' width='100%' role='img'><title>{title}</title>"]
        g = ymin
        while g <= ymax + 1e-9:
            s.append(f"<line x1='{L}' x2='{w-R}' y1='{Y(g):.1f}' y2='{Y(g):.1f}' stroke='{GRID}'/><text x='{L-5}' y='{Y(g)+3:.1f}' text-anchor='end' class='ax'>{fmt.format(g)}</text>")
            g += step
        if xlab:
            for x, lab in xlab(xs):
                s.append(f"<text x='{X(x):.1f}' y='{h-6}' text-anchor='middle' class='ax'>{lab}</text>")
        ends = []
        for name, pts, c in series:
            d = " ".join(f"{'M' if i == 0 else 'L'}{X(x):.1f},{Y(v):.1f}" for i, (x, v) in enumerate(pts))
            s.append(f"<path d='{d}' fill='none' stroke='{c}' stroke-width='2' stroke-linejoin='round'/>")
            x, v = pts[-1]
            ends.append([Y(v), X(x), name, v, c])
        ends.sort()
        for i in range(1, len(ends)):              # keep end labels 11px apart
            ends[i][0] = max(ends[i][0], ends[i - 1][0] + 11)
        for y, x, name, v, c in ends:
            s.append(f"<circle cx='{x:.1f}' cy='{Y(v):.1f}' r='4' fill='{c}' stroke='#fff' stroke-width='2'/><text x='{x+7:.1f}' y='{y+3:.1f}' class='lbl'>{name} {fmt.format(v)}</text>")
        return "".join(s) + "</svg>"

    @staticmethod
    def month_ticks(xs):
        seen, out = set(), []
        for x in xs:
            if x[:7] not in seen:
                seen.add(x[:7])
                out.append((x, dt.date.fromisoformat(x).strftime("%b")))
        return out

    def range_chart(self, b, w=330, h=120):
        bear, base, bull = (self.target(b, s) for s in ("bear", "base", "bull"))
        c = self.px[b]["c"]
        lo, hi = min(bear, c) * 0.93, max(bull, c) * 1.05
        X = lambda v: 14 + (v - lo) / (hi - lo) * (w - 28)
        return (f"<svg viewBox='0 0 {w} {h}' width='{w}' height='{h}' role='img'><title>{NAME[b]} target range</title>"
                f"<rect x='{X(bear):.1f}' y='40' width='{X(bull)-X(bear):.1f}' height='34' rx='4' fill='{LIGHT[b]}'/>"
                f"<rect x='{X(base)-2:.1f}' y='36' width='4' height='42' rx='2' fill='{COL[b]}'/>"
                f"<line x1='{X(c):.1f}' x2='{X(c):.1f}' y1='22' y2='92' stroke='{INK}' stroke-width='1.5' stroke-dasharray='3 3'/>"
                f"<text x='{X(c):.1f}' y='16' text-anchor='middle' class='lbl'>Price ₹{c:,.0f}</text>"
                f"<text x='{X(base):.1f}' y='92' text-anchor='middle' class='lbl'>Base ₹{base:,.0f}</text>"
                f"<text x='{X(bear):.1f}' y='110' class='ax'>Bear ₹{bear:,.0f}</text>"
                f"<text x='{X(bull):.1f}' y='110' text-anchor='end' class='ax'>Bull ₹{bull:,.0f}</text></svg>")

    # -- tables
    def adr_table(self):
        pq, cq, pm, cm = short_q(self.prev_q), short_q(self.cur_q), short_m(self.prev_m), short_m(self.cur_m)
        r = [f"<table><tr><th>₹ Cr / day</th><th>{pq}</th><th>{cq} QTD</th><th>QoQ</th><th>YoY</th><th>{pm}</th><th>{cm}</th><th>{cm} YoY</th></tr>"]
        for b in BROKERS:
            p = self.P(b, "Consolidated")
            r.append(f"<tr><td class='nm' style='color:{COL[b]}'>{NAME[b]}</td><td>{num(p['prev'])}</td><td>{num(p['cur'])} <span class='sm'>({self.B[b]['q_days']} d)</span></td>"
                     f"<td class='{cls(p['qoq'])}'>{pct(p['qoq'])}</td><td class='{cls(p['yoy'])}'>{pct(p['yoy'])}</td><td>{num(p['m_prev'])}</td><td>{num(p['m_cur'])}</td><td class='{cls(p['m_yoy'])}'>{pct(p['m_yoy'])}</td></tr>")
        return "".join(r) + "</table>"

    SEG = [("F&O", "F&amp;O"), ("Cash", "Cash"), ("Commodities", "Commodity"), ("MTF", "MTF")]

    def three_col_head(self, a, b_, c):
        return ("<table><tr><th>₹ Cr / day</th>" + "".join(f"<th colspan='3' style='text-align:center'>{NAME[b]}</th>" for b in BROKERS) + "</tr>"
                + "<tr class='sub'><th></th>" + f"<th>{a}</th><th>{b_}</th><th>{c}</th>" * 3 + "</tr>")

    def seg_table(self):
        r = [self.three_col_head(short_q(self.prev_q).split()[0], f"{short_q(self.cur_q).split()[0]} QTD", "QoQ")]
        for panel, lab in self.SEG + [("Consolidated", "Consolidated")]:
            cells = "".join(f"<td>{num(self.P(b,panel)['prev'],2)}</td><td>{num(self.P(b,panel)['cur'],2)}</td><td class='{cls(self.P(b,panel)['qoq'])}'>{pct(self.P(b,panel)['qoq'])}</td>" for b in BROKERS)
            lab2 = lab + (" <span class='sm'>(NII)</span>" if panel == "MTF" else "")
            r.append(f"<tr class='{'tot' if panel == 'Consolidated' else ''}'><td class='nm'>{lab2}</td>{cells}</tr>")
        r.append("<tr class='sub'><td class='nm' colspan='10'>Where the QoQ increase came from (₹ Cr / day; share of the total increase)</td></tr>")
        for panel, lab in self.SEG:
            cells = ""
            for b in BROKERS:
                tot = self.P(b, "Consolidated")["cur"] - self.P(b, "Consolidated")["prev"]
                dlt = self.P(b, panel)["cur"] - self.P(b, panel)["prev"]
                cells += f"<td></td><td>{dlt:+.2f}</td><td class='sm'>{dlt / tot * 100:.0f}%</td>"
            r.append(f"<tr><td class='nm'>{lab}</td>{cells}</tr>")
        return "".join(r) + "</table>"

    def fo_table(self):
        pq, cq = short_q(self.prev_q), short_q(self.cur_q)
        r = [f"<table><tr><th>F&amp;O</th><th>Orders / day, {pq} → {cq} QTD (Mn)</th><th>F&amp;O ADR QoQ</th></tr>"]
        for b in BROKERS:
            o2, o3 = self.orders(b, self.ps, self.pe), self.orders(b, self.qs, self.as_of)
            ords = f"{o2:.2f} → {o3:.2f} ({pct(o3 / o2 - 1)})" if o2 and o3 else "<span class='sm'>modelled on NSE index-option and BSE contracts, not orders</span>"
            r.append(f"<tr><td class='nm' style='color:{COL[b]}'>{NAME[b]}</td><td>{ords}</td><td class='{cls(self.P(b,'F&O')['qoq'])}'>{pct(self.P(b,'F&O')['qoq'])}</td></tr>")
        nse = self.C.get("nse_ref")
        if nse:
            r.append(f"<tr class='tot'><td class='nm'>NSE (exchange)</td><td class='sm'>{nse['text']}</td><td class='pos'>{nse['qoq']}</td></tr>")
        return "".join(r) + "</table>"

    def week_table(self):
        r = [self.three_col_head("Last 5", "Prev 5", "Change")]
        for panel, lab in self.SEG + [("Consolidated", "Consolidated")]:
            cells = "".join(f"<td>{num(self.P(b,panel)['last5'],2)}</td><td>{num(self.P(b,panel)['prev5'],2)}</td><td class='{cls(self.P(b,panel)['wow'])}'>{pct(self.P(b,panel)['wow'],1)}</td>" for b in BROKERS)
            r.append(f"<tr class='{'tot' if panel == 'Consolidated' else ''}'><td class='nm'>{lab}</td>{cells}</tr>")
        cells = "".join(f"<td colspan='3' class='sm' style='text-align:center'>last 20: {num(self.P(b,'Consolidated')['last20'])} · last 45: {num(self.P(b,'Consolidated')['last45'])}</td>" for b in BROKERS)
        return "".join(r) + f"<tr><td class='nm sm'>Consolidated</td>{cells}</tr></table>"

    def mtf_table(self):
        qs = self.F["mtf_brokers"]
        r = ["<table><tr><th>Share of exchanges' MTF book</th>" + "".join(f"<th>{short_q(q['label'])}</th>" for q in qs) + "</tr>",
             "<tr><td class='nm'>Exchanges' book, ₹ '000 Cr</td>" + "".join(f"<td>{q['industry_cr']/1000:.1f}</td>" for q in qs) + "</tr>"]
        meas = {"ANGELONE": "client funding, overstates", "GROWW": "net book, understates", "MOSL": "basis not stated"}
        for b in BROKERS:
            r.append(f"<tr><td class='nm' style='color:{COL[b]}'>{NAME[b]} <span class='sm'>({meas[b]})</span></td>"
                     + "".join("<td>–</td>" if q["shares"][b] is None else "<td>%.2f%%</td>" % q["shares"][b] for q in qs) + "</tr>")
        return "".join(r) + "</table>"

    def pat_table(self):
        fy = int(self.cur_q.split(" FY ")[1])
        q_keys = [k for k in (f"Q1 FY {fy}", f"Q2 FY {fy}", f"Q3 FY {fy}", f"Q4 FY {fy}") if k <= self.cur_q][-3:]
        heads = "".join(f"<th>{short_q(k)}{'E' if k == self.cur_q else ''}</th>" for k in q_keys)
        r = [f"<table><tr><th>₹ Cr</th>{heads}<th>{short_q(self.cur_q).split()[0]} QoQ</th><th>FY{str(fy-1)[2:]}</th><th>FY{str(fy)[2:]}E</th><th>FY{str(fy+1)[2:]}E</th><th>FY{str(fy+1)[2:]}E EPS (₹)</th></tr>"]
        for b in BROKERS:
            if self.pat(b, f"FY {fy}", "pat") is None:
                r.append(f"<tr><td class='nm' style='color:{COL[b]}'>{NAME[b]}</td><td colspan='{len(q_keys)+5}' class='sm'>No PAT model yet (the dashboard publishes none)</td></tr>")
                continue
            vals = "".join(f"<td>{'<b>' if k == self.cur_q else ''}{num(self.pat(b, k, 'pat'), 0)}{'</b>' if k == self.cur_q else ''}</td>" for k in q_keys)
            c, p = self.pat(b, self.cur_q, "pat"), self.pat(b, self.prev_q, "pat")
            g = c / p - 1 if c and p else None
            r.append(f"<tr><td class='nm' style='color:{COL[b]}'>{NAME[b]}</td>{vals}<td class='{cls(g)}'>{pct(g)}</td>"
                     f"<td>{num(self.pat(b, f'FY {fy-1}', 'pat'), 0)}</td><td>{num(self.pat(b, f'FY {fy}', 'pat'), 0)}</td><td>{num(self.pat(b, f'FY {fy+1}', 'pat'), 0)}</td>"
                     f"<td>{num(self.pat(b, f'FY {fy+1}', 'eps', 'base'), 2)}</td></tr>")
        return "".join(r) + "</table>"

    def val_table(self):
        dlab = dt.date.fromisoformat(self.as_of).strftime("%-d %b")
        qlab = dt.date.fromisoformat(self.px["ANGELONE"]["qtd_from"]).strftime("%-d %b")
        r = [f"<table><tr><th></th><th>Price {dlab}</th><th>Week</th><th>Since {qlab}</th><th>Method</th><th>Bear</th><th>Base</th><th>Bull</th><th>Base vs price</th></tr>"]
        for b in BROKERS:
            p = self.px[b]
            head = (f"<td class='nm' rowspan='{{n}}' style='color:{COL[b]}'>{NAME[b]}</td><td rowspan='{{n}}'>₹{p['c']:,.2f}</td>"
                    f"<td rowspan='{{n}}' class='{cls(p['wk'])}'>{pct(p['wk'],1)}</td><td rowspan='{{n}}' class='{cls(p['qtd'])}'>{pct(p['qtd'],1)}</td>")
            if not self.has_target(b):
                pbc, pbm, pbs = (self.val(b, "pb_bands", l, key="1y") for l in ("pb_current", "pb_mean", "pb_sd"))
                extra = f"P/B {pbc:.2f}x vs 1-year mean {pbm:.2f}x (SD {pbs:.2f}), {(pbc-pbm)/pbs:+.1f} SD" if pbc else ""
                r.append(f"<tr>{head.format(n=1)}<td colspan='5' class='sm' style='text-align:left'>No target (no PAT model). {extra}</td></tr>")
                continue
            rows = [(f"Ratio analysis ({WEIGHTS['ratio']:.0%})", lambda sc: self.val(b, "summary", "ratio", sc)),
                    (f"ADR / PAT model ({WEIGHTS['adr']:.0%})", lambda sc: self.val(b, "summary", "adr", sc)),
                    (f"<b>Target ({WEIGHTS['ratio']*100:.0f} / {WEIGHTS['adr']*100:.0f})</b>", lambda sc: self.target(b, sc))]
            for k, (lab, fn) in enumerate(rows):
                bear, base, bull = fn("bear"), fn("base"), fn("bull")
                up, last = base / p["c"] - 1, k == 2
                r.append(f"<tr class='{'tot' if last else ''}'>{head.format(n=3) if k == 0 else ''}<td style='text-align:left'>{lab}</td>"
                         f"<td>₹{bear:,.0f}</td><td>{'<b>' if last else ''}₹{base:,.0f}{'</b>' if last else ''}</td><td>₹{bull:,.0f}</td><td class='{cls(up)}'>{pct(up,1)}</td></tr>")
        return "".join(r) + "</table>"

    # -- page
    def html(self) -> str:
        B, as_of = self.B, self.as_of
        asof_long = dt.date.fromisoformat(as_of).strftime("%-d %b %Y")
        rep_long = dt.date.fromisoformat(self.date).strftime("%-d %b %Y")
        qfrom = self.px["ANGELONE"]["qtd_from"]
        idx = [(NAME[b], [(d, c / B[b]["prices"][qfrom] * 100) for d, c in sorted(B[b]["prices"].items()) if qfrom <= d <= as_of], COL[b])
               for b in BROKERS if qfrom in B[b]["prices"]]
        allv = [v for _, pts, _ in idx for _, v in pts]
        price_chart = self.line_chart(idx, ymin=10 * (int(min(allv)) // 10), ymax=10 * (int(max(allv)) // 10 + 1), step=10, h=165,
                                      title=f"Share prices indexed to {qfrom}",
                                      xlab=lambda xs: [(x, dt.date.fromisoformat(x).strftime("%-d %b")) for x in xs[::max(1, len(xs) // 5)]])
        mstart = (dt.date.fromisoformat(as_of) - dt.timedelta(days=240)).isoformat()
        mtf = [(d, v / 1000) for d, v in sorted(self.F["mtf_nse"].items()) if mstart <= d <= as_of]
        lo, hi = min(v for _, v in mtf), max(v for _, v in mtf)
        mtf_chart = self.line_chart([("NSE MTF book", mtf, "#2a78d6")], ymin=10 * (int(lo) // 10), ymax=10 * (int(hi) // 10 + 1), step=10,
                                    h=180, title="NSE MTF book", xlab=self.month_ticks)
        takes = "".join(f"<li>{x}</li>" for x in self.C.get("takeaways", [])) or "<li class='need'>[COMMENTARY NEEDED]</li>"
        cq = short_q(self.cur_q)
        sp = ", ".join(dt.date.fromisoformat(d).strftime("%-d %b") for d in sorted(self.special) if m_range(self.prev_m)[0] <= d <= as_of)
        runs = ", ".join(f"{NAME[b]} {B[b]['run_id'][:8]}" for b in BROKERS)
        nse_src = f" {self.C['nse_ref']['source']}." if self.C.get("nse_ref") else ""
        return f"""<!doctype html><html><head><meta charset='utf-8'><title>{self.date.replace('-', '')}_{TITLE}</title><style>
@page {{ size: A4; margin: 14mm 13mm 16mm; }}
body {{ font: 9.6pt/1.42 -apple-system, 'Helvetica Neue', Arial, sans-serif; color: {INK}; margin: 0; background:#fff; }}
.hero {{ background:#1d3557; color:#fff; padding:16px 20px 14px; border-radius:2px; }}
.hero h1 {{ margin:0 0 4px; font-size:18pt; }} .hero p {{ margin:2px 0; color:#d5dde8; }} .hero .s {{ font-size:8.4pt; color:#aab8cc; }}
.key {{ background:#eef4fb; border-left:5px solid #2a78d6; padding:10px 16px 6px; margin:14px 0 6px; }}
.key h3 {{ margin:0 0 4px; color:#2a78d6; font-size:11pt; }} .key ul {{ margin:0; padding-left:16px; }} .key li {{ margin-bottom:5px; }}
h2 {{ font-size:14pt; color:#1d3557; border-bottom:1px solid #d0d7de; padding-bottom:3px; margin:18px 0 8px; break-after:avoid; }}
table {{ border-collapse:collapse; width:100%; margin:6px 0 8px; font-size:8.8pt; break-inside:avoid; }}
th {{ background:#1d3557; color:#fff; font-weight:600; padding:5px 6px; text-align:right; }} th:first-child {{ text-align:left; }}
tr.sub th, tr.sub td {{ background:#e9eef5; color:{INK2}; font-weight:600; }}
td {{ padding:4px 6px; border-bottom:1px solid #e5e7ea; text-align:right; font-variant-numeric: tabular-nums; }}
td.nm {{ text-align:left; font-weight:600; }} tr.tot td {{ background:#f3f6fa; font-weight:600; }}
.pos {{ color:#0f7a3d; font-weight:600; }} .neg {{ color:#c0392b; font-weight:600; }} .sm {{ font-size:8pt; color:{INK2}; font-weight:400; }}
.cap {{ font-size:8.2pt; color:{INK2}; font-style:italic; margin:2px 0 8px; }}
.row3 {{ display:flex; justify-content:space-between; }}
.ax {{ font-size:8px; fill:{MUTED}; }} .lbl {{ font-size:8.5px; fill:{INK}; font-weight:600; }}
ul {{ padding-left:16px; margin:4px 0; }} li {{ margin-bottom:4px; }} .need {{ color:#c0392b; font-weight:600; }}
.dl b {{ display:block; font-size:8.6pt; margin-top:4px; }}
.brk {{ break-before:page; }} .src {{ font-size:7.8pt; color:{INK2}; font-style:italic; margin-top:12px; }}
</style></head><body>
<div class='hero'><h1>Brokers Update: Angel One · Groww · Motilal Oswal</h1>
<p>Revenue run-rate by segment, F&amp;O orders, MTF, PAT run-rate and valuation</p>
<p class='s'>Data to the close of {asof_long} · ADR = average daily revenue, ₹ Cr per trading day · broker figures are the dashboard's estimates until {cq} is reported</p></div>
<div class='key'><h3>Key takeaways</h3><ul>{takes}</ul></div>

<h2>1. Revenue per day (ADR), consolidated</h2>
{self.adr_table()}
<div class='row3'>{''.join(f"<div><b style='color:{COL[b]}'>{NAME[b]}</b><br>{self.bars_quarter(b)}</div>" for b in BROKERS)}</div>
<p class='cap'>Consolidated ADR by quarter, ₹ Cr / day (broking + MTF; MOSL: net brokerage + MTF NII). Current quarter ({cq}, {B['ANGELONE']['q_days']} sessions to {dt.date.fromisoformat(as_of).strftime('%-d %b')}) in full colour.</p>
{self.bullets('s1')}

<h2>2. Where the growth is: ADR by segment</h2>
{self.seg_table()}
<p class='cap'>{short_q(self.prev_q)} is reported; {cq} QTD is the dashboard estimate. MTF is gross interest income for Angel One and Groww and net interest income for MOSL.</p>
{self.bullets('s2')}

<h2>3. F&amp;O: brokers vs the exchange</h2>
{self.fo_table()}
{self.bullets('s3')}

<h2>4. This week</h2>
{self.week_table()}
<p class='cap'>Last 5 vs previous 5 trading days in each segment's own series (MTF and Consolidated can lag a day; commodity includes MCX-only sessions).</p>
<div class='dl'>{''.join(f"<b style='color:{COL[b]}'>{NAME[b]}: daily broking revenue (F&amp;O + cash + commodity), ₹ Cr</b>{self.daily_bars(b)}" for b in BROKERS)}</div>
<p class='cap'>{('Special sessions left out, as in the averages: ' + sp + '. ') if sp else ''}The tall bars are expiry days.</p>
{self.bullets('s4')}

<h2 class='brk'>5. MTF book</h2>
{mtf_chart}
<p class='cap'>NSE MTF closing book, ₹ '000 Cr (NSE daily margin-trading file, via the dashboard).</p>
{self.mtf_table()}
<p class='cap'>Each broker's book from its own filings ÷ the exchanges' combined book (NSE + BSE) on the same date. The bases differ, so compare each broker with itself over time.</p>
{self.bullets('s5')}

<h2>6. PAT run-rate (dashboard PAT model)</h2>
{self.pat_table()}
{self.bullets('s6')}

<h2>7. Share prices vs targets</h2>
{self.val_table()}
<div class='row3'>{''.join(self.range_chart(b) for b in BROKERS if self.has_target(b))}</div>
<p class='cap'>Target = {WEIGHTS['ratio']:.0%} ratio analysis + {WEIGHTS['adr']:.0%} ADR method (PAT model); the regression method is left out. Ratio analysis uses the Valuation tab's full-history window. Bear–Bull range, Base marked; dashed line = latest close.</p>
{price_chart}
<p class='cap'>Share prices indexed to {dt.date.fromisoformat(qfrom).strftime('%-d %b %Y')} = 100.</p>
{self.bullets('s7')}

<h2>8. Next week</h2>
{self.bullets('s8')}
<p class='src'>Sources: brokers-dashboard live runs as of {asof_long} ({runs}) via ExchangesDash /api/brokers; MTF from ExchangesDash mtf_daily.json and mtf_brokers.json (broker filings); prices from the dashboard.{nse_src}</p>
</body></html>"""


def render(facts: dict, commentary: dict, report_date: str, out_html: Path) -> Path:
    out_html.write_text(Report(facts, commentary, report_date).html())
    pdf = out_html.with_suffix(".pdf")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf}",
                    out_html.resolve().as_uri()], check=True, capture_output=True)
    return pdf
