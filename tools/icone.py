"""Ícones do Zé Gotinha's Revenge: o rosto do Zé (quadro parado do sprite) sobre o céu do jogo.
O rosto vem do mesmo recorte usado no jogo, em resolução dobrada (2x) para os ícones grandes e na resolução do jogo (1x) para o favicon."""
from PIL import Image
import numpy as np, sys
import os; os.chdir(os.path.dirname(os.path.abspath(__file__)))
Z2=Image.open('ze_2x.png').convert('RGBA'); Z1=Image.open('head_1.png').convert('RGBA')
SKY=[(0.00,(0,79,228)),(0.34,(9,135,254)),(0.66,(62,180,254))]
def sky(size,px):
    im=Image.new('RGBA',(size,size)); a=np.zeros((size,size,4),np.uint8); a[...,3]=255
    for i,(y0,c) in enumerate(SKY):
        y=int(round(y0*size/px))*px; a[y:,:,:3]=c
        if i:   # uma linha de xadrez entre as faixas, na grade do pixel do desenho
            for x in range(0,size,px*2): a[y-px:y,x:x+px,:3]=c
    return Image.fromarray(a,'RGBA')
def icon(size,px,spr,top,dx=0):
    im=sky(size,px); s=spr.resize((spr.width*px,spr.height*px),Image.NEAREST); im.alpha_composite(s.crop((0,0,s.width,min(s.height,size-top))),((size-s.width)//2+dx,top)); return im
out=sys.argv[1] if len(sys.argv)>1 else '../icons'
icon(512,13,Z2,26).save(out+'/icon-512.png',optimize=True)
icon(192,5,Z2,8).save(out+'/icon-192.png',optimize=True)
icon(180,5,Z2,2).save(out+'/apple-touch-icon.png',optimize=True)
icon(512,9,Z2,96).save(out+'/icon-maskable-512.png',optimize=True)
icon(64,3,Z1,9).save(out+'/favicon-64.png',optimize=True)




