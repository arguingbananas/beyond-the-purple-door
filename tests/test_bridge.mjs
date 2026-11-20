// Offline tests for tools/a2ts_bridge.mjs: no Chromium, no emulator. A fake client plays the part of the
// Apple2TS page (connect, receive commands over SSE, reply). Run with: node --test tests/*.mjs
import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import http from 'node:http';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import net from 'node:net';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const bridgePath = path.join(here, '..', 'tools', 'a2ts_bridge.mjs');
let proc, port, base, tmp, dist;

const freePort = () =>
  new Promise((r) => {
    const s = net.createServer().listen(0, '127.0.0.1', () => {
      const p = s.address().port;
      s.close(() => r(p));
    });
  });

// fetch cannot set Host or a foreign Origin freely, so use node:http for the hostile requests
const raw = (opts, body) =>
  new Promise((resolve, reject) => {
    const req = http.request({ host: '127.0.0.1', port, ...opts }, (res) => {
      let b = '';
      res.on('data', (c) => (b += c));
      res.on('end', () => resolve({ status: res.statusCode, body: b }));
    });
    req.on('error', reject);
    if (body) req.write(body);
    req.end();
  });

before(async () => {
  tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'a2ts-test-'));
  dist = path.join(tmp, 'dist');
  fs.mkdirSync(dist);
  fs.writeFileSync(path.join(dist, 'index.html'), '<title>fake</title>');
  fs.writeFileSync(path.join(tmp, 'secret.txt'), 'outside dist'); // must never be served
  fs.mkdirSync(path.join(tmp, 'dist-sibling'));
  fs.writeFileSync(path.join(tmp, 'dist-sibling', 'x.txt'), 'sibling');
  port = await freePort();
  base = `http://127.0.0.1:${port}`;
  proc = spawn('node', [bridgePath, '--dist', dist, '--port', String(port)], { stdio: ['ignore', 'pipe', 'inherit'] });
  await new Promise((resolve, reject) => {
    proc.stdout.on('data', (d) => /listening/.test(d) && resolve());
    proc.on('exit', () => reject(new Error('bridge exited early')));
  });
});

after(() => {
  proc?.kill();
  fs.rmSync(tmp, { recursive: true, force: true });
});

test('serves the web build', async () => {
  const r = await fetch(`${base}/index.html`);
  assert.equal(r.status, 200);
  assert.match(await r.text(), /fake/);
});

test('does not serve files outside the dist folder', async () => {
  for (const p of ['/../secret.txt', '/..%2Fsecret.txt', '/../dist-sibling/x.txt', '/%2e%2e/secret.txt']) {
    const r = await raw({ path: p, method: 'GET', headers: { Host: `127.0.0.1:${port}` } });
    assert.equal(r.status, 404, p);
    assert.doesNotMatch(r.body, /outside dist|sibling/);
  }
});

test('rejects a foreign Origin (a web page driving the emulator)', async () => {
  const r = await raw(
    { path: '/api/cmd', method: 'POST', headers: { Origin: 'http://evil.example', Host: `127.0.0.1:${port}` } },
    '{"action":"getStatus"}',
  );
  assert.equal(r.status, 403);
});

test('rejects a foreign Host (DNS rebinding)', async () => {
  const r = await raw({ path: '/api/state', method: 'GET', headers: { Host: 'evil.example' } });
  assert.equal(r.status, 403);
});

test("accepts the page's own Origin", async () => {
  const r = await raw({ path: '/api/state', method: 'GET', headers: { Origin: base, Host: `127.0.0.1:${port}` } });
  assert.equal(r.status, 200);
});

test('malformed JSON is a 400, and the server keeps running', async () => {
  const r = await fetch(`${base}/api/cmd`, { method: 'POST', body: '{nope' });
  assert.equal(r.status, 400);
  assert.deepEqual(await r.json(), { error: 'bad request' }); // no parser or stack details leak out
  assert.equal((await fetch(`${base}/index.html`)).status, 200);
});

test('an out-of-range timeoutMs is refused', async () => {
  for (const timeoutMs of [0, 600001, 'soon']) {
    const body = JSON.stringify({ action: 'getStatus', timeoutMs });
    const r = await (await fetch(`${base}/api/cmd`, { method: 'POST', body })).json();
    assert.equal(r.ok, false);
    assert.match(r.error, /timeoutMs must be between/);
  }
});

test('a command with no emulator page connected is a clean error', async () => {
  const r = await (await fetch(`${base}/api/cmd`, { method: 'POST', body: '{"action":"getStatus"}' })).json();
  assert.equal(r.ok, false);
  assert.match(r.error, /no emulator page/);
});

test('command round trip through a fake emulator client', async () => {
  const { clientId } = await (await fetch(`${base}/api/client/connect`, { method: 'POST', body: '{}' })).json();
  const events = await fetch(`${base}/api/client/events?clientId=${clientId}`);
  const reader = events.body.getReader();
  const dec = new TextDecoder();
  const nextCommand = async () => {
    let buf = '';
    for (;;) {
      const { value, done } = await reader.read();
      if (done) throw new Error('stream ended');
      buf += dec.decode(value);
      const m = buf.match(/event: command\ndata: (.*)\n\n/);
      if (m) return JSON.parse(m[1]);
    }
  };

  const pending = fetch(`${base}/api/cmd`, { method: 'POST', body: JSON.stringify({ action: 'getStatus', payload: { x: 1 } }) }).then((r) =>
    r.json(),
  );
  const cmd = await nextCommand();
  assert.equal(cmd.action, 'getStatus');
  assert.deepEqual(cmd.payload, { x: 1 });
  await fetch(`${base}/api/client/reply`, {
    method: 'POST',
    body: JSON.stringify({ clientId, commandId: cmd.commandId, ok: true, result: { cycles: 42 } }),
  });
  const reply = await pending;
  assert.equal(reply.ok, true);
  assert.deepEqual(reply.result, { cycles: 42 });

  await fetch(`${base}/api/client/state`, { method: 'POST', body: JSON.stringify({ clientId, state: { hello: 'state' } }) });
  assert.deepEqual(await (await fetch(`${base}/api/state`)).json(), { hello: 'state' });
  await reader.cancel();
});
