# Fase 3: drone, máquina quântica, amostras (pedra, banana, vaso), pote premium e xícara, em fundo magenta.
# A xícara gera duas peças: 'cup' inteira e 'cupf', a frente (da borda da frente para baixo), desenhada por cima do Zé.
# Uso: python3 objs3.py objs.png. Gera objs3_art.json e preview_objs3.png.
import sys
from art3 import *
f = Folha(sys.argv[1], 'magenta'); fr = {}
fr['drone0'] = f.recorta(30, 330, 260, 460, .078, 14); fr['drone1'] = f.recorta(270, 330, 510, 460, .078, 14)
fr['maq'] = f.recorta(520, 110, 900, 515, .42, 24)
fr['pedra'] = f.quadro(890, 295, 1080, 485); fr['banana'] = f.quadro(1105, 295, 1300, 485); fr['vaso'] = f.quadro(1325, 295, 1520, 485); fr['pote'] = f.quadro(1550, 295, 1745, 485)
cup = f.recorta(690, 580, 1085, 840, .072, 16); fr['cup'] = cup
r0 = round(cup.shape[0] * .3); fr['cupf'] = cup[r0:]; print('cup', cup.shape, 'frente a partir da linha', r0)
empacota(fr, 'objs3', {'cupf_y': r0})
