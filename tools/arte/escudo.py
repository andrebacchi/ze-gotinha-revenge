# Escudo de imunidade: anel refeito pixel a pixel com as cores e o desenho da arte do André
# (a redução direta de um aro de 43 px para 5 px perde sombra, brilho e cruz). Estilhaços reduzidos da arte.
import numpy as np, scipy.ndimage as ndi, json, base64, io, math
from PIL import Image
K=(11,16,48,255); W=(255,255,255,255)
a=np.asarray(Image.open('escudo.png').convert('RGB')).astype(float); r,g,b=a[...,0],a[...,1],a[...,2]
bgm=(r>150)&(g<120)&(b>150); fg=~bgm; lum=.3*r+.59*g+.11*b; dark=fg&(lum<70)
# tons do aro medidos na arte (de dentro para fora)
def tone(d0,d1):
    cx,cy=211.5,351.0; px=[]
    for th in np.linspace(-2.6,-.5,60):   # metade de baixo, longe do brilho e da cruz
        for d in np.arange(d0,d1): px.append(a[int(cy-d*math.sin(th)),int(cx+d*math.cos(th))])
    return (*np.median(np.array(px),0).astype(int),255)
T_IN,T_MID,T_OUT=(4,238,218,255),(4,207,202,255),(4,178,196,255)   # medidos no perfil radial da arte
TEAL=(T_IN,T_MID,T_OUT); ECO=((145,234,246,255),W,(72,170,230,255)); PALE=(196,244,240,255)
S4=ndi.generate_binary_structure(2,1)
def outline(img):
    m=img[...,3]>0; ring=ndi.binary_dilation(m,structure=S4)&~m; img[ring]=K; return img
def ring(D,tc,cell,push=0,gaps=None,shine=None,sparks=(),cross=True,tones=TEAL,echo=None,refl=False,drops=None,dots=(),body=True):
    T_IN,T_MID,T_OUT=tones
    out=np.zeros((cell,cell,4),np.uint8); c=cell/2; R=D/2+push
    for y in range(cell):
        for x in range(cell):
            dx,dy=x+.5-c,y+.5-c; d=math.hypot(dx,dy); th=math.degrees(math.atan2(-dy,dx))
            if echo and R+echo[0]<=d<R+echo[0]+1 and any(abs((th-g+180)%360-180)<echo[1] for g in (0,90,180,270)): out[y,x]=ECO[0]   # arcos de eco
            if refl and R-tc-5<=d<R-tc-3 and (112<th<150 or 157<th<166): out[y,x]=W   # reflexo de bolha de sabão
            if not body or not(R-1-tc<=d<R-1): continue
            if gaps and any(abs((th-g+180)%360-180)<gaps[1] for g in gaps[0]): continue
            f=(d-(R-1-tc))/tc
            col=T_IN if f<1/tc else T_OUT if f>=1-1/tc else T_MID
            if tc==2: col=T_IN if f<.5 else T_OUT
            if shine is not None and abs((th-shine+180)%360-180)<21 and (f<.5 if tc==2 else 1/tc<=f<1-1/tc): col=W
            out[y,x]=col
    for (th,k) in sparks:   # faíscas: pontos brancos sobre o aro
        rr=R-1-tc+k+.5; x=int(c+rr*math.cos(math.radians(th))); y=int(c-rr*math.sin(math.radians(th)))
        if out[y,x,3]: out[y,x]=W
    if cross:   # cruz branca no alto, atravessada no aro
        cy=int(round(c-(R-1-tc/2))); x0=int(c)-3; y0=cy-3
        for yy in range(6):
            for xx in range(6):
                if 2<=xx<4 or 2<=yy<4: out[y0+yy,x0+xx]=W
        out[y0+3,x0+5]=out[y0+5,x0+3]=out[y0+5,x0+2]=PALE   # sombra clara da arte
    for th,rr in (drops or ()):   # gotinhas
        x=int(round(c+rr*math.cos(math.radians(th))-2.5)); y=int(round(c-rr*math.sin(math.radians(th))-2.5))
        for yy in range(5):
            for xx in range(5):
                if (xx in (0,4)) and (yy in (0,4)): continue
                out[y+yy,x+xx]=ECO[2] if yy==4 or xx==4 or (xx==3 and yy==3) else ECO[0]
        out[y+1,x+1]=out[y+1,x+2]=out[y+2,x+1]=W
    out=outline(out)
    for th,rr in dots: out[int(c-rr*math.sin(math.radians(th))),int(c+rr*math.cos(math.radians(th)))]=W
    return out
