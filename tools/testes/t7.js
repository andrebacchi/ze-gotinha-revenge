const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs = [];
  const variants = { nulo: 'ready(fn){fn(null)},data:null', vazio: 'ready(fn){fn({})},data:{}', nuncaChama: 'ready(fn){},data:null', quebra: 'ready(fn){throw new Error("x")},data:null', retomada: 'ready(fn){fn({playing:true,cp:1})},data:{}', lixo: 'ready(fn){fn({playing:true,cp:9})},data:{}', sem: null };
  for (const k in variants) {
    const p = await (await b.newContext({ viewport: { width: 900, height: 600 } })).newPage();
    p.on('pageerror', e => errs.push(k + ' PAGEERR ' + e.message));
    if (variants[k]) await p.addInitScript(`window.claude={hot:{snapshot(){},${variants[k]}}}`);
    await p.goto('file://' + __dirname + '/page.html'); await p.waitForTimeout(700);
    const r = await p.evaluate(() => { const g = window.__mg; const c = document.querySelector('#jogo'); const d = c.getContext('2d').getImageData(c.width / 2, 10, 1, 1).data; return { st: !!g.st, mode: g.mode, pintou: d[3] > 0 && (d[0] + d[1] + d[2]) > 0, px: g.st && Math.round(g.st.p.x / 16) }; });
    await p.click(r.mode === 'pause' ? '#btResume' : '#btStart'); await p.keyboard.down('ArrowRight'); await p.waitForTimeout(500); await p.keyboard.up('ArrowRight');
    const r2 = await p.evaluate(() => ({ mode: window.__mg.mode, t: window.__mg.st.time }));
    console.log(k, JSON.stringify(r), JSON.stringify(r2)); await p.close();
  }
  console.log('ERRS', errs); await b.close(); })();
