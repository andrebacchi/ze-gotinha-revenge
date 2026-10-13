// Efeitos gravados da terceira leva (precisa de python3 -m http.server 8765 na raiz): seringa, golpe que não derrota, estouro, montar, erro e acerto.
const { chromium } = require('playwright');
(async () => { const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }); const p = await (await b.newContext({ viewport: { width: 1280, height: 800 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.addInitScript(() => { window.__plays = []; const AC = window.AudioContext; const orig = AC.prototype.createBufferSource; AC.prototype.createBufferSource = function () { const s = orig.call(this); const st = s.start.bind(s); s.start = (...a) => { window.__plays.push(+s.buffer.duration.toFixed(3)); return st(...a); }; return s; }; });
  await p.goto('http://localhost:8765/'); await p.waitForTimeout(700); const ver = await p.textContent('.tcred'); await p.click('#btStart'); await p.waitForTimeout(900);
  const r = await p.evaluate(async () => { const g = __mg, s = g.st, K = g.keys, out = {}; s.opening = null; s.enemies.forEach(e => e.dead = true); for (const k of ['i_gota', 'i_syr', 'i_sus', 'i_shield', 'i_boost', 'jac', 'gate', 'boato', 'fake', 'virus', 'boss']) s.seen[k] = 1; for (const k of ['fire','sus','move','ride','egg2']) s.hints[k] = 1;
    const dur = {}; for (const k in g.sfxBuf) dur[g.sfxBuf[k].duration.toFixed(3)] = (dur[g.sfxBuf[k].duration.toFixed(3)] ? dur[g.sfxBuf[k].duration.toFixed(3)] + '/' : '') + k; out.n = Object.keys(g.sfxBuf).sort().join(' ');
    const wait = ms => new Promise(r => setTimeout(r, ms)), take = () => { const a = window.__plays.map(d => dur[d.toFixed(3)] || d); window.__plays.length = 0; return a.join(','); };
    s.p.x = 36 * 16; s.p.y = 192 - 24; s.p.inv = 0; await wait(300); take();
    s.p.ammo = 3; s.p.cd = 0; s.p.face = 1; K.fire = true; await wait(60); K.fire = false; await wait(150); out.lancar = take();
    s.shots.length = 0; s.enemies.push({ t: 'virus', x: s.p.x + 40, y: 176, w: 16, h: 16, face: -1, vx: 0, vy: 0, hp: 9, tm: 9999, fl: 0 }); s.p.ammo = 3; s.p.cd = 0; K.fire = true; await wait(60); K.fire = false; await wait(400); out.virus1 = take();
    s.enemies.forEach(e => e.dead = true); s.p.shield = true; s.p.inv = 0; s.enemies.push({ t: 'boato', x: s.p.x + 2, y: 176, w: 14, h: 16, dir: -1, vx: 0, vy: 0, hp: 1, fl: 0 }); await wait(120); out.escudo = [take(), s.p.shield, s.p.dead]; s.enemies.forEach(e => e.dead = true);
    const j = s.jacs[0]; j.state = 'idle'; j.t = 30; j.x = 30 * 16; j.y = 180; s.p.x = j.x; s.p.y = 192 - s.p.h; s.p.inv = 0; await wait(250); out.montar = [take(), !!s.p.ride];
    const G0 = s.gates[0]; G0.lock = 0; G0.q = G0.q || { a: 'M' }; const certo = G0.q.a, errado = certo === 'M' ? 'F' : 'M';
    g.answer(errado === 'M' ? G0.mx : G0.fx, errado); await wait(120); out.erro = take(); if (s.intro) s.intro = null;
    G0.lock = 0; const c2 = G0.q.a; g.answer(c2 === 'M' ? G0.mx : G0.fx, c2); await wait(120); out.acerto = take();
    return out; });
  console.log(ver, JSON.stringify(r, null, 0).replace(/,"/g, ',\n"')); console.log('ERRS', errs); await b.close(); })();
