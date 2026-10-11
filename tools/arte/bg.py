import numpy as np, scipy.ndimage as ndi, pickle, sys
from PIL import Image
from scipy.cluster.vq import kmeans2
def load(path):
    a=np.asarray(Image.open(path).convert('RGB')).astype(float); r,g,b=a[...,0],a[...,1],a[...,2]
    bg=(r>180)&(g<90)&(b>180)&(np.abs(r-b)<70)
    fringe=(~bg)&((np.minimum(r,b)-g)>40)      # borda rosada da chave
    return a,bg,fringe
def reduce(a,bg,fringe,box,nw,nh,k=20,seed=1,thr=0.5,fcol=None):
    y0,y1,x0,x1=box; A=a[y0:y1,x0:x1]; fg=~bg[y0:y1,x0:x1]; good=fg&~fringe[y0:y1,x0:x1]
    px=A[good]; cent,_=kmeans2(px[::11],k,minit='++',seed=seed); pal=np.round(cent)
    cls=((A[...,None,:]-pal[None,None])**2).sum(-1).argmin(-1)
    ds=lambda m: np.asarray(Image.fromarray((m*255).astype(np.uint8)).resize((nw,nh),Image.BOX)).astype(float)/255
    F=ds(fg); V=np.stack([ds(good&(cls==q)) for q in range(k)],-1); out=np.zeros((nh,nw,4),np.uint8)
    idx=V.argmax(-1); out[...,:3]=pal[idx].astype(np.uint8); out[...,3]=np.where(F>=thr,255,0)
    FR=ds(fg&~good); weak=V.max(-1)<FR      # célula dominada pela borda: vira fio/sombra ou some
    if fcol is None: out[weak,3]=0
    else: out[weak,:3]=fcol
    return out
if __name__=='__main__':
    L={}
    a,bg,fr=load('bg_nat.png')
    L['hills']=reduce(a,bg,fr,(372,597,0,1672),640,86,k=8,seed=2)
    L['bush']=reduce(a,bg,fr,(648,912,0,1672),334,53,k=14,seed=3,fcol=(8,72,56))
    lab,n=ndi.label(ndi.binary_dilation(~bg[:340],iterations=3)); objs=ndi.find_objects(lab); cl=[]
    for o in sorted(objs,key=lambda o:o[1].start):
        h,w=o[0].stop-o[0].start,o[1].stop-o[1].start
        if w<60: continue
        cl.append(reduce(a,bg,fr,(o[0].start,o[0].stop,o[1].start,o[1].stop),round(w*.17),round(h*.17),k=5,seed=4))
    print('nuvens',[c.shape[:2] for c in cl]); L['clouds']=cl
    a,bg,fr=load('bg_town.png')
    L['townA']=reduce(a,bg,fr,(30,402,0,1983),576,108,k=28,seed=5,thr=0.42,fcol=(62,72,128))
    L['townB']=reduce(a,bg,fr,(500,764,0,1983),576,77,k=28,seed=6,thr=0.42,fcol=(62,72,128))
    for k_,v in L.items():
        if k_!='clouds': print(k_,v.shape[:2]); Image.fromarray(v,'RGBA').save('bg_%s.png'%k_)
    pickle.dump(L,open('bg.pkl','wb'))
