// Fase 3: carrega, percorre cada trecho com o Zé posto no lugar e tira uma captura de cada um (capturas em t80-*.png)
const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs = [];
  const p = await (await b.newContext({ viewport: { width: 1280, height: 720 } })).newPage(); p.on('pageerror', e => errs.push('PAGEERR ' + e.message)); p.on('console', m => { if (m.type() === 'error') errs.push('CONSOLE ' + m.text()); });
  await p.addInitScript('window.__mgNoSave=1'); await p.goto('file://' + __dirname + '/page.html'); await p.waitForTimeout(800);
  await p.evaluate(() => { const g = window.__mg; g.startFase(3, 'normal'); g.st.opening = null; });
  const trechos = [['recepcao', 3], ['lustres', 17], ['lounge', 57], ['vip', 78], ['soro', 104], ['soro2', 108], ['corredor', 140], ['farmacia', 228], ['farmacia2', 236], ['guru0', 280], ['maquina', 248], ['spa', 265], ['guru', 287], ['guru2', 290], ['auditorio', 320], ['auditorio2', 322], ['bonus', 350]];
  for (const [n, x] of trechos) {
    const r = await p.evaluate(x => { const g = window.__mg, s = g.st, T = 16; s.p.x = x * T + 3; s.p.y = 12 * T - 24; s.p.vx = 0; s.p.dead = false; s.cam.x = Math.max(0, x * T - 150); s.p.inv = 0; const b = s.boss; if (b.active) { b.active = false; b.st = 'wait'; s.arena = null; s.eshots.length = 0; }
      for (let i = 0; i < 90; i++) { if (s.p.dead) { s.p.dead = false; } s.p.inv = 2; g.step(); } return { x: +(s.p.x / T).toFixed(1), dead: s.p.dead, boss: s.boss.active ? s.boss.who + ':' + s.boss.st : '-', cart: !!s.p.cart, en: s.enemies.filter(e => !e.dead).length, esh: s.eshots.length }; }, x);
    await p.screenshot({ path: __dirname + '/t80-' + n + '.png' });
    console.log(n, JSON.stringify(r));
  }
  console.log('ERRS', errs); await b.close(); })();
