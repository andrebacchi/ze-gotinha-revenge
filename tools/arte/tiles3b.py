# Fase 3: blocos dos ambientes em fundo magenta. 5 linhas (corredor, farmácia, quântica, spa, auditório) x 3 colunas (topo, recheio, parede).
# Cada bloco é recortado por dentro do contorno, reduzido por média e devolvido à paleta dele. Uso: python3 tiles3b.py tiles.png
# Gera tiles3b_art.json (nomes corrF, corrf, corrw, farmF, ...) e preview_tiles3b.png.
import sys
from art3 import *
a = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(float); r, g, b = a[..., 0], a[..., 1], a[..., 2]
bg = (r > 170) & (b > 170) & (g < 120); fg = ndi.binary_opening(~bg, iterations=2)
lab, n = ndi.label(fg); objs = ndi.find_objects(lab); area = ndi.sum(fg, lab, range(1, n + 1))
big = [o for k, o in enumerate(objs) if area[k] > 20000]; assert len(big) == 15, len(big)
rows = sorted(big, key=lambda o: o[0].start); grid = []
for i in range(5): grid += sorted(rows[i * 3:i * 3 + 3], key=lambda o: o[1].start)
nomes = [z + s for z in ['corr', 'farm', 'quant', 'spa', 'aud'] for s in ['F', 'f', 'w']]
INSET = 11   # tira o contorno e a moldura da folha
fr = {}
for o, nm in zip(grid, nomes):
    y0, y1, x0, x1 = o[0].start + INSET, o[0].stop - INSET, o[1].start + INSET, o[1].stop - INSET
    crop = a[y0:y1, x0:x1]; im = np.asarray(Image.fromarray(crop.astype(np.uint8)).resize((16, 16), Image.BOX)).astype(float)
    px = crop.reshape(-1, 3)[::5]; cent, _ = kmeans2(px, 9, minit='++', seed=4)
    q = cent[((im[..., None, :] - cent[None, None]) ** 2).sum(-1).argmin(-1)]
    out = np.zeros((16, 16, 4), np.uint8); out[..., :3] = np.round(q); out[..., 3] = 255; fr[nm] = out
empacota(fr, 'tiles3b')
