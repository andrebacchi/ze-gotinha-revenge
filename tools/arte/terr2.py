from tk import *
import pickle
exec(open('terr.py').read().split("T={}")[0].split("from tk import *\nimport pickle\n")[1])
T={}
x0=467; X0,X1=x0+12,x0+256
T['dirt']=ground(1136,grass=False,y0=124,y1=343)
# corpo do bloco com grama: faixa verde contínua nas 3 primeiras linhas
A=avg(116,343,X0,X1,16,16); G=frac(isgreen,116,343,X0,X1,16,16)
def greenavg(y0,y1,nw,nh):
    m=isgreen[y0:y1,X0:X1].astype(float); num=np.stack([np.asarray(Image.fromarray(((a[y0:y1,X0:X1,c]*m)).astype(np.uint8)).resize((nw,nh),Image.BOX)).astype(float) for c in range(3)],-1)
    den=np.asarray(Image.fromarray((m*255).astype(np.uint8)).resize((nw,nh),Image.BOX)).astype(float)/255; return num/np.maximum(den,1e-3)[...,None]
GA=greenavg(116,343,16,16); body=np.zeros((16,16,4),np.uint8)
for y in range(16):
    for x in range(16):
        if y<3 or G[y,x]>=0.45: body[y,x]=(*near(GA[y,x] if G[y,x]>0.05 else np.array(GREEN[2]),GREEN).astype(int),255)
        else: body[y,x]=(*near(A[y,x],EARTH).astype(int),255)
T['grass']=body
# lâminas: altura por coluna tirada do quadro reto (0..4 linhas acima do bloco)
lit=isgreen&(s.lum>60); Gb=frac(lit,60,116,X0,X1,16,4); hts=[]
for x in range(16):
    h=0
    for y in (3,2,1,0):
        if Gb[y,x]>=0.28: h+=1
        else: break
    hts.append(h)
print('alturas',hts)
def blades(lean,rows=4):
    o=np.zeros((rows,16,4),np.uint8)
    for x,h in enumerate(hts):
        for k in range(h):               # k=0 é a linha colada na faixa
            dx=int(round(lean*(k+1)/3.0)) if k>=1 else 0
            col=GREEN[4] if k==h-1 and h>=2 else GREEN[3] if k>=1 else GREEN[2]
            o[rows-1-k,(x+dx)%16]=(*col.astype(int),255)
    return o
for i,l in enumerate((-1.5,0,1.5)): T['b%d'%(i+1)]=blades(l)
# tijolo: bloco com contorno
T['brick']=s.tile(420,637,49,285,16,16)
# madeira
def piece(box,w,cut):
    f=s.obj(box,w=w)
    return f
L=s.obj((430,600,333,574),w=15); M=s.obj((430,535,607,832),w=16); R=s.obj((430,600,865,1072),w=15)
L=L[:,:-1]; M=M[:,1:-1]; R=R[:,1:]
print('madeira',L.shape,M.shape,R.shape)
T['wl'],T['wm'],T['wr']=L,M,R
T['mplat']=s.obj((455,645,1105,1505),w=32)
T['spike']=s.obj((750,940,420,692),w=14)
T['gate']=s.tile(696,926,742,971,16,16,alpha=True)
for k,v in T.items(): print(k,v.shape[:2])
pickle.dump(T,open('terr.pkl','wb'))
show([T[k] for k in ('brick','wl','wm','wr','mplat','spike','gate')],'terr_prev2.png',zoom=10)
W=16*8; im=Image.new('RGBA',(W,4+48),(110,162,242,255))
for i,k in enumerate([1,2,3,2,1,2,3,2]):
    im.alpha_composite(Image.fromarray(T['b%d'%k],'RGBA'),(i*16,0)); im.alpha_composite(Image.fromarray(T['grass'],'RGBA'),(i*16,4))
    for r_ in (0,1): im.alpha_composite(Image.fromarray(T['dirt'],'RGBA'),(i*16,20+16*r_))
im.resize((W*8,im.height*8),Image.NEAREST).save('terr_prev1.png')
