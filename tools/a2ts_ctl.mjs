// usage: node a2ts_ctl.mjs <action> ['{"json":"payload"}'] [--png out.png]   (talks to a2ts_bridge.mjs, A2TS_BRIDGE=host:port)
import fs from 'fs';

// Minimum Node, kept in step with package.json "engines" (tests/test_min_versions.py checks this).
if (Number(process.versions.node.split('.')[0]) < 24) {
  console.error(`a2ts_ctl.mjs: needs Node 24 or newer (this is ${process.versions.node})`);
  process.exit(1);
}
const [action, payloadArg, flag, out] = process.argv.slice(2);
const bridge = `http://${process.env.A2TS_BRIDGE || '127.0.0.1:8765'}/api/cmd`;
const call = async (a, p = {}, t = 60000) =>
  (await fetch(bridge, { method: 'POST', body: JSON.stringify({ action: a, payload: p, timeoutMs: t }) })).json();
if (action === 'waitScreen') {
  // waitScreen <ref.png> [timeoutSec]: poll captureScreen until the frame is byte-identical to the reference PNG
  const ref = fs.readFileSync(payloadArg).toString('base64');
  const end = Date.now() + (Number(flag) || 120) * 1000;
  while (Date.now() < end) {
    const r = await call('captureScreen');
    if (r.ok && r.result.dataBase64 === ref) {
      console.log('matched', payloadArg);
      process.exit(0);
    }
    await new Promise((r) => setTimeout(r, 1000));
  }
  console.log('TIMEOUT waiting for', payloadArg);
  process.exit(1);
}
const payload = payloadArg && !payloadArg.startsWith('--') ? JSON.parse(payloadArg) : {};
if (payload.file) {
  payload.dataBase64 = fs.readFileSync(payload.file).toString('base64');
  delete payload.file;
} // importSaveState/mountDisk: {"file":"path"}
const r = await (
  await fetch(`http://${process.env.A2TS_BRIDGE || '127.0.0.1:8765'}/api/cmd`, {
    method: 'POST',
    body: JSON.stringify({ action, payload, timeoutMs: payload.timeoutMs ? payload.timeoutMs + 10000 : 60000 }),
  })
).json();
const png = [payloadArg, flag].includes('--png') ? (flag === '--png' ? out : process.argv[process.argv.indexOf('--png') + 1]) : null;
if (png && r.ok && r.result?.dataBase64) {
  fs.writeFileSync(png, Buffer.from(r.result.dataBase64, 'base64'));
  console.log('wrote', png);
} else console.log(JSON.stringify(r.ok ? r.result : r, null, 1).slice(0, 1500));
