// Fase 3: capturas das pontas da rampa (t86-*.png)
const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs = [];
  const p = await (await b.newContext({ viewport: { width: 1280, height: 720 } })).newPage(); p.on('pageerror', e => errs.push('PAGEERR ' + e.message));
  await p.addInitScript('window.__mgNoSave=1'); await p.goto('file://' + __dirname + '/page.html'); await p.waitForTimeout(800);
  for (const x of [118, 208, 216]) { await p.evaluate(x => { const g = window.__mg, T = 16; g.startFase(3, 'normal'); const s = g.st; s.opening = null; s.p.x = x * T; s.p.y = 12 * T - 24; s.cam.x = x * T - 150; for (let i = 0; i < 40; i++) { s.p.inv = 2; g.step(); } }, x);
    await p.screenshot({ path: __dirname + '/t86-' + x + '.png' }); }
  console.log('ERRS', errs); await b.close(); })();
