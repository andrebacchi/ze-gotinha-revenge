// Mito ou fato sem contador em todas as fases: a pergunta espera
const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs = [];
  const p = await (await b.newContext({ viewport: { width: 1280, height: 720 } })).newPage(); p.on('pageerror', e => errs.push(e.message));
  await p.addInitScript('window.__mgNoSave=1;window.__mgNoIntro=1'); await p.goto('file://' + __dirname + '/page.html'); await p.waitForTimeout(700);
  const r = await p.evaluate(() => { const g = window.__mg, T = 16, out = {};
    for (const fase of [1, 2, 3]) { g.startFase(fase, 'normal'); const s = g.st; s.opening = null; for (const e of s.enemies) e.dead = true; const gt = s.gates[0];
      s.p.x = ((gt.z0 + gt.z1) >> 1) * T; s.p.y = 12 * T - 24; for (let i = 0; i < 30; i++) { s.p.inv = 2; g.step(); }
      const tm0 = gt.tm; for (let i = 0; i < 1800; i++) { s.p.inv = 2; s.p.x = ((gt.z0 + gt.z1) >> 1) * T; g.step(); }
      out['fase' + fase] = { tm0: String(tm0), tmDepois: String(gt.tm), aberto: !!gt.open, erros: gt.err || 0 }; }
    return out; });
  console.log(JSON.stringify(r), errs);
  await p.evaluate(() => { const g = window.__mg, T = 16; g.startFase(3, 'normal'); const s = g.st; s.opening = null; for (const e of s.enemies) e.dead = true; const gt = s.gates[0]; s.p.x = ((gt.z0 + gt.z1) >> 1) * T; s.p.y = 12 * T - 24; for (let i = 0; i < 90; i++) { s.p.inv = 2; g.step(); } });
  await p.screenshot({ path: __dirname + '/t94.png' }); await b.close(); })();
