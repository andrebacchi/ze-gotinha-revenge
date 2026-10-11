const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs = [], out = {};
  for (const [n, vw, vh] of [['d', 1280, 800], ['m', 390, 800], ['l', 800, 390]]) { const p = await (await b.newContext({ viewport: { width: vw, height: vh }, hasTouch: n !== 'd' })).newPage(); p.on('pageerror', e => errs.push(n + ' ' + e.message)); await p.goto('file://' + __dirname + '/page_intro.html'); await p.waitForTimeout(900);
    await p.screenshot({ path: `o-title-${n}.png` });
    out['titulo_' + n] = await p.evaluate(() => ({ howto: !!document.querySelector('#howto'), msgVis: getComputedStyle(document.querySelector('#msg')).visibility, botoes: [...document.querySelectorAll('.tmenu button')].map(b => b.textContent) }));
    await p.click('#btHelp'); await p.waitForTimeout(200); await p.screenshot({ path: `o-help-${n}.png` });
    out['ajuda_' + n] = await p.evaluate(() => { const h = document.querySelector('#scHelp'), st = document.querySelector('#stage').getBoundingClientRect(), row = h.querySelector('.row').getBoundingClientRect(), h2 = h.querySelector('h2').getBoundingClientRect(); return { aberta: !h.hidden, linhas: h.querySelectorAll('dt').length, cabe: h2.top >= st.top - 1 && row.bottom <= st.bottom + 1, sobra: Math.round(st.bottom - row.bottom) }; });
    if (n === 'd') { await p.keyboard.press('Escape'); out.esc = await p.evaluate(() => document.querySelector('#scHelp').hidden); await p.click('#btHelp'); }
    await p.click('#btHelpStart'); await p.waitForTimeout(100);
    out['inicio_' + n] = await p.evaluate(() => { document.querySelector('#btPause').click(); const s = __mg.st; return { mode: __mg.mode, abertura: !!s.opening, camY: Math.round(s.cam.y), ajuda: document.querySelector('#scHelp').hidden, titulo: document.querySelector('#scTitle').hidden }; });
    if (n === 'd') { await p.addStyleTag({ content: '#scPause{display:none!important}' }); const cv = p.locator('canvas').first();
      for (const t of [25, 110, 150, 185, 215]) { const r = await p.evaluate(`(()=>{const g=__mg,s=g.st;while(s.opening&&s.opening.t<${t})g.step();return [s.opening?s.opening.t:null,Math.round(s.cam.y),s.time]})()`); await p.waitForTimeout(80); await cv.screenshot({ path: `o-open-${t}.png` }); out['t' + t] = r; }
      out.fim = await p.evaluate(`(()=>{const g=__mg,s=g.st;for(let i=0;i<30;i++)g.step();return [!!s.opening,Math.round(s.cam.y),s.time]})()`);
      out.pular = await p.evaluate(`(()=>{const g=__mg;g.start();document.querySelector('#btPause').click();const s=g.st;for(let i=0;i<20;i++)g.step();g.keys.jump=true;g.step();const cedo=!!s.opening;g.keys.jump=false;for(let i=0;i<20;i++)g.step();g.keys.jump=true;g.step();g.keys.jump=false;return [cedo,!!s.opening,Math.round(s.cam.y)]})()`); }
    await p.close(); }
  console.log(JSON.stringify(out, null, 0).replace(/},"/g, '},\n"').replace(/],"/g, '],\n"')); console.log('ERRS', errs); await b.close();
  require('child_process').execSync(`python3 -c "
from PIL import Image
ims=[Image.open('o-open-%d.png'%t).resize((560,315)) for t in (25,110,150,185,215)]+[Image.open('o-title-d.png').crop((80,0,1200,640)).resize((560,320))]
sh=Image.new('RGB',(560*3,320*2)); [sh.paste(im,((i%3)*560,(i//3)*320)) for i,im in enumerate(ims)]; sh.save('o-open.png')
a=Image.open('o-help-d.png').crop((80,0,1200,640)).resize((700,400)); m=Image.open('o-help-m.png').crop((0,0,390,330)); l=Image.open('o-help-l.png').resize((600,292)); t=Image.open('o-title-m.png').crop((0,0,390,330))
sh=Image.new('RGB',(700+390+390,400+292)); sh.paste(a,(0,0)); sh.paste(m,(700,0)); sh.paste(t,(1090,0)); sh.paste(l,(0,400)); sh.save('o-help.png')"`); })();
