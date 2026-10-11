const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await (await b.newContext({ viewport: { width: 1280, height: 800 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('file://' + __dirname + '/page.html'); await p.waitForTimeout(700);
  const R = await p.evaluate(() => {
    const g = window.__mg, K = g.keys, out = {}; let s;
    const fresh = () => { g.start(); s = g.st; s.enemies.forEach(e => e.dead = true); s.enemies.length = 0; for (let i = 0; i < 5; i++) g.step(); s.gates.forEach(G => { G.open = true; G.tm = null; for (const x of [G.x, G.x + 1]) for (let y = 8; y <= 11; y++) s.map[y][x] = '.'; }); };
    const put = (x, yTop, ride) => { const q = s.p; if (q.ride && !ride) { q.ride = null; q.w = 10; q.h = 24; } q.dead = false; q.drown = false; q.vx = q.vy = 0; q.inv = 9999; q.plat = null; q.stun = 0;
      if (ride && !q.ride) { const j = s.jacs[0]; j.state = 'idle'; j.t = 30; j.x = x; j.y = yTop - 12; j.vy = 0; q.x = x; q.y = yTop - q.h; for (let i = 0; i < 4; i++) g.step(); }
      q.x = x; q.y = yTop - q.h; q.vx = q.vy = 0; q.onG = true; for (let i = 0; i < 2; i++) g.step(); };
    // tenta chegar ao alvo: decola em x0 andando em dir, segurando o pulo; second = quadro do segundo toque (pulo duplo) ou -1
    const attempt = (x0, yTop, dir, ride, second, T) => { put(x0, yTop, ride); if (s.p.dead) return false; K.left = dir < 0; K.right = dir > 0; for (let i = 0; i < 14; i++) g.step(); K.jump = true; let ok = false;
      for (let i = 0; i < 110; i++) { if (i === second) { K.jump = false; g.step(); K.jump = true; } g.step(); const q = s.p; if (q.onG && Math.abs(q.y + q.h - T.y) < 1 && q.x + q.w > T.x0 && q.x < T.x1) { ok = true; break; } if (q.dead) break; } K.left = K.right = K.jump = false; for (let i = 0; i < 3; i++) g.step(); return ok; };
    const spots = { S1: { T: { y: 64, x0: 80 * 16, x1: 83 * 16 }, from: [[78, 192, 87 * 16 / 16, 192], [80, 176], [81, 160], [82, 144], [84, 144], [85, 144], [86, 144]] },
      S2: { T: { y: 112, x0: 112 * 16, x1: 115 * 16 }, from: [[108, 192], [109, 192], [111, 192], [112, 192], [113, 192], [114, 192], [115, 192], [117, 192], [119, 192], [120, 160], [121, 160], [122, 96], [123, 96], [124, 64], [125, 64]] },
      S3: { T: { y: 112, x0: 136 * 16, x1: 139 * 16 }, from: [[132, 192], [136, 192], [137, 192], [138, 192], [139, 192], [141, 192], [143, 192]] } };
    for (const k in spots) { const { T, from } = spots[k]; const r = { zeSozinho: 0, montadoUmPulo: 0, duplo: 0, tent: 0, duploDe: [] };
      for (const [c, y] of from) for (let off = 0; off < 16; off += 4) for (const dir of [-1, 0, 1]) { fresh(); r.tent++;
        if (attempt(c * 16 + off, y, dir, false, -1, T)) { r.zeSozinho++; (r.zeDe = r.zeDe || []).push([c, y, off, dir]); }
        fresh(); if (attempt(c * 16 + off, y, dir, true, -1, T)) { r.montadoUmPulo++; (r.montDe = r.montDe || []).push([c, y, off, dir]); }
        for (const sec of [12, 18]) { fresh(); if (attempt(c * 16 + off, y, dir, true, sec, T)) { r.duplo++; if (!r.duploDe.includes(c)) r.duploDe.push(c); } } }
      out[k] = r; }
    // percurso real: pulo duplo, pega os itens, cai de volta no jacaré
    fresh(); put(113 * 16, 192, true); K.jump = true; for (let i = 0; i < 16; i++) g.step(); K.jump = false; g.step(); K.jump = true; g.step(); const j = s.jacs[0]; let landed = false; for (let i = 0; i < 80; i++) { g.step(); if (s.p.onG && Math.abs(s.p.y + s.p.h - 112) < 1) { landed = true; break; } } K.jump = false;
    const g0 = s.gotas; s.p.inv = 0; K.right = true; for (let i = 0; i < 60 && !s.p.shield; i++) g.step(); K.right = false; const sh = s.p.shield; for (let i = 0; i < 200 && !s.p.ride && !s.p.dead; i++) { const onTop = s.p.onG && s.p.y + s.p.h < 120, d = (j.x + 11) - (s.p.x + 5); K.right = onTop || d > 2; K.left = !onTop && d < -2; g.step(); } K.left = K.right = false;
    out.percurso = { subiu: landed, jac: j.state, gotas: s.gotas - g0, escudo: sh, remontou: !!s.p.ride, morto: s.p.dead };
    return out; });
  console.log(JSON.stringify(R, null, 1)); console.log('ERRS', errs); await b.close(); })();
