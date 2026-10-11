import pickle, json, base64, io, numpy as np
from PIL import Image
from proc2 import Sheet, PAL, NAMES
W,S,K,B=(*PAL['W'],255),(*PAL['S'],255),(*PAL['K'],255),(*PAL['B'],255)
def deblue(f):
    f=f.copy(); m=(f[...,:3]==np.array(PAL['B'])).all(-1)&(f[...,3]>0); f[m]=S; return f
def setpx(f,col,cells):
    for y,x0,x1 in cells:
        for x in range(x0,x1+1):
            if f[y,x,3] and tuple(f[y,x,:3])!=PAL['K'] and tuple(f[y,x,:3])!=PAL['R']: f[y,x]=col
frames,sc=pickle.load(open('run_n.pkl','rb'))
A=deblue(frames[0][0]); P=deblue(frames[1][0])
# passada oposta: mesma silhueta, sombra trocada entre os membros de perto e de longe
Bf=A.copy()
setpx(Bf,S,[(18,6,8),(19,5,8),(20,5,8),(21,5,6)])                     # braço de trás vira o de longe
setpx(Bf,W,[(18,13,14),(19,14,18)])                                   # braço da frente vira o de perto
setpx(Bf,W,[(23,3,8),(24,2,9),(25,2,5),(26,2,3)])                     # perna de trás vira a de perto
setpx(Bf,S,[(23,10,14),(24,12,15),(25,13,15),(26,14,18),(27,15,15)])  # perna da frente vira a de longe
P2=P.copy()
setpx(P2,S,[(23,8,11),(24,8,11),(25,8,10),(26,7,9),(27,8,9),(28,8,9)])
setpx(P2,W,[(25,4,5),(26,4,6),(27,3,5),(28,3,6)])
run=[(A,frames[0][1],frames[0][2],frames[0][3]),(P,frames[1][1],frames[1][2],frames[1][3]),(Bf,frames[0][1],frames[0][2],frames[0][3]),(P2,frames[1][1],frames[1][2],frames[1][3])]
n=Sheet('sheet.png'); scn=28/356
rest=[n.frame(i,scn) for i in range(4,8)]; rest=[(deblue(f),ax,t,bt) for f,ax,t,bt in rest]
fr=run+rest; idle=fr[4]
half=max(max(int(np.ceil(ax)) for _,ax,_,_ in fr), max(f.shape[1]-int(np.floor(ax)) for f,ax,_,_ in fr))+1; CW=half*2
CH=max(bt+2 for f,ax,t,bt in fr)+1; BASE=CH-1; idle_top=BASE-(idle[3]+2)+idle[2]
sheet=Image.new('RGBA',(CW*8,CH),(0,0,0,0))
for i,(f,ax,t,bt) in enumerate(fr):
    x0=i*CW+half-int(round(ax)); y0=BASE-(bt+2) if NAMES[i] not in('jump','fall') else idle_top-t; y0=max(0,min(CH-f.shape[0],y0))
    sheet.alpha_composite(Image.fromarray(f,'RGBA'),(x0,y0))
buf=io.BytesIO(); sheet.save(buf,'PNG',optimize=True); sheet.save('ze_n2.png')
json.dump({'cw':CW,'ch':CH,'base':BASE,'data':'data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode()},open('ze_n2.json','w'))
print('cell',CW,CH,'base',BASE,len(buf.getvalue()))
bgc=Image.new('RGBA',sheet.size,(110,162,242,255)); bgc.alpha_composite(sheet); bgc.resize((sheet.width*6,sheet.height*6),Image.NEAREST).save('preview3.png')
# gif da corrida para conferir o movimento
cells=[bgc.crop((i*CW,0,(i+1)*CW,CH)).resize((CW*8,CH*8),Image.NEAREST).convert('P',palette=Image.ADAPTIVE) for i in range(4)]
cells[0].save('run_n.gif',save_all=True,append_images=cells[1:],duration=100,loop=0)
