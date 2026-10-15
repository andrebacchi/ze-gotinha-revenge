# Fase 3: blocos da clínica em fundo ciano. Linha 1: mármore creme (topo, recheio), mármore verde (topo, recheio), parede, prateleira de vidro,
# cristais, bloco VIP (?) e bloco usado. Linha 2: porta de vidro (2 x 4 blocos); o poste é desenhado em código.
# Cada bloco é recortado por dentro do contorno, reduzido por média e devolvido à paleta do próprio bloco. Uso: python3 tiles3.py tiles3.png
import sys, json, base64, io
from PIL import Image
import numpy as np, scipy.ndimage as ndi
from scipy.cluster.vq import kmeans2
K = (11, 16, 48)
a = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(float); r, g, b = a[..., 0], a[..., 1], a[..., 2]
bg = (g > 180) & (b > 180) & (r < 120); fg = ndi.binary_opening(~bg, iterations=2)
lab, n = ndi.label(fg); objs = ndi.find_objects(lab); area = ndi.sum(fg, lab, range(1, n + 1))
big = sorted([o for k, o in enumerate(objs) if area[k] > 1500], key=lambda o: (o[0].start > 280, o[1].start))
print(len(big), [(o[1].start, o[0].start, o[1].stop - o[1].start, o[0].stop - o[0].start) for o in big])
names = ['mF', 'mf', 'gF', 'gf', 'wall', 'shelf', 'cris', 'q', 'u', 'door', 'pole']
assert len(big) == len(names), len(big)
def red(o, w, h, inset, ncol=10, keep_k=False):
    y0, y1, x0, x1 = o[0].start + inset, o[0].stop - inset, o[1].start + inset, o[1].stop - inset
    crop = a[y0:y1, x0:x1]; msk = fg[y0:y1, x0:x1]
    im = np.asarray(Image.fromarray(crop.astype(np.uint8)).resize((w, h), Image.BOX)).astype(float)
    al = np.asarray(Image.fromarray((msk * 255).astype(np.uint8)).resize((w, h), Image.BOX)) >= 128
    px = crop[msk][::3]; cent, _ = kmeans2(px, ncol, minit='++', seed=4)
    q = cent[((im[..., None, :] - cent[None, None]) ** 2).sum(-1).argmin(-1)]
    out = np.zeros((h, w, 4), np.uint8); out[..., :3] = np.round(q); out[..., 3] = al * 255
    if keep_k: out[(out[..., :3].astype(int).sum(-1) < 150) & al] = (*K, 255)
    return out
fr = {}
for o, nm in zip(big, names):
    W, H = o[1].stop - o[1].start, o[0].stop - o[0].start
    if nm == 'shelf': fr[nm] = red(o, 16, max(4, round(H * 16 / W)), 0, 6, True)
    elif nm == 'cris': fr[nm] = red(o, 16, max(6, round(H * 16 / W)), 0, 8, True)
    elif nm == 'door': fr[nm] = red(o, 32, 64, 0, 12, True)
    elif nm in ('q', 'u'): fr[nm] = red(o, 16, 16, 0, 8, True)
    elif nm == 'pole': continue
    else: fr[nm] = red(o, 16, 16, 5, 8)
    if nm == 'cris': c = fr[nm]; c[(c[..., 1] > 150) & (c[..., 2] > 150) & (c[..., 0] < 150)] = 0   # franja ciana entre as pontas
    print(nm, fr[nm].shape[:2])
Wt = sum(f.shape[1] + 1 for f in fr.values()); Ht = max(f.shape[0] for f in fr.values())
sheet = Image.new('RGBA', (Wt, Ht), (0, 0, 0, 0)); rects = {}; x = 0
for nm, f in fr.items(): sheet.alpha_composite(Image.fromarray(f, 'RGBA'), (x, 0)); rects[nm] = [x, 0, f.shape[1], f.shape[0]]; x += f.shape[1] + 1
bio = io.BytesIO(); sheet.save(bio, 'PNG', optimize=True)
json.dump({'rects': rects, 'src': 'data:image/png;base64,' + base64.b64encode(bio.getvalue()).decode()}, open('tiles3_art.json', 'w')); print('bytes', len(bio.getvalue()))
bgc = Image.new('RGBA', sheet.size, (60, 70, 110, 255)); bgc.alpha_composite(sheet); bgc.resize((sheet.width * 6, sheet.height * 6), Image.NEAREST).save('preview_tiles3.png')
