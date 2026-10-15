# Fase 3: fundos da recepção (faixa de cima) e do lounge (faixa de baixo). Corta duas baias entre centros de coluna, para emendar,
# reduz, limita a paleta e escurece um pouco. Uso: python3 fundo3.py fundo3.png [escala]. Gera fundo3_art.json e preview_fundo3.png.
import sys, json, base64, io
from PIL import Image
import numpy as np
SC = float(sys.argv[2]) if len(sys.argv) > 2 else 0.46
im = Image.open(sys.argv[1]).convert('RGB'); W, H = im.size; a = np.asarray(im).astype(float)
dark = a.sum(-1) < 120; rows = np.nonzero(dark[:, W // 4: 3 * W // 4].mean(1) > .8)[0]   # linha preta que separa as faixas
sep = int(np.median(rows)) if len(rows) else H // 2
def seam(y0, y1, x0, guess):   # x1 perto de guess cuja coluna de pixels mais se parece com a de x0 (a emenda some)
    ref = a[y0:y1, x0 - 2:x0 + 3]; best = min(range(guess - 20, guess + 21), key=lambda x: np.abs(a[y0:y1, x - 2:x + 3] - ref).mean()); return best
out = {}
for nm, y0, y1 in (('recep', 0, sep - 2), ('lounge', sep + 4, H)):
    x0 = round(585 * W / 2000); x1 = seam(y0, y1, x0, round(1457 * W / 2000)); print(nm, 'corte', x0, x1)   # duas baias, de centro de coluna a centro de coluna
    crop = im.crop((x0, y0, x1, y1))
    w, h = round((x1 - x0) * SC), round((y1 - y0) * SC); small = crop.resize((w, h), Image.BOX)
    small = small.quantize(48, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert('RGB')
    arr = (np.asarray(small).astype(float) * .8).round().astype(np.uint8)   # um pouco mais escuro: o fundo não compete com o Zé
    img = Image.fromarray(arr); bio = io.BytesIO(); img.save(bio, 'PNG', optimize=True)
    out[nm] = {'w': w, 'h': h, 'src': 'data:image/png;base64,' + base64.b64encode(bio.getvalue()).decode()}; print(nm, w, h, len(bio.getvalue()))
    img.resize((w * 3, h * 3), Image.NEAREST).save('preview_fundo3_' + nm + '.png')
json.dump(out, open('fundo3_art.json', 'w'))
