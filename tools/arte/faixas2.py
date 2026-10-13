# Faixas em magenta reduzidas por média só dos pixels do desenho (o magenta não contamina as bordas).
# Uso: python3 faixas2.py imagem.png escala saida.json [emenda]   (emenda: junta as faixas lado a lado, alinhadas pela base)
import sys, json, base64, io
from PIL import Image
import numpy as np, scipy.ndimage as ndi
def png(im): b = io.BytesIO(); im.save(b, 'PNG', optimize=True); return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()
img, sc, saida = sys.argv[1], float(sys.argv[2]), sys.argv[3]; emenda = len(sys.argv) > 4
a = np.asarray(Image.open(img).convert('RGB')).astype(float); r, g, b = a[..., 0], a[..., 1], a[..., 2]
fg = ndi.binary_opening(~((r > 170) & (b > 170) & (g < 120)), iterations=2)
rows = fg.mean(1) > 0.01; bands = []; y = 0; H = len(rows)
while y < H:
    if rows[y]:
        y0 = y
        while y < H and rows[y]: y += 1
        if y - y0 > 20: bands.append((y0, y))
    else: y += 1
ims = []
for y0, y1 in bands:
    crop = a[y0:y1]; m = fg[y0:y1]; h, w = m.shape; nw, nh = round(w * sc), round(h * sc)
    num = np.stack([np.asarray(Image.fromarray((crop[..., c] * m).astype(np.float32), 'F').resize((nw, nh), Image.BOX)) for c in range(3)], -1)
    den = np.asarray(Image.fromarray(m.astype(np.float32), 'F').resize((nw, nh), Image.BOX))
    im = Image.fromarray(np.dstack([np.clip(num / np.maximum(den, 1e-6)[..., None], 0, 255), (den >= 0.5) * 255]).astype(np.uint8), 'RGBA')
    rgb = im.convert('RGB').quantize(28, method=Image.Quantize.MEDIANCUT).convert('RGB').convert('RGBA'); rgb.putalpha(im.getchannel('A')); ims.append(rgb)
    print('faixa', (y0, y1), rgb.size)
if emenda:
    W = sum(i.width for i in ims); Hh = max(i.height for i in ims); out = Image.new('RGBA', (W, Hh), (0, 0, 0, 0)); x = 0
    for i in ims: out.alpha_composite(i, (x, Hh - i.height)); x += i.width
    ims = [out]
row = np.asarray(ims[0])[-1]; row = row[row[:, 3] > 0][:, :3]; v, c = np.unique(row, axis=0, return_counts=True); fill = '#%02x%02x%02x' % tuple(v[c.argmax()])
json.dump({'src': png(ims[0]), 'w': ims[0].width, 'h': ims[0].height, 'fill': fill}, open(saida, 'w')); print(saida, ims[0].size, fill)
