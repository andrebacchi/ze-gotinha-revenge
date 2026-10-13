// Pausa → Tela inicial: volta ao título com a música do título e o jogo salvo no último posto (precisa do servidor na 8765).
const { chromium } = require('playwright');
(async () => { const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }); const errs = []; const out = {};
  for (const [nome, vw, vh, touch] of [['d', 1280, 800, false], ['m', 390, 800, true], ['l', 800, 390, true]]) {
    const ctx = await b.newContext({ viewport: { width: vw, height: vh }, hasTouch: touch, isMobile: touch }); const p = await ctx.newPage(); p.on('pageerror', e => errs.push(nome + ': ' + e.message));
    await p.goto('http://localhost:8765/'); await p.waitForTimeout(700); await p.evaluate(() => localStorage.removeItem('mg-salvo'));
    await p.click('#btStart'); await p.click('#btFacil'); await p.waitForTimeout(300);
    await p.evaluate(() => { const s = __mg.st; s.opening = null; for (const k of ['boato','fake','virus','i_gota','i_syr','i_sus','i_shield','i_boost','jac','gate']) s.seen[k] = 1; s.enemies.forEach(e => e.dead = true); s.p.x = 50 * 16; s.p.y = 192 - 24; });
    await p.waitForTimeout(400); await p.click('#btPause'); await p.waitForTimeout(200);
    const r = { nota: await p.textContent('#homeNote') }; await p.screenshot({ path: `/tmp/claude-0/pausa-${nome}.png` });
    await p.click('#btHome'); await p.waitForTimeout(400);
    r.titulo = await p.evaluate(() => [__mg.mode, !document.querySelector('#scTitle').hidden, document.querySelector('#scPause').hidden, __mg.music, !document.querySelector('#btCont').hidden, document.querySelector('#contInfo').textContent, document.querySelector('.tools').hidden]);
    await p.click('#btCont'); await p.waitForTimeout(300); r.continua = await p.evaluate(() => [__mg.mode, __mg.st.diff, __mg.st.cur, __mg.music]);
    out[nome] = r; await ctx.close(); }
  console.log(JSON.stringify(out, null, 0).replace(/},"/g, '},\n"')); console.log('ERRS', errs); await b.close(); })();
