// dev/serve.mjs — local stand-in for `vercel dev` (replica only; no dependencies).
//
//   node dev/serve.mjs                 # http://localhost:8787, data from upstream GitHub main
//   DATA_SOURCE=local node dev/serve.mjs   # data from this checkout's dashboard/data
//
// Serves dashboard/ as static files, the `/live` rewrite, and dashboard/api/*.js
// through a small req/res shim. `/data/*` goes through api/upstream-data.js, as
// on the replica deploy. /api/trigger-live-polls is refused: it dispatches the
// owner's workflows and must never run from here. Env vars come from
// .env.local at the repo root (gitignored), e.g. BROKERS_SUPABASE_URL / _KEY.

import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const ROOT = process.env.APP_ROOT;
const DASH = path.join(ROOT, 'dashboard');
const PORT = Number(process.env.PORT || 8787);
const DATA_SOURCE = process.env.DATA_SOURCE || 'upstream';
const BLOCKED_API = new Set(['trigger-live-polls']);
const require = createRequire(import.meta.url);

const envFile = process.env.ENV_FILE;
if (fs.existsSync(envFile)) {
  for (const line of fs.readFileSync(envFile, 'utf8').split('\n')) {
    const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*?)\s*$/);
    if (m && !(m[1] in process.env)) process.env[m[1]] = m[2].replace(/^['"]|['"]$/g, '');
  }
}

const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8',
  '.json': 'application/json', '.svg': 'image/svg+xml', '.csv': 'text/csv; charset=utf-8', '.png': 'image/png' };

function shimRes(res) {
  res.status = code => { res.statusCode = code; return res; };
  res.json = obj => { if (!res.getHeader('Content-Type')) res.setHeader('Content-Type', 'application/json'); res.end(JSON.stringify(obj)); return res; };
  res.send = body => { res.end(body); return res; };
  return res;
}

async function runApi(name, query, req, res) {
  if (BLOCKED_API.has(name)) return shimRes(res).status(403).json({ error: `${name} is disabled in the replica` });
  const file = path.join(DASH, 'api', `${name}.js`);
  if (!/^[a-z0-9-]+$/.test(name) || !fs.existsSync(file)) return shimRes(res).status(404).json({ error: 'No such function' });
  delete require.cache[file];   // pick up edits without a restart
  req.query = query;
  try { await require(file)(req, shimRes(res)); }
  catch (err) { console.error(name, err); if (!res.headersSent) shimRes(res).status(500).json({ error: err.message }); }
}

function serveStatic(rel, res) { return serveFile(DASH, rel, res); }

// dev/out/ holds the parity check's generated pages (dev/parity/excel_summary.py)
function serveFile(dir, rel, res) {
  const file = path.normalize(path.join(dir, rel));
  if (!file.startsWith(dir) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
    res.statusCode = 404; return res.end('Not found');
  }
  res.setHeader('Content-Type', TYPES[path.extname(file)] || 'application/octet-stream');
  res.setHeader('Cache-Control', 'no-store');
  fs.createReadStream(file).pipe(res);
}

http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);
  const p = decodeURIComponent(url.pathname);
  const query = Object.fromEntries(url.searchParams);
  try {
    if (p === '/api/brokers' && query.view === 'valuation' && process.env.VAL_DIR) {   // dry-run stand-in until sb_valuation_lines exists
      const f = path.join(process.env.VAL_DIR, `${(query.broker || '').toUpperCase()}_valuation_lines.json`);
      res.setHeader('Content-Type', 'application/json');
      if (!fs.existsSync(f)) return res.end(JSON.stringify({ run: null, rows: [], reason: 'no local dry run' }));
      const rows = JSON.parse(fs.readFileSync(f, 'utf8'));
      return res.end(JSON.stringify({ run: { run_id: rows[0].run_id, as_of_date: process.env.VAL_ASOF }, rows }));
    }
    if (p.startsWith('/api/')) return await runApi(p.slice(5).replace(/\/$/, ''), query, req, res);
    if (p.startsWith('/data/') && DATA_SOURCE === 'upstream') return await runApi('upstream-data', { file: p.slice(6) }, req, res);
    if (p.startsWith('/dev-out/')) return serveFile(path.join(ROOT, 'dev', 'out'), p.slice(9), res);
    if (p === '/' ) return serveStatic('index.html', res);
    if (p === '/live') return serveStatic('live.html', res);
    return serveStatic(p.slice(1), res);
  } finally {
    console.log(`${req.method} ${p} ${res.statusCode}`);
  }
}).listen(PORT, () => console.log(`replica on http://localhost:${PORT} (data: ${DATA_SOURCE})`));
