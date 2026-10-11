// Vitória sobre o chefão: capturas de cada etapa (vi-*.png) em três tamanhos de tela.
const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs = []; const out = {};
  for (const [nome, vw, vh, big] of [['d', 1280, 800, false], ['m', 390, 800, true], ['l', 800, 390, false]]) {
    const p = await (await b.newContext({ viewport: { width: vw, height: vh } })).newPage(); p.on('pageerror', e => errs.push(e.message));
    await p.goto('file://' + __dirname + '/page_intro.html'); await p.waitForTimeout(700); await p.addStyleTag({ content: '#scPause{display:none!important}' });
    const pre = `const g=__mg,s=g.st,K=g.keys,run=n=>{for(let i=0;i<n;i++)g.step()};`;
    await p.evaluate(`(()=>{__mg.start();${pre}s.opening=null;s.cam.y=44;for(const k of ['boato','fake','virus','i_gota','i_syr','i_sus','i_shield','i_boost','jac','gate','boss'])s.seen[k]=1;for(const k of ['fire','sus','move','tired','bubble'])s.hints[k]=1;document.querySelector('#btPause').click();
      s.enemies.forEach(e=>e.dead=true);s.p.x=160*16;s.p.y=192-24;if(${big}){s.p.big=true;s.p.w=14;s.p.h=32;s.p.y=192-32}s.p.shield=true;g.bossStart();run(150);s.boss.hp=1;s.boss.st='tired';s.boss.bubble=false;s.boss.y=192-s.boss.h;s.boss.x=s.p.x+40;s.boss.inv=0;})()`);
    const cv = p.locator('canvas').first(); const shot = async n => { await p.waitForTimeout(90); await cv.screenshot({ path: `vi-${nome}-${n}.png` }); };
    // golpe final com seringa
    const r0 = await p.evaluate(`(()=>{${pre}s.p.face=1;s.p.ammo=3;s.p.cd=0;K.fire=true;g.step();K.fire=false;let i=0;for(;i<60&&s.boss.st!=='dying';i++)g.step();return [i,s.boss.st,s.slow,s.boss.hp,g.music]})()`);
    await p.evaluate(`(()=>{${pre}run(20)})()`); await shot('0-morrendo');
    const r1 = await p.evaluate(`(()=>{${pre}let i=0;for(;i<200&&!s.vic;i++)g.step();return [i,!!s.vic,s.boss.dead,s.slow,s.finalT>0]})()`);
    const r2 = await p.evaluate(`(()=>{${pre}let i=0;for(;i<200&&s.vic.g<0;i++)g.step();run(8);return [i,s.vic.g]})()`); await shot('1-preparo');
    await p.evaluate(`(()=>{${pre}run(14)})()`); await shot('2-salto'); await p.evaluate(`(()=>{${pre}run(26)})()`); await shot('3-pose');
    await p.evaluate(`(()=>{${pre}run(30)})()`); await shot('4-letreiro');
    const r3 = await p.evaluate(`(()=>{${pre}run(60);return [s.vic.g,Math.round(s.cam.y)]})()`); await shot('5-subindo');
    const r4 = await p.evaluate(`(()=>{${pre}run(80);return [s.vic.g,Math.round(s.cam.y),g.mode]})()`); await shot('6-ceu');
    const r5 = await p.evaluate(`(()=>{${pre}let i=0;for(;i<200&&g.mode==='pause';i++)g.step();return [i,g.mode,s.vic.g,Math.round(s.cam.y),!document.querySelector('#scSoon').hidden]})()`); await p.waitForTimeout(120); await p.screenshot({ path: `vi-${nome}-7-fim.png` });
    out[nome] = { golpe: r0, vic: r1, pouso: r2, sobe: r3, ceu: r4, fim: r5, rolagem: await p.evaluate('document.documentElement.scrollWidth>innerWidth') };
    await p.close(); }
  console.log(JSON.stringify(out, null, 0).replace(/},"/g, '},\n"')); console.log('ERRS', errs); await b.close(); })();
