import pickle, json, base64, io, numpy as np
from PIL import Image
it=pickle.load(open('items.pkl','rb'))
GLY={'M':['X...X','XX.XX','X.X.X','X...X','X...X','X...X','X...X'],'F':['XXXXX','X....','X....','XXXX.','X....','X....','X....'],'?':['.XXX.','X...X','....X','...X.','..X..','.....','..X..']}
def glyph(f,ch,x,y,col):
    for j,r in enumerate(GLY[ch]):
        for i,c in enumerate(r):
            if c=='X': f[y+j,x+i]=(*col,255)
q=it['q'].copy(); q[3:13,4:12]=(253,213,5,255); glyph(q,'?',6,5,(160,70,4)); glyph(q,'?',5,4,(255,255,255)); it['q']=q
for ch,col in (('M',(161,42,106)),('F',(22,105,122))):
    b=it['blank'].copy(); glyph(b,ch,5,4,col); glyph(b,ch,6,4,col); it[ch]=b
del it['blank']
names=list(it); W=sum(f.shape[1]+1 for f in it.values()); H=max(f.shape[0] for f in it.values())
atlas=Image.new('RGBA',(W,H),(0,0,0,0)); rects={}; x=0
for n in names:
    f=it[n]; atlas.alpha_composite(Image.fromarray(f,'RGBA'),(x,0)); rects[n]=[x,0,int(f.shape[1]),int(f.shape[0])]; x+=f.shape[1]+1
b=io.BytesIO(); atlas.save(b,'PNG',optimize=True)
json.dump({'rects':rects,'data':'data:image/png;base64,'+base64.b64encode(b.getvalue()).decode()},open('items_art.json','w'))
print(rects,len(b.getvalue()))
bg=Image.new('RGBA',atlas.size,(110,162,242,255)); bg.alpha_composite(atlas); bg.resize((W*6,H*6),Image.NEAREST).save('preview_items2.png')
