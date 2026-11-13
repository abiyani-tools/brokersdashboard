"""PAT predictor vectors for the dashboard page's port of src/engine/pat_kit.py (ExchangesDash
tests/fixtures/pat_vectors_<BROKER>.json, contract of 10 Nov 2026; two growth inputs since 13 Nov 2026).

    python3 seed/build_pat_vectors.py <vectors.json> [<out.json>]

Reads a vectors file (its `rows`: sb_pat_lines rows as /api/brokers?view=pat returns them), adds the
in_mtf_qoq_growth input row when the rows predate it (value = in_qoq_growth, the rate MTF grew at in that run, so
the published lines stay reproducible), and rewrites `cases` from pat_kit.recompute(): the defaults, broking growth
moved, MTF growth moved, both moved, and other P/E and discounts. test_pat_kit.py checks recompute() against
pat.build() for the same inputs.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.engine import pat_kit as K  # noqa: E402

MTF_ROW = dict(period_key='inputs', line='in_mtf_qoq_growth', label='QoQ MTF ADR growth', scenario='',
               unit='fraction', regime='projected', sort_order=1014)


def main(src, dst):
    doc = json.loads(Path(src).read_text())
    rows = doc['rows']
    if not any(r['line'] == 'in_mtf_qoq_growth' for r in rows):
        g = next(r['value'] for r in rows if r['line'] == 'in_qoq_growth')
        rows.append(dict(MTF_ROW, value=g,
                         rule='pat_adr_qoq_growth (sb_assumptions; no pat_mtf_qoq_growth row)'))
    for r in rows:
        if r['line'] == 'in_qoq_growth':
            r['label'] = 'QoQ broking ADR growth'
    kit = K.kit_from_rows(rows)
    d = kit['defaults']
    g, gm, pe = d['g'], d['gm'], d['pe']
    cases = [('defaults', g, gm, pe, d['disc'], d['today']),
             ('g - 0.02', g - 0.02, gm, pe, d['disc'], d['today']),
             ('g + 0.015', g + 0.015, gm, pe, d['disc'], d['today']),
             ('gm 12.7%', g, 0.127, pe, d['disc'], d['today']),
             ('g 2%, gm 0%', 0.02, 0.0, pe, d['disc'], d['today']),
             ('pe 20/25/30, disc 15%, today 8%', g, gm, [20.0, 25.0, 30.0], 0.15, 0.08)]
    doc['cases'] = []
    for name, cg, cgm, cpe, disc, today in cases:
        out = K.recompute(kit, cg, cpe, disc, today, cgm)
        doc['cases'].append(dict(name=name, g=cg, gm=cgm, pe=cpe, disc=disc, today=today,
                                 expect={f'{pk}|{line}|{s}': v for (pk, line, s), v in sorted(out.items())}))
    doc['_about'] = (doc.get('_about', '').split(' Two growth inputs')[0]
                     + ' Two growth inputs since 13 Nov 2026: g (broking and cash ADR) and gm (MTF ADR); cases are '
                       'recompute(kit, g, pe, disc, today, gm), written by seed/build_pat_vectors.py.')
    Path(dst).write_text(json.dumps(doc, indent=1, ensure_ascii=False) + '\n')
    print(f'{dst}: {len(rows)} rows, {len(doc["cases"])} cases')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else sys.argv[1])
