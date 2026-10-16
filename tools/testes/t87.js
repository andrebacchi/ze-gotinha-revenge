// Fase 3: a balança de três evidências resolvida por robô (só setas, pulo e empurrão; busca por força bruta para chegar a cada ponto),
// e as duas armadilhas: metanálise primeiro e evidência enterrada no buraco raso. Aceita 'normal' ou 'facil'.
const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs = [];
  const p = await (await b.newContext()).newPage(); p.on('pageerror', e => errs.push('PAGEERR ' + e.message));
  await p.addInitScript('window.__mgNoSave=1'); await p.goto('file://' + __dirname + '/page.html'); await p.waitForTimeout(700);
  const r = await p.evaluate(diff => {
    const g = window.__mg, K = g.keys, T = 16, out = {};
    const fresh = () => { g.startFase(3, diff); const s = g.st; s.opening = null; for (const e of s.enemies) if (e.x > 214 * T && e.x < 262 * T) e.dead = true; for (const gt of s.gates) gt.open = true; for (let y = 8; y <= 11; y++) s.map[y][222] = s.map[y][223] = '.'; s.drips = []; return s; };
    const P = () => g.st.p, Bk = () => g.st.blocks.filter(k => k.bal === 0), by = l => Bk().find(k => k.lab === l);
    const pos = () => Bk().map(k => k.lab + '@' + (k.x / T).toFixed(2) + ',' + (k.y / T).toFixed(2) + (k.gone ? 'X' : '')).join(' ');
    const idle = n => { K.left = K.right = K.jump = false; for (let i = 0; i < n; i++) { P().inv = 2; g.step(); } };
    const push = (dir, l, until, max = 1200) => { let k = by(l); K[dir] = true; let last = k.x, still = 0; for (let i = 0; i < max; i++) { P().inv = 2; g.step(); k = by(l); if (until(k)) break; if (Math.abs(k.x - last) < .01) { if (++still > 50) break; } else still = 0; last = k.x; } K[dir] = false; push.last = [(P().x / T).toFixed(2), (P().y / T).toFixed(2), P().onG, P().big, P().dead, P().pushT].join(' '); idle(40); };
    // chega a um ponto só com setas e pulo: busca em largura sobre (espera, direção, tempo de pulo, corrida), com os blocos que não podem mexer
    const reach = (ok, keep) => {
      const ks = Bk().filter(k => keep.includes(k.lab)).map(k => [k.lab, k.x, k.y]);
      const same = () => ks.every(([l, x, y]) => { const k = Bk().find(k => k.lab === l); return Math.abs(k.x - x) < .5 && Math.abs(k.y - y) < .5; });
      let q = [structuredClone(g.st)], seen = new Set();
      for (let depth = 0; depth < 4; depth++) {
        const next = [];
        for (const snap of q) for (const dir of ['right', 'left', null]) for (const jl of [0, 6, 12, 20]) for (const run of [4, 10, 20, 34]) {
          g.st = structuredClone(snap); K.left = K.right = K.jump = false;
          if (dir) K[dir] = true; if (jl) K.jump = true;
          let i = 0; for (; i < 100; i++) { P().inv = 2; if (jl && i === jl) K.jump = false; if (i === run && dir) K[dir] = false; g.step(); if (i > Math.max(run, jl) && P().onG) break; }
          idle(6); if (P().dead || !same()) continue;
          if (ok(P())) return true;
          const key = Math.round(P().x / 3) + ',' + Math.round(P().y / 3); if (seen.has(key)) continue; seen.add(key);
          if (next.length < 120) next.push(structuredClone(g.st));
        }
        q = next; if (!q.length) break;
      }
      return false;
    };
    const ground = (a, b2) => p => p.onG && Math.abs(p.y + p.h - 12 * T) < 1 && p.x >= a && p.x + p.w <= b2;
    const log = [];
    const step = (n, f) => { const r = f(); log.push(n + (r === false ? ' FALHOU' : '') + ' | ' + pos() + ' | zé ' + push.last); return r !== false; };
    // solução
    let s = fresh(); P().x = 223 * T + 2; P().y = 12 * T - P().h; idle(4);
    const IMP = 'IMPORTADO', DADOS = 'DADOS', ENS = 'ENSAIO CLÍNICO', RS = 'R$ 890', META = 'METANÁLISE', X = l => by(l).x;
    const plan = [
      ['pote até perto da prateleira', () => push('right', IMP, k => k.x >= 227 * T)],
      ['sobe na prateleira alta', () => reach(p => p.onG && Math.abs(p.y + p.h - 9 * T) < 1 && p.x + p.w <= X(DADOS) + .5, ['DADOS', 'ENSAIO CLÍNICO', 'R$ 890', 'METANÁLISE'])],
      ['derruba DADOS', () => push('right', DADOS, k => k.onG && k.y >= 11 * T - 1 && k.vy === 0 && k.fell === 0 && k.x > 231.5 * T)],
      ['vai para depois do R$ 890', () => reach(ground(238 * T, 239 * T + 2), ['ENSAIO CLÍNICO', 'R$ 890', 'METANÁLISE'])],
      ['R$ 890 tapa o buraco', () => push('left', RS, k => k.y >= 12 * T - 1)],
      ['volta para antes do ensaio', () => reach(p => ground(X(DADOS) + 16, X(ENS) + .5)(p), ['ENSAIO CLÍNICO', 'DADOS', 'METANÁLISE'])],
      ['ensaio até o fim do prato', () => push('right', ENS, k => false)],
      ['volta para antes de DADOS', () => reach(p => ground(225 * T, X(DADOS) + .5)(p), ['ENSAIO CLÍNICO', 'DADOS', 'METANÁLISE'])],
      ['DADOS no prato', () => push('right', DADOS, k => false)],
      ['sobe na prateleira baixa', () => reach(p => p.onG && Math.abs(p.y + p.h - 10 * T) < 1 && p.x + p.w <= X(META) + .5, ['ENSAIO CLÍNICO', 'DADOS', 'METANÁLISE'])],
      ['metanálise empilhada', () => push('right', META, k => g.st.bals[0].solved || (k.onG && k.y > 9.5 * T && k.fell === 0 && k.x > 240.5 * T))],
    ];
    for (const [n, f] of plan) if (!step(n, f)) break;
    idle(30);
    out.solucao = { peso: g.st.bals[0].w, resolvida: g.st.bals[0].solved, porta: g.st.map[10][243], log };
    // armadilha 1: metanálise primeiro
    s = fresh(); P().x = 236 * T; P().y = 12 * T - P().h; idle(4);
    reach(p => p.onG && Math.abs(p.y + p.h - 10 * T) < 1 && p.x + p.w <= X('METANÁLISE') + .5, ['METANÁLISE']); push('right', 'METANÁLISE', k => k.onG && k.y > 9.5 * T && k.fell === 0 && k.x > 240.5 * T);
    out.metaPrimeiro = { meta: (X('METANÁLISE') / T).toFixed(1) + ',' + (by('METANÁLISE').y / T).toFixed(1), peso: g.st.bals[0].w };
    // armadilha 2: ensaio empurrado direto para o buraco
    s = fresh(); P().x = 233 * T; P().y = 12 * T - P().h; idle(4);
    push('right', 'ENSAIO CLÍNICO', k => k.y >= 12 * T - 1); const E2 = by('ENSAIO CLÍNICO');
    out.ensaioNoBuraco = { ensaio: (E2.x / T).toFixed(1) + ',' + (E2.y / T).toFixed(1), dica: [...document.querySelectorAll('#msg, .msg, #hint')].map(e => e.textContent).join(' | ').slice(0, 120) };
    // o posto novo
    out.postos = g.st.cps.map(c => c.x);
    return out;
  }, process.argv[2] || 'normal');
  console.log(JSON.stringify(r, null, 1)); console.log('ERRS', errs); await b.close(); })();
