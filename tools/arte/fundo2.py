# Fundo da fase 2: céu (imagem inteira, reduzida para 320x180) e faixas em magenta (nuvens, serra, muro), cada faixa reduzida pela mesma escala.
# Uso: python3 fundo2.py ceu.png faixas.png escala nomes...   ->  fundo2.json
import sys, json, base64, io
from PIL import Image
import numpy as np, scipy.ndimage as ndi
def png(im): b = io.BytesIO(); im.save(b, 'PNG', optimize=True); return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()
def quant(im, n):   # reduz cores mantendo a transparência
    rgb = im.convert('RGB').quantize(n, method=Image.Quantize.MEDIANCUT).convert('RGB'); out = rgb.convert('RGBA'); out.putalpha(im.getchannel('A')); return out
ceu, faixas, sc, nomes = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4:]
out = {'ceu': png(quant(Image.open(ceu).convert('RGBA').resize((320, 180), Image.BOX), 12))}
a = np.asarray(Image.open(faixas).convert('RGB')).astype(float); r, g, b = a[..., 0], a[..., 1], a[..., 2]
fg = ~((r > 170) & (b > 170) & (g < 120)); fg = ndi.binary_opening(fg, iterations=2)
rows = fg.mean(1) > 0.01; bands = []; y = 0; H = len(rows)
while y < H:
    if rows[y]:
        y0 = y
        while y < H and rows[y]: y += 1
        if y - y0 > 20: bands.append((y0, y))
    else: y += 1
print('faixas', bands); assert len(bands) == len(nomes)
for (y0, y1), nm in zip(bands, nomes):
    crop = a[y0:y1]; m = fg[y0:y1]; h, w = m.shape; nw, nh = round(w * sc), round(h * sc)
    # cor: média só dos pixels do desenho (o magenta não contamina a borda)
    num = np.stack([np.asarray(Image.fromarray((crop[..., c] * m).astype(np.float32), 'F').resize((nw, nh), Image.BOX)) for c in range(3)], -1)
    den = np.asarray(Image.fromarray(m.astype(np.float32), 'F').resize((nw, nh), Image.BOX))
    rgb = num / np.maximum(den, 1e-6)[..., None]; alpha = (den >= 0.5) * 255
    im = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), alpha]).astype(np.uint8), 'RGBA')
    im = quant(im, 20); out[nm] = png(im); print(nm, im.size)
json.dump(out, open('fundo2.json', 'w'))
