// Fase 2: força bruta. A pé dá para cruzar o vão dos sinos e o rio pela roda d'água? E o portão do telhado?
const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs = [];
  const p = await (await b.newContext()).newPage(); p.on('pageerror', e => errs.push('PAGEERR ' + e.message));
  await p.addInitScript('window.__mgNoSave=1'); await p.goto('file://' + __dirname + '/page.html'); await p.waitForTimeout(700);
  const r = await p.evaluate(() => {
    const g = window.__mg, K = g.keys, T = 16;
    const search = (sx, targetX, opts = {}) => {
      g.startFase(2); const s0 = g.st; s0.opening = null; for (const e of s0.enemies) e.dead = true; for (const j of s0.jacs) j.state = 'spent';
      s0.p.x = sx * T + 2; s0.p.y = 12 * T - 24; for (let i = 0; i < 3; i++) g.step();
      const root = structuredClone(g.st); let q = [{ snap: root, path: [] }], tried = 0;
      const ok = st => !st.p.dead && st.p.onG && st.p.x >= targetX * T && st.p.y + st.p.h <= 12 * T + .5;
      for (let depth = 0; depth < (opts.depth || 3); depth++) {
        const next = [];
        for (const node of q) for (let w = 0; w <= (opts.wmax || 150); w += 6) for (const jl of [8, 16]) for (const dx of depth === 0 ? [0, 20, 40] : [0, 6]) {
          tried++; g.st = structuredClone(node.snap); K.left = K.right = K.jump = false;
          for (let i = 0; i < w; i++) g.step(); if (g.st.p.dead) continue;
          const x0 = g.st.p.x; K.right = true; let land = null, jt = -1;
          for (let i = 0; i < 160; i++) { const P = g.st.p; if (jt < 0 && P.x >= x0 + dx) { jt = i; K.jump = true; } if (jt >= 0 && i === jt + jl) K.jump = false; g.step(); if (P.dead || P.y > 14 * T) break; if (jt >= 0 && i > jt + 4 && P.onG) { land = P; break; } }
          K.right = K.jump = false; if (!land || g.st.p.dead) continue;
          for (let i = 0; i < 4; i++) g.step(); if (g.st.p.dead) continue;
          const path = node.path.concat([[w, jl, dx, +(g.st.p.x / T).toFixed(1), +((g.st.p.y + g.st.p.h) / T).toFixed(1)]]);
          if (ok(g.st)) return { ok: true, path, tried };
          if (g.st.p.x > node.snap.p.x + 8 && next.length < 60) next.push({ snap: structuredClone(g.st), path });
        }
        q = next; if (!q.length) break;
      }
      return { ok: false, tried };
    };
    return { sinos: search(65, 75, { depth: 3 }) };
  });
  console.log(JSON.stringify(r)); console.log('ERRS', errs); await b.close(); })();
