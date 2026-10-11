import numpy as np, scipy.ndimage as ndi, json, base64, io
from PIL import Image
from scipy.cluster.vq import kmeans2
K=(11,16,48)
class Sheet:
    def __init__(s,path,bg='magenta',k=14,seed=3,dark_lum=45):
        a=np.asarray(Image.open(path).convert('RGB')).astype(float); s.a=a; r,g,b=a[...,0],a[...,1],a[...,2]; lum=0.3*r+0.59*g+0.11*b; s.lum=lum
        if bg=='magenta': s.bg=(r>170)&(g<110)&(b>170)&(np.abs(r-b)<70); fr=(r>g+30)&(b>g+30)&(np.abs(r-b)<70)
        else: s.bg=(g>170)&(r<120)&(b<120); fr=(g>r+60)&(g>b+60)
        s.fg=~s.bg; s.fringe=s.fg&fr; s.dark=s.fg&((lum<dark_lum)|(fr&(lum<150)))
        lab,n=ndi.label(ndi.binary_dilation(s.fg,iterations=6)); s.lab=lab
        objs=ndi.find_objects(lab); s.boxes=[]
        for i,o in enumerate(objs):
            m=(lab[o]==i+1)&s.fg[o]
            if m.sum()>400:
                ys,xs=np.nonzero(m); s.boxes.append((o[0].start+ys.min(),o[0].start+ys.max()+1,o[1].start+xs.min(),o[1].start+xs.max()+1,i+1))
        px=a[s.fg&~s.dark&~s.fringe]; np.random.seed(seed); cent,_=kmeans2(px[::7],k,minit='++',seed=seed); s.pal=np.round(cent)
        s.cls=((a[...,None,:]-s.pal[None,None])**2).sum(-1).argmin(-1)
    def obj(s,box,scale=None,w=None,h=None,outline=True,merge=None):
        """sprite com contorno regenerado. merge: lista de caixas a unir"""
        y0,y1,x0,x1=box[:4]; o=(slice(y0,y1),slice(x0,x1)); m=s.fg[o].copy()
        if len(box)>4: m&=(s.lab[o]==box[4])
        ys,xs=np.nonzero(m); o=(slice(y0+ys.min(),y0+ys.max()+1),slice(x0+xs.min(),x0+xs.max()+1)); m=m[ys.min():ys.max()+1,xs.min():xs.max()+1]
        H,W=m.shape
        if scale is None: scale=(w/W) if w else (h/H)
        nh,nw=max(1,round(H*scale)),max(1,round(W*scale))
        ds=lambda x: np.asarray(Image.fromarray((x*255).astype(np.uint8)).resize((nw,nh),Image.BOX)).astype(float)/255
        dk=s.dark[o]&m; col=m&~dk; inner=ndi.binary_fill_holes(col)
        I=ds(inner); D=ds(dk&inner); votes=np.stack([ds(col&(s.cls[o]==q)) for q in range(len(s.pal))],-1)
        body=I>=0.5; out=np.zeros((nh+2,nw+2,4),np.uint8)
        for y in range(nh):
            for x in range(nw):
                if body[y,x]: out[y+1,x+1]=(*K,255) if D[y,x]/max(I[y,x],1e-6)>0.55 else (*s.pal[votes[y,x].argmax()].astype(int),255)
        if outline:
            bm=np.zeros((nh+2,nw+2),bool); bm[1:-1,1:-1]=body
            ring=ndi.binary_dilation(bm,structure=ndi.generate_binary_structure(2,1))&~bm; out[ring]=(*K,255)
        return trim(out)
    def tile(s,y0,y1,x0,x1,nw=16,nh=16,alpha=False):
        """bloco de borda a borda: reduz a região e quantiza por maioria"""
        o=(slice(y0,y1),slice(x0,x1))
        ds=lambda x: np.asarray(Image.fromarray((x*255).astype(np.uint8)).resize((nw,nh),Image.BOX)).astype(float)/255
        fg=s.fg[o]&~s.fringe[o]; F=ds(fg); dk=s.dark[o]&s.fg[o]; D=ds(dk); col=fg&~dk
        votes=np.stack([ds(col&(s.cls[o]==q)) for q in range(len(s.pal))],-1); out=np.zeros((nh,nw,4),np.uint8)
        for y in range(nh):
            for x in range(nw):
                if alpha and F[y,x]<0.5: continue
                out[y,x]=(*K,255) if D[y,x]>0.5 else (*s.pal[votes[y,x].argmax()].astype(int),255)
        return out
def trim(f):
    ys,xs=np.nonzero(f[...,3]); return f[ys.min():ys.max()+1,xs.min():xs.max()+1]
def show(frames,name,zoom=8,bg=(110,162,242,255),gap=3):
    W=sum(f.shape[1]+gap for f in frames); H=max(f.shape[0] for f in frames); sh=Image.new('RGBA',(W,H),bg); x=0
    for f in frames: sh.alpha_composite(Image.fromarray(f,'RGBA'),(x,H-f.shape[0])); x+=f.shape[1]+gap
    sh.resize((W*zoom,H*zoom),Image.NEAREST).save(name)
def atlas(d,name):
    names=list(d); W=sum(f.shape[1]+1 for f in d.values()); H=max(f.shape[0] for f in d.values())
    at=Image.new('RGBA',(W,H),(0,0,0,0)); rects={}; x=0
    for n in names:
        f=d[n]; at.alpha_composite(Image.fromarray(f,'RGBA'),(x,0)); rects[n]=[x,0,int(f.shape[1]),int(f.shape[0])]; x+=f.shape[1]+1
    b=io.BytesIO(); at.save(b,'PNG',optimize=True)
    json.dump({'rects':rects,'data':'data:image/png;base64,'+base64.b64encode(b.getvalue()).decode()},open(name,'w')); print(name,at.size,len(b.getvalue()),'bytes')
    return rects
