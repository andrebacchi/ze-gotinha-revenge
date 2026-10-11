import pickle, numpy as np, scipy.ndimage as ndi
from PIL import Image
from proc3 import Color
old=Color('jac.png'); pal=pickle.load(open('jac_pal.pkl','rb'))
big=sorted([x for x in old.comps if x[2]>20000],key=lambda t:(t[1][0].start//512,t[1][1].start)); red_old=[i for i,p in enumerate(old.pal) if p[0]>200 and p[1]<80 and p[2]<80]
def sadw(c,li,o,red,cut=.6):
    m=(c.lab[o]==li)&~c.dark[o]&np.isin(c.cls[o],red); m[:,int(m.shape[1]*cut):]=False; ys,xs=np.nonzero(m); return xs.max()-xs.min()+1,(xs.min()+xs.max())/2,ys.min()
w_old=sadw(old,big[4][0],big[4][1],red_old)[0]
c=Color('jac_swim.png'); print('paleta nova',[tuple(int(v) for v in p) for p in c.pal]); print('paleta antiga',[tuple(int(v) for v in p) for p in pal])
c.pal=np.array(pal); c.cls=((c.a[...,None,:]-c.pal[None,None])**2).sum(-1).argmin(-1)
red=[i for i,p in enumerate(c.pal) if p[0]>200 and p[1]<80 and p[2]<80]
comps=sorted([x for x in c.comps if x[2]>20000],key=lambda t:t[1][1].start); print(len(comps))
w_new=[sadw(c,li,o,red,.72)[0] for li,o,_ in comps]; print('sela antiga',w_old,'nova',w_new)
sc=0.088; print('escala',round(sc,4)); out=[]
for li,o,_ in comps:
    f,ax,t,bt=c.frame(li,o,sc); w,cx,ty=sadw(c,li,o,red,.72); out.append((f,cx*sc+1,ty*sc+1,bt)); print(f.shape[:2],'sela x',round(cx*sc+1,1),'topo',round(ty*sc+1,1))
pickle.dump(out,open('jswim.pkl','wb'))
Z=8; W=sum(f.shape[1]+3 for f,*_ in out); H=max(f.shape[0] for f,*_ in out); sh=Image.new('RGBA',(W,H),(110,162,242,255)); x=0
for f,*_ in out: sh.alpha_composite(Image.fromarray(f,'RGBA'),(x,H-f.shape[0])); x+=f.shape[1]+3
sh.resize((W*Z,H*Z),Image.NEAREST).save('jswim_prev.png')
