const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await (await b.newContext({ viewport: { width: 1280, height: 800 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('file://' + __dirname + '/page.html'); await p.waitForTimeout(700); await p.addStyleTag({ content: '#scPause{display:none!important}#msg{display:none!important}' });
  const R = await p.evaluate(() => {
    const g = window.__mg, out = {}, K = g.keys; let s;
    const run = n => { for (let i = 0; i < n; i++) g.step(); };
    const clearCol = (a, b) => { for (let c = a; c <= b; c++) { let ok = true; for (let dc = -1; dc <= 1; dc++) for (let r = 3; r <= 11; r++) if (g.tileAt(c + dc, r) !== '.') ok = false; if (ok) return c; } return -1; };
    const fresh = () => { g.start(); s = g.st; s.enemies.forEach(e => e.dead = true); run(25); for (const k of ['fire', 'sus', 'move', 'egg', 'water', 'ride', 'egg2']) s.hints[k] = 1; };
    const place = tx => { const q = s.p; q.x = tx * 16 + 3; q.y = 192 - q.h; q.vx = q.vy = 0; q.inv = 0; q.plat = null; s.cam.x = Math.max(0, tx * 16 - 160); run(2); };
    const mountAt = (ji, tx) => { const j = s.jacs[ji]; j.state = 'idle'; j.t = 30; j.x = tx * 16; j.y = 192 - 12; place(tx); s.p.x = j.x; run(4); return !!s.p.ride; };
    const hit = (dx) => { s.p.inv = 0; s.enemies.push({ t: 'fake', x0: s.p.x + dx, y0: s.p.y + 8, x: s.p.x + dx, y: s.p.y + 8, w: 14, h: 10, ph: 0, r: 0, hp: 1, fl: 0 }); run(2); s.enemies.forEach(e => e.dead = true); };
    // a) golpe de inimigo em terra: jacaré foge para o lado oposto
    fresh(); out.a = { ride: mountAt(0, 30) }; hit(12); const j = s.jacs[0]; out.a.depois = { ride: !!s.p.ride, jac: j.state, dir: j.dir, zeVx: Math.sign(s.p.vx), dead: s.p.dead };
    // b) fugindo em terra rumo ao lago (62–73): entra, nada, sai do outro lado e segue
    fresh(); mountAt(0, 58); s.p.face = 1; hit(12); const j0 = s.jacs[0]; j0.dir = 1; j0.x = 60.6 * 16; out.b0 = j0.state; let wet = 0, minV = 9, maxX = 0, turned = false, log = [];
    for (let i = 0; i < 520 && j0.state === 'flee'; i++) { s.p.inv = 999; s.p.x = 50 * 16; s.p.y = 192 - s.p.h; g.step(); if (j0.inW) wet++; if (j0.dir < 0) turned = true; maxX = Math.max(maxX, j0.x); if (i % 60 === 0) log.push([Math.round(j0.x / 16), j0.inW ? 'agua' : 'terra', +Math.abs(j0.vx).toFixed(2)]); }
    out.b = { framesNaAgua: wet, virou: turned, chegouCol: Math.round(maxX / 16), estado: j0.state, log };
    // c) fugindo rumo ao buraco (20–21): cai e some; depois o ovo volta ao ninho
    fresh(); mountAt(0, 16); hit(12); const j1 = s.jacs[0]; j1.dir = 1; let fell = false, t = 0; for (; t < 300 && j1.state === 'flee'; t++) { s.p.inv = 999; s.p.x = 5 * 16; s.p.y = 192 - s.p.h; g.step(); if (j1.y > 200) fell = true; }
    out.c = { caiu: fell, estado: j1.state, quadros: t, ultimaCol: Math.round(j1.x / 16) }; run(130); out.c.volta = [j1.state, Math.round(j1.x / 16)];
    // d) golpe sobre a água: perde o jacaré; guiando de volta, cai na sela
    const waterHit = steer => { fresh(); mountAt(0, 58); K.right = true; for (let i = 0; i < 400 && s.p.x < 66 * 16; i++) { K.jump = s.p.x > 58.6 * 16 && s.p.x < 60 * 16; g.step(); } K.right = K.jump = false; run(10); const w = s.p.inW; hit(12); const jj = s.jacs[0], r = { naAgua: w, soltou: !s.p.ride, jacNada: jj.inW, jac: jj.state }; let re = -1;
      for (let i = 0; i < 120; i++) { if (steer) { const d = (jj.x + jj.w / 2) - (s.p.x + s.p.w / 2); K.left = d < -2; K.right = d > 2; } g.step(); if (s.p.ride && re < 0) re = i; if (s.p.dead) break; } K.left = K.right = false; r.remontouEm = re; r.morreu = s.p.dead; r.afogou = !!s.p.drown; return r; };
    out.d_guiando = waterHit(true); out.d_parado = waterHit(false);
    // e) bombado com escudo sobre a água: perde só o jacaré
    fresh(); mountAt(0, 58); s.p.shield = true; K.right = true; for (let i = 0; i < 400 && s.p.x < 66 * 16; i++) { K.jump = s.p.x > 58.6 * 16 && s.p.x < 60 * 16; g.step(); } K.right = K.jump = false; hit(12); out.e = { escudo: s.p.shield, ride: !!s.p.ride };
    // f) pulo duplo em terra: desce, sobe mais, jacaré parado; caindo em cima, monta de novo
    const tap = () => { K.jump = true; g.step(); };
    fresh(); const cf = clearCol(24, 45); mountAt(0, cf); let top1 = 999; K.jump = true; for (let i = 0; i < 60; i++) { g.step(); top1 = Math.min(top1, s.p.y + s.p.h); if (s.p.onG && i > 5) break; } K.jump = false; run(3);
    const jf = s.jacs[0]; K.jump = true; run(8); K.jump = false; g.step(); const antes = !!s.p.ride; tap(); const x0 = jf.x; let top2 = 999, re = -1;
    const f = { col: cf, pulouMontado: Math.round(192 - top1), antes, desceu: !s.p.ride, jac: jf.state };
    for (let i = 0; i < 140; i++) { g.step(); top2 = Math.min(top2, s.p.y + s.p.h); if (s.p.ride && re < 0) { re = i; break; } } K.jump = false;
    f.alturaDuplo = Math.round(192 - top2); f.jacAndou = Math.round(jf.x - x0); f.remontouEm = re; out.f = f;
    // g) um toque só no chão não desce
    fresh(); mountAt(0, 30); K.jump = true; g.step(); K.jump = false; run(50); out.g = { ride: !!s.p.ride };
    // h) pulo duplo sobre a água: jacaré boia parado; Zé cai de volta e monta
    fresh(); const cw = clearCol(62, 73); mountAt(0, 58); K.right = true; for (let i = 0; i < 600 && s.p.x + 10 < cw * 16 + 8; i++) { K.jump = s.p.x > 58.6 * 16 && s.p.x < 60 * 16; g.step(); } K.right = K.jump = false; run(14);
    K.jump = true; run(8); K.jump = false; g.step(); tap(); const jh = s.jacs[0], h = { col: cw, desceu: !s.p.ride, jac: jh.state }; let rh = -1; for (let i = 0; i < 140; i++) { g.step(); if (s.p.ride) { rh = i; break; } if (s.p.dead) break; } K.jump = false;
    h.boia = jh.inW; h.remontouEm = rh; h.morreu = s.p.dead; out.h = h;
    // i) pulo duplo sobre o buraco: jacaré cai e some
    fresh(); mountAt(0, 17); K.right = true; let did = false; for (let i = 0; i < 200; i++) { const cx = s.p.x + s.p.w / 2; K.jump = cx > 19.2 * 16 && s.p.onG; if (!did && !s.p.onG && cx > 20.95 * 16 && s.p.ride) { K.jump = false; g.step(); K.jump = true; did = true; } g.step(); if (did && !s.p.ride && s.p.onG) break; } K.right = K.jump = false; const ji = s.jacs[0]; run(120);
    out.i = { fez: did, ze: [Math.round(s.p.x / 16), s.p.dead], jac: ji.state }; run(140); out.i.depois = [ji.state, Math.round(ji.x / 16)];
    return out; });
  console.log(JSON.stringify(R, null, 1)); 
  // captura: jacaré fugindo a nado
  await p.evaluate(() => { const g = __mg; g.start(); const s = g.st; s.enemies.forEach(e => e.dead = true); for (let i = 0; i < 25; i++) g.step(); document.querySelector('#btPause').click(); const j = s.jacs[0]; j.state = 'flee'; j.t = 40; j.dir = 1; j.x = 65 * 16; j.y = 180; j.vy = 0; s.p.x = 59 * 16; s.p.y = 192 - s.p.h; s.cam.x = 56 * 16; for (let i = 0; i < 12; i++) { s.p.inv = 0; g.step(); } });
  await p.waitForTimeout(80); await p.locator('canvas').first().screenshot({ path: 'jf-swim.png' });
  await p.evaluate(() => { const g = __mg, s = g.st, j = s.jacs[0]; j.x = 57 * 16; j.t = 40; s.p.x = 52 * 16; s.cam.x = 50 * 16; for (let i = 0; i < 12; i++) g.step(); });
  await p.waitForTimeout(80); await p.locator('canvas').first().screenshot({ path: 'jf-run.png' });
  console.log('ERRS', errs); await b.close(); })();
