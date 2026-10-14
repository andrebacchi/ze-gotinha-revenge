// Fase 3: o Zé, sem invulnerabilidade, escapa da investida do Dr. Soro Platinum pulando por cima e esperando na plataforma; e alcança as plataformas das arenas
const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs = [];
  const p = await (await b.newContext()).newPage(); p.on('pageerror', e => errs.push('PAGEERR ' + e.message));
  await p.addInitScript('window.__mgNoSave=1'); await p.goto('file://' + __dirname + '/page.html'); await p.waitForTimeout(700);
  const r = await p.evaluate(() => {
    const g = window.__mg, K = g.keys, T = 16, out = {};
    const setup = (diff, px, py) => { g.startFase(3, diff); const s = g.st; s.opening = null; s.drips = []; for (const e of s.enemies) e.dead = true;
      s.p.x = 108 * T; s.p.y = 12 * T - 24; for (let i = 0; i < 100; i++) g.step(); const b = s.boss; s.eshots.length = 0;
      s.p.x = px; s.p.y = py - s.p.h; s.p.vy = 0; s.p.inv = 0; b.x = 117 * T; b.st = 'flex'; b.next = 'charge'; b.t = 0; return s; };
    // 1. pulo por cima: espera no chão e pula quando ele chega perto
    for (const diff of ['normal', 'facil']) {
      const s = setup(diff, 106 * T, 12 * T), b = s.boss; let jt = -1, i = 0;
      for (; i < 240 && !s.p.dead && b.st !== 'tired'; i++) { const d = b.x - (s.p.x + s.p.w); if (jt < 0 && b.st === 'charge' && d < 40) jt = i; K.jump = jt >= 0 && i - jt < 20; g.step(); }
      K.jump = false; out['pulo_' + diff] = { vivo: !s.p.dead, golpe: s.p.inv > 0, cansou: b.st === 'tired' };
    }
    // 2. na plataforma da linha 10
    { const s = setup('normal', 105 * T, 10 * T), b = s.boss; let i = 0; for (; i < 240 && !s.p.dead && b.st !== 'tired'; i++) g.step(); out.plataforma = { vivo: !s.p.dead, golpe: s.p.inv > 0, cansou: b.st === 'tired', pe: (s.p.y + s.p.h) / T }; }
    // 3. a plataforma se alcança do chão
    { g.startFase(3); const s = g.st; s.opening = null; for (const e of s.enemies) e.dead = true; s.bossDone.bomb = true; s.p.x = 102 * T; s.p.y = 12 * T - 24; for (let i = 0; i < 5; i++) g.step();
      K.right = true; K.jump = true; let best = 99; for (let i = 0; i < 60; i++) { g.step(); if (s.p.onG) best = Math.min(best, (s.p.y + s.p.h) / T); } K.right = K.jump = false; out.alcanca = best; }
    return out;
  });
  console.log(JSON.stringify(r)); console.log('ERRS', errs); await b.close(); })();
