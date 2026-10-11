import pickle, numpy as np, json, io, base64
from PIL import Image
FX,FY=pickle.load(open('zex.pkl','rb')); JS=pickle.load(open('jswim.pkl','rb'))
K=(11,16,48,255); W=(255,255,255,255)
d=FX[2][0]
for (y,x) in ((7,11),(7,14),(7,15),(8,10),(8,11),(8,14)): d[y,x]=W
for (y,x) in ((6,9),(6,11),(7,10),(8,9),(8,11),(6,13),(7,14),(8,13),(8,15)): d[y,x]=K
def uri(im):
    b=io.BytesIO(); im.save(b,'PNG',optimize=True); return 'data:image/png;base64,'+base64.b64encode(b.getvalue()).decode()
def pack(fr,names):
    half=max(max(int(np.ceil(ax)) for _,ax,_,_ in fr), max(f.shape[1]-int(np.floor(ax)) for f,ax,_,_ in fr))+1; CW=half*2; CH=max(f.shape[0] for f,*_ in fr); BASE=CH-1
    sh=Image.new('RGBA',(CW*len(fr),CH),(0,0,0,0))
    for i,(f,ax,t,bt) in enumerate(fr):
        ys=np.nonzero(f[...,3].any(1))[0]; f=f[ys.min():ys.max()+1]          # apara linhas vazias
        sh.alpha_composite(Image.fromarray(np.ascontiguousarray(f),'RGBA'),(i*CW+half-int(round(ax)),CH-f.shape[0]))
    return sh,CW,CH,BASE
out={}
for key,fr,names,seat in (('n',FX,['ride','rthrow','dead','drownA','drownB'],6),('b',FY,['ride','rthrow','drownA','drownB'],8)):
    sh,CW,CH,BASE=pack(fr,names); out[key]=dict(cw=CW,ch=CH,base=BASE,seat=seat,names=names,data=uri(sh)); print(key,CW,CH,BASE); sh.save('zex_sheet_%s.png'%key)
# jacaré nadando: âncora = centro da sela; topo da sela a 16 px da base, como nos quadros de terra
half=max(max(int(np.ceil(ax)) for _,ax,_,_ in JS), max(f.shape[1]-int(np.floor(ax)) for f,ax,_,_ in JS))+1; CW=half*2
top=max(int(round(t)) for _,_,t,_ in JS); BASE=top+16; CH=max(top-int(round(t))+f.shape[0] for f,_,t,_ in JS)
sh=Image.new('RGBA',(CW*3,CH),(0,0,0,0))
for i,(f,ax,t,bt) in enumerate(JS): sh.alpha_composite(Image.fromarray(f,'RGBA'),(i*CW+half-int(round(ax)),top-int(round(t))))
out['j']=dict(cw=CW,ch=CH,base=BASE,names=['swim1','swim2','sbite'],data=uri(sh)); print('j',CW,CH,BASE); sh.save('jsw_sheet.png')
json.dump(out,open('zex_art.json','w')); print({k:len(v['data']) for k,v in out.items()})
