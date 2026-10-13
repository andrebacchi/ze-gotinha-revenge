// Tela inicial com jogo salvo: o botão FASES abre a escolha já na fase 2
const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs = [];
  for (const vp of [{ width: 1280, height: 720 }, { width: 390, height: 844 }]) {
    const p = await (await b.newContext({ viewport: vp })).newPage(); p.on('pageerror', e => errs.push(e.message));
    await p.addInitScript(() => localStorage.setItem('mg-salvo', JSON.stringify({ v: 1, fase: 1, diff: 'normal', cp: 0, time: 100, kills: {}, stats: {}, pu: [], seen: {}, hints: {}, gates: [], bals: [], d: 1 })));
    await p.goto('file://' + __dirname + '/page_intro.html'); await p.waitForTimeout(800);
    const antes = await p.evaluate(() => [...document.querySelectorAll('.tmenu button')].filter(x => !x.hidden).map(x => x.textContent));
    await p.screenshot({ path: '/tmp/claude-0/-home-claude-ze-gotinha-revenge/a3133384-fc12-5888-960f-19fb74f8d857/scratchpad/titulo_' + vp.width + '.png' });
    await p.click('#btFases'); await p.waitForTimeout(200);
    const modo = await p.evaluate(() => ({ visivel: !document.querySelector('#scMode').hidden, fase2: document.querySelector('#faseRow [data-fase="2"]').getAttribute('aria-pressed') }));
    await p.click('#btNormal'); await p.waitForTimeout(300);
    console.log(vp.width, JSON.stringify({ antes, modo, fase: await p.evaluate(() => window.__mg.st.fase) }));
  }
  console.log('ERRS', errs); await b.close(); })();