def shards(D,cell):
    # quadro 5 da arte, reduzido na mesma escala do anel
    x0,x1,y0,y1=1765,2160,165,545; sc=D/362; sub=fg[y0:y1,x0:x1]; col=sub&~dark[y0:y1,x0:x1]
    nw,nh=round((x1-x0)*sc),round((y1-y0)*sc)
    ds=lambda m: np.asarray(Image.fromarray((m*255).astype(np.uint8)).resize((nw,nh),Image.BOX)).astype(float)/255
    cov=ds(col); wh=ds(col&(lum[y0:y1,x0:x1]>215)); br=ds(col&(g[y0:y1,x0:x1]>215)&(lum[y0:y1,x0:x1]<=215))
    lab,_=ndi.label(ndi.binary_dilation(sub,iterations=2)); big=np.isin(lab,[i+1 for i,o in enumerate(ndi.find_objects(lab)) if (lab[o]==i+1).sum()>900]); bigc=ds(big&col)
    out=np.zeros((cell,cell,4),np.uint8); ox=(cell-nw)//2; oy=(cell-nh)//2-1
    for y in range(nh):
        for x in range(nw):
            if bigc[y,x]>=.42: out[oy+y,ox+x]=W if wh[y,x]>.3*cov[y,x] else T_IN if br[y,x]>.45*cov[y,x] else T_OUT
    out=outline(out)
    sl,ns=ndi.label((cov-bigc>=.1))   # faíscas soltas: um ponto branco cada, sem contorno
    for cyx in ndi.center_of_mass(np.ones_like(sl),sl,range(1,ns+1)):
        y,x=int(cyx[0]),int(cyx[1])
        if not out[oy+y,ox+x,3]: out[oy+y,ox+x]=W
    return out
def conj(D,tc,cell):
    sp=[[(200,0),(310,tc-1),(20,1 if tc>2 else 0)],[(165,tc-1),(255,0),(335,1 if tc>2 else 0)],[(215,1 if tc>2 else 0),(290,0),(160,tc-1)]]
    idle=[ring(D,tc,cell,shine=s,sparks=q) for s,q in zip((132,None,48),sp)]
    # no quadro do meio o brilho passa pelo alto, dos dois lados da cruz
    m=ring(D,tc,cell,shine=90,sparks=sp[1]); idle[1]=m
    G6=([0,60,120,180,240,300],9 if D<46 else 7.5)
    return idle+[ring(D,tc,cell,push=2,gaps=G6,sparks=[(100,0)]),ring(D,tc,cell,push=5,gaps=(G6[0],G6[1]+3),cross=True),shards(D,cell)]
def eco(D,cell):
    tc=3; R=D/2; G6=([30,90,150,210,270,330],13)
    idle=[ring(D,tc,cell,cross=False,tones=ECO,echo=e,refl=True) for e in ((3,24),(5,22),(7,13))]
    pop=ring(D,tc,cell,push=2,gaps=G6,cross=False,tones=ECO,drops=[(g,R+2-tc/2) for g in G6[0]])
    gone=ring(D,tc,cell,cross=False,body=False,drops=[(k*45+90,R+4+(k%2)) for k in range(8)],dots=[(20,R-8),(110,R-10),(200,R-7),(250,R-12),(310,R-9),(160,R+7),(350,R+8)])
    return idle+[pop,gone]
SETS={'s':(40,3,54),'b':(52,3,66)}
fr={k:conj(*v) for k,v in SETS.items()}; SETS['eco']=(68,3,90); fr['eco']=eco(68,90)
Wd=max(SETS[k][2]*len(fr[k]) for k in SETS); Hh=sum(v[2] for v in SETS.values()); at=Image.new('RGBA',(Wd,Hh),(0,0,0,0)); y=0; meta={}
for k,v in SETS.items():
    for i,f in enumerate(fr[k]): at.alpha_composite(Image.fromarray(f,'RGBA'),(i*v[2],y))
    meta[k]={'cw':v[2],'y':y,'n':len(fr[k])}; y+=v[2]
bf=io.BytesIO(); at.save(bf,'PNG',optimize=True); print(at.size,len(bf.getvalue()),'bytes',meta)
json.dump({'meta':meta,'data':'data:image/png;base64,'+base64.b64encode(bf.getvalue()).decode()},open('escudo_art.json','w'))
pv=Image.new('RGBA',at.size,(110,162,242,255)); pv.alpha_composite(at); pv.resize((Wd*4,Hh*4),Image.NEAREST).save('escudo_prev.png')
