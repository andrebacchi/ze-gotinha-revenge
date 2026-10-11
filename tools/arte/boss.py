import sys, json, base64, io, pickle
from PIL import Image
import numpy as np, scipy.ndimage as ndi
from scipy.cluster.vq import kmeans2
K=(11,16,48)
SC=float(sys.argv[1]) if len(sys.argv)>1 else 0.145
im=Image.open('boss.png').convert('RGB'); a=np.asarray(im).astype(float); r,g,b=a[...,0],a[...,1],a[...,2]; H,W=a.shape[:2]
bg=(r>170)&(g<110)&(b>170)&(np.abs(r-b)<60); fg=~bg; lum=0.3*r+0.59*g+0.11*b
dark=fg&((lum<30)|((r>g+25)&(b>g+25)&(lum<150)))     # contorno e franja misturada com o fundo
lab,n=ndi.label(fg); sizes=ndi.sum(fg,lab,range(1,n+1)); cents=ndi.center_of_mass(fg,lab,range(1,n+1)); objs=ndi.find_objects(lab)
np.random.seed(4); px=a[fg&~dark]; cent,_=kmeans2(px[::9],16,minit='++',seed=4); pal=np.round(cent).astype(int)
pal=np.array([p for p in pal if not (p[0]>p[1]+25 and p[2]>p[1]+25 and p[0]>120)]); print('paleta',[tuple(int(v) for v in p) for p in pal])
cls=((a[...,None,:]-pal[None,None])**2).sum(-1).argmin(-1)
names=['hover1','hover2','wind','throw','dive','tired1','tired2','ko']; frames=[]
for i,nm in enumerate(names):
    cx0,cy0=(i%4)*W//4,(i//4)*H//2
    ids=[k+1 for k in range(n) if sizes[k]>40 and cx0<=cents[k][1]<cx0+W//4 and cy0<=cents[k][0]<cy0+H//2]
    m=np.isin(lab,ids); ys,xs=np.nonzero(m); o=(slice(ys.min(),ys.max()+1),slice(xs.min(),xs.max()+1)); m=m[o]
    main=max(ids,key=lambda k:sizes[k-1]); mm=(lab[o]==main)
    dk=dark[o]&m; col=m&~dk; inner=ndi.binary_fill_holes(col); h,w=m.shape; nh,nw=round(h*SC),round(w*SC)
    ds=lambda x: np.asarray(Image.fromarray((x*255).astype(np.uint8)).resize((nw,nh),Image.BOX)).astype(float)/255
    I=ds(inner); D=ds(dk&inner); votes=np.stack([ds(col&(cls[o]==k)) for k in range(len(pal))],-1)
    body=I>=0.5; out=np.zeros((nh+2,nw+2,4),np.uint8)
    for y in range(nh):
        for x in range(nw):
            if body[y,x]: out[y+1,x+1]=(*K,255) if D[y,x]/max(I[y,x],1e-6)>0.5 else (*pal[votes[y,x].argmax()],255)
    bm=np.zeros((nh+2,nw+2),bool); bm[1:-1,1:-1]=body
    ring=ndi.binary_dilation(bm,structure=ndi.generate_binary_structure(2,1))&~bm; out[ring]=(*K,255)
    # âncoras em pixels da fonte, relativas ao recorte: centro do celular grande e linha de baixo dele (sem as chamas)
    L=lum[o]; darkish=mm&(L<110); rows=darkish.sum(1); wide=np.nonzero(rows>0.25*mm.any(0).sum())[0]; pb=wide.max()+1   # base do celular
    band=mm[int(pb-0.22*h):pb]; xs2=np.nonzero(band.any(0))[0]; pcx=(xs2.min()+xs2.max())/2
    if nm=='dive': mys,mxs=np.nonzero(mm); pcx=(mxs.min()+mxs.max())/2; pb=mys.max()+1
    frames.append(dict(name=nm,img=out,ax=pcx*SC+1,base=pb*SC+1)); print(nm,out.shape[:2],'ax',round(pcx*SC+1,1),'base',round(pb*SC+1,1))
pickle.dump(frames,open('boss_frames.pkl','wb'))
half=max(max(int(np.ceil(f['ax'])) for f in frames), max(f['img'].shape[1]-int(np.floor(f['ax'])) for f in frames))+1; CW=half*2
up=max(int(np.ceil(f['base'])) for f in frames)+1; down=max(f['img'].shape[0]-int(np.floor(f['base'])) for f in frames)+1; CH=up+down; BASE=up
sheet=Image.new('RGBA',(CW*8,CH),(0,0,0,0))
for i,f in enumerate(frames): sheet.alpha_composite(Image.fromarray(f['img'],'RGBA'),(i*CW+half-int(round(f['ax'])),BASE-int(round(f['base']))))
bio=io.BytesIO(); sheet.save(bio,'PNG',optimize=True); sheet.save('boss_sheet.png')
json.dump({'cw':CW,'ch':CH,'base':BASE,'names':names,'data':'data:image/png;base64,'+base64.b64encode(bio.getvalue()).decode()},open('boss_art.json','w'))
print('cell',CW,CH,'base',BASE,'bytes',len(bio.getvalue()))
bgc=Image.new('RGBA',sheet.size,(110,162,242,255)); bgc.alpha_composite(sheet)
from PIL import ImageDraw; d=ImageDraw.Draw(bgc); d.line([(0,BASE),(sheet.width,BASE)],fill=(255,0,0,255))
bgc.resize((sheet.width*3,sheet.height*3),Image.NEAREST).save('preview_boss.png'); print(bgc.size)
