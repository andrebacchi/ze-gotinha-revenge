from tk import *
import pickle
s=Sheet('terrain.png','magenta',k=18,seed=7,dark_lum=38)
a=s.a
EARTH=np.array([(96,44,24),(150,62,20),(178,76,20),(201,93,20),(228,118,24),(246,160,60)],float)
GREEN=np.array([(6,92,44),(9,133,45),(67,193,16),(124,222,7),(200,246,54)],float)
def avg(y0,y1,x0,x1,nw,nh):
    return np.asarray(Image.fromarray(a[y0:y1,x0:x1].astype(np.uint8)).resize((nw,nh),Image.BOX)).astype(float)
def near(c,pal): return pal[((pal-c)**2).sum(-1).argmin()]
def frac(m,y0,y1,x0,x1,nw,nh): return np.asarray(Image.fromarray((m[y0:y1,x0:x1]*255).astype(np.uint8)).resize((nw,nh),Image.BOX)).astype(float)/255
r,g,b=a[...,0],a[...,1],a[...,2]
isgreen=(g>r+25)&(g>b+25)&s.fg
def ground(x0,grass=True,y0=116,y1=343):
    X0,X1=x0+12,x0+256
    A=avg(y0,y1,X0,X1,16,16); G=frac(isgreen,y0,y1,X0,X1,16,16); out=np.zeros((16,16,4),np.uint8)
    for y in range(16):
        for x in range(16):
            if grass and G[y,x]>=0.5:
                # média só dos pixels verdes
                out[y,x]=(*near(A[y,x],GREEN).astype(int),255)
            else: out[y,x]=(*near(A[y,x],EARTH).astype(int),255)
    return out
def blades(x0,rows=3,y0=67,y1=116):
    X0,X1=x0+12,x0+256
    lit=isgreen&(s.lum>70); G=frac(lit,y0,y1,X0,X1,16,rows); A=avg(y0,y1,X0,X1,16,rows); out=np.zeros((rows,16,4),np.uint8)
    for y in range(rows):
        for x in range(16):
            if G[y,x]>=0.33: out[y,x]=(*(GREEN[3] if G[y,x]>0.6 else GREEN[2]).astype(int),255)
    return out
T={}
body=ground(467); T['dirt']=ground(1136,grass=False,y0=124,y1=343)
for i,x0 in enumerate((135,467,802)): T['b%d'%(i+1)]=blades(x0); T['gfull%d'%(i+1)]=ground(x0)
T['grass']=body
pickle.dump(T,open('terr_raw.pkl','wb'))
def tiled(seq,name,zoom=8,full=False):
    W=16*len(seq); im=Image.new('RGBA',(W,3+16+32),(110,162,242,255))
    for i,k in enumerate(seq):
        im.alpha_composite(Image.fromarray(T['b%d'%k],'RGBA'),(i*16,0)); im.alpha_composite(Image.fromarray(T['gfull%d'%k] if full else T['grass'],'RGBA'),(i*16,3))
        for r_ in (0,1): im.alpha_composite(Image.fromarray(T['dirt'],'RGBA'),(i*16,19+16*r_))
    im.resize((W*zoom,im.height*zoom),Image.NEAREST).save(name)
tiled([1,2,3,2,1,2,3,2],'terr_prev1.png')
