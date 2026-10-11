const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await (await b.newContext({ viewport: { width: 1280, height: 800 } })).newPage();
  const errs = []; p.on('pageerror', e => errs.push('PAGEERR ' + e.message)); p.on('console', m => { if (m.type() === 'warning' || (m.type() === 'error' && !/ERR_TUNNEL/.test(m.text()))) errs.push(m.text()); });
  await p.goto('file://' + __dirname + '/page.html'); await p.waitForTimeout(500);
  const R = await p.evaluate(() => {
    const g = window.__mg, out = {}, K = g.keys; let s;
    const run = n => { for (let i = 0; i < n; i++) g.step(); };
    const fresh = () => { g.start(); s = g.st; s.enemies.forEach(e => e.dead = true); run(25); s.hints.fire = 1; };
    const place = (tx, onY) => { const q = s.p; q.x = tx * 16 + 3; q.y = (onY ?? 12) * 16 - q.h; q.vx = q.vy = 0; q.inv = 0; q.plat = null; s.cam.x = Math.max(0, tx * 16 - 160); run(2); };
    const hit = () => { const q = s.p; q.inv = 0; s.enemies.push({ t: 'fake', x0: q.x, y0: q.y + 6, x: q.x, y: q.y + 6, w: 14, h: 10, ph: 0, r: 0, hp: 1, fl: 0 }); run(2); s.enemies.forEach(e => e.dead = true); };
    const jumpHold = n => { K.jump = true; run(n); K.jump = false; };
    const sz = () => [s.p.w, s.p.h, s.p.big];
    fresh(); out.inicio = sz();
    // bloco do SUS
    place(16); jumpHold(30); run(60); const it = s.items.find(i => i.t === 'sus' && i.phys); out.bloco = { tile: s.map[8][16], item: it && [Math.round(it.x / 16 * 10) / 10, it.y + it.h, it.vx] };
    s.p.x = it.x; run(3); out.pegou = { size: sz(), bottom: s.p.y + s.p.h, got: it.got };
    // bombado: 1º golpe encolhe, 2º derruba
    hit(); out.golpe1 = { size: sz(), dead: s.p.dead, inv: s.p.inv > 0 }; run(120); hit(); out.golpe2 = { dead: s.p.dead, quedas: s.stats.quedas };
    run(100); out.renasce = { size: sz(), x: Math.round(s.p.x / 16), blocoVolta: s.map[8][16], susSoltos: s.items.filter(i => i.t === 'sus' && i.phys && !i.got).length };
    // escudo protege antes do tamanho
    s.p.shield = true; place(5); s.p.big = false; g.st.p.w = 10; s.items.push({ t: 'sus', x: s.p.x, y: s.p.y + 8, w: 15, h: 9 }); run(2); const big1 = sz(); hit(); out.escudo = { antes: big1, depois: sz(), shield: s.p.shield, dead: s.p.dead };
    // SUS com ele já bombado: fica no chão
    s.items.push({ t: 'sus', x: s.p.x, y: s.p.y + 8, w: 15, h: 9 }); run(3); out.susExtra = s.items[s.items.length - 1].got === true;
    // bombado bate a cabeça em bloco e passa pelos portões
    const G1 = s.gates[0]; place(G1.q.a === 'M' ? G1.mx : G1.fx); jumpHold(30); out.portao = G1.open; place(44); K.right = true; run(120); K.right = false; out.passou = Math.round(s.p.x / 16);
    // montar e desmontar bombado
    const j = s.jacs[0]; j.state = 'idle'; j.t = 30; j.x = 58 * 16; j.y = 180; place(58); s.p.x = j.x; run(4); out.montado = { ride: !!s.p.ride, size: sz() };
    hit(); out.fugiu = { ride: !!s.p.ride, size: sz(), jac: j.state, dead: s.p.dead };
    // montado na água: golpe encolhe (não desmonta); pequeno na água: derruba
    run(60); s.p.x = j.x; s.p.y = j.y - 16; run(4); const r2 = !!s.p.ride; s.p.x = 66 * 16; s.p.y = 192 - s.p.h; run(4); hit(); out.agua1 = { r2, inW: s.p.inW, ride: !!s.p.ride, big: s.p.big, dead: s.p.dead }; run(120); s.p.x = 66 * 16; hit(); out.agua2 = { dead: s.p.dead };
    // ovo extra: pequeno e montado → SUS
    fresh(); const j0 = s.jacs[0]; j0.state = 'idle'; j0.t = 30; j0.x = 108 * 16; j0.y = 180; place(108); s.p.x = j0.x; run(4); K.right = true; run(60); K.right = false; out.ovo = { ride: !!s.p.ride, j2: s.jacs[1].state, item: s.items[s.items.length - 1].t };
    // 25 gotas → SUS
    fresh(); s.gotas = 24; place(6); K.right = true; run(40); K.right = false; out.gotas25 = { gotas: s.gotas, size: sz() };
    // chefão até o fim, com SUS caindo na metade
    fresh(); place(150); run(3); out.sus151 = s.items.some(i => i.fixed && !i.got); place(151); run(4); out.pegou151 = sz();
    place(157); run(3); const B = s.boss; let susDrop = false;
    for (let i = 0; i < 9000 && g.mode === 'play'; i++) {
      s.p.inv = 50; if (s.items.some(i => i.t === 'sus' && i.arena)) susDrop = true;
      if (B.st === 'tired') { const dx = (B.x + B.w / 2) - (s.p.x + 5); K.left = dx < -40; K.right = dx > 40; if (Math.abs(dx) <= 60) { s.p.face = Math.sign(dx) || 1; K.fire = (i % 16 < 2) && s.p.ammo > 0; } }
      else { K.left = K.right = K.fire = false; if (B.st === 'fly' && s.p.ammo < 3) { const it = s.items.find(i => i.arena && i.t === 'syr' && !i.got); if (it) { s.p.x = it.x; s.p.y = it.y - 10; s.p.vy = 0; } } }
      g.step();
    }
    out.chefao = { mode: g.mode, susDrop, total: s.total };
    return out;
  });
  console.log(JSON.stringify(R)); console.log('ERRS', errs);
  const shot = async (name, js) => { await p.evaluate(js); await p.waitForTimeout(150); await p.screenshot({ path: name, clip: { x: 80, y: 8, width: 1120, height: 632 } }); };
  await shot('s-big.png', `(()=>{const g=__mg;g.start();const s=g.st;s.enemies.forEach(e=>e.dead=true);s.p.x=14*16;g.keys.jump=true;for(let i=0;i<3;i++)g.step();g.keys.jump=false;s.p.x=16*16+3;g.keys.jump=true;for(let i=0;i<30;i++)g.step();g.keys.jump=false;for(let i=0;i<22;i++)g.step();})()`);
  await shot('s-big2.png', `(()=>{const g=__mg,s=g.st;const it=s.items.find(i=>i.t==='sus'&&i.phys);for(let i=0;i<40;i++)g.step();s.p.x=it.x;for(let i=0;i<40;i++)g.step();g.keys.right=true;for(let i=0;i<14;i++)g.step();g.keys.right=false;s.p.shield=true;})()`);
  await shot('s-ride.png', `(()=>{const g=__mg,s=g.st;const j=s.jacs[0];j.state='idle';j.t=30;j.x=22.5*16;j.y=180;s.p.x=j.x;s.p.y=192-28;for(let i=0;i<6;i++)g.step();})()`);
  await shot('s-boss.png', `(()=>{const g=__mg;g.start();const s=g.st;s.p.x=157*16;for(let i=0;i<260;i++){s.p.inv=50;g.step();}})()`);
  await shot('s-boss2.png', `(()=>{const g=__mg,s=g.st;for(let i=0;i<2000&&s.boss.st!=='tired';i++){s.p.inv=50;g.step();}for(let i=0;i<20;i++)g.step();})()`);
  await b.close();
})();
