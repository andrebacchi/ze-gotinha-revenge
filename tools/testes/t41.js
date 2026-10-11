const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs = [], out = {};
  for (const [n, vw, vh] of [['d', 1280, 800], ['m', 390, 800]]) { const p = await (await b.newContext({ viewport: { width: vw, height: vh } })).newPage(); p.on('pageerror', e => errs.push(e.message)); await p.goto('file://' + __dirname + '/page.html'); await p.waitForTimeout(700);
    await p.evaluate(() => { __mg.start(); const s = __mg.st; for (let i = 0; i < 30; i++) __mg.step(); s.finalT = 5000; s.winT = 1; __mg.step(); }); await p.waitForTimeout(300);
    out['soon_' + n] = await p.evaluate(() => { const e = document.querySelector('#scSoon'), st = document.querySelector('#stage').getBoundingClientRect(), r = e.querySelector('.row').getBoundingClientRect(); return { mode: __mg.mode, visivel: !e.hidden, resultado: !document.querySelector('#scWin').hidden, texto: e.querySelector('p').textContent, foco: document.activeElement.id, cabe: r.bottom <= st.bottom + 1 }; });
    await p.screenshot({ path: `soon-${n}.png` }); await p.keyboard.press('Enter'); await p.waitForTimeout(200);
    out['depois_' + n] = await p.evaluate(() => ({ soon: document.querySelector('#scSoon').hidden, resultado: !document.querySelector('#scWin').hidden, total: document.querySelector('#sTotal').textContent, mode: __mg.mode }));
    await p.click('#btAgain'); await p.waitForTimeout(150); out['denovo_' + n] = await p.evaluate(() => [__mg.mode, document.querySelector('#scSoon').hidden, document.querySelector('#scWin').hidden]); await p.close(); }
  console.log(JSON.stringify(out, null, 1)); console.log('ERRS', errs); await b.close(); })();
