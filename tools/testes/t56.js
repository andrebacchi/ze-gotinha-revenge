// Fanfarra de vitória em tempo real (precisa de python3 -m http.server 8765 na raiz do repositório): começa no pouso, não repete e segue na tela seguinte.
const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await (await b.newContext({ viewport: { width: 1280, height: 800 } })).newPage(); const errs = [], out = {}; p.on('pageerror', e => errs.push(e.message));
  const st = () => p.evaluate(() => { const m = __mg.music, a = m && __mg.tracks[m]; return [m, a ? !a.paused : null, a ? +a.currentTime.toFixed(2) : null, a ? +(a.duration || 0).toFixed(2) : null, a ? a.loop : null, __mg.st.vic ? __mg.st.vic.g : null, __mg.mode]; });
  await p.goto('http://localhost:8765/'); await p.waitForTimeout(800); out.versao = await p.textContent('.tcred');
  await p.click('#btStart'); await p.waitForTimeout(600);
  await p.evaluate(() => { const s = __mg.st; s.opening = null; s.cam.y = 44; for (const k of ['boato','fake','virus','i_gota','i_syr','i_sus','i_shield','i_boost','jac','gate','boss']) s.seen[k] = 1; for (const k of ['fire','sus','move','tired','bubble']) s.hints[k] = 1; s.enemies.forEach(e => e.dead = true); s.p.x = 160 * 16; s.p.y = 192 - 24; s.p.inv = 99999; __mg.bossStart(); });
  await p.waitForTimeout(2600);
  await p.evaluate(() => { const s = __mg.st, b = s.boss; b.hp = 1; b.st = 'tired'; b.t = 0; b.bubble = false; b.y = 192 - b.h; b.x = s.p.x + 40; b.inv = 0; s.p.inv = 0; s.p.face = 1; s.p.ammo = 3; s.p.cd = 0; __mg.keys.fire = true; });
  await p.waitForTimeout(80); await p.evaluate(() => { __mg.keys.fire = false; });
  out.lenta = await st(); await p.waitForTimeout(3600); out.pousou = await st();
  await p.waitForTimeout(3000); out.acorde = await st();
  await p.waitForTimeout(2600); out.telaSeguinte = await st(); out.soon = await p.evaluate(() => !document.querySelector('#scSoon').hidden);
  await p.waitForTimeout(3000); out.acabou = await st();
  await p.keyboard.press('KeyM'); await p.waitForTimeout(200); await p.keyboard.press('KeyM'); await p.waitForTimeout(600); out.semRecomecar = await st();
  console.log(JSON.stringify(out, null, 0).replace(/],"/g, '],\n"')); console.log('ERRS', errs); await b.close(); })();
