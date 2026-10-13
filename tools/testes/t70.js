// Fase 2: capturas de cada trecho (pula a abertura e os cartões)
const { chromium } = require('playwright');
const OUT = process.argv[2] || '.';
(async () => { const b = await chromium.launch(); const errs = [];
  const p = await (await b.newContext({ viewport: { width: 960, height: 600 } })).newPage();
  p.on('pageerror', e => errs.push('PAGEERR ' + e.message)); p.on('console', m => { if (m.type() === 'error' && !/ERR_FILE|fonts/.test(m.text())) errs.push(m.text()); });
  await p.addInitScript('window.__mgNoSave=1');
  await p.goto('file://' + __dirname + '/page.html'); await p.waitForTimeout(800);
  await p.evaluate(() => window.__mg.startFase(2));
  const go = async (tx, name, steps = 30, ty) => {
    await p.evaluate(([tx, ty, steps]) => { const g = window.__mg, s = g.st; s.p.x = tx * 16; s.p.y = (ty ?? 12) * 16 - s.p.h; s.p.vy = 0; s.cam.x = Math.max(0, tx * 16 - 140); for (let i = 0; i < steps; i++) g.step(); }, [tx, ty, steps]);
    await p.waitForTimeout(120); await p.locator('#jogo').screenshot({ path: `${OUT}/${name}.png` });
  };
  await go(3, 'f2_00_inicio'); await go(16, 'f2_01_telhados', 30, 9); await go(31, 'f2_02_varal', 30, 8); await go(48, 'f2_03_portao');
  await go(64, 'f2_04_sinos'); await go(80, 'f2_05_balanca1'); await go(103, 'f2_06_mina'); await go(130, 'f2_07_mina2', 10);
  await go(205, 'f2_08_rio'); await go(228, 'f2_09_arco'); await go(252, 'f2_10_balanca2'); await go(285, 'f2_11_passarola');
  const r = await p.evaluate(() => { const s = window.__mg.st; return { fase: s.fase, lw: s.map[0].length, en: s.enemies.length, tot: s.enemyTotal, gotas: s.total, pu: s.puTotal, bals: s.bals.length, blocks: s.blocks.length }; });
  console.log(JSON.stringify(r)); console.log('ERRS', errs); await b.close(); })();
