// Pergunta do portão sobre o jogo no computador, deitado e em pé (precisa do servidor na 8765).
const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs = []; const out = {};
  for (const [nome, vw, vh, touch, diff] of [['d', 1280, 800, false, 'normal'], ['l', 800, 390, true, 'facil'], ['m', 390, 800, true, 'facil']]) {
    const ctx = await b.newContext({ viewport: { width: vw, height: vh }, hasTouch: touch, isMobile: touch }); const p = await ctx.newPage(); p.on('pageerror', e => errs.push(nome + ': ' + e.message));
    await p.goto('http://localhost:8765/'); await p.waitForTimeout(700); await p.evaluate(() => localStorage.removeItem('mg-salvo'));
    await p.click('#btStart'); await p.waitForTimeout(200); await p.click(diff === 'facil' ? '#btFacil' : '#btNormal'); await p.waitForTimeout(300);
    await p.evaluate(() => { const s = __mg.st; s.opening = null; s.cam.y = 44; for (const k of ['boato','fake','virus','i_gota','i_syr','i_sus','i_shield','i_boost','jac','gate']) s.seen[k] = 1; for (const k of ['move','fire','sus','jump','ride','egg2']) s.hints[k] = 1; s.enemies.forEach(e => e.dead = true); const g = s.gates[0]; s.p.x = (g.z0 + 1) * 16; s.p.y = 192 - 24; });
    await p.waitForTimeout(4500);
    out[nome] = await p.evaluate(() => { const m = document.querySelector('#msg'), rc = m.getBoundingClientRect(), st = document.querySelector('#stage').getBoundingClientRect(); return [m.className, m.textContent.slice(-42), Math.round(rc.top - st.top), Math.round(st.bottom - rc.bottom), __mg.st.gates[0].tm]; });
    await p.screenshot({ path: `q-${nome}.png` }); await ctx.close(); }
  console.log(JSON.stringify(out, null, 0).replace(/],"/g, '],\n"')); console.log('ERRS', errs); await b.close(); })();
