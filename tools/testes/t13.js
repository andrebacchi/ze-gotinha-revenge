const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1280, height: 800 } }); const p = await ctx.newPage();
  const errs = []; p.on('pageerror', e => errs.push('PAGEERR ' + e.message)); p.on('console', m => { if (m.type() === 'warning' || (m.type() === 'error' && !/ERR_TUNNEL/.test(m.text()))) errs.push(m.text()); });
  await p.goto('file://' + __dirname + '/page.html'); await p.waitForTimeout(500);
  await p.evaluate(() => localStorage.removeItem('mg-placar'));
  await p.screenshot({ path: 'p-title.png' });
  const R = await p.evaluate(() => {
    const g = window.__mg, out = {}, K = g.keys; let s;
    const run = n => { for (let i = 0; i < n; i++) g.step(); };
    const place = (tx, onY) => { const q = s.p; q.x = tx * 16 + 3; q.y = (onY ?? 12) * 16 - q.h; q.vx = q.vy = 0; q.inv = 0; q.plat = null; s.cam.x = Math.max(0, tx * 16 - 160); run(2); };
    const jumpHold = n => { K.jump = true; run(n); K.jump = false; };
    const hud = () => { let t = 0; const o = CanvasRenderingContext2D.prototype.fillText; return t; };
    g.start(); s = g.st; run(25); s.hints.fire = 1;
    out.totais = { inimigos: s.enemyTotal, powerups: s.puTotal, gotas: s.total };
    // matar um boato da fase pontua; um boato nascido de erro não
    const e0 = s.enemies.find(e => e.t === 'boato'); place(Math.floor(e0.x / 16) - 3); s.p.face = 1; K.fire = true; g.step(); K.fire = false; run(40);
    out.kill = { dead: e0.dead, kills: { ...s.kills } };
    s.enemies.forEach(e => e.dead = true);
    const G1 = s.gates[0]; place(G1.q.a === 'M' ? G1.fx : G1.mx); jumpHold(30); out.erro = { err: G1.err, minions: s.enemies.filter(e => e.minion && !e.dead).length };
    const m = s.enemies.find(e => e.minion && !e.dead); m.y = 180; m.x = s.p.x + 40; m.vy = 0; s.p.ammo = 3; s.p.face = 1; K.fire = true; g.step(); K.fire = false; run(30); out.erro.minionDead = m.dead; out.erro.kills = { ...s.kills };
    s.enemies.forEach(e => e.dead = true); s.p.inv = 9999; run(340); s.p.inv = 0;
    place(G1.q.a === 'M' ? G1.mx : G1.fx); jumpHold(30); out.portao1 = { open: G1.open, err: G1.err };
    // SUS do bloco: pequeno pega (1 fonte); morrer e pegar de novo não soma; bombado pega outro bloco e soma
    place(16); jumpHold(30); run(70); let it = s.items.find(i => i.t === 'sus' && i.phys && !i.got); s.p.x = it.x; run(3); out.pu1 = s.pu.size;
    s.p.inv = 0; s.enemies.push({ t: 'fake', x0: s.p.x, y0: s.p.y + 6, x: s.p.x, y: s.p.y + 6, w: 14, h: 10, ph: 0, r: 0, hp: 1, fl: 0, minion: true }); run(2); s.enemies.forEach(e => e.dead = true); run(120);
    s.p.inv = 0; s.enemies.push({ t: 'fake', x0: s.p.x, y0: s.p.y + 6, x: s.p.x, y: s.p.y + 6, w: 14, h: 10, ph: 0, r: 0, hp: 1, fl: 0, minion: true }); run(2); s.enemies.forEach(e => e.dead = true); run(100);
    out.morreu = { quedas: s.stats.quedas, cur: s.cur, x: Math.round(s.p.x / 16) };
    place(51); jumpHold(30); run(70); it = s.items.find(i => i.t === 'sus' && i.phys && !i.got); s.p.x = it.x; run(3); out.pu2 = { n: s.pu.size, big: s.p.big };
    place(110); jumpHold(30); run(70); it = s.items.find(i => i.t === 'sus' && i.phys && !i.got); s.p.x = it.x; run(3); out.pu3 = { n: s.pu.size, big: s.p.big, got: it.got };
    out.parcial = g.score ? null : 'sem acesso';
    // encerrar: fixa o tempo e confere a soma
    s.gotas = 40; s.time = 60 * 222; s.boss.dead = true; s.finalT = s.time; s.winT = 2; run(3);
    out.fim = { mode: g.mode, total: document.querySelector('#sTotal').textContent, linhas: [...document.querySelectorAll('#sBreak dt')].map((d, i) => d.firstChild.textContent + ' [' + d.querySelector('small').textContent + '] = ' + document.querySelectorAll('#sBreak dd')[i].textContent), panelVisible: !document.querySelector('#scWin').hidden };
    return out;
  });
  console.log(JSON.stringify(R, null, 1));
  // teclas no fim de jogo não recomeçam; digitar nome com M, P e espaço não dispara atalhos
  await p.keyboard.press('Space'); await p.keyboard.press('Enter'); await p.waitForTimeout(100);
  const m1 = await p.evaluate(() => window.__mg.mode);
  await p.click('#btReg'); const vazio = await p.textContent('#sReg');
  await p.click('#inNome'); await p.keyboard.type('pam m ap'); const muted = await p.evaluate(() => document.querySelector('#btSom').getAttribute('aria-pressed'));
  await p.keyboard.press('Enter'); await p.waitForTimeout(150);
  const reg = await p.evaluate(() => ({ mode: window.__mg.mode, msg: document.querySelector('#sReg').textContent, form: document.querySelector('#fReg').hidden, board: [...document.querySelectorAll('#sBoard li')].map(l => l.textContent + (l.className ? ' *' : '')), stored: JSON.parse(localStorage.getItem('mg-placar')).length }));
  console.log(JSON.stringify({ m1, vazio, muted, reg }));
  await p.screenshot({ path: 'p-win.png' });
  // segunda inscrição não duplica; outro jogador com menos pontos fica abaixo
  await p.evaluate(() => { const b = JSON.parse(localStorage.getItem('mg-placar')); b.push({ n: 'BRUNO', s: 6100, t: 9000, d: 1, id: 'x1' }, { n: 'CARLA', s: 2990, t: 15000, d: 2, id: 'x2' }, { n: '<b>HTML</b>', s: 100, t: 30000, d: 3, id: 'x3' }); localStorage.setItem('mg-placar', JSON.stringify(b)); });
  await p.reload(); await p.waitForTimeout(500); await p.click('#btBoard'); await p.waitForTimeout(150);
  console.log(JSON.stringify(await p.evaluate(() => ({ mode: document.querySelector('#scWin').dataset.mode, rows: [...document.querySelectorAll('#sBoard li')].map(l => [...l.children].map(c => c.textContent).join(' | ')), injected: !!document.querySelector('#sBoard b') }))));
  await p.screenshot({ path: 'p-board.png' });
  await p.keyboard.press('Escape'); await p.keyboard.press('Enter'); await p.waitForTimeout(100); console.log('apos fechar e Enter:', await p.evaluate(() => [document.querySelector('#scWin').hidden, window.__mg.mode]));
  // celular
  const c2 = await b.newContext({ viewport: { width: 400, height: 780 }, hasTouch: true, isMobile: true, deviceScaleFactor: 2 }); const q = await c2.newPage(); q.on('pageerror', e => errs.push('M PAGEERR ' + e.message));
  await q.goto('file://' + __dirname + '/page.html'); await q.waitForTimeout(400); await q.screenshot({ path: 'p-mtitle.png' });
  await q.tap('#btStart'); await q.evaluate(() => { const g = window.__mg, s = g.st; for (let i = 0; i < 30; i++) g.step(); s.gotas = 51; s.kills.boato = 4; s.kills.virus = 2; s.pu.add('a'); s.pu.add('b'); s.gates.forEach((x, i) => { x.open = true; x.err = i === 1 ? 1 : 0; }); s.time = 60 * 301; s.boss.dead = true; s.finalT = s.time; s.winT = 2; g.step(); g.step(); g.step(); });
  await q.waitForTimeout(200); console.log('mobile', JSON.stringify(await q.evaluate(() => ({ total: document.querySelector('#sTotal').textContent, hscroll: document.documentElement.scrollWidth > innerWidth, panelScroll: [document.querySelector('#scWin').scrollHeight, document.querySelector('#scWin').clientHeight] }))));
  await q.screenshot({ path: 'p-mwin.png' });
  console.log('ERRS', errs); await b.close();
})();
