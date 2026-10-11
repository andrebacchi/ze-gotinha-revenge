import pickle, json, base64, io, numpy as np
from PIL import Image
fr=pickle.load(open('jac_frames.pkl','rb')); pal=pickle.load(open('jac_pal.pkl','rb'))
names=['walk1','walk2','walk3','walk4','idle','bite','scared']; body=fr[:7]; objs=fr[7:]
half=max(max(int(np.ceil(ax)) for _,ax,_,_ in body), max(f.shape[1]-int(np.floor(ax)) for f,ax,_,_ in body))+1; CW=half*2
CH=max(bt+2 for f,ax,t,bt in body)+1; BASE=CH-1
sheet=Image.new('RGBA',(CW*7,CH),(0,0,0,0)); seat=None
for i,(f,ax,t,bt) in enumerate(body):
    x0=i*CW+half-int(round(ax)); y0=BASE-(bt+2); sheet.alpha_composite(Image.fromarray(f,'RGBA'),(x0,y0))
    if names[i]=='idle':
        red=(f[...,0]>220)&(f[...,1]<70)&(f[...,3]>0); ys,xs=np.nonzero(red); seat=BASE-(y0+ys.min()); print('sela: topo a',seat,'px da base; x',xs.min()+x0-i*CW,xs.max()+x0-i*CW,'centro célula',half)
def uri(im):
    b=io.BytesIO(); im.save(b,'PNG',optimize=True); return 'data:image/png;base64,'+base64.b64encode(b.getvalue()).decode(), len(b.getvalue())
egg=Image.fromarray(objs[0][0],'RGBA'); s1=Image.fromarray(objs[1][0],'RGBA'); s2=Image.fromarray(objs[2][0],'RGBA')
shell=Image.new('RGBA',(s1.width+s2.width-1,max(s1.height,s2.height)),(0,0,0,0)); shell.alpha_composite(s1,(0,shell.height-s1.height)); shell.alpha_composite(s2,(s1.width-1,shell.height-s2.height))
def trim(im):
    a=np.asarray(im); ys,xs=np.nonzero(a[...,3]); return im.crop((xs.min(),ys.min(),xs.max()+1,ys.max()+1))
egg=trim(egg); shell=trim(shell)
u,n1=uri(sheet); ue,n2=uri(egg); us,n3=uri(shell)
json.dump({'cw':CW,'ch':CH,'base':BASE,'seat':int(seat),'data':u,'egg':ue,'eggSize':egg.size,'shell':us,'shellSize':shell.size},open('jac_art.json','w'))
print('cell',CW,CH,'base',BASE,'bytes',n1,n2,n3,'egg',egg.size,'shell',shell.size)
sheet.save('jac_sheet.png')
