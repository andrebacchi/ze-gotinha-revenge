// Fase 3: capturas da rampa do corredor (t85-*.png), andando no suporte de soro
const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs = [];
  const p = await (await b.newContext({ viewport: { width: 1280, height: 720 } })).newPage(); p.on('pageerror', e => errs.push('PAGEERR ' + e.message));
  await p.addInitScript('window.__mgNoSave=1'); await p.goto('file://' + __dirname + '/page.html'); await p.waitForTimeout(800);
  await p.evaluate(() => { const g = window.__mg, T = 16; g.startFase(3, 'normal'); const s = g.st; s.opening = null; s.p.x = 123 * T; s.p.y = 12 * T - 24; s.cam.x = 123 * T - 150; g.keys.right = true; for (let i = 0; i < 80 && !g.st.p.cart; i++) g.step(); g.keys.right = false; });
  for (const n of [0, 1, 2, 3, 4, 5]) {
    const r = await p.evaluate(n => { const g = window.__mg, T = 16; for (let i = 0; i < (n ? 110 : 30); i++) { const P = g.st.p; P.inv = 2; const f = P.x + P.w; let j = false; for (let d = 2; d < 18; d += 2) { const tx = Math.floor((f + d) / T); if (g.st.map[12][tx] === '.' && d < 6) j = true; if (g.st.map[11][tx] === 'X' && d > 8) j = true; } if (j && P.onG && !(window.__h > 0)) window.__h = 16; g.keys.jump = window.__h > 0; if (window.__h > 0) window.__h--; g.step(); } return { x: +(g.st.p.x / T).toFixed(1), y: +((g.st.p.y + g.st.p.h) / T).toFixed(2), cart: !!g.st.p.cart }; }, n);
    await p.screenshot({ path: __dirname + '/t85-' + n + '.png' }); console.log(n, JSON.stringify(r));
  }
  console.log('ERRS', errs); await b.close(); })();
