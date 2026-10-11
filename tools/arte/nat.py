from tk import *
import pickle
s=Sheet('nature.png','magenta',k=18,seed=5,dark_lum=40)
print([tuple(int(v) for v in p) for p in s.pal])
N={}
for i,x0 in enumerate((110,460,806)): N['w%d'%(i+1)]=s.tile(99+8,352-8,x0+9,x0+272-9,16,16,alpha=True)
N['deep']=s.tile(99+10,352-10,1155+10,1427-10,16,16)
N['pad']=s.obj((440,610,150,662),w=20)
N['nest']=s.obj((425,602,748,1412),w=30)
for i,r in enumerate(((675,930,40,297),(675,930,312,563),(675,930,570,830))): N['t%d'%(i+1)]=s.obj(r,h=13)
for i,r in enumerate(((680,930,862,1072),(680,930,1100,1258),(680,930,1284,1498))): N['f%d'%(i+1)]=s.obj(r,h=13)
for k,v in N.items(): print(k,v.shape[:2])
pickle.dump(N,open('nat_raw.pkl','wb'))
show(list(N.values()),'nat_prev.png',zoom=8)
