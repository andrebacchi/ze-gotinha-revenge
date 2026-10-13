# Blocos da fase 2 (grade 4x4 em magenta) e objetos da balança (uma fileira em magenta).
# Blocos inteiros: recorta por dentro do contorno e reduz para 16x16 (o contorno faria linhas de grade ao repetir).
# Blocos parciais e objetos soltos: passam pelo recortador normal (fase2.py), com contorno.
import sys, json
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from PIL import Image
import numpy as np, scipy.ndimage as ndi
from fase2 import corta, salva, mascara_fundo
def bloco(a, fg, caixa, inset=0.045, quant=14):
    y0, y1, x0, x1 = caixa; sub = fg[y0:y1, x0:x1]; ys, xs = np.nonzero(sub)
    t, b, l, r = ys.min() + y0, ys.max() + y0 + 1, xs.min() + x0, xs.max() + x0 + 1
    dy, dx = int((b - t) * inset), int((r - l) * inset)
    sub = a[t + dy:b - dy, l + dx:r - dx].copy(); mg = mascara_fundo(sub, 'magenta') | ((sub[..., 0] > 150) & (sub[..., 2] > 150) & (sub[..., 1] < 110))
    if mg.any(): idx = ndi.distance_transform_edt(mg, return_distances=False, return_indices=True); sub = sub[idx[0], idx[1]]   # franja do fundo vira a cor vizinha
    im = Image.fromarray(sub.astype(np.uint8)).resize((16, 16), Image.BOX)
    im = np.asarray(im.quantize(quant, method=Image.Quantize.MEDIANCUT).convert('RGBA')).copy(); c = im[..., :3].astype(int)
    roxo = (c[..., 0] > c[..., 1] + 14) & (c[..., 2] > c[..., 1] + 14) & (c[..., 2] > 40)   # borda que misturou contorno e magenta: vira a cor vizinha de dentro
    if roxo.any(): idx = ndi.distance_transform_edt(roxo, return_distances=False, return_indices=True); im = im[idx[0], idx[1]]
    return im
img = sys.argv[1]; a = np.asarray(Image.open(img).convert('RGB')).astype(float); H, W = a.shape[:2]
fg = ~mascara_fundo(a, 'magenta')
caixas = [(int(i // 4 * H / 4), int((i // 4 + 1) * H / 4), int(i % 4 * W / 4), int((i % 4 + 1) * W / 4)) for i in range(16)]
nomes = ['calc', 'terra', 'W', 'Wwin', 'Wdoor', 'T', 'C', 'V', 'R', 'K', 'X', 'B', 'spike', 'plank', 'pa', 'barril']
inteiros = {'calc', 'terra', 'W', 'Wwin', 'Wdoor', 'T', 'R', 'K', 'X', 'B'}
q = {nm: bloco(a, fg, caixas[i], 0.085) for i, nm in enumerate(nomes) if nm in inteiros}
k = q['K']; lum = k[..., :3].astype(float).mean(2); fila = int(np.argmax(lum.mean(1)))   # linha mais clara: o trilho
q['K'] = np.roll(k, -max(0, fila - 1), axis=0); print('trilho estava na linha', fila)
# parciais: escala para 16 de largura (a pá e o barril têm tamanho próprio)
largura = {'C': 16, 'V': 16, 'spike': 16, 'plank': 16, 'pa': 24, 'barril': 12}
for i, nm in enumerate(nomes):
    if nm in inteiros: continue
    y0, y1, x0, x1 = caixas[i]; sub = fg[y0:y1, x0:x1]; xs = np.nonzero(sub.any(0))[0]; w = xs.max() - xs.min() + 1
    Image.fromarray(a[y0:y1, x0:x1].astype(np.uint8)).save('_t.png')
    q.update(corta('_t.png', 'magenta', [nm], (largura[nm] - 2) / w))
salva(q, 'tiles_art.json', 'prev_tiles.png')
