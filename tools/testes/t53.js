// Escudo de imunidade e bolha de eco: tira capturas (au-*.png) de cada estado para conferir a olho.
const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await (await b.newContext({ viewport: { width: 1280, height: 800 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('file://' + __dirname + '/page.html'); await p.waitForTimeout(700); await p.addStyleTag({ content: '#scPause{display:none!important}#msg{display:none!important}' });
  const pre = `const g=__mg,s=g.st,K=g.keys,run=n=>{for(let i=0;i<n;i++)g.step()};`;
  await p.evaluate(`(()=>{__mg.start();${pre}run(5);for(const k in {fire:1,sus:1,move:1,ride:1,egg2:1,tired:1,bubble:1})s.hints[k]=1;document.querySelector('#btPause').click();s.enemies.forEach(e=>e.dead=true)})()`);
  const cv = p.locator('canvas').first(); const shot = async n => { await p.waitForTimeout(80); await cv.screenshot({ path: `au-${n}.png` }); return p.evaluate(`(()=>{const s=__mg.st;return [s.p.x-s.cam.x,s.p.y-(s.cam.y||0),s.boss.x-s.cam.x,s.boss.y-(s.cam.y||0)]})()`); };
  const pos = {};
  await p.evaluate(`(()=>{${pre}s.p.x=36*16;s.p.y=192-24;s.cam.x=36*16-120;s.p.shield=true;run(3)})()`);
  for (let i = 0; i < 3; i++) { pos['p' + i] = await shot('p' + i); await p.evaluate(`(()=>{${pre}run(7)})()`); }
  // quebra do escudo
  await p.evaluate(`(()=>{${pre}s.enemies.push({t:'boato',x:s.p.x+2,y:176,w:14,h:16,dir:-1,vx:0,vy:0,hp:1,fl:0});run(1);s.enemies.forEach(e=>e.dead=true)})()`);
  const brk = await p.evaluate(`(()=>{const s=__mg.st;return [s.p.shield,s.p.dead,s.fx.length,s.fx[0]&&s.fx[0].t]})()`); console.log('quebra', brk);
  for (let i = 0; i < 4; i++) { pos['q' + i] = await shot('q' + i); await p.evaluate(`(()=>{${pre}run(5)})()`); }
  // sarado
  await p.evaluate(`(()=>{${pre}run(80);s.p.big=true;s.p.w=14;s.p.h=32;s.p.y=192-32;s.p.shield=true;s.p.inv=0;run(3)})()`); pos.g0 = await shot('g0');
  await p.evaluate(`(()=>{${pre}s.enemies.push({t:'boato',x:s.p.x+2,y:176,w:14,h:16,dir:-1,vx:0,vy:0,hp:1,fl:0});run(1);s.enemies.forEach(e=>e.dead=true);run(2)})()`); pos.g1 = await shot('g1');
  await p.evaluate(`(()=>{${pre}run(6)})()`); pos.g2 = await shot('g2'); await p.evaluate(`(()=>{${pre}run(5)})()`); pos.g3 = await shot('g3');
  // montado
  const m = await p.evaluate(`(()=>{${pre}run(80);const j=s.jacs[0];j.state='idle';j.x=s.p.x+30;j.y=192-j.h;s.p.x=j.x+4;s.p.y=120;s.p.vy=1;s.p.shield=true;for(let i=0;i<60&&!s.p.ride;i++)g.step();run(10);return [!!s.p.ride,s.p.big,s.p.w,s.p.h]})()`); console.log('montado', m); pos.m0 = await shot('m0');
  await p.evaluate(`(()=>{${pre}s.p.big=false;run(4)})()`); pos.m1 = await shot('m1');
  // chefão
  await p.evaluate(`(()=>{${pre}s.p.ride=null;s.p.w=10;s.p.h=24;s.p.shield=false;s.p.x=156*16;s.p.y=192-24;s.p.inv=99999;g.bossStart();run(150)})()`);
  for (let i = 0; i < 3; i++) { pos['b' + i] = await shot('b' + i); await p.evaluate(`(()=>{${pre}run(8)})()`); }
  const seq = await p.evaluate(`(()=>{${pre}const b=s.boss,log=[];let last=b.st;for(let i=0;i<4000;i++){g.step();s.p.inv=999;if(b.st!==last){log.push(i+':'+b.st);last=b.st;if(b.st==='tired')break}}return [log.join(' '),b.bubble,s.fx.length]})()`); console.log(seq);
  for (let i = 0; i < 3; i++) { pos['t' + i] = await shot('t' + i); await p.evaluate(`(()=>{${pre}run(7)})()`); }
  const seq2 = await p.evaluate(`(()=>{${pre}const b=s.boss;for(let i=0;i<400&&b.st==='tired';i++){g.step();s.p.inv=999}run(1);return [b.st,b.bubble,b.bubIn]})()`); console.log(seq2);
  for (let i = 0; i < 4; i++) { pos['r' + i] = await shot('r' + i); await p.evaluate(`(()=>{${pre}run(5)})()`); }
  require('fs').writeFileSync('au-pos.json', JSON.stringify(pos)); console.log('ERRS', errs); await b.close(); })();
