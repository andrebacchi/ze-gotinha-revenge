// Fase 2: as duas balanças se resolvem empurrando de verdade (o deslocamento entre um empurrão e outro é por teletransporte)
const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs = [];
  const p = await (await b.newContext({ viewport: { width: 900, height: 560 } })).newPage();
  p.on('pageerror', e => errs.push('PAGEERR ' + e.message));
  await p.addInitScript('window.__mgNoSave=1');
  await p.goto('file://' + __dirname + '/page.html'); await p.waitForTimeout(700);
  const r = await p.evaluate(() => {
    const g = window.__mg, K = g.keys, T = 16, out = {};
    g.startFase(2); const s = g.st; s.opening = null;
    for (const e of s.enemies) if ((e.x > 70 * T && e.x < 100 * T) || (e.x > 244 * T && e.x < 272 * T)) e.dead = true;
    const P = () => g.st.p, B = () => g.st.blocks;
    const tp = (x, y) => { const p = P(); p.x = x; p.y = y - p.h; p.vx = 0; p.vy = 0; p.ride = null; for (let i = 0; i < 4; i++) g.step(); };
    const push = (dir, k, until, max = 900) => { K[dir] = true; let last = k.x, still = 0, i = 0; for (; i < max; i++) { g.step(); if (until(k)) break; if (Math.abs(k.x - last) < .01) { if (++still > 40) break; } else still = 0; last = k.x; } K[dir] = false; for (let j = 0; j < 30; j++) g.step(); return +(k.x / T).toFixed(2); };
    // balança 1
    const [T1, T2, E1, E2] = B();
    out.b1_t2 = (tp(86 * T + 3, 12 * T), push('right', T2, k => false));
    out.b1_t1 = (tp(85 * T - 11, 12 * T), push('right', T1, k => false));
    out.b1_pesoTrad = s.bals[0].w;
    out.b1_e1 = (tp(83 * T + 2, 7 * T), push('right', E1, k => k.y > 8 * T));
    out.b1_e2 = (tp(88 * T + 2, 7 * T), push('right', E2, k => k.y > 8 * T));
    out.b1_e2y = +(E2.y / T).toFixed(2);
    out.b1_e2b = (tp(E2.x - 11, 12 * T), push('right', E2, k => false));
    out.b1_e1b = (tp(E1.x - 11, 12 * T), push('right', E1, k => false));
    out.b1 = { w: s.bals[0].w, solved: s.bals[0].solved, porta: s.map[10][96] };
    // reset: bater no bloco da balança 2 antes de mexer não estraga nada; mexe num bloco e recoloca
    const [F2, U1, U2, F1] = B().slice(4);
    tp(253 * T + 2, 12 * T); push('right', U1, k => false, 120); const antes = U1.x;
    tp(250 * T + 3, 12 * T); K.jump = true; for (let i = 0; i < 20; i++) g.step(); K.jump = false; for (let i = 0; i < 40; i++) g.step();
    out.reset = { moveu: +(antes / T).toFixed(2), voltou: +(U1.x / T).toFixed(2) };
    // balança 2: tradição vira aterro e degrau
    out.b2_aterro = (tp(253 * T + 3, 12 * T), push('right', U1, k => false));
    out.b2_aterroY = +(U1.y / T).toFixed(2);
    out.b2_degrau = (tp(257 * T + 3, 12 * T), push('right', U2, k => k.x >= 259 * T));
    // sobe no degrau e na tábua: pula de cima do bloco
    tp(U2.x + 3, U2.y); K.right = true; K.jump = true; for (let i = 0; i < 14; i++) g.step(); K.jump = false; for (let i = 0; i < 40 && !(P().onG && P().y + P().h <= 9 * T + 1); i++) g.step(); K.right = false;
    out.b2_naTabua = { x: +(P().x / T).toFixed(2), pe: +((P().y + P().h) / T).toFixed(2) };
    out.b2_e1 = push('right', F1, k => k.y > 10 * T);
    out.b2_e1b = (tp(F1.x - 11, 12 * T), push('right', F1, k => false));
    out.b2_t2 = (tp(U2.x - 11, 12 * T), push('right', U2, k => false));
    out.b2_e2 = (tp(F2.x - 11, 12 * T), push('right', F2, k => false));
    out.b2 = { w: s.bals[1].w, solved: s.bals[1].solved, porta: s.map[10][268] };
    out.mode = g.mode; return out;
  });
  console.log(JSON.stringify(r, null, 0)); console.log('ERRS', errs); await b.close(); })();
