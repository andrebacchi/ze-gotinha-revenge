// Fase 3: a prateleira de vidro da recepção (33 a 35) e a do lounge (93 a 95) dão a pé; o Zé fica em cima do corpo do lustre (capturas t89-*.png)
const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs = [];
  const p = await (await b.newContext({ viewport: { width: 1280, height: 720 } })).newPage(); p.on('pageerror', e => errs.push(e.message));
  await p.addInitScript('window.__mgNoSave=1'); await p.goto('file://' + __dirname + '/page.html'); await p.waitForTimeout(700);
  const r = await p.evaluate(() => { const g = window.__mg, K = g.keys, T = 16, out = {};
    const fresh = () => { g.startFase(3, 'normal'); const s = g.st; s.opening = null; for (const e of s.enemies) e.dead = true; s.drips = []; return s; };
    // sobe numa prateleira: busca simples por (distância de corrida, tempo de pulo) a partir de vários pontos de partida
    const sobe = (x0, x1, row, tx0, tx1) => { for (let sx = x0; sx <= x1; sx += 1) for (const jl of [10, 14, 18, 24]) for (const run of [0, 6, 12, 20]) {
      const s = fresh(); s.p.x = sx * T; s.p.y = 12 * T - s.p.h; for (let i = 0; i < 4; i++) g.step();
      K.right = true; let ok = false; for (let i = 0; i < 120; i++) { s.p.inv = 2; if (i === run) K.jump = true; if (i === run + jl) K.jump = false; if (i > run + 30) K.right = false; g.step(); if (s.p.onG && Math.abs(s.p.y + s.p.h - row * T) < 1 && s.p.x >= tx0 * T - 8 && s.p.x <= tx1 * T + 8) { ok = true; break; } }
      K.right = K.jump = false; if (ok) return [sx, run, jl]; } return false; };
    out.recepcao = sobe(28, 33, 10, 33, 35);
    out.lounge = (() => { // do degrau da linha 10 (91 e 92) para a linha 8 (93 a 95)
      for (let sx = 90; sx <= 92; sx += .5) for (const jl of [8, 12, 16, 22]) for (const run of [0, 4, 8]) { const s = fresh(); s.p.x = sx * T; s.p.y = 10 * T - s.p.h; for (let i = 0; i < 4; i++) g.step();
        K.right = true; let ok = false; for (let i = 0; i < 100; i++) { s.p.inv = 2; if (i === run) K.jump = true; if (i === run + jl) K.jump = false; if (i > run + 24) K.right = false; g.step(); if (s.p.onG && Math.abs(s.p.y + s.p.h - 8 * T) < 1 && s.p.x >= 93 * T - 8) { ok = true; break; } } K.right = K.jump = false; if (ok) return [sx, run, jl]; } return false; })();
    return out; });
  console.log(JSON.stringify(r), 'ERRS', errs);
  // o Zé em cima do lustre
  await p.evaluate(() => { const g = window.__mg, T = 16; g.startFase(3, 'normal'); const s = g.st; s.opening = null; for (const e of s.enemies) e.dead = true; s.p.x = 17 * T; s.p.y = 12 * T - 24; s.cam.x = 10 * T; for (let i = 0; i < 4; i++) g.step(); });
  const stand = await p.evaluate(() => { const g = window.__mg, K = g.keys, T = 16, s = g.st; let on = null; K.right = true;
    for (let i = 0; i < 600; i++) { s.p.inv = 2; K.jump = (i % 40) < 16; g.step(); s.cam.x = Math.max(0, s.p.x - 150); const pl = s.plats.find(q => q.kind === 'swing' && s.p.onG && Math.abs(s.p.y + s.p.h - q.y) < 1.5 && s.p.x + s.p.w > q.x && s.p.x < q.x + q.w); if (pl) { on = { quadro: i, plx: +(pl.x / T).toFixed(1), w: pl.w }; K.right = K.jump = false; for (let j = 0; j < 3; j++) g.step(); break; } }
    K.right = K.jump = false; return on; });
  console.log('em cima do lustre', JSON.stringify(stand));
  await p.screenshot({ path: __dirname + '/t89-lustre.png' });
  await p.evaluate(() => { const g = window.__mg, T = 16, s = g.st; s.p.x = 34 * T; s.p.y = 10 * T - 24; s.cam.x = 28 * T; for (let i = 0; i < 4; i++) { s.p.inv = 2; g.step(); } });
  await p.screenshot({ path: __dirname + '/t89-prateleira.png' });
  await b.close(); })();
