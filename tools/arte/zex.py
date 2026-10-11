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
n=Sheet('sheet.png'); b=Sheet('big.png'); scn=28/356; scb=scn*n.headw(4)[0]/b.headw(4)[0]
x=SN('ze_x.png',5); y=SN('big_x.png',4)
hw_n=n.headw(4)[0]; print('cabeça ref normal',hw_n,'nova',[x.headw(i)[0] for i in range(5)],'| ref bombado',b.headw(4)[0],'nova',[y.headw(i)[0] for i in range(4)])
sx=scn*hw_n/x.headw(0)[0]; sy=scb*b.headw(4)[0]/y.headw(0)[0]; print('escalas',round(scn,4),round(sx,4),round(scb,4),round(sy,4))
FX=[x.frame(i,sx) for i in range(5)]; FX=[(deblue(f),ax,t,bt) for f,ax,t,bt in FX]; FY=[y.frame(i,sy) for i in range(4)]
pickle.dump((FX,FY),open('zex.pkl','wb'))
for nm,fr in (('n',FX),('b',FY)):
    print(nm,[(f.shape[:2],round(ax,1)) for f,ax,t,bt in fr])
    Z=10; W=sum(f.shape[1]+3 for f,*_ in fr); H=max(f.shape[0] for f,*_ in fr); sh=Image.new('RGBA',(W,H),(110,162,242,255)); xx=0
    for f,*_ in fr: sh.alpha_composite(Image.fromarray(f,'RGBA'),(xx,H-f.shape[0])); xx+=f.shape[1]+3
    sh=sh.resize((W*Z,H*Z),Image.NEAREST); 
    from PIL import ImageDraw; d=ImageDraw.Draw(sh)
    for r in range(0,H,5): d.line([(0,(H-r)*Z),(W*Z,(H-r)*Z)],fill=(0,0,0,60)); d.text((2,(H-r)*Z-11),str(r),fill=(0,0,0,255))
    sh.save('zex_%s.png'%nm)
