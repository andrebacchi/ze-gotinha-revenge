const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs = [];
  const p = await (await b.newContext({ viewport: { width: 1280, height: 720 } })).newPage(); p.on('pageerror', e => errs.push(e.message));
  await p.addInitScript('window.__mgNoSave=1'); await p.goto('file://' + __dirname + '/page.html'); await p.waitForTimeout(700);
  const r = await p.evaluate(() => { const g = window.__mg, T = 16; g.startFase(3, 'normal'); const s = g.st; s.opening = null; for (const e of s.enemies) e.dead = true;
    const sw = s.plats.filter(q => q.kind === 'swing').map(q => ({ px: q.px / T, py: q.py / T, L: q.L, w: q.w, x: q.x / T, y: q.y }));
    const pl = s.plats.find(q => q.kind === 'swing'); const out = { sw };
    // deixa o Zé cair em cima do primeiro lustre
    s.p.y = pl.y - 30; s.p.vy = 0; let ok = null;
    for (let i = 0; i < 90; i++) { s.p.inv = 2; if (!s.p.onG) s.p.x = pl.x + pl.w / 2 - s.p.w / 2; g.step(); s.cam.x = Math.max(0, s.p.x - 150); if (s.p.onG && i > 2) { ok = { i, pe: s.p.y + s.p.h, topo: pl.y, dx: s.p.x + s.p.w / 2 - (pl.x + pl.w / 2) }; break; } }
    out.pouso = ok; return out; });
  console.log(JSON.stringify(r), errs);
  await p.screenshot({ path: __dirname + '/t90-lustre.png' });
  await b.close(); })();
