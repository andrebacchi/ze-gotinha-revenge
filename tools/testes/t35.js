const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs = []; const out = {};
  const open = async (vw, vh) => { const p = await (await b.newContext({ viewport: { width: vw, height: vh } })).newPage(); p.on('pageerror', e => errs.push(e.message)); await p.goto('file://' + __dirname + '/page_intro.html'); await p.waitForTimeout(700); await p.addStyleTag({ content: '#scPause{display:none!important}' }); return p; };
  const pre = `const g=__mg,s=g.st,K=g.keys,run=n=>{for(let i=0;i<n;i++)g.step()},card=()=>s.intro?[s.intro.type,document.querySelector('#inName').textContent,!document.querySelector('#intro').hidden]:null,
    closeCard=()=>{if(!s.intro)return;run(50);K.jump=true;g.step();K.jump=false;run(20)},go=(col)=>{s.p.x=col*16;s.p.y=192-s.p.h;s.p.vx=s.p.vy=0;s.p.inv=0;s.cam.x=Math.max(0,col*16-150)},
    until=(f,n=900)=>{let i=0;for(;i<n&&!f();i++)g.step();return i};`;
  const p = await open(1280, 800);
  const ev = js => p.evaluate(`(()=>{${pre}${js}})()`);
  const shot = async n => { await p.waitForTimeout(120); await p.screenshot({ path: n, clip: { x: 80, y: 0, width: 1120, height: 760 } }); };
  await ev(`__mg.start();document.querySelector('#btPause').click();`);
  out.inicio = await ev(`const i=until(()=>s.intro);run(30);return [i,card(),s.time]`); await shot('q-gota.png');
  out.fecha = await ev(`const t=s.time;closeCard();return [!!s.intro,s.time-t]`);
  // cartões no caminho: seringa, SUS, jacaré
  out.syr = await ev(`s.enemies.forEach(e=>e.dead=true);go(29.5);s.p.y=8*16-s.p.h;until(()=>s.intro,60);run(30);return card()`); await shot('q-syr.png'); await ev(`closeCard()`);
  out.sus = await ev(`go(12);s.items.push({t:'sus',x:s.p.x+30,y:176,w:15,h:9,src:'t'});until(()=>s.intro,60);run(30);return card()`); await shot('q-sus.png'); await ev(`closeCard();s.items.filter(i=>i.src==='t').forEach(i=>i.got=true)`);
  // portão: cartão de apresentação, depois contador
  out.gate = await ev(`go(37.5);until(()=>s.intro,60);run(30);return [card(),s.gates[0].tm]`); await shot('q-gate.png');
  out.timer0 = await ev(`closeCard();run(3);const G0=s.gates[0];return [G0.tm,document.querySelector('#msg').textContent.slice(0,60)]`);
  await ev(`run(200)`); await shot('q-t1.png'); await ev(`until(()=>s.gates[0].tm<=150)`); await shot('q-t2.png');
  out.timeout = await ev(`const G0=s.gates[0],q0=G0.q.q;const i=until(()=>s.intro,400);run(30);const r=[i,card(),document.querySelector('#inQuote').textContent===('“'+q0+'”'),G0.err,G0.lock,G0.tm,s.enemies.filter(e=>e.minion&&!e.dead).length];window.__q0=q0;return r`); await shot('q-timeout.png');
  out.aposTempo = await ev(`const G0=s.gates[0];closeCard();s.enemies.forEach(e=>e.dead=true);const m=document.querySelector('#msg').textContent;until(()=>G0.lock===0,400);run(3);return [m,G0.q.q!==window.__q0,G0.tm>500,G0.open]`);
  // erro batendo no bloco errado
  out.erro = await ev(`const G0=s.gates[0],w=G0.q.a==='M'?G0.fx:G0.mx;g.answer(w,G0.q.a==='M'?'F':'M');run(40);return [card(),G0.err,document.querySelector('#intro').className]`); await shot('q-erro.png');
  out.aposErro = await ev(`const G0=s.gates[0];closeCard();s.enemies.forEach(e=>e.dead=true);until(()=>G0.lock===0,400);run(3);return [G0.tm>500,G0.err]`);
  // acerto
  out.certo = await ev(`const G0=s.gates[0],w=G0.q.a==='M'?G0.mx:G0.fx;run(60);const t=G0.tm;g.answer(w,G0.q.a);run(40);return [t,card(),G0.open,document.querySelector('#intro').className,s.stats.acertos]`); await shot('q-certo.png');
  out.aposCerto = await ev(`closeCard();run(5);return [document.querySelector('#msg').textContent,s.gates[0].tm,!!s.intro]`);
  // jacaré
  out.jac = await ev(`go(50);until(()=>s.intro,80);run(30);return [card(),[...document.querySelectorAll('#inList li')].length]`); await shot('q-jac.png'); await ev(`closeCard()`);
  out.pontos = await ev(`return s.gates.map(g=>[g.open,g.err||0])`);
  // celular em pé e deitado: o cartão cabe?
  for (const [n, vw, vh] of [['m', 390, 800], ['l', 800, 390]]) { const pm = await open(vw, vh); await pm.evaluate(`__mg.start();document.querySelector('#btPause').click()`); const r = await pm.evaluate(`(()=>{${pre}s.seen.i_gota=1;s.seen.i_syr=1;s.enemies.forEach(e=>e.dead=true);run(50);go(50);until(()=>s.intro,80);run(30);const el=document.querySelector('#intro'),st2=document.querySelector('#stage').getBoundingClientRect(),r=el.getBoundingClientRect();return [card(),Math.round(r.height),Math.round(st2.height),el.scrollHeight>el.clientHeight+1,r.top>=st2.top-1&&r.bottom<=st2.bottom+1]})()`); out['jac_' + n] = r; await pm.waitForTimeout(120); await pm.screenshot({ path: 'q-jac-' + n + '.png' });
    const r2 = await pm.evaluate(`(()=>{${pre}closeCard();go(37.5);until(()=>s.intro,60);closeCard();run(3);const G0=s.gates[0];g.answer(G0.mx,G0.q.a==='M'?'F':'M');g.answer(G0.fx,G0.q.a==='M'?'F':'M');run(40);const el=document.querySelector('#intro'),st2=document.querySelector('#stage').getBoundingClientRect(),r=el.getBoundingClientRect();return [card(),Math.round(r.height),Math.round(st2.height),el.scrollHeight>el.clientHeight+1]})()`); out['erro_' + n] = r2; await pm.waitForTimeout(120); await pm.screenshot({ path: 'q-erro-' + n + '.png' }); }
  console.log(JSON.stringify(out, null, 0).replace(/],"/g, '],\n"')); console.log('ERRS', errs); await b.close(); })();
