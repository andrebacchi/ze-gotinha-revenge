// Fase 2: telas (escolha de fase, abertura, cartão novo, fim da fase 1 liberando a 2) no computador e no celular em pé
const { chromium } = require('playwright');
const OUT = process.argv[2] || '.';
(async () => { const b = await chromium.launch(); const errs = [];
  for (const [nome, vp, touch] of [['pc', { width: 1280, height: 720 }, false], ['cel', { width: 390, height: 844 }, true]]) {
    const ctx = await b.newContext({ viewport: vp, hasTouch: touch, isMobile: touch }); const p = await ctx.newPage(); p.on('pageerror', e => errs.push(nome + ' PAGEERR ' + e.message));
    await p.goto('file://' + __dirname + '/page_intro.html'); await p.waitForTimeout(800);
    await p.click('#btStart'); await p.waitForTimeout(200);
    const fr = await p.evaluate(() => ({ visivel: !document.querySelector('#faseRow').hidden, pressed: [...document.querySelectorAll('#faseRow .chip')].map(c => c.getAttribute('aria-pressed')), hscroll: document.documentElement.scrollWidth > innerWidth }));
    await p.screenshot({ path: `${OUT}/f2_30_modo_${nome}.png` });
    await p.click('#faseRow [data-fase="2"]'); await p.click('#btNormal'); await p.waitForTimeout(1300);
    await p.screenshot({ path: `${OUT}/f2_31_abertura_${nome}.png` });
    const ab = await p.evaluate(() => ({ fase: window.__mg.st.fase, nome: window.__mg.PHASE.name }));
    // cartão do humor
    await p.evaluate(() => { const g = window.__mg, s = g.st; s.opening = null; s.seen.move = 1; s.p.x = 57 * 16; for (let i = 0; i < 200 && !(s.intro && s.intro.shown); i++) g.step(); });
    await p.waitForTimeout(200); await p.screenshot({ path: `${OUT}/f2_32_cartao_${nome}.png` });
    const card = await p.evaluate(() => [document.querySelector('#inName').textContent, !document.querySelector('#intro').hidden]);
    // fim da fase 1 libera a 2
    await p.evaluate(() => { localStorage.clear(); window.__mg.startFase(1); const s = window.__mg.st; s.opening = null; s.boss.dead = true; s.finalT = 3600; });
    await p.evaluate(() => { const s = window.__mg.st; s.vic = { t: 0, g: 500, done: false }; window.__mg.step(); });
    await p.waitForTimeout(300); await p.screenshot({ path: `${OUT}/f2_33_fim1_${nome}.png` });
    const fim = await p.evaluate(() => ({ titulo: document.querySelector('#soonTitle').textContent, txt: document.querySelector('#soonText').textContent, fases: localStorage.getItem('mg-fases'), salvo: JSON.parse(localStorage.getItem('mg-salvo') || 'null') }));
    await p.click('#btSoon'); await p.waitForTimeout(200); await p.screenshot({ path: `${OUT}/f2_34_placar_${nome}.png`, fullPage: false });
    const prox = await p.evaluate(() => !document.querySelector('#btNext').hidden);
    await p.click('#btNext'); await p.waitForTimeout(300); const depois = await p.evaluate(() => ({ fase: window.__mg.st.fase, mode: window.__mg.mode }));
    console.log(nome, JSON.stringify({ fr, ab, card, fim: { ...fim, salvo: fim.salvo && [fim.salvo.fase, fim.salvo.cp] }, prox, depois }));
    await ctx.close();
  }
  console.log('ERRS', errs); await b.close(); })();
