// Fase 3: alcance a pé (lustres e suportes de soro), robô no suporte de soro e na xícara, balança, máquina quântica e os três chefes
const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs = [];
  const p = await (await b.newContext()).newPage(); p.on('pageerror', e => errs.push('PAGEERR ' + e.message));
  await p.addInitScript('window.__mgNoSave=1'); await p.goto('file://' + __dirname + '/page.html'); await p.waitForTimeout(700);
  const only = process.argv[2] || 'all';
  const r = await p.evaluate(only => {
    const g = window.__mg, K = g.keys, T = 16, out = {};
    const fresh = (diff = 'normal') => { g.startFase(3, diff); const s = g.st; s.opening = null; return s; };
    // 1. força bruta: atravessar a pé
    const search = (sx, targetX, opts = {}) => {
      const s0 = fresh(); for (const e of s0.enemies) e.dead = true; s0.drips = [];
      s0.p.x = sx * T + 2; s0.p.y = 12 * T - 24; for (let i = 0; i < 3; i++) g.step();
      const root = structuredClone(g.st); let q = [{ snap: root, path: [] }], tried = 0;
      const ok = st => !st.p.dead && st.p.onG && st.p.x >= targetX * T && st.p.y + st.p.h <= 12 * T + .5;
      for (let depth = 0; depth < (opts.depth || 4); depth++) {
        const next = [];
        for (const node of q) for (let w = 0; w <= (opts.wmax || 150); w += 6) for (const jl of [8, 16]) for (const dx of depth === 0 ? [0, 20, 40] : [0, 6]) {
          tried++; g.st = structuredClone(node.snap); K.left = K.right = K.jump = false;
          for (let i = 0; i < w; i++) g.step(); if (g.st.p.dead) continue;
          const x0 = g.st.p.x; K.right = true; let land = null, jt = -1;
          for (let i = 0; i < 160; i++) { const P = g.st.p; if (jt < 0 && P.x >= x0 + dx) { jt = i; K.jump = true; } if (jt >= 0 && i === jt + jl) K.jump = false; g.step(); if (P.dead || P.y > 14 * T) break; if (jt >= 0 && i > jt + 4 && P.onG) { land = P; break; } }
          K.right = K.jump = false; if (!land || g.st.p.dead) continue;
          for (let i = 0; i < 4; i++) g.step(); if (g.st.p.dead) continue;
          const path = node.path.concat([[w, jl, dx, +(g.st.p.x / T).toFixed(1), +((g.st.p.y + g.st.p.h) / T).toFixed(1)]]);
          if (ok(g.st)) return { ok: true, saltos: path.length, tried };
          if (g.st.p.x > node.snap.p.x + 8 && next.length < 60) next.push({ snap: structuredClone(g.st), path });
        }
        q = next; if (!q.length) break;
      }
      return { ok: false, tried };
    };
    if (only === 'all' || only === 'pe') { out.lustres = search(14, 25); out.postes = search(56, 71); }
    // 2. robô nos veículos: pula buraco, caixote e drone baixo
    const ride = (diff, sx, kind, viaHole) => {
      const s = fresh(diff), P = () => g.st.p; for (const e of s.enemies) if (e.t !== 'drone' && e.t !== 'bolsa') e.dead = true; s.drips = [];
      P().x = sx * T + 3; P().y = 12 * T - 24; s.cur = viaHole ? 3 : 1; for (let i = 0; i <= s.cur; i++) s.cps[i].on = true;
      const v = s.vehs.find(v => v.k === kind); K.right = true; let i = 0; for (; i < 400 && !P().cart; i++) g.step(); K.right = false;
      let hold = 0, mortes = 0, golpes = 0, lastInv = 0, frames = 0, wasDead = false, saiu = false; const log = [];
      for (; frames < 2600; frames++) {
        const p = P(); if (p.dead && !wasDead) { mortes++; log.push('morte ' + (p.x / T).toFixed(1)); } wasDead = p.dead; if (p.inv > lastInv) golpes++; lastInv = p.inv;
        if (!p.cart) { if (kind === 'xicara' && frames > 20 && p.x < 300 * T) { saiu = true; break; } if (kind === 'poste' && v.state === 'done') break; if (!p.dead && v.state === 'park') { K.right = true; g.step(); K.right = false; continue; } }
        const front = p.x + p.w; let jump = false;
        for (let d = 0; d < 40; d += 2) { const tx = Math.floor((front + d) / T); if (g.st.map[12][tx] === '.' && d > 1 && d < 6) jump = true; if (g.st.map[11][tx] === 'X' && d > 8 && d < 18) jump = true; }
        for (const e of g.st.enemies) if (!e.dead && e.t === 'drone' && e.awake && e.y > 150 && e.x - front > 0 && e.x - front < 46) jump = true;
        if (jump && p.onG && hold === 0) hold = 16;
        K.jump = hold > 0; if (hold > 0) hold--; g.step();
      }
      K.jump = false;
      return { diff, embarcou: i < 400, chegou: kind === 'poste' ? v.state === 'done' : saiu, mortes, golpes, s: +(frames / 60).toFixed(1), x: +(P().x / T).toFixed(1), log };
    };
    if (only === 'all' || only === 'veic') { out.poste = [ride('normal', 123, 'poste'), ride('facil', 123, 'poste')]; out.xicara = [ride('normal', 267, 'xicara', true), ride('facil', 267, 'xicara', true)]; }
    // 3. balança (a mesma sequência do t71, deslocada 148 blocos) e máquina quântica
    if (only === 'all' || only === 'puz') {
      const s = fresh(); for (const e of s.enemies) if (e.x > 215 * T && e.x < 262 * T) e.dead = true; s.drips = [];
      const P = () => g.st.p, B = () => g.st.blocks;
      const tp = (x, y) => { const p = P(); p.x = x; p.y = y - p.h; p.vx = 0; p.vy = 0; for (let i = 0; i < 4; i++) g.step(); };
      const push = (dir, k, until, max = 900) => { K[dir] = true; let last = k.x, still = 0, i = 0; for (; i < max; i++) { g.step(); if (until(k)) break; if (Math.abs(k.x - last) < .01) { if (++still > 40) break; } else still = 0; last = k.x; } K[dir] = false; for (let j = 0; j < 30; j++) g.step(); return +(k.x / T).toFixed(2); };
      const [T1, T2, E1, E2, Q1, Q2, Q3] = B();
      tp(234 * T + 3, 12 * T); push('right', T2, k => false);
      tp(233 * T - 11, 12 * T); push('right', T1, k => false);
      const pesoTrad = s.bals[0].w;
      tp(231 * T + 2, 7 * T); push('right', E1, k => k.y > 8 * T);
      tp(236 * T + 2, 7 * T); push('right', E2, k => k.y > 8 * T);
      tp(E2.x - 11, 12 * T); push('right', E2, k => false);
      tp(E1.x - 11, 12 * T); push('right', E1, k => false);
      out.balanca = { pesoTrad, w: s.bals[0].w, solved: s.bals[0].solved, porta: s.map[10][244] };
      const M = s.maq, lab = [];
      for (const q of [Q3, Q2, Q1]) { tp(q.x - 11, 12 * T); push('right', q, k => k.y > 12 * T - 1); lab.push([q.obj, +(q.x / T).toFixed(1), +(q.y / T).toFixed(1), M.lights]); }
      out.maquina = { lab, luzes: M.lights, done: M.done, porta: s.map[10][259] };
      // o Zé na plataforma: laudo, mas não acende luz
      const s2 = fresh(); tp(253 * T + 3, 12 * T); for (let i = 0; i < 40; i++) g.step(); out.maqZe = { luzes: s2.maq.lights, tela: s2.maq.screen && s2.maq.screen.obj };
    }
    // 4. chefes: robô invulnerável, com seringas sem fim, só para conferir que a luta anda até o fim
    const fight = (who, diff) => {
      const s = fresh(diff), A = { bomb: 101, guru: 283, prof: 316 }[who], P = () => g.st.p; s.drips = [];
      for (const e of s.enemies) e.dead = true; if (who === 'guru') s.bossDone.bomb = true; if (who === 'prof') s.bossDone.bomb = s.bossDone.guru = true;
      for (const gt of s.gates) gt.open = true;
      P().x = (A + 4) * T; P().y = 12 * T - 24; let f = 0, hold = 0; const b = s.boss, sts = {};
      for (; f < 60 * 240; f++) {
        const p = P(); p.inv = 2; p.ammo = 3; if (p.dead) { p.dead = false; p.vy = 0; p.y = 12 * T - 24; }
        if (b.active) {
          sts[b.st] = (sts[b.st] || 0) + 1;
          const bx = b.x + b.w / 2, px = p.x + p.w / 2, d = bx - px, want = b.st === 'tired' ? 0 : (who === 'prof' && b.dip > 0 ? 50 : 70);
          K.left = d < 0 ? Math.abs(d) > want + 6 : Math.abs(d) < want - 6; K.right = d > 0 ? Math.abs(d) > want + 6 : Math.abs(d) < want - 6;
          if (b.st === 'tired' && Math.abs(d) < 26 && p.onG && hold === 0) hold = 14;
          else if ((who === 'guru' || (who === 'prof' && b.st === 'graph')) && p.onG && hold === 0 && f % 40 === 0) hold = 16;
          K.jump = hold > 0; if (hold > 0) hold--;
          K.fire = f % 14 < 7 && !K.left === (d > 0) ? true : f % 14 < 7;
          if (!K.left && !K.right) p.face = d > 0 ? 1 : -1;
        } else { K.right = true; K.fire = false; K.jump = false; }
        g.step(); if (!b.active && (b.dead || s.bossDone[who])) break; if (g.st.vic || g.mode === 'win') break;
      }
      K.left = K.right = K.jump = K.fire = false;
      return { who, diff, venceu: !!(b.dead || s.bossDone[who]), s: +(f / 60).toFixed(0), hp: b.hp, dip: b.dip, sts, porta: who !== 'prof' ? s.map[10][A + 20] : '-', vic: !!g.st.vic };
    };
    if (only === 'all' || only === 'boss') out.chefes = ['bomb', 'guru', 'prof'].flatMap(w => ['normal', 'facil'].map(d => fight(w, d)));
    return out;
  }, only);
  console.log(JSON.stringify(r, null, 1)); console.log('ERRS', errs); await b.close(); })();
