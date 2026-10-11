import pickle, numpy as np
from PIL import Image
from tk import show, atlas, K
T=pickle.load(open('terr.pkl','rb')); N=pickle.load(open('nat_raw.pkl','rb')); F=pickle.load(open('fx.pkl','rb'))
def px(c): return (*[int(v) for v in c],255)
KK=px(K); S={}
# ── chão
S['grass']=T['grass']; S['dirt']=T['dirt']
for i in (1,2,3): S['bl%d'%i]=T['b%d'%i]
# ── tijolo redesenhado na grade, com as cores da arte (juntas casam nos quatro lados)
HI,RED,SH=(246,148,47),(193,46,30),(117,41,31)
b=np.zeros((16,16,4),np.uint8)
for (r0,r1,joints) in ((0,4,(7,15)),(5,9,(3,11)),(10,14,(7,15))):
    for y in range(r0,r1): b[y,:]=px(HI if y==r0 else SH if y==r1-1 else RED)
    b[r1,:]=KK
    for j in joints: b[r0:r1,j]=KK
    for j in joints: b[r0+1:r1-1,(j+1)%16]=px((226,80,40))      # luz na face esquerda do tijolo
b[15,:]=KK; S['brick']=b
# ── madeira: uma tábua só, pontas arredondadas e mãos-francesas tiradas das peças da arte
M=T['wm'].copy(); print('tabua'); 
for r in M: print(' ',[tuple(int(v) for v in p[:3]) if p[3] else None for p in r[:6]])
CREAM=(248,209,113)
M[1,:]=px(CREAM)
def endpiece(src,left):
    o=np.zeros((11,16,4),np.uint8); o[:6]=M
    e=0 if left else 15; n=1 if left else 14
    o[1:5,e]=KK; o[0,e]=0; o[5,e]=0; o[0,n]=KK; o[5,n]=KK
    br=src[6:11] if src.shape[0]>=11 else src[-5:]
    w=br.shape[1]; o[6:11,:w]=br if left else 0
    if not left: o[6:11,16-w:]=br
    return o
S['wl']=endpiece(T['wl'],True); S['wm']=M; S['wr']=endpiece(T['wr'],False)
one=np.zeros((11,16,4),np.uint8); one[:,:8]=S['wl'][:,:8]; one[:,8:]=S['wr'][:,8:]; S['w1']=one
# ── plataforma móvel (refeita com 32 de largura) e chama curta
S['mp1']=None
# ── espinhos redesenhados
W_,L_,S_,B1,B2=(242,245,232),(179,205,217),(114,142,179),(60,96,140),(40,62,100)
sp=np.zeros((16,16,4),np.uint8)
for i in range(4):
    x=i*4
    sp[3,x+1]=KK
    for y in (4,5,6): sp[y,x+1]=px(W_); sp[y,x]=KK; sp[y,x+2]=KK
    for y in range(7,12): sp[y,x]=px(L_); sp[y,x+1]=px(W_ if y<9 else L_); sp[y,x+2]=px(S_); sp[y,x+3]=KK
sp[11,:]=KK; sp[12,:]=px(S_); sp[13,:]=px(B1); sp[14,:]=px(B1); sp[15,:]=px(B2)
for x in (2,6,10,14): sp[13,x]=px(L_)
S['spike']=sp
# ── grade redesenhada (repete na vertical)
g=np.zeros((16,16,4),np.uint8)
for x in (1,6,11):
    g[:,x]=KK; g[:,x+1]=px(L_); g[:,x+2]=px(B1); g[:,x+3]=KK
g[6,:]=KK; g[7,:]=px(S_); g[8,:]=px(B1); g[9,:]=KK
for x in (2,7,12): g[7,x]=px(W_); g[8,x]=px(L_)
S['gate']=g
# ── água: linha da onda periódica + faixas e brilhos nas cores da arte
FOAM,CY,B_1,B_2,B_3,DEEP=(240,251,253),(125,233,251),(3,178,253),(1,136,253),(2,88,249),(2,55,209)
w=np.zeros((16,16,4),np.uint8)
ys=[3+int(round(np.cos(2*np.pi*(x+.5)/16))) for x in range(16)]
for x in range(16):
    y=ys[x]; w[y,x]=px(FOAM); w[y+1,x]=px(CY if ys[x]<=3 else B_1)
    for yy in range(y+2,16): w[yy,x]=px(B_1 if yy<7 else B_2 if yy<12 else B_3)
