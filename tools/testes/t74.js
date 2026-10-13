// Fase 2: travessia do rio a pé pela roda d'água (pula na pá, dá a volta por cima, pula para as tábuas e a margem)
const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await (await b.newContext()).newPage(); await p.addInitScript('window.__mgNoSave=1');
  await p.goto('file://' + __dirname + '/page.html'); await p.waitForTimeout(700);
  console.log(await p.evaluate(() => { const g = window.__mg, K = g.keys, T = 16; g.startFase(2); const s0 = g.st; s0.opening = null; for (const e of s0.enemies) e.dead = true; for (const j of s0.jacs) j.state = 'spent';
    s0.p.x = 205 * T + 2; s0.p.y = 12 * T - 24; for (let i = 0; i < 3; i++) g.step(); const root = structuredClone(g.st); const out = [];
    const pas = g.st.plats.filter(q => q.kind === 'pa').map(q => [Math.round(q.x), Math.round(q.y)]); out.push('pas ' + JSON.stringify(pas));
    K.right = true; let jt = -1; for (let i = 0; i < 160; i++) { const P = g.st.p; if (jt < 0 && P.x >= 208 * T + 4) { jt = i; K.jump = true; } if (i === jt + 16) K.jump = false; g.step(); if (jt >= 0 && i > jt + 4 && P.onG) break; } K.right = K.jump = false;
    for (let i = 0; i < 336; i++) { g.step(); const P = g.st.p; if (i % 80 === 0) out.push(i + ' x=' + (P.x / T).toFixed(2) + ' pe=' + ((P.y + P.h) / T).toFixed(2) + ' plat=' + !!P.plat + ' dead=' + P.dead); if (P.dead) break; }
    K.right = true; K.jump = true; for (let i = 0; i < 200; i++) { if (i === 14) K.jump = false; if (i === 60 || i === 110) K.jump = true; if (i === 74 || i === 124) K.jump = false; g.step(); const P = g.st.p; if (i % 10 === 0) out.push('salto ' + i + ' x=' + (P.x / T).toFixed(2) + ' pe=' + ((P.y + P.h) / T).toFixed(2) + ' onG=' + P.onG + ' dead=' + P.dead); if (P.dead) break; } K.right = false;
    return out.join('\n'); })); await b.close(); })();
