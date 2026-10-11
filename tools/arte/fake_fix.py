import pickle, numpy as np, scipy.ndimage as ndi
from enemy import pack
fr=pickle.load(open('fake_frames.pkl','rb')); A=fr[1]['img'].copy(); B=fr[0]['img']
Kc=(11,16,48); C=(240,234,204,255); W=(251,252,251,255); K=(*Kc,255)
isK=lambda p: p[3] and tuple(int(v) for v in p[:3])==Kc
def wingcol(p):
    r,g,b=int(p[0]),int(p[1]),int(p[2]); return p[3] and ((r>240 and g>240 and b>240) or (b>r+12 and b>200))
def px(f,c,pts):
    for y,x in pts: f[y,x]=c
# 1) rosto mais limpo na página (olhos semicerrados e sonsos)
for y in range(7,11):
    for x in range(14,22): A[y,x]=C
for y in range(7,10):
    for x in range(22,26): A[y,x]=C
px(A,K,[(7,15),(7,16),(8,17),(8,18),(8,21),(7,22),(7,23),(7,24)])
px(A,W,[(8,15),(8,16),(9,15),(9,16),(9,17),(9,18),(8,22),(8,23),(8,24),(9,21),(9,22),(9,23),(9,24)])
px(A,K,[(9,17),(9,22)])
# 2) separa corpo (página, nariz, folha) das asas no quadro de asas para baixo
H,Wd=A.shape[:2]; PAD=4
def layer(): return np.zeros((H+PAD,Wd,4),np.uint8)
body=layer(); wdown=layer(); wup=layer()
for y in range(H):
    for x in range(Wd):
        p=A[y,x]
        if not p[3]: continue
        wing=wingcol(p) and ((x<=10 and y>=8) or (x>=27 and y>=12))
        if wing: wdown[y+PAD,x]=p
        elif not isK(p) or (11<=x<=25 and 2<=y<=19): body[y+PAD,x]=p      # mantém só o preto de dentro da página
# 3) asas para cima vêm do outro quadro, deslocadas para encaixar nesta página
DX,DY=2,-3
for y in range(B.shape[0]):
    for x in range(B.shape[1]):
        p=B[y,x]
        if wingcol(p) and y<=11 and (x<=8 or x>=25):
            yy,xx=y+DY+PAD,x+DX
            if 0<=yy<H+PAD and 0<=xx<Wd: wup[yy,xx]=p
def compose(wings):
    out=wings.copy(); m=body[...,3]>0; out[m]=body[m]
    solid=ndi.binary_fill_holes(out[...,3]>0)
    hole=solid&~(out[...,3]>0); out[hole]=K
    big=np.zeros((H+PAD+2,Wd+2,4),np.uint8); big[1:-1,1:-1]=out; sm=np.zeros(big.shape[:2],bool); sm[1:-1,1:-1]=solid
    ring=ndi.binary_dilation(sm,structure=ndi.generate_binary_structure(2,1))&~sm; big[ring]=K
    ys,xs=np.nonzero(big[...,3]); return big[ys.min():ys.max()+1]
down=compose(wdown); up=compose(wup)
# âncora: centro da página; base: parte de baixo da página
page_cx=18+1+0.5; 
frames=[dict(name='fly1',img=up,ax=page_cx,base=up.shape[0]-1),dict(name='fly2',img=down,ax=page_cx,base=down.shape[0]-1)]
for f in fr[2:]: frames.append(dict(name=f['name'],img=f['img'],ax=f['img'].shape[1]/2,base=f['img'].shape[0]-1))
print([(f['name'],f['img'].shape[:2]) for f in frames]); pack(frames,'fake_art',zoom=7)
