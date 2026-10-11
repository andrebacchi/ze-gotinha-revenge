import pickle, numpy as np
from enemy import pack
fr=pickle.load(open('boato_frames.pkl','rb'))
M=(196,246,180,255); R=(241,13,15,255); W=(251,252,250,255); K=(11,16,48,255); Gy=(104,122,128,255)
def fill(f,y0,y1,x0,x1,c):
    for y in range(y0,y1+1):
        for x in range(x0,x1+1):
            if f[y,x,3] and tuple(f[y,x,:3])!=(11,16,48) or (f[y,x,3] and c!=M): f[y,x]=c
def px(f,c,pts):
    for y,x in pts: f[y,x]=c
def symbols(f):
    for y in range(3,8):
        for x in range(5,20): 
            if f[y,x,3] and tuple(f[y,x,:3])!=(11,16,48): f[y,x]=M
    for x in (12,15,18): px(f,R,[(3,x),(4,x),(5,x),(7,x)])            # !!!
    px(f,Gy,[(4,5),(5,6),(6,5),(4,8),(5,9),(6,8)])                      # >> (encaminhada)
def eyes(f):
    for y in range(8,13):
        for x in range(8,20): f[y,x]=M
    px(f,K,[(8,9),(8,10),(9,11),(9,12),(9,15),(9,16),(8,17),(8,18)])    # sobrancelhas bravas
    px(f,W,[(9,9),(9,10),(10,9),(10,10),(10,11),(10,12),(11,9),(11,10),(11,11),(11,12),(9,17),(9,18),(10,15),(10,16),(10,17),(10,18),(11,15),(11,16),(11,17),(11,18)])
    px(f,K,[(10,11),(11,11),(10,16),(11,16)])                            # pupilas
a=fr[0]['img']; symbols(a); eyes(a)
for y in (13,14,15):
    for x in range(10,18):
        if a[y,x,3] and tuple(a[y,x,:3])!=(11,16,48) or (y<15 and 11<=x<=16): a[y,x]=M
px(a,K,[(13,12),(13,13),(13,14),(13,15)]); px(a,R,[(14,12),(14,13),(14,14),(14,15),(15,13),(15,14)])   # boca aberta
b=fr[1]['img']; symbols(b); eyes(b)
for y in (13,14):
    for x in range(10,18): b[y,x]=M
px(b,K,[(14,12),(13,13),(13,14),(14,15)])                                # boca fechada, emburrada
pack(fr,'boato_art',zoom=7)