for (y,x0,n,c) in ((8,2,4,CY),(8,3,2,FOAM),(10,10,3,B_1),(13,5,4,B_2),(13,6,2,CY),(6,11,3,CY)):
    for x in range(x0,x0+n): w[y,x%16]=px(c)
S['water']=w
d=np.zeros((16,16,4),np.uint8)
for y in range(16): d[y,:]=px(B_3 if y<3 else DEEP)
for (y,x0,n,c) in ((5,3,4,B_3),(10,9,5,B_3),(13,1,3,B_3)):
    for x in range(x0,x0+n): d[y,x%16]=px(c)
S['deep']=d
S['pad']=N['pad']; S['nest']=N['nest']
def shear(f,lean,pad=2):
    H,Wd=f.shape[:2]; o=np.zeros((H,Wd+2*pad,4),np.uint8)
    for y in range(H):
        dx=int(round(lean*((H-1-y)/(H-1))**1.4)); o[y,pad+dx:pad+dx+Wd]=f[y]
    return o
for i,l in enumerate((-2,-1,0,1,2)): S['tuft%d'%i]=shear(N['t2'],l); S['flor%d'%i]=shear(N['f2'],l)
for k in ('b1','b2','pop','w1','w2','w3','w4'): S['fx_'+k]=F[k]
pickle.dump(S,open('scene.pkl','wb'))
# ── plataforma móvel
mp=T['mplat'].copy()
for y in range(mp.shape[0]):
    for x in range(mp.shape[1]):
        r_,g_,b_,a_=[int(v) for v in mp[y,x]]
        if a_ and y<8 and ((g_>200 and b_<120) or (r_>200 and b_<150) or (r_>230 and g_>230 and y>2)): mp[y,x]=px((255,210,63))
S['mp1']=mp
# chama curta: tira uma linha do meio da chama
fl0=None
for y in range(mp.shape[0]):
    if any(int(p[2])>230 and int(p[0])<140 and p[3] for p in mp[y]) and fl0 is None: fl0=y
print('chama começa na linha',fl0,'altura',mp.shape[0])
mp2=mp.copy(); mp2[fl0+1:-1]=mp[fl0+2:]; mp2[-1]=0; S['mp2']=mp2
pickle.dump(S,open('scene.pkl','wb'))
for k,v in S.items(): print(k,v.shape[:2],end=' | ')
show([S[k] for k in ('grass','dirt','brick','wl','wm','wr','w1','mp1','mp2','spike','gate')],'sc_prev1.png',zoom=9)
show([S[k] for k in ('water','deep','pad','nest','tuft0','tuft2','tuft4','flor0','flor2','flor4','fx_b1','fx_b2','fx_pop')],'sc_prev2.png',zoom=9)
# luzes da plataforma refeitas em posições fixas
for m_ in (S['mp1'],S['mp2']):
    for y in range(1,8):
        for x in range(32):
            if tuple(int(v) for v in m_[y,x][:3])==(255,210,63): m_[y,x]=px((60,96,140))
    for x in (6,15,24): m_[3,x]=px((255,210,63)); m_[3,x+1]=px((255,210,63)); m_[4,x]=px((246,148,47)); m_[4,x+1]=px((246,148,47))
pickle.dump(S,open('scene.pkl','wb'))
order=['grass','dirt','bl1','bl2','bl3','brick','wl','wm','wr','w1','mp1','mp2','spike','gate','water','deep','pad','nest']+['tuft%d'%i for i in range(5)]+['flor%d'%i for i in range(5)]+['fx_b1','fx_b2','fx_pop','fx_w1','fx_w2','fx_w3','fx_w4']
rects=atlas({k:S[k] for k in order},'scene_art.json'); print(rects)
show([S['mp1'],S['mp2']],'sc_prev3.png',zoom=9)
