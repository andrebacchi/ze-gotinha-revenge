// Fase 3 com cartões e abertura: atravessa pontos da fase fechando os cartões e confere que nenhum quebra (capturas t83-*.png)
const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs = [];
  const p = await (await b.newContext({ viewport: { width: 1280, height: 720 } })).newPage(); p.on('pageerror', e => errs.push('PAGEERR ' + e.message));
  await p.addInitScript('window.__mgNoSave=1'); await p.goto('file://' + __dirname + '/page_intro.html'); await p.waitForTimeout(900);
  await p.evaluate(() => window.__mg.startFase(3, 'normal'));
  await p.waitForTimeout(1200); await p.screenshot({ path: __dirname + '/t83-abertura.png' });
  const cards = [];
  for (const x of [3, 12, 27, 50, 60, 76, 103, 126, 140, 222, 230, 247, 266, 269, 285, 315, 318]) {
    const r = await p.evaluate(x => { const g = window.__mg, s = g.st, T = 16, K = g.keys, seen = [];
      s.opening = null; if (s.boss.active) { s.boss.active = false; s.boss.st = 'wait'; s.arena = null; } if (!s.p.cart) { s.p.x = x * T + 3; s.p.y = 12 * T - 24; s.p.vy = 0; }
      for (let i = 0; i < 260; i++) { s.p.inv = 2; if (s.intro && s.intro.shown) { seen.push(s.intro.card.name); K.jump = true; g.step(); K.jump = false; g.step(); continue; } g.step(); }
      return seen; }, x);
    cards.push(...r);
    if (x === 247 || x === 103) await p.screenshot({ path: __dirname + '/t83-' + x + '.png' });
  }
  console.log('cartões', JSON.stringify([...new Set(cards)])); console.log('ERRS', errs); await b.close(); })();
