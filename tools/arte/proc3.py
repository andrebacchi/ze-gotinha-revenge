import sys, json, base64, io, pickle
from PIL import Image
import numpy as np, scipy.ndimage as ndi
from scipy.cluster.vq import kmeans2
K=(11,16,48)
class Color:
    def __init__(s,path,k=9,seed=3):
        im=Image.open(path).convert('RGB'); s.a=a=np.asarray(im).astype(float); r,g,b=a[...,0],a[...,1],a[...,2]
        s.bg=(r>170)&(g<110)&(b>170)&(np.abs(r-b)<60); fg=~s.bg; s.lab,n=ndi.label(fg); sizes=ndi.sum(fg,s.lab,range(1,n+1)); objs=ndi.find_objects(s.lab)
        s.comps=[(i+1,o,int(z)) for i,(z,o) in enumerate(zip(sizes,objs)) if z>300]
        s.lum=0.3*r+0.59*g+0.11*b; s.dark=fg&((s.lum<75)|((r>g+25)&(b>g+25)))   # contorno e franja misturada com o fundo
        px=a[fg&~s.dark]; np.random.seed(seed); cent,_=kmeans2(px[::7],k,minit='++',seed=seed); pal=np.round(cent).astype(int)
        s.pal=np.array([p for p in pal if not (p[0]>p[1]+20 and p[2]>p[1]+20)])   # descarta a mistura com o fundo magenta
        d=((a[...,None,:]-s.pal[None,None])**2).sum(-1); s.cls=d.argmin(-1)
    def frame(s,li,o,sc,anchor_cls=None):
        m=(s.lab[o]==li); dark=s.dark[o]&m; col=m&~dark; cls=s.cls[o]
        inner=ndi.binary_fill_holes(col); h,w=m.shape; nh,nw=max(1,round(h*sc)),max(1,round(w*sc))
        ds=lambda x: np.asarray(Image.fromarray((x*255).astype(np.uint8)).resize((nw,nh),Image.BOX)).astype(float)/255
        I=ds(inner); D=ds(dark&inner); votes=np.stack([ds(col&(cls==k)) for k in range(len(s.pal))],-1)
        body=I>=0.5; out=np.zeros((nh+2,nw+2,4),np.uint8)
        for y in range(nh):
            for x in range(nw):
                if not body[y,x]: continue
                if D[y,x]/max(I[y,x],1e-6)>0.5: out[y+1,x+1]=(*K,255)
                else: out[y+1,x+1]=(*s.pal[votes[y,x].argmax()],255)
        bm=np.zeros((nh+2,nw+2),bool); bm[1:-1,1:-1]=body
        ring=ndi.binary_dilation(bm,structure=ndi.generate_binary_structure(2,1))&~bm; out[ring]=(*K,255)
        ys,xs=np.nonzero(bm); ax=None
        if anchor_cls is not None:
            am=col&np.isin(cls,anchor_cls); am[:, int(w*0.6):]=False
            if am.sum()>50: yy,xx=np.nonzero(am); ax=(xx.min()+xx.max())/2*sc+1
        return out,ax,int(ys.min()),int(ys.max())
if __name__=='__main__':
    c=Color('jac.png'); print('paleta',[tuple(int(v) for v in p) for p in c.pal])
    pickle.dump(c.pal,open('jac_pal.pkl','wb'))
    sc=float(sys.argv[1]) if len(sys.argv)>1 else 0.127
    big=sorted([x for x in c.comps if x[2]>20000],key=lambda t:(t[1][0].start//512,t[1][1].start)); small=sorted([x for x in c.comps if x[2]<=20000],key=lambda t:t[1][1].start)
    red=[i for i,p in enumerate(c.pal) if p[0]>200 and p[1]<80 and p[2]<80]; print('classe vermelha',red)
    fr=[c.frame(li,o,sc,red) for li,o,_ in big]+[c.frame(li,o,sc) for li,o,_ in small]
    for f,ax,t,bt in fr: print(f.shape[:2],'ax',None if ax is None else round(ax,1),'top',t,'bot',bt)
    W=sum(f[0].shape[1]+2 for f in fr); H=max(f[0].shape[0] for f in fr); sheet=Image.new('RGBA',(W,H),(110,162,242,255)); x=0
    for f,ax,t,bt in fr: sheet.alpha_composite(Image.fromarray(f,'RGBA'),(x,H-f.shape[0])); x+=f.shape[1]+2
    sheet.resize((W*4,H*4),Image.NEAREST).save('preview_jac.png'); print(sheet.size)
    pickle.dump(fr,open('jac_frames.pkl','wb'))
