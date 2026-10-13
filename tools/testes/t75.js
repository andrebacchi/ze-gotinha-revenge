// Fase 2: passarola e chefão no ar. Decola, poeira cai com seringa, exposto leva dano, vitória e tela seguinte.
const { chromium } = require('playwright');
const OUT = process.argv[2] || '.';
(async () => { const b = await chromium.launch(); const errs = [];
  for (const page of ['page.html', 'page_intro.html']) {
    const p = await (await b.newContext({ viewport: { width: 960, height: 600 } })).newPage(); p.on('pageerror', e => errs.push(page + ' PAGEERR ' + e.message));
    await p.addInitScript('window.__mgNoSave=1'); await p.goto('file://' + __dirname + '/' + page); await p.waitForTimeout(700);
    const r = await p.evaluate(async () => {
      const g = window.__mg, K = g.keys, T = 16, out = {}; g.startFase(2); let s = g.st; s.opening = null; s.seen.balao = 1;
      for (let i = 0; i < 4; i++) s.cps[i].on = true; s.cur = 3; for (const gt of s.gates) { gt.open = true; for (const x of [gt.x, gt.x + 1]) for (let y = 8; y <= 11; y++) s.map[y][x] = '.'; }
      s.p.x = 287 * T; s.p.y = 12 * T - 24; K.right = true; for (let i = 0; i < 120 && !s.launch; i++) { g.step(); if (s.intro) { s.intro = null; } } K.right = false;
      out.decolou = !!s.launch; for (let i = 0; i < 400 && !s.air; i++) { g.step(); if (s.intro) s.intro = null; }
      out.noAr = !!s.air; out.chefe = s.boss.active; out.camadas = s.boss.layers;
      for (let i = 0; i < 140; i++) { s.p.inv = 200; s.p.y = 90; g.step(); if (s.intro) { s.intro = null; } }   // entrada do Barão (o Zé parado no ar)
      const b = s.boss, P = s.p; out.estado = b.st;
      const shootAt = () => { P.ammo = 3; P.x = b.x - 40; P.y = b.y + 12; P.face = 1; P.cd = 0; P.inv = 200; K.fire = true; g.step(); K.fire = false; for (let i = 0; i < 16; i++) { P.x = b.x - 40; P.y = b.y + 12; P.inv = 200; g.step(); } };
      let n = 0; while (b.layers > 0 && n++ < 20) shootAt();
      out.exposto = b.st; out.tiros = n; const hp0 = b.hp; shootAt(); out.danoSeringa = hp0 - b.hp;
      P.x = b.x + 8; P.y = b.y - P.h - 2; P.vy = 1; P.inv = 0; const hp1 = b.hp; for (let i = 0; i < 8 && b.hp === hp1; i++) g.step(); out.danoPisao = hp1 - b.hp;
      for (let k = 0; k < 40 && b.hp > 0; k++) { if (b.st !== 'exposed') { while (b.layers > 0 && n++ < 200) shootAt(); } shootAt(); }
      out.hp = b.hp; out.morrendo = b.st;
      for (let i = 0; i < 1200 && g.mode === 'play'; i++) { g.step(); if (i === 600) { K.jump = true; } if (i === 602) K.jump = false; }
      out.mode = g.mode; out.soon = document.querySelector('#soonTitle').textContent + ' | ' + document.querySelector('#soonEyebrow').textContent;
      out.next = !document.querySelector('#btNext').hidden; out.eyebrow = document.querySelector('#winEyebrow').textContent;
      out.linhas = [...document.querySelectorAll('#sBreak dt')].map(d => d.firstChild.textContent);
      return out;
    });
    console.log(page, JSON.stringify(r));
    await p.close();
  }
  // capturas do voo
  const p = await (await b.newContext({ viewport: { width: 960, height: 600 } })).newPage(); p.on('pageerror', e => errs.push('cap PAGEERR ' + e.message));
  await p.addInitScript('window.__mgNoSave=1'); await p.goto('file://' + __dirname + '/page.html'); await p.waitForTimeout(700);
  await p.evaluate(() => { const g = window.__mg; g.startFase(2); g.st.opening = null; g.st.cur = 4; g.startAir(); for (let i = 0; i < 300; i++) { const P = g.st.p; P.inv = i < 290 ? 200 : 0; P.y = 92 + Math.sin(i * .05) * 8; P.x = 60; if (g.st.intro) g.st.intro = null; g.keys.fire = i % 50 === 0; g.step(); } g.keys.fire = false; });
  await p.waitForTimeout(150); await p.locator('#jogo').screenshot({ path: OUT + '/f2_20_ar.png' });
  await p.evaluate(() => { const g = window.__mg, b = g.st.boss; b.layers = 0; b.st = "exposed"; b.t = 0; for (let i = 0; i < 30; i++) { g.st.p.inv = 0; g.st.p.y = 92; g.step(); } });
  await p.waitForTimeout(150); await p.locator('#jogo').screenshot({ path: OUT + '/f2_21_exposto.png' });
  console.log('ERRS', errs); await b.close(); })();
