# Chefes da fase 3 (Guru Glow e Prof. Magnus Aurum): folha de 6 poses em fundo magenta, âncora nos pés.
# Uso: python3 chefe3.py folha.png guru|prof [altura em px do quadro mais alto]. Gera <chefe>_art.json e preview_<chefe>.png.
# Separa as figuras pelos 6 maiores componentes (ordenados da esquerda para a direita): objetos soltos (cristal, adesivo, livro, estrelas) ficam de fora.
import sys, os, json, base64, io
from PIL import Image
import numpy as np, scipy.ndimage as ndi
from scipy.cluster.vq import kmeans2
K = (11, 16, 48)
WHO = sys.argv[2]; TARGET = float(sys.argv[3]) if len(sys.argv) > 3 else 46
a = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(float); r, g, b = a[..., 0], a[..., 1], a[..., 2]; H, W = a.shape[:2]
bg = (r > 170) & (b > 170) & (g < 110); fg = ~bg; fg = ndi.binary_opening(fg, iterations=1)
lum = 0.3 * r + 0.59 * g + 0.11 * b
dark = fg & ((lum < 32) | ((r > g + 70) & (b > g + 70)))          # contorno e franja magenta
lab, n = ndi.label(fg); sizes = ndi.sum(fg, lab, range(1, n + 1)); cents = ndi.center_of_mass(fg, lab, range(1, n + 1))
np.random.seed(3); px = a[fg & ~dark]; cent, _ = kmeans2(px[::5], int(os.environ.get('NCOR', 40)), minit='++', seed=3); pal = np.round(cent).astype(int)
pal = np.array([p for p in pal if not (p[0] > p[1] + 70 and p[2] > p[1] + 70)])
cls = ((a[..., None, :] - pal[None, None]) ** 2).sum(-1).argmin(-1)
NAMES = {'guru': ['idle', 'throw', 'vela', 'adesivo', 'medita', 'hurt'], 'prof': ['idle', 'walk', 'throw', 'graph', 'tired', 'hurt']}
names = NAMES[WHO]
order = sorted(np.argsort(-sizes)[:len(names)], key=lambda k: cents[k][1]); print('componentes', [int(sizes[k]) for k in order])
objs = ndi.find_objects(lab); SC = TARGET / max(objs[k][0].stop - objs[k][0].start for k in order); print('escala', round(SC, 4))
frames = []
for k0, nm in zip(order, names):
    ids = [k0 + 1]
    m = np.isin(lab, ids); ys, xs = np.nonzero(m); o = (slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1)); m = m[o]
    dk = dark[o] & m; col = m & ~dk; inner = ndi.binary_fill_holes(m); h, w = m.shape; nh, nw = round(h * SC), round(w * SC)
    ds = lambda z: np.asarray(Image.fromarray((z * 255).astype(np.uint8)).resize((nw, nh), Image.BOX)).astype(float) / 255
    I = ds(inner); D = ds(dk & inner); votes = np.stack([ds(col & (cls[o] == k)) for k in range(len(pal))], -1)
    body = I >= 0.5; edge = ~ndi.binary_erosion(body, iterations=2, border_value=0); DET = float(os.environ.get('DET', 0.22));   # detalhes escuros do rosto (olhos, boca) longe da borda: limiar baixo
    out = np.zeros((nh + 2, nw + 2, 4), np.uint8)
    for y in range(nh):
        for xx in range(nw):
            if body[y, xx]: out[y + 1, xx + 1] = (*K, 255) if D[y, xx] / max(I[y, xx], 1e-6) > (0.55 if edge[y, xx] else DET) else (*pal[votes[y, xx].argmax()], 255)
    # rosto refeito à mão: acha olhos e boca no desenho original (buracos escuros dentro da pele, na cabeça) e pinta marcas nítidas no quadro reduzido
    cr = a[o]; rr, gg, bb = cr[..., 0], cr[..., 1], cr[..., 2]
    skin = ((rr > 220) & (gg > 130) & (gg < 190) & (bb > 50) & (bb < 115)) if WHO == 'prof' else ((rr > 225) & (gg > 165) & (gg < 215) & (bb > 85) & (bb < 150))
    skin &= m; top = np.zeros_like(skin); top[:max(int(h * 0.34), 1)] = True; skin &= top
    sl, sn = ndi.label(skin)
    if sn:
        big = 1 + int(np.argmax(ndi.sum(skin, sl, range(1, sn + 1)))); face = ndi.binary_fill_holes(ndi.binary_closing(sl == big, iterations=3))
        lum2 = 0.3 * rr + 0.59 * gg + 0.11 * bb; blue = (bb > rr + 20) & (bb > 110); red = (rr > 150) & (gg < 110) & (bb < 120)
        feat = face & ~skin & (lum2 < 95 | blue | red) if False else face & ~skin & ((lum2 < 95) | blue | red)
        feat = ndi.binary_opening(feat, iterations=1) | (feat & (lum2 < 60))
        fy, fx = np.nonzero(face); fh = fy.max() - fy.min() + 1; fy0 = fy.min()
        fl, fn = ndi.label(feat); marks = []
        for k in range(1, fn + 1):
            ys2, xs2 = np.nonzero(fl == k)
            if len(ys2) < 6: continue
            cy, cx = ys2.mean(), xs2.mean(); w2, h2 = xs2.max() - xs2.min() + 1, ys2.max() - ys2.min() + 1
            marks.append((cx, cy, w2, h2, len(ys2), (cy - fy0) / fh, bool(red[fl == k].mean() > .4)))
        marks.sort(key=lambda z: -z[4]); eyes = [z for z in marks if z[5] < 0.62 and not z[6]][:2]; mouth = [z for z in marks if z[5] >= 0.55 or z[6]][:1]
        print('  rosto', nm, 'olhos', len(eyes), 'boca', len(mouth))
        ey = (47, 95, 200) if WHO == 'guru' else K
        for cx, cy, w2, h2, ar, rel, isr in eyes:
            px_, py_ = int(cx * SC) + 1, int(cy * SC) + 1
            if 0 <= py_ < out.shape[0] and 0 <= px_ < out.shape[1]: out[py_, px_] = (*K, 255)
            if h2 * SC >= 1.4 and py_ + 1 < out.shape[0]: out[py_ + 1, px_] = (*K, 255)
        if not eyes and mouth and WHO == 'guru':   # olhos azuis pequenos demais para achar: dois pontos acima da boca (rosto de três quartos, para a direita)
            mx, my = int(mouth[0][0] * SC) + 1, int(mouth[0][1] * SC) + 1
            for ex in (mx - 1, mx + 2):
                if 0 <= my - 3 < out.shape[0] and 0 <= ex < out.shape[1]: out[my - 3, ex] = (*K, 255); out[my - 2, ex] = (60, 100, 190, 255)
        for cx, cy, w2, h2, ar, rel, isr in mouth:
            px_, py_ = int(cx * SC) + 1, int(cy * SC) + 1; mc = (150, 40, 50) if WHO == 'prof' else (190, 70, 80); n2 = max(2, min(4, int(round(w2 * SC))))
            for d in range(n2):
                x2 = px_ - n2 // 2 + d
                if 0 <= py_ < out.shape[0] and 0 <= x2 < out.shape[1]: out[py_, x2] = (*mc, 255)
    bm = np.zeros((nh + 2, nw + 2), bool); bm[1:-1, 1:-1] = body
    ring = ndi.binary_dilation(bm, structure=ndi.generate_binary_structure(2, 1)) & ~bm; out[ring] = (*K, 255)
    # âncora: pés (fundo do recorte) e o centro de massa na horizontal
    pb = h; pcx = np.nonzero(m)[1].mean()
    frames.append(dict(name=nm, img=out, ax=pcx * SC + 1, base=pb * SC + 1)); print(nm, out.shape[:2], 'ax', round(pcx * SC + 1, 1), 'base', round(pb * SC + 1, 1))
