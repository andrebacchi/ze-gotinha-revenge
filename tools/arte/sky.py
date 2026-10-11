import numpy as np, pickle
from PIL import Image
a=np.asarray(Image.open('bg_sky.png').convert('RGB')).astype(int)
# faixas: cor mediana em linhas de amostra
rows=[60,300,490,680,880]; cols=[tuple(int(v) for v in np.median(a[y,100:1100],0)) for y in rows]; print('faixas',cols)
# limites das faixas na arte (pontilhado em ~200-240, 385-425, 570-610, 750-790) → em 180 linhas
edges=[round(v/941*180) for v in (222,405,590,770)]; print('limites',edges)
sky=np.zeros((180,320,3),np.uint8); b=0
for y in range(180):
    while b<len(edges) and y>=edges[b]: b+=1
    sky[y,:]=cols[b]
for i,e in enumerate(edges):       # 2 linhas de xadrez entre faixas
    for y in (e-1,e):
        for x in range(320): sky[y,x]=cols[i] if (x+y)%2==0 else cols[i+1]
# sol refeito com as cores da arte
sun=[tuple(int(v) for v in a[190,1440]),tuple(int(v) for v in a[190,1330]),tuple(int(v) for v in a[190,1312])]; print('sol',sun)
cx,cy=262,36
for y in range(180):
    for x in range(320):
        d=((x-cx)**2+(y-cy)**2)**.5
        if d<13.5: sky[y,x]=sun[0]
        elif d<15.5: sky[y,x]=(255,246,90)
        elif d<17.5: sky[y,x]=(255,228,40)
        elif d<21.5 and (x+y)%2==0: sky[y,x]=(214,214,130)
Image.fromarray(sky).save('bg_skyout.png'); pickle.dump(sky,open('sky.pkl','wb'))
