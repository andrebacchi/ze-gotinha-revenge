import sys, json, base64, io, pickle
from PIL import Image
import numpy as np, scipy.ndimage as ndi
K=(11,16,48)
def load(path):
    a=np.asarray(Image.open(path).convert('RGB')).astype(float); r,g,b=a[...,0],a[...,1],a[...,2]
    bg=(r>170)&(g<110)&(b>170)&(np.abs(r-b)<60); fg=~bg; lum=0.3*r+0.59*g+0.11*b
    dark=fg&((lum<30)|((r>g+25)&(b>g+25)&(lum<150))); lab,n=ndi.label(fg)
    return dict(a=a,fg=fg,lum=lum,dark=dark,lab=lab,n=n,sizes=ndi.sum(fg,lab,range(1,n+1)),cents=ndi.center_of_mass(fg,lab,range(1,n+1)))
def phone(S,ids):
    """largura do celular grande (faixa de baixo do maior componente), em pixels da fonte"""
    main=max(ids,key=lambda k:S['sizes'][k-1]); mm=S['lab']==main; ys,xs=np.nonzero(mm); h=ys.max()-ys.min()+1
    band=mm[ys.max()-int(0.12*h):ys.max()+1]; xb=np.nonzero(band.any(0))[0]; return xb.max()-xb.min()+1
old=load('boss.png'); H,W=old['a'].shape[:2]
ids_old=[k+1 for k in range(old['n']) if old['sizes'][k]>40 and W//4<=old['cents'][k][1]<W//2 and H//2<=old['cents'][k][0]<H]   # quadro tired1
pw_old=phone(old,ids_old)*0.145
new=load('boss_hurt.png'); H2,W2=new['a'].shape[:2]
# paleta: a mesma do sprite já instalado, lida da folha pronta
sheet_old=np.asarray(Image.open('boss_sheet.png').convert('RGBA')); cols=np.unique(sheet_old[sheet_old[...,3]>0][:,:3],axis=0); pal=np.array([c for c in cols if tuple(c)!=K]).astype(float)
extra=np.array([[250,230,40],[255,255,255]]); pal=np.vstack([pal,extra]); print('cores',len(pal))
cls=((new['a'][...,None,:]-pal[None,None])**2).sum(-1).argmin(-1)
frames=[]
for i,nm in enumerate(['hurt1','hurt2']):
    ids=[k+1 for k in range(new['n']) if new['sizes'][k]>60 and i*W2//2<=new['cents'][k][1]<(i+1)*W2//2]
    SC=pw_old/phone(new,ids)
    m=np.isin(new['lab'],ids); ys,xs=np.nonzero(m); o=(slice(ys.min(),ys.max()+1),slice(xs.min(),xs.max()+1)); m=m[o]
    main=max(ids,key=lambda k:new['sizes'][k-1]); mm=(new['lab'][o]==main)
    dk=new['dark'][o]&m; col=m&~dk; inner=ndi.binary_fill_holes(col); h,w=m.shape; nh,nw=round(h*SC),round(w*SC)
    ds=lambda x: np.asarray(Image.fromarray((x*255).astype(np.uint8)).resize((nw,nh),Image.BOX)).astype(float)/255
    I=ds(inner); D=ds(dk&inner); votes=np.stack([ds(col&(cls[o]==k)) for k in range(len(pal))],-1)
    body=I>=0.5; out=np.zeros((nh+2,nw+2,4),np.uint8)
    for y in range(nh):
        for x in range(nw):
            if body[y,x]: out[y+1,x+1]=(*K,255) if D[y,x]/max(I[y,x],1e-6)>0.5 else (*pal[votes[y,x].argmax()].astype(int),255)
    bm=np.zeros((nh+2,nw+2),bool); bm[1:-1,1:-1]=body
    ring=ndi.binary_dilation(bm,structure=ndi.generate_binary_structure(2,1))&~bm; out[ring]=(*K,255)
    mys,mxs=np.nonzero(mm); pb=mys.max()+1; band=mm[int(pb-0.12*(mys.max()-mys.min())):pb]; xb=np.nonzero(band.any(0))[0]; pcx=(xb.min()+xb.max())/2
    frames.append(dict(name=nm,img=out,ax=pcx*SC+1,base=pb*SC+1)); print(nm,'escala',round(SC,4),out.shape[:2],'ax',round(pcx*SC+1,1),'base',round(pb*SC+1,1))
allf=pickle.load(open('boss_frames.pkl','rb'))+frames; names=[f['name'] for f in allf]
half=max(max(int(np.ceil(f['ax'])) for f in allf), max(f['img'].shape[1]-int(np.floor(f['ax'])) for f in allf))+1; CW=half*2
up=max(int(np.ceil(f['base'])) for f in allf)+1; down=max(f['img'].shape[0]-int(np.floor(f['base'])) for f in allf)+1; CH=up+down; BASE=up
sheet=Image.new('RGBA',(CW*len(allf),CH),(0,0,0,0))
for i,f in enumerate(allf): sheet.alpha_composite(Image.fromarray(f['img'],'RGBA'),(i*CW+half-int(round(f['ax'])),BASE-int(round(f['base']))))
bio=io.BytesIO(); sheet.save(bio,'PNG',optimize=True)
json.dump({'cw':CW,'ch':CH,'base':BASE,'names':names,'data':'data:image/png;base64,'+base64.b64encode(bio.getvalue()).decode()},open('boss_art2.json','w'))
print('cell',CW,CH,'base',BASE,'bytes',len(bio.getvalue()),names)
bgc=Image.new('RGBA',(CW*4,CH),(110,162,242,255)); bgc.alpha_composite(sheet.crop((5*CW,0,7*CW,CH)),(0,0)); bgc.alpha_composite(sheet.crop((8*CW,0,10*CW,CH)),(2*CW,0))
bgc.resize((bgc.width*4,bgc.height*4),Image.NEAREST).save('preview_hurt.png')
