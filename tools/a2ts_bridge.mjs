// Minimal server for Apple2TS's built-in remote-control bridge (src/ui/api/remotecontrol.ts).
// Serves the web build and implements the /api/client/* endpoints the page talks to when loaded
// with ?remoteControl=1. Adds /api/cmd so scripts can send commands and wait for the reply.
//
//   node a2ts_bridge.mjs --dist <apple2ts-dist/dist> [--disk game.dsk] [--port 8765] [--chromium]
//   curl -s localhost:8765/api/cmd -d '{"action":"getStatus"}'
//
// --disk  is served at /disks/game.dsk and loaded by the page via its #game.dsk URL fragment, which
//         also boots it. The emulator writes to its in-browser copy only, so the file is never modified.
// --chromium  also launches headless Chromium (no window) pointed at the page.
import http from 'http';
import fs from 'fs';
import path from 'path';
import { spawn } from 'child_process';

const arg = (n, d) => { const i = process.argv.indexOf('--' + n); return i < 0 ? d : (process.argv[i + 1]?.startsWith('--') || i + 1 >= process.argv.length ? true : process.argv[i + 1]); };
const dist = path.resolve(arg('dist'));
const disk = arg('disk') ? path.resolve(arg('disk')) : null;
const port = Number(arg('port', 8765));
const MIME = { html: 'text/html', js: 'text/javascript', css: 'text/css', png: 'image/png', jpg: 'image/jpeg', mp3: 'audio/mpeg', json: 'application/json', svg: 'image/svg+xml', woff2: 'font/woff2', woff: 'font/woff', ico: 'image/x-icon' };

const clients = new Map();            // clientId -> {res, state}
const waiting = new Map();            // commandId -> resolve
let nextId = 1;
const body = req => new Promise(r => { let b = ''; req.on('data', c => b += c); req.on('end', () => r(b ? JSON.parse(b) : {})); });
const json = (res, o, code = 200) => { res.writeHead(code, { 'Content-Type': 'application/json' }); res.end(JSON.stringify(o)); };

function sendCommand(action, payload = {}, timeoutMs = 120000) {
  const c = [...clients.values()][0];
  if (!c) return Promise.resolve({ ok: false, error: 'no emulator page connected' });
  const commandId = 'c' + nextId++;
  return new Promise(resolve => {
    const t = setTimeout(() => { waiting.delete(commandId); resolve({ ok: false, error: 'timeout waiting for reply' }); }, timeoutMs);
    waiting.set(commandId, r => { clearTimeout(t); resolve(r); });
    c.res.write(`event: command\ndata: ${JSON.stringify({ commandId, action, payload })}\n\n`);
  });
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, 'http://x');
  try {
    if (url.pathname === '/api/client/connect') {
      const clientId = 'client' + nextId++; clients.set(clientId, { res: null, state: null });
      return json(res, { clientId });
    }
    if (url.pathname === '/api/client/events') {
      const c = clients.get(url.searchParams.get('clientId'));
      if (!c) return json(res, { error: 'unknown client' }, 404);
      res.writeHead(200, { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache', Connection: 'keep-alive' });
      res.write(': ok\n\n'); c.res = res;
      req.on('close', () => clients.delete(url.searchParams.get('clientId')));
      return;
    }
    if (url.pathname === '/api/client/state') { const b = await body(req); const c = clients.get(b.clientId); if (c) c.state = b.state; return json(res, { ok: true }); }
    if (url.pathname === '/api/client/reply') { const b = await body(req); waiting.get(b.commandId)?.(b); waiting.delete(b.commandId); return json(res, { ok: true }); }
    if (url.pathname === '/api/cmd' && req.method === 'POST') { const b = await body(req); return json(res, await sendCommand(b.action, b.payload, b.timeoutMs)); }
    if (url.pathname === '/api/state') return json(res, [...clients.values()][0]?.state ?? null);
    if (url.pathname === '/disks/game.dsk' && disk) { res.writeHead(200, { 'Content-Type': 'application/octet-stream' }); return res.end(fs.readFileSync(disk)); }
    let p = path.join(dist, url.pathname === '/' ? 'index.html' : decodeURIComponent(url.pathname));
    if (!p.startsWith(dist) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end('not found'); }
    res.writeHead(200, { 'Content-Type': MIME[path.extname(p).slice(1)] || 'application/octet-stream' });
    fs.createReadStream(p).pipe(res);
  } catch (e) { json(res, { error: String(e) }, 500); }
});

server.listen(port, '127.0.0.1', async () => {
  console.log(`bridge listening on http://127.0.0.1:${port}`);
  if (arg('chromium')) {
    const prof = fs.mkdtempSync('/tmp/a2ts-chromium-');
    spawn('chromium', ['--headless=new', '--no-first-run', `--user-data-dir=${prof}`, '--autoplay-policy=no-user-gesture-required',
      '--window-size=1100,800', `http://127.0.0.1:${port}/index.html?remoteControl=1${disk ? '#game.dsk' : ''}`], { stdio: 'ignore', detached: true }).unref();
  }
});
