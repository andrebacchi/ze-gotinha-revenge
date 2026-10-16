// Fase 3: o atalho alto do spa (prateleira 269 a 272, dose de reforço) dá a pé, e a prateleira não atrapalha o buraco do bônus nem o vapor
const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs = [];
  const p = await (await b.newContext({ viewport: { width: 1280, height: 720 } })).newPage(); p.on('pageerror', e => errs.push(e.message));
  await p.addInitScript('window.__mgNoSave=1'); await p.goto('file://' + __dirname + '/page.html'); await p.waitForTimeout(700);
  const r = await p.evaluate(() => { const g = window.__mg, K = g.keys, T = 16, out = {};
    const fresh = () => { g.startFase(3, 'normal'); const s = g.st; s.opening = null; for (const e of s.enemies) if (e.x > 255 * T && e.x < 282 * T) e.dead = true; s.drips = s.drips.filter(d => d.x < 255 * T || d.x > 282 * T); return s; };
    // sobe na prateleira: corre desde 266 e pula
    let s = fresh(); s.p.x = 266 * T + 2; s.p.y = 12 * T - s.p.h; for (let i = 0; i < 4; i++) g.step();
    const got0 = s.items.filter(i => i.got).length; K.right = true; let on = false, ok = false;
    for (let i = 0; i < 160; i++) { s.p.inv = 2; K.jump = i > 6 && i < 22; g.step(); if (s.p.onG && Math.abs(s.p.y + s.p.h - 10 * T) < 1 && s.p.x > 268 * T) { on = true; } if (on && !K.right) break; if (on) K.right = false; }
    K.right = K.jump = false; for (let i = 0; i < 6; i++) g.step();
    out.naPrateleira = on; out.pe = +(s.p.y / T + s.p.h / T).toFixed(2);
    // dose de reforço: anda na prateleira até o item
    K.left = true; for (let i = 0; i < 40; i++) { s.p.inv = 2; g.step(); } K.left = false; for (let i = 0; i < 10; i++) g.step();
    out.boost = s.p.boost > 0; out.gotas = s.items.filter(i => i.got && i.t === 'gota').length - got0;
    // o buraco do bônus continua acessível por baixo da prateleira
    s = fresh(); s.p.x = 266 * T + 2; s.p.y = 12 * T - s.p.h; for (let i = 0; i < 4; i++) g.step(); K.right = true; let cair = false;
    for (let i = 0; i < 200; i++) { s.p.inv = 2; g.step(); if (s.p.cart || s.p.x > 340 * T) { cair = true; break; } } K.right = false;
    out.buracoBonusAinda = cair;
    return out; });
  console.log(JSON.stringify(r), 'ERRS', errs);
  await p.evaluate(() => { const g = window.__mg, T = 16; g.startFase(3, 'normal'); const s = g.st; s.opening = null; for (const e of s.enemies) e.dead = true; s.p.x = 266 * T; s.p.y = 12 * T - 24; s.cam.x = 266 * T - 150; for (let i = 0; i < 30; i++) { s.p.inv = 2; g.step(); } });
  await p.screenshot({ path: __dirname + '/t88-spa.png' });
  for (const [n, x] of [['farm', 234], ['maq', 252], ['corr0', 123]]) { await p.evaluate(x => { const g = window.__mg, T = 16; g.startFase(3, 'normal'); const s = g.st; s.opening = null; for (const e of s.enemies) e.dead = true; s.p.x = x * T; s.p.y = 12 * T - 24; s.cam.x = x * T - 150; for (let i = 0; i < 30; i++) { s.p.inv = 2; g.step(); } }, x); await p.screenshot({ path: __dirname + '/t88-' + n + '.png' }); }
  await b.close(); })();
