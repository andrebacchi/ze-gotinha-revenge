// Fase 2: a mina dá para atravessar no vagonete só pulando (robô simples que pula buraco, caixote e morcego baixo)
const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs = [];
  const p = await (await b.newContext()).newPage(); p.on('pageerror', e => errs.push('PAGEERR ' + e.message));
  await p.addInitScript('window.__mgNoSave=1'); await p.goto('file://' + __dirname + '/page.html'); await p.waitForTimeout(700);
  for (const diff of ['normal', 'facil']) {
    const r = await p.evaluate(diff => {
      const g = window.__mg, K = g.keys, T = 16; g.startFase(2, diff); const s = g.st; s.opening = null;
      const P = () => g.st.p; P().x = 100 * T + 3; P().y = 12 * T - 24; s.cur = 1; s.cps[0].on = s.cps[1].on = true;
      K.right = true; let i = 0; for (; i < 200 && !P().cart; i++) g.step(); K.right = false; const embarcou = P().cart;
      let hold = 0, mortes = 0, frames = 0, wasDead = false, golpes = 0, lastInv = 0; const log = [];
      for (; frames < 2400; frames++) {
        const p = P(), s = g.st; if (s.cart.state === 'done') break; if (p.hurtT === 16 && !p.dead) log.push('hurt ' + (p.x/T).toFixed(1));
        if (p.dead && !wasDead) { mortes++; log.push("morte " + (p.x / T).toFixed(1) + (p.y > 13 * T ? " caiu" : " golpe") + " y=" + (p.y/T).toFixed(2) + " vy=" + p.vy.toFixed(1) + " " + s.enemies.filter(e => !e.dead && Math.abs(e.x - p.x) < 40).map(e => e.t + "@" + (e.x/T).toFixed(1) + "," + (e.y/T).toFixed(1)).join("|") + " fx=" + s.fx.length); } wasDead = p.dead;
        if (p.inv > lastInv) golpes++; lastInv = p.inv;
        if (!p.dead && !p.cart && s.cart.state === 'park') { K.right = true; g.step(); K.right = false; continue; }
        const front = p.x + p.w; let jump = false;
        for (let d = 0; d < 40; d += 2) { const tx = Math.floor((front + d) / T); if (s.map[12][tx] === '.' && d > 1 && d < 6) jump = true; if (s.map[11][tx] === 'X' && d > 8 && d < 18) jump = true; }
        for (const e of s.enemies) if (!e.dead && e.t === 'morcego' && e.awake && e.y > 150 && e.x - front > 0 && e.x - front < 46) jump = true;
        if (jump && p.onG && hold === 0) hold = 16;
        K.jump = hold > 0; if (hold > 0) hold--; g.step();
      }
      K.jump = false;
      return { diff, embarcou, chegou: g.st.cart.state === 'done', mortes, golpes, segundos: +(frames / 60).toFixed(1), log, x: +(P().x / T).toFixed(1) };
    }, diff);
    console.log(JSON.stringify(r));
  }
  console.log('ERRS', errs); await b.close(); })();
