# Poses de vitória (preparo, salto, pose final) do Zé nos dois tamanhos, na mesma escala das folhas anteriores.
import pickle, numpy as np, scipy.ndimage as ndi
from PIL import Image, ImageDraw
from proc2 import Sheet, PAL
from zexsn import SN
class SV(SN):
    def __init__(s,path):
        im=Image.open(path).convert('RGB'); s.a=a=np.asarray(im).astype(float); r,g,b=a[...,0],a[...,1],a[...,2]
        bg=(r>170)&(g<110)&(b>170); fg=ndi.binary_closing(~bg,iterations=2); s.lab,k=ndi.label(fg); sizes=ndi.sum(fg,s.lab,range(1,k+1)); objs=ndi.find_objects(s.lab)
        c=[(i+1,o) for i,(z,o) in enumerate(zip(sizes,objs)) if z>12000]; c.sort(key=lambda t:((t[1][0].start+t[1][0].stop)//2//(im.height//2),t[1][1].start)); s.comps=c; s.lum=0.3*r+0.59*g+0.11*b
        s.lab=np.where(~bg,s.lab,0); assert len(c)==6,len(c)
    def head(s,idx):   # largura da cabeça: maior largura contínua a partir do topo, na coluna da ponta
        m=s.masks(idx)[0]; ys,xs=np.nonzero(m); best=0
        for y in range(ys.min(),ys.max()):
            row=np.nonzero(m[y])[0]; 
            if len(row)==0: continue
            runs=np.split(row,np.nonzero(np.diff(row)>1)[0]+1); w=max(len(r) for r in runs); best=max(best,w) if y<ys.min()+(ys.max()-ys.min())*.45 else best
        return best
if __name__=='__main__':
    n=Sheet('sheet.png'); b=Sheet('big.png'); scn=28/356; hn=n.headw(4)[0]; hb=b.headw(4)[0]; scb=scn*hn/hb
    v=SV('ze_vit.png'); print('cabeça ref',hn,hb,'| nova',[v.head(i) for i in range(6)], [ (o[0].stop-o[0].start,o[1].stop-o[1].start) for _,o in v.comps])
    sc=scn*hn/172; print('escala',round(sc,4))
    FR=[v.frame(i,sc) for i in range(6)]; pickle.dump(FR,open('zev.pkl','wb'))
    print([(f.shape[:2],round(ax,1),t,bt) for f,ax,t,bt in FR])
    Z=12; W=sum(f.shape[1]+3 for f,*_ in FR); H=max(f.shape[0] for f,*_ in FR); sh=Image.new('RGBA',(W,H),(110,162,242,255)); xx=0
    for f,*_ in FR: sh.alpha_composite(Image.fromarray(f,'RGBA'),(xx,H-f.shape[0])); xx+=f.shape[1]+3
    sh=sh.resize((W*Z,H*Z),Image.NEAREST); d=ImageDraw.Draw(sh)
    for r in range(0,H,5): d.line([(0,(H-r)*Z),(W*Z,(H-r)*Z)],fill=(0,0,0,50)); d.text((2,(H-r)*Z-11),str(r),fill=(0,0,0,255))
    for c in range(0,W,5): d.line([(c*Z,0),(c*Z,H*Z)],fill=(0,0,0,30)); d.text((c*Z+2,2),str(c),fill=(0,0,0,255))
    sh.save('zev_prev.png'); print(sh.size)