half = max(max(int(np.ceil(f['ax'])) for f in frames), max(f['img'].shape[1] - int(np.floor(f['ax'])) for f in frames)) + 1; CW = half * 2
up = max(int(np.ceil(f['base'])) for f in frames) + 1; down = max(f['img'].shape[0] - int(np.floor(f['base'])) for f in frames) + 1; CH = up + down; BASE = up
sheet = Image.new('RGBA', (CW * len(frames), CH), (0, 0, 0, 0))
for i, f in enumerate(frames): sheet.alpha_composite(Image.fromarray(f['img'], 'RGBA'), (i * CW + half - int(round(f['ax'])), BASE - int(round(f['base']))))
bio = io.BytesIO(); sheet.save(bio, 'PNG', optimize=True); sheet.save(''+WHO+'_sheet.png')
json.dump({'cw': CW, 'ch': CH, 'base': BASE, 'names': names, 'src': 'data:image/png;base64,' + base64.b64encode(bio.getvalue()).decode()}, open(WHO + '_art.json', 'w'))
print('celula', CW, CH, 'base', BASE, 'bytes', len(bio.getvalue()))
bgc = Image.new('RGBA', sheet.size, (201, 162, 192, 255)); bgc.alpha_composite(sheet)
bgc.resize((sheet.width * 4, sheet.height * 4), Image.NEAREST).save('preview_' + WHO + '.png')
