// Vitória: pular encerra, montado desce do jacaré, espera pousar, tempo parado e câmera lenta no laço real.
const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs = []; const out = {};
  const p = await (await b.newContext({ viewport: { width: 1280, height: 800 } })).newPage(); p.on('pageerror', e => errs.push(e.message));
  const pre = `const g=__mg,s=g.st,K=g.keys,run=n=>{for(let i=0;i<n;i++)g.step()};`;
  const prep = async () => { await p.goto('file://' + __dirname + '/page_intro.html'); await p.waitForTimeout(600); await p.addStyleTag({ content: '#scPause{display:none!important}' });
    await p.evaluate(`(()=>{__mg.start();${pre}s.opening=null;s.cam.y=44;for(const k of ['boato','fake','virus','i_gota','i_syr','i_sus','i_shield','i_boost','jac','gate','boss'])s.seen[k]=1;for(const k of ['fire','sus','move','tired','bubble','ride','egg2'])s.hints[k]=1;document.querySelector('#btPause').click();
      s.enemies.forEach(e=>e.dead=true);s.p.x=160*16;s.p.y=192-24;g.bossStart();run(150);s.boss.hp=1;s.boss.st='tired';s.boss.bubble=false;s.boss.y=192-s.boss.h;s.boss.x=s.p.x+40;s.boss.inv=0;})()`); };
  const kill = `s.p.face=1;s.p.ammo=3;s.p.cd=0;K.fire=true;g.step();K.fire=false;for(let i=0;i<300&&!s.vic;i++)g.step();`;
  // 1) pular encerra depois da pose
  await prep(); out.pular = await p.evaluate(`(()=>{${pre}${kill}for(let i=0;i<200&&s.vic.g<60;i++)g.step();const antes=[s.vic.g,g.mode];K.jump=true;g.step();K.jump=false;const cedo=[s.vic.g,!!s.vic.done];run(20);K.jump=true;g.step();K.jump=false;return {antes,cedo,depois:[s.vic.g,!!s.vic.done,g.mode,!document.querySelector('#scSoon').hidden]}})()`);
  // 2) montado no jacaré
  await prep(); out.montado = await p.evaluate(`(()=>{${pre}const j=s.jacs[0];j.state='idle';j.t=30;j.x=s.p.x;j.y=192-12;run(4);const mont=!!s.p.ride;${kill}run(1);const a=[!!s.p.ride,j.state,Math.round(j.x-s.p.x)];for(let i=0;i<200&&s.vic.g<50;i++)g.step();return {mont,logo:a,pose:[s.vic.g,!!s.p.ride,j.state,s.p.w,s.p.h,s.p.onG]}})()`);
  // 3) no ar na hora da vitória: espera pousar; e comandos não mexem o Zé
  await prep(); out.noAr = await p.evaluate(`(()=>{${pre}${kill}s.p.y-=60;s.p.onG=false;s.p.vy=-3;K.right=true;run(10);const ar=[s.vic.g,s.p.onG];for(let i=0;i<200&&s.vic.g<0;i++)g.step();const x0=s.p.x;run(30);K.right=false;return {ar,pousou:[s.vic.g,s.p.onG],andou:Math.round(s.p.x-x0)}})()`);
  // 4) pontuação igual ao tempo do golpe final
  out.tempo = await p.evaluate(`(()=>{${pre}const f=s.finalT;run(300);return [f>0,s.finalT===f,g.mode]})()`);
  // 5) laço real: câmera lenta
  await prep(); const t0 = await p.evaluate(`(()=>{${pre}s.p.face=1;s.p.ammo=3;s.p.cd=0;K.fire=true;g.step();K.fire=false;for(let i=0;i<60&&s.boss.st!=='dying';i++)g.step();document.querySelector('#scPause .btn')?.click();return [g.mode,s.slow,s.time]})()`);
  await p.waitForTimeout(100); const m1 = await p.evaluate(`[__mg.mode,__mg.st.slow,__mg.st.time]`); await p.waitForTimeout(1000); const m2 = await p.evaluate(`[__mg.mode,__mg.st.slow,__mg.st.time]`); await p.waitForTimeout(2500); const m3 = await p.evaluate(`[__mg.mode,__mg.st.slow,__mg.st.time]`);
  out.lenta = { t0, m1, m2, m3 };
  console.log(JSON.stringify(out, null, 0).replace(/},"/g, '},\n"')); console.log('ERRS', errs); await b.close(); })();
