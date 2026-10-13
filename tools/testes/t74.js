// Fase 2: travessia do rio a pé pela roda d'água, com os miasmas vivos: em quantos momentos dá para embarcar na pá, e desses quantos chegam à tábua do outro lado (normal e sarado)
const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await (await b.newContext()).newPage(); await p.addInitScript('window.__mgNoSave=1');
  await p.goto('file://' + __dirname + '/page.html'); await p.waitForTimeout(800);
  const r = await p.evaluate(() => { const g = window.__mg, K = g.keys, T = 16, out = {};
    let RR = 10; const run = (big, d, w) => { g.startFase(2); const s = g.st; s.opening = null; s.hints.move = s.hints.fire = 1; for (const e of s.enemies) if (e.t !== 'miasma') e.dead = true; for (const j of s.jacs) j.state = 'spent';
      s.p.big = big; s.p.h = big ? 32 : 24; s.p.w = big ? 14 : 10; s.p.x = 207.6 * T; s.p.y = 12 * T - s.p.h; for (let i = 0; i < d; i++) g.step();
      K.right = true; K.jump = true; let on = false; for (let i = 0; i < 70; i++) { if (i === 16) K.jump = false; g.step(); const P = s.p; if (P.plat && P.plat.kind === 'pa') { on = true; break; } if (P.dead || (P.onG && i > 3)) break; } K.right = K.jump = false;
      if (!on) return 0; for (let i = 0; i < w; i++) { g.step(); if (s.p.dead) return 1; }
      const st0 = g.st; let best = 1; for (const rr of [6, 10, 14, 18, 24, 32]) { /* sem clonar: cada rr refaz do zero */ }
      K.right = true; K.jump = true; for (let i = 0; i < 90; i++) { if (i === 16) K.jump = false; if (i === RR) K.right = false; g.step(); if (s.p.dead) return 1; if (s.p.onG && i > 4) break; }
      K.right = K.jump = false; return !s.p.dead && s.p.onG && Math.abs(s.p.y + s.p.h - 9 * T) < 1 && s.p.x > 215.5 * T ? 2 : 1; };
    for (const big of [false, true]) { let emb = 0, atr = 0, tot = 0, pares = 0;
      for (let d = 0; d < 524; d += 12) { tot++; let best = 0; for (let w = 0; w < 330; w += 10) for (const rr of [8, 14, 20, 28]) { RR = rr; const r = run(big, d, w); if (r === 0) { w = 999; break; } best = Math.max(best, r); if (r === 2) pares++; } if (best >= 1) emb++; if (best === 2) atr++; }
      out[big ? 'sarado' : 'normal'] = { tot, embarca: emb, atravessa: atr, pares }; }
    return out; });
  console.log(JSON.stringify(r)); await b.close(); })();
