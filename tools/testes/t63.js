// Controle (gamepad) simulado: menus, jogo, pausa, controle da tela some e volta ao tocar (precisa do servidor na 8765).
const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs = []; const out = {};
  for (const [nome, vw, vh, touch] of [['m', 390, 800, true], ['l', 800, 390, true], ['d', 1280, 800, false]]) {
    const ctx = await b.newContext({ viewport: { width: vw, height: vh }, hasTouch: touch, isMobile: touch }); const p = await ctx.newPage(); p.on('pageerror', e => errs.push(nome + ': ' + e.message));
    await p.addInitScript(() => {   // controle falso no padrão "standard"
      const pad = { id: 'GameSir X2 (simulado)', index: 0, connected: true, mapping: 'standard', axes: [0, 0, 0, 0], buttons: Array.from({ length: 17 }, () => ({ pressed: false, value: 0 })), timestamp: 0 };
      window.__pad = pad; window.__ligado = false; navigator.getGamepads = () => [window.__ligado ? pad : null, null, null, null];
      window.__aperta = (i, on) => { pad.buttons[i].pressed = on; pad.buttons[i].value = on ? 1 : 0; };
    });
    await p.goto('http://localhost:8765/'); await p.waitForTimeout(700); await p.evaluate(() => localStorage.removeItem('mg-salvo'));
    const tap = async (i, ms = 90) => { await p.evaluate(i => __aperta(i, true), i); await p.waitForTimeout(ms); await p.evaluate(i => __aperta(i, false), i); await p.waitForTimeout(90); };
    const r = {}; const stageH = () => p.evaluate(() => Math.round(document.querySelector('#stage').getBoundingClientRect().height));
    r.antes = [await p.evaluate(() => getComputedStyle(document.querySelector('#pads')).display), await stageH()];
    await p.evaluate(() => { window.__ligado = true; }); await tap(0);   // A no título sem foco: começa (sem jogo salvo, abre o modo)
    r.titulo = await p.evaluate(() => [document.body.classList.contains('pad-on'), getComputedStyle(document.querySelector('#pads')).display, !document.querySelector('#scMode').hidden, document.activeElement.id]);
    r.palcoComControle = await stageH();
    await tap(15); r.foco = await p.evaluate(() => document.activeElement.id); await tap(1); r.voltou = await p.evaluate(() => document.querySelector('#scMode').hidden);
    await tap(9); await p.waitForTimeout(150); await tap(15); await tap(0); await p.waitForTimeout(300);   // Start abre o modo, direita → Fácil, A confirma
    r.jogo = await p.evaluate(() => [__mg.mode, __mg.st.diff]);
    await p.evaluate(() => { const s = __mg.st; s.opening = null; s.cam.y = 44; for (const k of ['boato','fake','virus','i_gota','i_syr','i_sus','i_shield','i_boost','jac','gate']) s.seen[k] = 1; for (const k of ['move','fire','sus']) s.hints[k] = 1; s.enemies.forEach(e => e.dead = true); s.p.x = 36 * 16; s.p.y = 192 - 24; });
    const x0 = await p.evaluate(() => __mg.st.p.x); await p.evaluate(() => { __pad.axes[0] = 1; }); await p.waitForTimeout(400); await p.evaluate(() => { __pad.axes[0] = 0; }); await p.waitForTimeout(200);
    r.andou = Math.round(await p.evaluate(() => __mg.st.p.x) - x0);
    await p.evaluate(() => __aperta(0, true)); await p.waitForTimeout(120); r.pulou = await p.evaluate(() => [!__mg.st.p.onG, __mg.keys.jump]); await p.evaluate(() => __aperta(0, false)); await p.waitForTimeout(600);
    const a0 = await p.evaluate(() => __mg.st.p.ammo); await tap(2); r.seringa = [a0, await p.evaluate(() => __mg.st.p.ammo)];
    await tap(9); r.pausa = await p.evaluate(() => __mg.mode); await tap(13); await tap(13); r.focoPausa = await p.evaluate(() => document.activeElement.id); await tap(9); r.voltaJogo = await p.evaluate(() => __mg.mode);
    if (touch) { await p.touchscreen.tap(Math.round(vw / 2), 40); await p.waitForTimeout(200); r.toque = await p.evaluate(() => [document.body.classList.contains('pad-on'), getComputedStyle(document.querySelector('#pads')).display]); }
    await p.evaluate(() => { window.__ligado = false; }); await p.waitForTimeout(200); r.desligado = await p.evaluate(() => document.body.classList.contains('pad-on'));
    r.rolagem = await p.evaluate(() => document.documentElement.scrollWidth > innerWidth);
    out[nome] = r; await ctx.close(); }
  console.log(JSON.stringify(out, null, 0).replace(/},"/g, '},\n"')); console.log('ERRS', errs); await b.close(); })();
