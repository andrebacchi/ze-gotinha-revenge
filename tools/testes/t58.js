// Modo de jogo, jogo salvo e textos sobre o jogo (precisa de python3 -m http.server 8765 na raiz).
const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs = []; const out = {};
  for (const [nome, vw, vh, touch] of [['d', 1280, 800, false], ['dg', 1920, 1000, false], ['m', 390, 800, true], ['l', 800, 390, true]]) {
    const ctx = await b.newContext({ viewport: { width: vw, height: vh }, hasTouch: touch, isMobile: touch }); const p = await ctx.newPage(); p.on('pageerror', e => errs.push(nome + ': ' + e.message));
    await p.goto('http://localhost:8765/'); await p.waitForTimeout(900);
    const r = {}; r.titulo = await p.evaluate(() => [!document.querySelector('#btCont').hidden, document.querySelector('#btStart').textContent, !document.querySelector('#fs-pill').hidden]);
    await p.screenshot({ path: `md-${nome}-0-titulo.png` });
    await p.click('#btStart'); await p.waitForTimeout(250); r.modo = await p.evaluate(() => !document.querySelector('#scMode').hidden); await p.screenshot({ path: `md-${nome}-1-modo.png` });
    await p.click('#btFacil'); await p.waitForTimeout(400);
    r.jogo = await p.evaluate(() => { const s = __mg.st; return [s.diff, s.p.shield, document.querySelector('#app').classList.contains('wide'), Math.round(document.querySelector('#stage').getBoundingClientRect().width), document.documentElement.scrollWidth > innerWidth]; });
    // pergunta do portão: mensagem sobre o jogo
    await p.evaluate(() => { const s = __mg.st; s.opening = null; s.cam.y = 44; for (const k of ['boato','fake','virus','i_gota','i_syr','i_sus','i_shield','i_boost','jac','gate']) s.seen[k] = 1; s.enemies.forEach(e => e.dead = true); const g = s.gates[0]; s.p.x = (g.z0 + 1) * 16; s.p.y = 192 - 24; });
    await p.waitForTimeout(700); r.pergunta = await p.evaluate(() => { const m = document.querySelector('#msg'), rc = m.getBoundingClientRect(), st = document.querySelector('#stage').getBoundingClientRect(); return [m.className, m.textContent.slice(-30), Math.round(rc.top - st.top), Math.round(rc.bottom - st.bottom), __mg.st.gates[0].tm]; });
    await p.screenshot({ path: `md-${nome}-2-pergunta.png` });
    // posto 1: salva; recarrega e continua
    await p.evaluate(() => { const s = __mg.st; s.p.x = 50 * 16; s.p.y = 192 - 24; }); await p.waitForTimeout(300);
    r.salvo = await p.evaluate(() => { const v = JSON.parse(localStorage.getItem('mg-salvo')); return [v.cp, v.diff, v.time > 0]; });
    await p.reload(); await p.waitForTimeout(900); r.titulo2 = await p.evaluate(() => [!document.querySelector('#btCont').hidden, document.querySelector('#contInfo').textContent, document.querySelector('#btStart').textContent]);
    await p.screenshot({ path: `md-${nome}-3-continuar.png` });
    await p.click('#btCont'); await p.waitForTimeout(400); r.continua = await p.evaluate(() => { const s = __mg.st; return [s.diff, s.cur, Math.round(s.p.x / 16), s.gates[0].open, s.p.shield, s.time]; });
    await p.evaluate(() => localStorage.removeItem('mg-salvo'));
    out[nome] = r; await ctx.close(); }
  console.log(JSON.stringify(out, null, 0).replace(/},"/g, '},\n"')); console.log('ERRS', errs); await b.close(); })();
