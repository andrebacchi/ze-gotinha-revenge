from tk import *
import pickle
s=Sheet('fx.png','green',k=10,seed=4,dark_lum=60)
print([tuple(int(v) for v in p) for p in s.pal])
sc=11/243
b1=s.obj((140,380,390,660),scale=sc); b2=s.obj((140,380,750,1020),scale=sc); pop=s.obj((90,445,1090,1455),scale=sc)
ws=16/257
w=[s.obj(r,scale=ws) for r in ((590,790,40,430),(520,790,465,855),(515,790,895,1310),(595,790,1340,1750))]
fr=dict(b1=b1,b2=b2,pop=pop,w1=w[0],w2=w[1],w3=w[2],w4=w[3])
for k,v in fr.items(): print(k,v.shape[:2])
pickle.dump(fr,open('fx.pkl','wb')); show(list(fr.values()),'fx_prev.png',zoom=8)
