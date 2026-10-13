// Tela cheia, teclado no título, chefão no normal e no fácil, escudo ao renascer no fácil (precisa do servidor na 8765).
const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs = []; const out = {};
  const p = await (await b.newContext({ viewport: { width: 1280, height: 720 } })).newPage(); p.on('pageerror', e => errs.push(e.message));
  await p.goto('http://localhost:8765/'); await p.waitForTimeout(700); await p.evaluate(() => localStorage.removeItem('mg-salvo'));
  // tela cheia
  await p.click('#fs-pill'); await p.waitForTimeout(500);
  out.cheia = await p.evaluate(() => [!!document.fullscreenElement, document.querySelector('#app').classList.contains('full'), Math.round(document.querySelector('#stage').getBoundingClientRect().width), innerWidth, innerHeight, document.querySelector('#fs-pill').textContent]);
  await p.keyboard.press('KeyF'); await p.waitForTimeout(400); out.saiu = await p.evaluate(() => [!!document.fullscreenElement, Math.round(document.querySelector('#stage').getBoundingClientRect().width)]);
  // Enter no título sem jogo salvo abre o modo; Esc volta
  await p.keyboard.press('Enter'); await p.waitForTimeout(200); out.enter = await p.evaluate(() => [!document.querySelector('#scMode').hidden, document.activeElement.id]);
  await p.keyboard.press('Escape'); await p.waitForTimeout(200); out.esc = await p.evaluate(() => [document.querySelector('#scMode').hidden, __mg.mode]);
  await p.keyboard.press('Enter'); await p.waitForTimeout(200); await p.keyboard.press('Enter'); await p.waitForTimeout(300); out.normalPeloTeclado = await p.evaluate(() => [__mg.mode, __mg.st.diff, __mg.st.p.shield]);
  // chefão: normal x fácil
  const boss = async diff => p.evaluate(d => { const g = __mg; g.start(d); const s = g.st; s.opening = null; for (const k of ['boato','fake','virus','i_gota','i_syr','i_sus','i_shield','i_boost','jac','gate','boss']) s.seen[k] = 1; document.querySelector('#btPause').click(); s.p.x = 160 * 16; s.p.y = 192 - 24; s.p.inv = 1e9; g.bossStart();
      const b = s.boss, log = {}; let last = b.st, t0 = 0, n = 0, throws = 0;
      for (let i = 0; i < 6000 && n < 2; i++) { const e0 = s.eshots.length; g.step(); s.p.inv = 1e9; if (s.eshots.length > e0 && b.st === 'fly') throws++; if (b.st !== last) { if (last === 'tired') { log['tired' + n] = i - t0; n++; } if (b.st === 'tired') t0 = i; if (b.st === 'warn') log['tiros' + n] = throws, throws = 0; last = b.st; } }
      return [d, b.max, log, document.querySelector('#msg').textContent.includes(d === 'facil' ? '15' : '10') || 'sem pergunta']; }, diff);
  out.chefeNormal = await boss('normal'); out.chefeFacil = await boss('facil');
  // respawn no fácil volta com escudo
  out.renasce = await p.evaluate(() => { const s = __mg.st; s.p.y = 600; for (let i = 0; i < 300 && !s.p.dead; i++) __mg.step(); for (let i = 0; i < 400 && s.p.dead; i++) __mg.step(); return [s.p.dead, s.p.shield]; });
  console.log(JSON.stringify(out, null, 0).replace(/],"/g, '],\n"')); console.log('ERRS', errs); await b.close(); })();
