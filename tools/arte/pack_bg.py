import numpy as np, pickle, io, base64, json, colorsys
from PIL import Image
L=pickle.load(open('bg.pkl','rb'))
def tone(a,contrast=1,sat=1,haze=0,hc=(120,190,235)):
    o=a.copy(); rgb=a[...,:3].astype(float)
    g=rgb.mean(-1,keepdims=True); rgb=g+(rgb-g)*sat; rgb=128+(rgb-128)*contrast; rgb=rgb*(1-haze)+np.array(hc)*haze
    o[...,:3]=np.clip(rgb,0,255).astype(np.uint8); return o
A,B=L['townA'],L['townB']; H=max(A.shape[0],B.shape[0]); town=np.zeros((H,A.shape[1]+B.shape[1],4),np.uint8)
town[H-A.shape[0]:,:A.shape[1]]=A; town[H-B.shape[0]:,A.shape[1]:]=B
town=tone(town,contrast=.88,sat=.9,haze=.2); bush=tone(L['bush'],contrast=.78,sat=.85,haze=.17)
cl=L['clouds']; CW=640; clouds=Image.new('RGBA',(CW,84),(0,0,0,0))
for (i,x,y,fl) in ((0,14,24,0),(1,118,50,0),(2,196,8,0),(4,292,44,0),(3,350,30,1),(5,430,6,0),(1,486,54,1),(0,548,16,1),(4,92,4,1)):
    c=cl[i][:,::-1] if fl else cl[i]; assert x+c.shape[1]<CW; clouds.alpha_composite(Image.fromarray(np.ascontiguousarray(c),'RGBA'),(x,y))
out={}
def enc(arr,name):
    im=Image.fromarray(np.ascontiguousarray(arr),'RGBA'); q=im.quantize(colors=64,method=Image.FASTOCTREE) if False else im
    b=io.BytesIO(); im.save(b,'PNG',optimize=True); out[name]='data:image/png;base64,'+base64.b64encode(b.getvalue()).decode(); print(name,im.size,len(b.getvalue()),'bytes',len(set(map(tuple,arr.reshape(-1,4)))),'cores'); im.save('bgf_%s.png'%name)
enc(np.asarray(clouds),'clouds'); enc(L['hills'],'hills'); enc(town,'town'); enc(bush,'bush')
print('base morros',L['hills'][-1,5],'base arbustos',bush[-1,5],bush[-6,5])
json.dump(out,open('bg_art.json','w'))
