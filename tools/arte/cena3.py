# Fase 3: objetos de cenário (farmácia, diagnóstico, spa, auditório) em fundo ciano. Uma janela e uma escala por objeto.
# A fumaça da cafeteira sai do recorte (o jogo desenha a sua). Os cinco quadros da galeria saem juntos, na posição da folha.
# Uso: python3 cena3.py cena.png. Gera cena3_art.json e preview_cena3.png.
import sys
from art3 import *
f = Folha(sys.argv[1], 'ciano'); fr = {}
JAN = [('vitrine', (50, 20, 270, 345), .16, 20), ('balcaoF', (310, 100, 615, 345), .15, 20), ('carrinho', (655, 80, 865, 345), .14, 18), ('estante', (910, 20, 1160, 345), .16, 22),
       ('painel', (50, 350, 255, 640), .2, 16), ('galeria', (295, 380, 660, 620), .12, 12), ('relogio', (665, 405, 865, 610), .1, 8), ('nome', (895, 420, 1170, 595), .16, 8),
       ('cafe', (30, 640, 365, 970), .22, 24), ('cano', (400, 640, 530, 975), .15, 10), ('bambu', (615, 625, 840, 970), .14, 14), ('spa', (855, 770, 1180, 970), .14, 16),
       ('podio', (55, 985, 260, 1275), .14, 14), ('tela', (290, 975, 610, 1275), .17, 12), ('cadeiras', (615, 1050, 935, 1265), .1, 12), ('cartaz', (945, 995, 1150, 1270), .085, 8)]
for nm, win, esc, nc in JAN:
    clip = (lambda X, Y: ~((X < 104) & (Y < 860))) if nm == 'cafe' else None   # fumaça
    fr[nm] = f.recorta(*win, esc, nc, clip); print(nm, fr[nm].shape[:2])
empacota(fr, 'cena3')
