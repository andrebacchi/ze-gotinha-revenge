# Fase 3: recepcionista (parado, arremesso), cartão VIP e as cinco gotinhas de grife em dois quadros, fundo ciano.
# Uso: python3 grife.py grife.png [escala]. Gera grife_art.json (atlas em data URI) e preview_grife.png.
import sys, json, base64, io
from PIL import Image
import numpy as np, scipy.ndimage as ndi
from scipy.cluster.vq import kmeans2
K = (11, 16, 48); SC = float(sys.argv[2]) if len(sys.argv) > 2 else 0.06
a = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(float); r, g, b = a[..., 0], a[..., 1], a[..., 2]
bg = (g > 180) & (b > 180) & (r < 120); fg = ndi.binary_opening(~bg, iterations=1)
lum = 0.3 * r + 0.59 * g + 0.11 * b
dark = fg & ((lum < 40) | ((g > r + 70) & (b > r + 70) & (lum > 120)))   # contorno e franja ciana
lab, n = ndi.label(fg); objs = ndi.find_objects(lab); area = ndi.sum(fg, lab, range(1, n + 1))
boxes = [[o[0].start, o[0].stop, o[1].start, o[1].stop, [k + 1]] for k, o in enumerate(objs) if area[k] > 150]
merged = True   # junta pedaços próximos (coroa, pés) num objeto só
while merged:
    merged = False
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            A, B = boxes[i], boxes[j]
            if A[0] - 10 < B[1] and B[0] - 10 < A[1] and A[2] - 10 < B[3] and B[2] - 10 < A[3]:
                boxes[i] = [min(A[0], B[0]), max(A[1], B[1]), min(A[2], B[2]), max(A[3], B[3]), A[4] + B[4]]; del boxes[j]; merged = True; break
        if merged: break
boxes.sort(key=lambda B: (round((B[0] + B[1]) / 2 / 300), B[2]))
print(len(boxes), [(B[0], B[2], B[1] - B[0], B[3] - B[2]) for B in boxes])
if len(boxes) == 12:   # o cartão veio colado no arremesso pelos rastros: separa o maior pedaço da ponta direita
    B = boxes[1]; right = [k for k in B[4] if objs[k - 1][1].start > B[2] + 0.75 * (B[3] - B[2])]
    card = max(right, key=lambda k: area[k - 1]); o = objs[card - 1]; B[4] = [k for k in B[4] if k not in right]
    B[3] = max(objs[k - 1][1].stop for k in B[4]); boxes.insert(2, [o[0].start, o[0].stop, o[1].start, o[1].stop, [card]])
names = ['ridle', 'rthrow', 'card'] + ['g%da' % v for v in range(5)] + ['g%db' % v for v in range(5)]
assert len(boxes) == 13, len(boxes)
np.random.seed(3); px = a[fg & ~dark]; cent, _ = kmeans2(px[::5], 28, minit='++', seed=3); pal = np.round(cent).astype(int)
pal = np.array([p for p in pal if not (p[1] > p[0] + 70 and p[2] > p[0] + 70 and p[1] > 170)])
cls = ((a[..., None, :] - pal[None, None]) ** 2).sum(-1).argmin(-1)
frames = {}
for B, nm in zip(boxes, names):
    o = (slice(B[0], B[1]), slice(B[2], B[3])); m = np.isin(lab[o], B[4])
    dk = dark[o] & m; col = m & ~dk; inner = ndi.binary_fill_holes(m); h, w = m.shape; nh, nw = max(1, round(h * SC)), max(1, round(w * SC))
    ds = lambda z: np.asarray(Image.fromarray((z * 255).astype(np.uint8)).resize((nw, nh), Image.BOX)).astype(float) / 255
    I = ds(inner); D = ds(dk & inner); votes = np.stack([ds(col & (cls[o] == k)) for k in range(len(pal))], -1)
    body = I >= 0.5; out = np.zeros((nh + 2, nw + 2, 4), np.uint8)
    for y in range(nh):
        for x in range(nw):
            if body[y, x]: out[y + 1, x + 1] = (*K, 255) if D[y, x] / max(I[y, x], 1e-6) > 0.6 else (*pal[votes[y, x].argmax()], 255)
    bm = np.zeros((nh + 2, nw + 2), bool); bm[1:-1, 1:-1] = body
    out[ndi.binary_dilation(bm, structure=ndi.generate_binary_structure(2, 1)) & ~bm] = (*K, 255)
    if nm[0] == 'g':   # o rosto some na redução: olhos semicerrados e sorriso refeitos à mão, virados para a direita
        hh, ww = out.shape[:2]; ys = np.nonzero(out[..., 3].any(1))[0]; y0 = ys.min() + round((ys.max() - ys.min()) * (0.5 if nm != 'g2b' else 0.56)); x0 = ww - 8
        if nm.startswith('g4'): y0 += 1
        for dx in (0, 1, 3, 4): out[y0, x0 + dx] = (*K, 255)
        out[y0 + 1, x0] = out[y0 + 1, x0 + 3] = (255, 255, 255, 255); out[y0 + 1, x0 + 1] = out[y0 + 1, x0 + 4] = (*K, 255)
        for dx in (1, 2, 3): out[y0 + 3, x0 + dx] = (*K, 255)
        out[y0 + 2, x0 + 4] = (*K, 255)
    frames[nm] = out; print(nm, out.shape[:2])
W = sum(f.shape[1] + 1 for f in frames.values()); H = max(f.shape[0] for f in frames.values())
sheet = Image.new('RGBA', (W, H), (0, 0, 0, 0)); rects = {}; x = 0
for nm, f in frames.items(): sheet.alpha_composite(Image.fromarray(f, 'RGBA'), (x, 0)); rects[nm] = [x, 0, f.shape[1], f.shape[0]]; x += f.shape[1] + 1
bio = io.BytesIO(); sheet.save(bio, 'PNG', optimize=True)
json.dump({'rects': rects, 'src': 'data:image/png;base64,' + base64.b64encode(bio.getvalue()).decode()}, open('grife_art.json', 'w'))
print('bytes', len(bio.getvalue()))
bgc = Image.new('RGBA', sheet.size, (230, 224, 207, 255)); bgc.alpha_composite(sheet); bgc.resize((sheet.width * 4, sheet.height * 4), Image.NEAREST).save('preview_grife.png')
