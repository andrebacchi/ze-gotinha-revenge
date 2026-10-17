// Fase 3: bloco ↺ da máquina na entrada (245) reposiciona as amostras; tela final mostra o dinheiro recuperado
const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs = [];
  const p = await (await b.newContext({ viewport: { width: 1280, height: 720 } })).newPage(); p.on('pageerror', e => errs.push(e.message));
  await p.addInitScript('window.__mgNoSave=1;window.__mgNoIntro=1'); await p.goto('file://' + __dirname + '/page.html'); await p.waitForTimeout(700);
  const r = await p.evaluate(() => { const g = window.__mg, K = g.keys, T = 16; g.startFase(3, 'normal'); const s = g.st; s.opening = null; for (const e of s.enemies) e.dead = true;
    const k = s.blocks.find(k => k.obj === 'banana'); const x0 = k.x; k.x = 262 * T; // fora do lugar
    s.p.x = 245 * T + 2; s.p.y = 12 * T - 24; for (let i = 0; i < 4; i++) g.step();
    K.jump = true; for (let i = 0; i < 30; i++) { s.p.inv = 2; g.step(); } K.jump = false; for (let i = 0; i < 30; i++) g.step();
    const out = { bananaVoltou: Math.abs(k.x - x0) < 2, x: k.x / T, x0: x0 / T };
    s.grana = 7; document.querySelector('#soonText') && 0; return out; });
  console.log(JSON.stringify(r), errs); await b.close(); })();
