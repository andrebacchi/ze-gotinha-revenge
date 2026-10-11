import pickle, numpy as np, scipy.ndimage as ndi, sys
from PIL import Image
from proc2 import Sheet, PAL
class SN(Sheet):
    def __init__(s,path,n):
        im=Image.open(path).convert('RGB'); s.a=a=np.asarray(im).astype(float); r,g,b=a[...,0],a[...,1],a[...,2]
        bg=(r>170)&(g<110)&(b>170); fg=ndi.binary_closing(~bg,iterations=2); s.lab,k=ndi.label(fg); sizes=ndi.sum(fg,s.lab,range(1,k+1)); objs=ndi.find_objects(s.lab)
        c=[(i+1,o) for i,(z,o) in enumerate(zip(sizes,objs)) if z>12000]; c.sort(key=lambda t:t[1][1].start); s.comps=c; s.lum=0.3*r+0.59*g+0.11*b
        s.lab=np.where(~bg,s.lab,0); assert len(c)==n,(len(c),[int(z) for z in sizes if z>3000])
    def masks(s,idx):
        li,o=s.comps[idx]; m=(s.lab[o]==li); sub=s.a[o]; L=s.lum[o]; R,G,B=sub[...,0],sub[...,1],sub[...,2]
        red=m&(R>150)&(G<120)&(B<120); bl=m&(B>150)&(R<90)&(G<140); lb,k=ndi.label(bl); blue=np.zeros_like(m)
        if k:
            sz=ndi.sum(bl,lb,range(1,k+1))
            for q in range(k):
                if sz[q]>700: blue|=(lb==q+1)
            blue=ndi.binary_dilation(blue,iterations=4)&m&~red
        dark=m&(L<95)&~red&~blue; light=m&~dark&~red&~blue; shade=light&(R<215)
        return m,red,dark,blue,light,shade
def deblue(f):
    f=f.copy(); m=(f[...,:3]==np.array(PAL['B'])).all(-1)&(f[...,3]>0); f[m]=(*PAL['S'],255); return f
