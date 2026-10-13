// Juice: estica no pulo, espreme no pouso, poeira, pausa no impacto e tremores (capturas ju-*.png).
const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await (await b.newContext({ viewport: { width: 1280, height: 800 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('file://' + __dirname + '/page_intro.html'); await p.waitForTimeout(700); await p.addStyleTag({ content: '#scPause{display:none!important}#msg{display:none!important}' });
  const pre = `const g=__mg,s=g.st,K=g.keys,run=n=>{for(let i=0;i<n;i++)g.step()};`;
  await p.evaluate(`(()=>{__mg.start('normal');${pre}s.opening=null;s.cam.y=44;for(const k of ['boato','fake','virus','i_gota','i_syr','i_sus','i_shield','i_boost','jac','gate','boss'])s.seen[k]=1;for(const k of ['fire','sus','move'])s.hints[k]=1;document.querySelector('#btPause').click();s.enemies.forEach(e=>e.dead=true);s.p.x=36*16;s.p.y=192-24;s.cam.x=36*16-120;run(5)})()`);
  const cv = p.locator('canvas').first(), out = {}; const shot = async n => { await p.waitForTimeout(70); await cv.screenshot({ path: `ju-${n}.png` }); return p.evaluate(`[__mg.st.p.x-__mg.st.cam.x,__mg.st.p.y-__mg.st.cam.y]`); };
  const pos = {};
  pos.parado = await shot('parado');
  out.pulo = await p.evaluate(`(()=>{${pre}K.jump=true;g.step();return [s.p.jT,s.p.vy.toFixed(1)]})()`); pos.estica = await shot('estica');
  await p.evaluate(`(()=>{${pre}K.jump=false;for(let i=0;i<80&&!s.p.onG;i++)g.step()})()`); out.pouso = await p.evaluate(`[__mg.st.p.landT,__mg.st.p.landK]`); pos.espreme = await shot('espreme');
  // queda alta: poeira e tremor
  out.queda = await p.evaluate(`(()=>{${pre}run(20);s.p.y=40;s.p.vy=0;s.p.onG=false;const n0=s.parts.length;for(let i=0;i<80&&!s.p.onG;i++)g.step();return [s.p.landK.toFixed(2),s.parts.length-n0,s.shake,s.shakeA]})()`); pos.poeira = await shot('poeira');
  // pausa no impacto ao derrotar inimigo
  out.inimigo = await p.evaluate(`(()=>{${pre}run(30);s.enemies.push({t:'virus',x:s.p.x+30,y:176,w:16,h:16,face:-1,vx:0,vy:0,hp:9,tm:9999,fl:0});s.p.face=1;s.p.ammo=3;s.p.cd=0;K.fire=true;g.step();K.fire=false;let i=0;for(;i<40&&!(s.hitstop>0);i++)g.step();const e=s.enemies[s.enemies.length-1];const t0=s.time;const h=s.hitstop;run(h);return [h,s.time===t0,e.fl,e.hp]})()`); pos.treme = await shot('treme');
  // golpe no Zé: pausa, tremor, Zé tremendo
  out.dano = await p.evaluate(`(()=>{${pre}s.enemies.forEach(e=>e.dead=true);run(40);s.p.big=true;s.p.w=14;s.p.h=32;s.p.y=192-32;s.p.inv=0;s.enemies.push({t:'boato',x:s.p.x+2,y:176,w:14,h:16,dir:-1,vx:0,vy:0,hp:1,fl:0});g.step();return [s.hitstop,s.shake,s.shakeA,s.p.hurtT,s.p.big]})()`); pos.dano = await shot('dano');
  require('fs').writeFileSync('ju-pos.json', JSON.stringify(pos));
  console.log(JSON.stringify(out)); console.log('ERRS', errs); await b.close(); })();
