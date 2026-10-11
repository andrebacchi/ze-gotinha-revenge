# Retoques à mão (olhos, piscadela, seringa) e empacotamento das poses de vitória.
import pickle, numpy as np, json, io, base64
from PIL import Image
FR=pickle.load(open('zev.pkl','rb')); F=[f.copy() for f,*_ in FR]
C={'K':(11,16,48,255),'W':(255,255,255,255),'B':(51,192,238,255),'H':(183,231,243,255),'L':(215,233,238,255),'.':(0,0,0,0)}
def px(f,pts,c):
    for y,x in pts: f[y,x]=C[c]
# olhos: dois traços verticais de 3 px, como no resto do jogo
px(F[0],[(11,11),(12,11)],'W'); px(F[0],[(13,12)],'K')
px(F[1],[(9,13),(10,13),(11,13)],'W'); px(F[1],[(11,14)],'K')
px(F[3],[(10,16),(11,16)],'W'); px(F[3],[(12,17),(12,20)],'K')
# piscadela em "^"
px(F[2],[(15,10),(16,10),(16,11)],'W'); px(F[2],[(16,9),(15,10),(16,11)],'K')
px(F[5],[(14,16),(15,16),(15,17)],'W'); px(F[5],[(15,15),(14,16),(15,17)],'K'); px(F[5],[(13,20),(14,20)],'K')
SYR=["...K...","...K...","...K...","..KKK..",".KBBBK.",".KBHBK.",".KBBBK.",".KLLLK.","KKKKKKK","KWWWWWK",".KKKKK."]
def syringe(f,x0,y0,clear):
    (ya,yb,xa,xb)=clear; f[ya:yb,xa:xb]=C['.']
    for j,row in enumerate(SYR):
        for i,ch in enumerate(row):
            if ch!='.': f[y0+j,x0+i]=C[ch]
syringe(F[2],16,1,(0,12,16,23)); px(F[2],[(12,18),(12,19)],'W'); px(F[2],[(12,17),(12,20)],'K')
syringe(F[5],22,0,(0,11,22,30))
def anchor(f,jump):
    m=f[...,3]>0; ys,xs=np.nonzero(m)
    if jump: return xs.mean()
    lo=xs[ys>=ys.max()-2]; return (lo.min()+lo.max()+1)/2
def uri(im):
    b=io.BytesIO(); im.save(b,'PNG',optimize=True); return 'data:image/png;base64,'+base64.b64encode(b.getvalue()).decode()
out={}; names=['vprep','vjump','vpose']
for key,fr in (('vn',F[:3]),('vb',F[3:])):
    fr=[f[np.nonzero(f[...,3].any(1))[0].min():np.nonzero(f[...,3].any(1))[0].max()+1] for f in fr]; ax=[anchor(f,i==1) for i,f in enumerate(fr)]
    half=max(max(int(np.ceil(a)) for a in ax),max(f.shape[1]-int(np.floor(a)) for f,a in zip(fr,ax)))+1; CW=half*2; CH=max(f.shape[0] for f in fr)
    sh=Image.new('RGBA',(CW*3,CH),(0,0,0,0))
    for i,(f,a) in enumerate(zip(fr,ax)): sh.alpha_composite(Image.fromarray(np.ascontiguousarray(f),'RGBA'),(i*CW+half-int(round(a)),CH-f.shape[0]))
    out[key]=dict(cw=CW,ch=CH,base=CH-1,names=names,data=uri(sh)); print(key,CW,CH,[round(a,1) for a in ax],len(out[key]['data'])); sh.save('zev_sheet_%s.png'%key)
json.dump(out,open('zev_art.json','w'))
a=Image.open('zev_sheet_vn.png'); b=Image.open('zev_sheet_vb.png'); pv=Image.new('RGBA',(a.width+b.width+6,max(a.height,b.height)),(110,162,242,255)); pv.alpha_composite(a,(0,pv.height-a.height)); pv.alpha_composite(b,(a.width+6,pv.height-b.height)); pv.resize((pv.width*8,pv.height*8),Image.NEAREST).save('zev_prev2.png')
