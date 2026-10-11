import sys, pickle, json, base64, io, numpy as np, scipy.ndimage as ndi
from PIL import Image
from proc2 import Sheet, PAL, NAMES
FACT=float(sys.argv[1]) if len(sys.argv)>1 else 1.06
class S4(Sheet):
    def __init__(s,path):
        im=Image.open(path).convert('RGB'); s.a=a=np.asarray(im).astype(float); r,g,b=a[...,0],a[...,1],a[...,2]
        bg=(r>170)&(g<110)&(b>170); fg=~bg; s.lab,n=ndi.label(fg); sizes=ndi.sum(fg,s.lab,range(1,n+1)); objs=ndi.find_objects(s.lab)
        c=[(i+1,o) for i,(z,o) in enumerate(zip(sizes,objs)) if z>20000]; c.sort(key=lambda t:t[1][1].start); s.comps=c; s.lum=0.3*r+0.59*g+0.11*b
    def frame_edit(s,idx,sc,edits,sc0):
        """edits: lista de (cor, [(linha, x0, x1)]) em coordenadas da grade reduzida com escala sc0 (1px de margem)."""
        m,red,dark,blue,light,shade=[x.copy() for x in s.masks(idx)]
        for col,cells in edits:
            for y,x0,x1 in cells:
                ys=slice(int((y-1)/sc0),int(np.ceil(y/sc0))); xs=slice(int((x0-1)/sc0),int(np.ceil(x1/sc0)))
                reg=np.zeros_like(m); reg[ys,xs]=True
                if col=='W': conv=reg&(shade|blue); light|=conv; blue&=~conv; shade&=~reg
                else: conv=reg&light; shade|=conv
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
n=Sheet('sheet.png'); b=Sheet('big.png'); r=S4('run_b.png')
sc0=(28/356)*n.headw(4)[0]/r.headw(0)[0]; sc=sc0*FACT; scb=(28/356)*n.headw(4)[0]/b.headw(4)[0]
EA=[('S',[(16,5,8),(17,4,8),(18,4,6),(19,4,7),(20,5,6),(21,5,6),(22,5,7),(23,6,6)])]
EB=[('S',[(16,25,26),(17,20,21),(17,25,27),(18,20,22),(18,26,27),(19,20,24),(20,22,24)]),
    ('W',[(25,9,10),(26,7,10),(27,3,11),(28,2,12),(29,2,4),(30,2,4)]),
    ('S',[(24,15,17),(25,15,19),(26,15,19),(27,16,20),(28,18,20),(29,18,20),(30,18,21),(31,19,21),(31,24,26),(32,20,24),(33,21,23)])]
EP2=[('S',[(25,10,12),(26,9,12),(27,10,13),(28,10,13),(29,9,12),(30,8,11),(31,9,10),(32,9,9),(33,8,10),(34,8,12)]),
     ('W',[(28,5,7),(29,5,6),(30,4,6),(31,4,6),(32,5,6)])]
run=[r.frame_edit(0,sc,EA,sc0),r.frame_edit(1,sc,[],sc0),r.frame_edit(0,sc,EB,sc0),r.frame_edit(1,sc,EP2,sc0)]
fr=run+[b.frame(i,scb) for i in range(4,8)]; idle=fr[4]
print('alturas',[f.shape[0] for f,_,_,_ in fr],'larguras',[f.shape[1] for f,_,_,_ in fr])
half=max(max(int(np.ceil(ax)) for _,ax,_,_ in fr), max(f.shape[1]-int(np.floor(ax)) for f,ax,_,_ in fr))+1; CW=half*2
CH=max(bt+2 for f,ax,t,bt in fr)+1; BASE=CH-1; idle_top=BASE-(idle[3]+2)+idle[2]
sheet=Image.new('RGBA',(CW*8,CH),(0,0,0,0))
for i,(f,ax,t,bt) in enumerate(fr):
    x0=i*CW+half-int(round(ax)); y0=BASE-(bt+2) if NAMES[i] not in('jump','fall') else idle_top-t; y0=max(0,min(CH-f.shape[0],y0))
    sheet.alpha_composite(Image.fromarray(f,'RGBA'),(x0,y0))
buf=io.BytesIO(); sheet.save(buf,'PNG',optimize=True); sheet.save('ze_b2.png')
json.dump({'cw':CW,'ch':CH,'base':BASE,'data':'data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode()},open('ze_b2.json','w'))
print('cell',CW,CH,'base',BASE,len(buf.getvalue()))
bgc=Image.new('RGBA',sheet.size,(110,162,242,255)); bgc.alpha_composite(sheet); bgc.resize((sheet.width*5,sheet.height*5),Image.NEAREST).save('preview4.png')
