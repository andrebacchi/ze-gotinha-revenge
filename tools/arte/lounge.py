# Fase 3: objetos do lounge em fundo ciano. Cada objeto sai de uma janela da folha, com escala própria.
# Uso: python3 lounge.py lounge.png. Gera lounge_art.json (atlas em data URI) e preview_lounge.png.
import sys, json, base64, io
from PIL import Image
import numpy as np, scipy.ndimage as ndi
from scipy.cluster.vq import kmeans2
K = (11, 16, 48)
a = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(float); r, g, b = a[..., 0], a[..., 1], a[..., 2]; H, W = a.shape[:2]
fx, fy = W / 1145, H / 1374   # as janelas abaixo foram medidas numa folha de 1145 x 1374
bg = (g > 180) & (b > 180) & (r < 120); fg = ndi.binary_opening(~bg, iterations=1)
lum = 0.3 * r + 0.59 * g + 0.11 * b
dark = fg & ((lum < 40) | ((g > r + 70) & (b > r + 70) & (lum > 120)))
np.random.seed(3); px = a[fg & ~dark]; cent, _ = kmeans2(px[::5], 36, minit='++', seed=3); pal = np.round(cent).astype(int)
pal = np.array([p for p in pal if not (p[1] > p[0] + 70 and p[2] > p[0] + 70 and p[1] > 170)])
cls = ((a[..., None, :] - pal[None, None]) ** 2).sum(-1).argmin(-1)
lab, n = ndi.label(fg); objs = ndi.find_objects(lab); area = ndi.sum(fg, lab, range(1, n + 1))
# (nome, janela x0, y0, x1, y1, quantos objetos da esquerda para a direita, escala)
JAN = [('b', 25, 100, 680, 410, 5, .054), ('d', 720, 220, 1120, 310, 5, .13), ('p', 700, 345, 1125, 400, 5, .2),
       ('lustre', 30, 540, 490, 840, 1, .07), ('poste', 520, 440, 780, 880, 1, .082), ('gancho', 860, 600, 1070, 730, 1, .1),
       ('poltrona', 15, 980, 330, 1280, 1, .085), ('planta', 290, 880, 530, 1280, 1, .085), ('balcao', 505, 1030, 985, 1280, 1, .1), ('coluna', 985, 860, 1130, 1280, 1, .12)]
def cut(m, o, SC):
    dk = dark[o] & m; col = m & ~dk; inner = ndi.binary_fill_holes(m); h, w = m.shape; nh, nw = max(1, round(h * SC)), max(1, round(w * SC))
    ds = lambda z: np.asarray(Image.fromarray((z * 255).astype(np.uint8)).resize((nw, nh), Image.BOX)).astype(float) / 255
    I = ds(inner); D = ds(dk & inner); votes = np.stack([ds(col & (cls[o] == k)) for k in range(len(pal))], -1)
    body = I >= 0.5; out = np.zeros((nh + 2, nw + 2, 4), np.uint8)
    for y in range(nh):
        for x in range(nw):
            if body[y, x]: out[y + 1, x + 1] = (*K, 255) if D[y, x] / max(I[y, x], 1e-6) > 0.6 else (*pal[votes[y, x].argmax()], 255)
    bm = np.zeros((nh + 2, nw + 2), bool); bm[1:-1, 1:-1] = body
    out[ndi.binary_dilation(bm, structure=ndi.generate_binary_structure(2, 1)) & ~bm] = (*K, 255)
    return out
frames = {}
for nm, x0, y0, x1, y1, cnt, SC in JAN:
    x0, x1, y0, y1 = int(x0 * fx), int(x1 * fx), int(y0 * fy), int(y1 * fy)
    ids = [k + 1 for k, o in enumerate(objs) if area[k] > 40 and x0 <= (o[1].start + o[1].stop) / 2 < x1 and y0 <= (o[0].start + o[0].stop) / 2 < y1]
    if cnt == 1: groups = [ids]
    else:   # agrupa por coluna: pedaços cujo centro cai no mesmo quinto da largura dos objetos
        cx = {k: (objs[k - 1][1].start + objs[k - 1][1].stop) / 2 for k in ids}; big = sorted([k for k in ids if area[k - 1] > 0.3 * max(area[i - 1] for i in ids)], key=lambda k: cx[k])
        assert len(big) == cnt, (nm, len(big)); groups = [[] for _ in big]
        for k in ids: groups[min(range(cnt), key=lambda i: abs(cx[k] - cx[big[i]]))].append(k)
    for i, gr in enumerate(groups):
        ys = slice(min(objs[k - 1][0].start for k in gr), max(objs[k - 1][0].stop for k in gr)); xs = slice(min(objs[k - 1][1].start for k in gr), max(objs[k - 1][1].stop for k in gr))
        name = nm + (str(i) if cnt > 1 else ''); frames[name] = cut(np.isin(lab[ys, xs], gr), (ys, xs), SC); print(name, frames[name].shape[:2])
Wt = sum(f.shape[1] + 1 for f in frames.values()); Ht = max(f.shape[0] for f in frames.values())
sheet = Image.new('RGBA', (Wt, Ht), (0, 0, 0, 0)); rects = {}; x = 0
for nm, f in frames.items(): sheet.alpha_composite(Image.fromarray(f, 'RGBA'), (x, 0)); rects[nm] = [x, 0, f.shape[1], f.shape[0]]; x += f.shape[1] + 1
bio = io.BytesIO(); sheet.save(bio, 'PNG', optimize=True)
json.dump({'rects': rects, 'src': 'data:image/png;base64,' + base64.b64encode(bio.getvalue()).decode()}, open('lounge_art.json', 'w'))
print('bytes', len(bio.getvalue()))
bgc = Image.new('RGBA', sheet.size, (60, 70, 110, 255)); bgc.alpha_composite(sheet); bgc.resize((sheet.width * 4, sheet.height * 4), Image.NEAREST).save('preview_lounge.png')
