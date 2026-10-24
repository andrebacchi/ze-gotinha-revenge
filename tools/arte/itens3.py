# Fase 3: projéteis e itens em fundo ciano (cristais, livros, vela, chama, adesivo, diploma, grana, moeda).
# Uso: python3 itens3.py itens.png. Gera itens3_art.json e preview_itens3.png.
import sys
from art3 import *
f = Folha(sys.argv[1], 'ciano'); fr = {}
XS = [(100, 300), (390, 570), (680, 860), (960, 1140), (1250, 1430)]
for i, (a, b) in enumerate(XS): fr['cr%d' % i] = f.recorta(a, 90, b, 350, .056, 14)
for i, (a, b) in enumerate(XS): fr['bk%d' % i] = f.recorta(a, 380, b, 640, .056, 14)
for nm, win, esc, nc in [('vela', (40, 700, 200, 930), .06, 10), ('ch0', (220, 690, 370, 930), .055, 8), ('ch1', (385, 700, 530, 930), .055, 8), ('adesivo', (550, 700, 770, 930), .05, 8),
                          ('diploma', (770, 700, 1040, 930), .057, 12), ('grana', (1045, 700, 1290, 930), .042, 8), ('coin', (1300, 700, 1500, 930), .035, 8)]:
    fr[nm] = f.recorta(*win, esc, nc)
empacota(fr, 'itens3')
