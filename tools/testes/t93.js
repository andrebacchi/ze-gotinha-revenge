// Fase 3: captura da placa "vai um cafezinho?" ao lado do buraco do spa
const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs = [];
  const p = await (await b.newContext({ viewport: { width: 1280, height: 720 } })).newPage(); p.on('pageerror', e => errs.push(e.message));
  await p.addInitScript('window.__mgNoSave=1;window.__mgNoIntro=1'); await p.goto('file://' + __dirname + '/page.html'); await p.waitForTimeout(700);
  await p.evaluate(() => { const g = window.__mg, T = 16; g.startFase(3, 'normal'); const s = g.st; s.opening = null; for (const e of s.enemies) e.dead = true; s.p.x = 272 * T; s.p.vx = 0; s.p.y = 12 * T - 24; for (let i = 0; i < 40; i++) { s.p.inv = 2; g.step(); } });
  await p.waitForTimeout(300); await p.screenshot({ path: __dirname + '/t93.png' }); console.log(errs); await b.close(); })();
