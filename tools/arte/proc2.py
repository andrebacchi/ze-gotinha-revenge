import sys, json, base64, io
from PIL import Image
import numpy as np, scipy.ndimage as ndi
NAMES=['run1','run2','run3','run4','idle','jump','fall','throw']
PAL={'W':(255,255,255),'S':(176,208,250),'K':(11,16,48),'R':(226,59,78),'B':(47,123,255),'D':(28,84,200)}
class Sheet:
    def __init__(s,path):
        im=Image.open(path).convert('RGB'); s.a=a=np.asarray(im).astype(float); r,g,b=a[...,0],a[...,1],a[...,2]
        bg=(r>170)&(g<110)&(b>170); fg=~bg; s.lab,n=ndi.label(fg); sizes=ndi.sum(fg,s.lab,range(1,n+1)); objs=ndi.find_objects(s.lab)
        c=[(i+1,o) for i,(z,o) in enumerate(zip(sizes,objs)) if z>20000]; c.sort(key=lambda t:(t[1][0].start//(im.height//2),t[1][1].start)); s.comps=c
        s.lum=0.3*r+0.59*g+0.11*b
        assert len(c)==8, len(c)
    def masks(s,idx):
        li,o=s.comps[idx]; m=(s.lab[o]==li); sub=s.a[o]; L=s.lum[o]; R,G,B=sub[...,0],sub[...,1],sub[...,2]
        red=m&(R>150)&(G<120)&(B<120); dark=m&(L<95)&~red
        blue=m&~dark&~red&(B>150)&(R<135)&(B-R>90)
        light=m&~dark&~red&~blue; shade=light&(R<215)
        return m,red,dark,blue,light,shade
    def headw(s,idx=4):
        m=s.masks(idx)[0]; ys,xs=np.nonzero(m); h=ys.max()-ys.min(); top=ys.min()
        rows=[np.ptp(xs[ys==y])+1 for y in range(top,top+int(h*0.38))]; return max(rows), h+1
    def frame(s,idx,sc):
        m,red,dark,blue,light,shade=s.masks(idx)
        inner=ndi.binary_fill_holes(light|red|blue); h,w=m.shape; nh,nw=max(1,round(h*sc)),max(1,round(w*sc))
        ds=lambda x: np.asarray(Image.fromarray((x*255).astype(np.uint8)).resize((nw,nh),Image.BOX)).astype(float)/255
        I,D,Rr,Sh,Li,Bl=ds(inner),ds(dark&inner),ds(red),ds(shade),ds(light),ds(blue)
        body=I>=0.5; out=np.zeros((nh+2,nw+2,4),np.uint8)
        for y in range(nh):
            for x in range(nw):
                if not body[y,x]: continue
                i=max(I[y,x],1e-6); c='W'
                if Rr[y,x]/i>0.30: c='R'
                elif D[y,x]/i>0.46: c='K'
                elif Bl[y,x]/i>0.45: c='B'
                elif Sh[y,x]>0.5*max(Li[y,x],1e-6): c='S'
                out[y+1,x+1]=(*PAL[c],255)
        bm=np.zeros((nh+2,nw+2),bool); bm[1:-1,1:-1]=body
        ring=ndi.binary_dilation(bm,structure=ndi.generate_binary_structure(2,1))&~bm; out[ring]=(*PAL['K'],255)
        ys,xs=np.nonzero(bm); top,bot=ys.min(),ys.max(); hx=xs[ys<=top+int((bot-top)*0.36)]; ax=(hx.min()+hx.max())/2
        return out,ax,int(top),int(bot)
def pack(sh,sc,name):
    fr=[sh.frame(i,sc) for i in range(8)]; idle=fr[4]
    half=max(max(int(np.ceil(ax)) for _,ax,_,_ in fr), max(f.shape[1]-int(np.floor(ax)) for f,ax,_,_ in fr))+1; CW=half*2
    CH=max(bt+2 for f,ax,t,bt in fr)+1; BASE=CH-1; idle_top=BASE-(idle[3]+2)+idle[2]
    sheet=Image.new('RGBA',(CW*8,CH),(0,0,0,0)); meta=[]
    for i,(f,ax,t,bt) in enumerate(fr):
        x0=i*CW+half-int(round(ax)); y0=BASE-(bt+2) if NAMES[i] not in('jump','fall') else idle_top-t; y0=max(0,min(CH-f.shape[0],y0))
        sheet.alpha_composite(Image.fromarray(f,'RGBA'),(x0,y0)); meta.append((NAMES[i],f.shape[1],f.shape[0]))
    buf=io.BytesIO(); sheet.save(buf,'PNG',optimize=True); sheet.save(name+'.png')
    json.dump({'cw':CW,'ch':CH,'base':BASE,'data':'data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode()},open(name+'.json','w'))
    print(name,'cell',CW,CH,'base',BASE,'bytes',len(buf.getvalue()),meta); return sheet,CW,CH
if __name__=='__main__':
    n=Sheet('sheet.png'); b=Sheet('big.png'); scn=28/356
    hn,hhn=n.headw(); hb,hhb=b.headw(); print('cabeça normal',hn,'alt',hhn,'| bombado',hb,'alt',hhb)
    for i,(li,o) in enumerate(b.comps): print(NAMES[i],'h',o[0].stop-o[0].start,'w',o[1].stop-o[1].start, 'blue px',int(b.masks(i)[3].sum()))
    scb=scn*hn/hb; print('escala normal',round(scn,4),'bombado',round(scb,4))
    s1,cw1,ch1=pack(n,scn,'ze_n'); s2,cw2,ch2=pack(b,scb,'ze_b'); s3,cw3,ch3=pack(b,scn,'ze_b_same')
    Z=5; W=max(s1.width,s2.width,s3.width); out=Image.new('RGBA',(W,ch1+ch2+ch3+8),(110,162,242,255)); out.alpha_composite(s1,(0,0)); out.alpha_composite(s2,(0,ch1+4)); out.alpha_composite(s3,(0,ch1+ch2+8))
    out.resize((out.width*Z,out.height*Z),Image.NEAREST).save('preview2.png'); print(out.size)
