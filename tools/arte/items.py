import sys, json, base64, io, pickle
from PIL import Image
import numpy as np, scipy.ndimage as ndi
from proc3 import Color
c=Color('items.png',k=14,seed=5); print('paleta',[tuple(int(v) for v in p) for p in c.pal])
comps=sorted(c.comps,key=lambda t:(t[1][0].start>380,t[1][1].start)); print(len(comps),[(o[0].stop-o[0].start,o[1].stop-o[1].start) for _,o,_ in comps])
names=['gota','syr','sus','shield','boost','q','used','blank','flag0','flag1']
# altura-alvo do corpo (sem o contorno de 1px) no jogo
target={'gota':11,'syr':None,'sus':None,'shield':12,'boost':13,'q':14,'used':14,'blank':14,'flag0':28,'flag1':28}
targetw={'syr':17,'sus':18}
def trim(f):
    ys,xs=np.nonzero(f[...,3]); return f[ys.min():ys.max()+1,xs.min():xs.max()+1]
out={}
for n,(li,o,_) in zip(names,comps):
    h,w=o[0].stop-o[0].start,o[1].stop-o[1].start
    best=None
    for adj in np.linspace(0.90,1.12,23):     # procura a escala que dá o tamanho pedido depois de aparar
        sc=(target[n]/h if target[n] else targetw[n]/w)*adj; f=trim(c.frame(li,o,sc)[0])
        want=(target[n]+2) if target[n] else (targetw[n]+2); got=f.shape[0] if target[n] else f.shape[1]
        ok=(got==want) and (n not in('q','used','blank') or f.shape[1]==16)
        if ok: best=(f,sc); break
    if best is None: f=trim(c.frame(li,o,(target[n]/h if target[n] else targetw[n]/w))[0]); best=(f,0)
    out[n]=best[0]; print(n,best[0].shape[:2],'escala',round(best[1],4))
pickle.dump(out,open('items.pkl','wb'))
W=sum(f.shape[1]+3 for f in out.values()); H=max(f.shape[0] for f in out.values()); sh=Image.new('RGBA',(W,H),(110,162,242,255)); x=0
for f in out.values(): sh.alpha_composite(Image.fromarray(f,'RGBA'),(x,H-f.shape[0])); x+=f.shape[1]+3
sh.resize((W*7,H*7),Image.NEAREST).save('preview_items.png'); print(sh.size)
