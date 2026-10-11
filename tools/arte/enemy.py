import sys, json, base64, io, pickle
from PIL import Image
import numpy as np, scipy.ndimage as ndi
from scipy.cluster.vq import kmeans2
K=(11,16,48)
def process(path,names,target_h,k=10,seed=2,dark_lum=40,bgkind='magenta',ref=0,extra_pal=()):
    a=np.asarray(Image.open(path).convert('RGB')).astype(float); r,g,b=a[...,0],a[...,1],a[...,2]; H,W=a.shape[:2]; lum=0.3*r+0.59*g+0.11*b
    if bgkind=='magenta': bg=(r>170)&(g<110)&(b>170)&(np.abs(r-b)<60); fringe=(r>g+25)&(b>g+25)&(lum<150)
    elif bgkind=='yellow': bg=(r>200)&(g>200)&(b<120); fringe=(r>b+60)&(g>b+60)&(np.abs(r-g)<50)
    else: bg=(g>180)&(r<110)&(b<110); fringe=(g>r+60)&(g>b+60)&(lum<150)
    fg=~bg; dark=fg&((lum<dark_lum)|fringe); lab,n=ndi.label(fg); sizes=ndi.sum(fg,lab,range(1,n+1)); cents=ndi.center_of_mass(fg,lab,range(1,n+1))
    np.random.seed(seed); px=a[fg&~dark]; cent,_=kmeans2(px[::5],k,minit='++',seed=seed); pal=np.round(cent)
    pal=np.array([p for p in pal if not (bgkind=='magenta' and p[0]>p[1]+25 and p[2]>p[1]+25 and p[0]>120)]+[np.array(e,float) for e in extra_pal])
    cls=((a[...,None,:]-pal[None,None])**2).sum(-1).argmin(-1); N=len(names); frames=[]; SC=None
    order=[ref]+[i for i in range(N) if i!=ref]; res={}
    for i in order:
        ids=[q+1 for q in range(n) if sizes[q]>40 and i*W//N<=cents[q][1]<(i+1)*W//N]
        m=np.isin(lab,ids); ys,xs=np.nonzero(m); o=(slice(ys.min(),ys.max()+1),slice(xs.min(),xs.max()+1)); m=m[o]; h,w=m.shape
        if SC is None: SC=target_h/h
        dk=dark[o]&m; col=m&~dk; inner=ndi.binary_fill_holes(col); nh,nw=max(1,round(h*SC)),max(1,round(w*SC))
        ds=lambda x: np.asarray(Image.fromarray((x*255).astype(np.uint8)).resize((nw,nh),Image.BOX)).astype(float)/255
        I=ds(inner); D=ds(dk&inner); votes=np.stack([ds(col&(cls[o]==q)) for q in range(len(pal))],-1)
        body=I>=0.5; out=np.zeros((nh+2,nw+2,4),np.uint8)
        for y in range(nh):
            for x in range(nw):
                if body[y,x]: out[y+1,x+1]=(*K,255) if D[y,x]/max(I[y,x],1e-6)>0.5 else (*pal[votes[y,x].argmax()].astype(int),255)
        bm=np.zeros((nh+2,nw+2),bool); bm[1:-1,1:-1]=body
        ring=ndi.binary_dilation(bm,structure=ndi.generate_binary_structure(2,1))&~bm; out[ring]=(*K,255)
        res[i]=dict(name=names[i],img=out,ax=out.shape[1]/2,base=out.shape[0]-1)
    frames=[res[i] for i in range(N)]
    print('escala',round(SC,4),[(f['name'],f['img'].shape[:2]) for f in frames]); return frames
def pack(frames,name,zoom=6):
    half=max(max(int(np.ceil(f['ax'])) for f in frames), max(f['img'].shape[1]-int(np.floor(f['ax'])) for f in frames))+1; CW=half*2
    CH=max(f['img'].shape[0] for f in frames)+1; BASE=CH-1
    sheet=Image.new('RGBA',(CW*len(frames),CH),(0,0,0,0))
    for i,f in enumerate(frames): sheet.alpha_composite(Image.fromarray(f['img'],'RGBA'),(i*CW+half-int(round(f['ax'])),BASE-int(round(f['base']))-1))
    bio=io.BytesIO(); sheet.save(bio,'PNG',optimize=True)
    json.dump({'cw':CW,'ch':CH,'base':BASE,'names':[f['name'] for f in frames],'data':'data:image/png;base64,'+base64.b64encode(bio.getvalue()).decode()},open(name+'.json','w'))
    bgc=Image.new('RGBA',sheet.size,(110,162,242,255)); bgc.alpha_composite(sheet); bgc.resize((sheet.width*zoom,sheet.height*zoom),Image.NEAREST).save(name+'_prev.png')
    print(name,'cell',CW,CH,'base',BASE,'bytes',len(bio.getvalue()))
if __name__=='__main__':
    fr=process('boato.png',['walk1','walk2','stomp','debunk'],float(sys.argv[1]) if len(sys.argv)>1 else 18); pack(fr,'boato_art')
