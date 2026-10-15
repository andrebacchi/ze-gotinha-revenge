# Dr. Soro Platinum (fase 3): folha de 6 quadros em fundo magenta (parado, flexão, arremesso, investida, cansado, dor). Âncora: pés.
# Uso: python3 barao.py barao.png [escala]. Gera soro_art.json (data URI + medidas) e preview_soro.png.
import sys, json, base64, io
from PIL import Image
import numpy as np, scipy.ndimage as ndi
from scipy.cluster.vq import kmeans2
K = (11, 16, 48)
SC = float(sys.argv[2]) if len(sys.argv) > 2 else 0.14
a = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(float); r, g, b = a[..., 0], a[..., 1], a[..., 2]; H, W = a.shape[:2]
bg = (r > 170) & (b > 170) & (g < 110); fg = ~bg; fg = ndi.binary_opening(fg, iterations=1)
lum = 0.3 * r + 0.59 * g + 0.11 * b
dark = fg & ((lum < 32) | ((r > g + 70) & (b > g + 70)))          # contorno e franja magenta
lab, n = ndi.label(fg); sizes = ndi.sum(fg, lab, range(1, n + 1)); cents = ndi.center_of_mass(fg, lab, range(1, n + 1))
np.random.seed(3); px = a[fg & ~dark]; cent, _ = kmeans2(px[::7], 22, minit='++', seed=3); pal = np.round(cent).astype(int)
pal = np.array([p for p in pal if not (p[0] > p[1] + 70 and p[2] > p[1] + 70)])
cls = ((a[..., None, :] - pal[None, None]) ** 2).sum(-1).argmin(-1)
names = ['idle', 'flex', 'throw', 'charge', 'tired', 'hurt']
# colunas: separa pelos vãos verdes verticais
colfg = fg.sum(0) > 0; runs = []; x = 0
while x < W:
    if colfg[x]:
        x0 = x
        while x < W and colfg[x]: x += 1
        runs.append((x0, x))
    else: x += 1
runs = [rr for rr in runs if rr[1] - rr[0] > 60]; print('colunas', runs)
cs = fg.sum(0)
while len(runs) < 6:   # poses que se encostam na horizontal: corta a coluna mais larga no ponto mais vazio do meio
    i = max(range(len(runs)), key=lambda k: runs[k][1] - runs[k][0]); x0, x1 = runs[i]; q = (x1 - x0) // 4
    xc = x0 + q + int(np.argmin(cs[x0 + q:x1 - q])); runs[i:i + 1] = [(x0, xc), (xc, x1)]; print('corte', xc)
assert len(runs) == 6, len(runs)
frames = []
for (x0, x1), nm in zip(runs, names):
    ids = [k + 1 for k in range(n) if sizes[k] > 30 and x0 <= cents[k][1] < x1]
    m = np.isin(lab, ids); ys, xs = np.nonzero(m); o = (slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1)); m = m[o]
    dk = dark[o] & m; col = m & ~dk; inner = ndi.binary_fill_holes(m); h, w = m.shape; nh, nw = round(h * SC), round(w * SC)
    ds = lambda z: np.asarray(Image.fromarray((z * 255).astype(np.uint8)).resize((nw, nh), Image.BOX)).astype(float) / 255
    I = ds(inner); D = ds(dk & inner); votes = np.stack([ds(col & (cls[o] == k)) for k in range(len(pal))], -1)
    body = I >= 0.5; out = np.zeros((nh + 2, nw + 2, 4), np.uint8)
    for y in range(nh):
        for xx in range(nw):
            if body[y, xx]: out[y + 1, xx + 1] = (*K, 255) if D[y, xx] / max(I[y, xx], 1e-6) > 0.55 else (*pal[votes[y, xx].argmax()], 255)
    bm = np.zeros((nh + 2, nw + 2), bool); bm[1:-1, 1:-1] = body
    ring = ndi.binary_dilation(bm, structure=ndi.generate_binary_structure(2, 1)) & ~bm; out[ring] = (*K, 255)
    # âncora: pés (fundo do recorte) e o centro de massa na horizontal
    pb = h; pcx = np.nonzero(m)[1].mean()
    frames.append(dict(name=nm, img=out, ax=pcx * SC + 1, base=pb * SC + 1)); print(nm, out.shape[:2], 'ax', round(pcx * SC + 1, 1), 'base', round(pb * SC + 1, 1))
half = max(max(int(np.ceil(f['ax'])) for f in frames), max(f['img'].shape[1] - int(np.floor(f['ax'])) for f in frames)) + 1; CW = half * 2
up = max(int(np.ceil(f['base'])) for f in frames) + 1; down = max(f['img'].shape[0] - int(np.floor(f['base'])) for f in frames) + 1; CH = up + down; BASE = up
sheet = Image.new('RGBA', (CW * len(frames), CH), (0, 0, 0, 0))
for i, f in enumerate(frames): sheet.alpha_composite(Image.fromarray(f['img'], 'RGBA'), (i * CW + half - int(round(f['ax'])), BASE - int(round(f['base']))))
bio = io.BytesIO(); sheet.save(bio, 'PNG', optimize=True); sheet.save('soro_sheet.png')
json.dump({'cw': CW, 'ch': CH, 'base': BASE, 'names': names, 'src': 'data:image/png;base64,' + base64.b64encode(bio.getvalue()).decode()}, open('soro_art.json', 'w'))
print('celula', CW, CH, 'base', BASE, 'bytes', len(bio.getvalue()))
bgc = Image.new('RGBA', sheet.size, (201, 162, 192, 255)); bgc.alpha_composite(sheet)
bgc.resize((sheet.width * 4, sheet.height * 4), Image.NEAREST).save('preview_soro.png')
