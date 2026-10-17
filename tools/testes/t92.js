const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs = [];
  const p = await (await b.newContext({ viewport: { width: 1280, height: 720 } })).newPage(); p.on('pageerror', e => errs.push(e.message));
  await p.addInitScript('window.__mgNoSave=1;window.__mgNoIntro=1'); await p.goto('file://' + __dirname + '/page.html'); await p.waitForTimeout(700);
  const r = await p.evaluate(() => { const g = window.__mg; g.startFase(3, 'normal'); g.st.opening = null; g.st.grana = 7; g.st.finalT = g.st.time; g.st.winT = 110; for (let i = 0; i < 200; i++) g.step(); return document.querySelector('#soonText').innerHTML; });
  console.log(r, errs); await p.screenshot({ path: __dirname + '/t92.png' }); await b.close(); })();
