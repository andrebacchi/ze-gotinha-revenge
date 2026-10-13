# Recortador das folhas da fase 2: fundo de chroma (verde, magenta ou ciano), quadros em grade ou em colunas separadas por vão,
# redução por maioria de cores com contorno refeito. Gera um atlas (tira horizontal) com o retângulo de cada quadro.
# Uso como módulo: atlas = corta(img, fundo, nomes, escala, grade=(linhas, colunas) | None); salva(atlas, 'saida.json')
import json, base64, io
from PIL import Image
import numpy as np, scipy.ndimage as ndi
from scipy.cluster.vq import kmeans2
K = (11, 16, 48)
def mascara_fundo(a, fundo):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    if fundo == 'verde': return (g > 150) & (r < 130) & (b < 130)
    if fundo == 'magenta': return (r > 170) & (b > 170) & (g < 120)
    if fundo == 'ciano': return (g > 170) & (b > 170) & (r < 120)
    raise ValueError(fundo)
def franja(a, fundo):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    if fundo == 'verde': return (g > r + 35) & (g > b + 35)
    if fundo == 'magenta': return (r > g + 50) & (b > g + 50)
    return (g > r + 50) & (b > r + 50)
def corta(caminho, fundo, nomes, escala, grade=None, cores=24, limiar_escuro=45, escalas=None, tapa=True):   # tapa=False mantém vazados os vãos fechados (cordas da passarola)
    a = np.asarray(Image.open(caminho).convert('RGB')).astype(float); H, W = a.shape[:2]
    fg = ndi.binary_opening(~mascara_fundo(a, fundo), iterations=1)
    lum = 0.3 * a[..., 0] + 0.59 * a[..., 1] + 0.11 * a[..., 2]
    dark = fg & ((lum < limiar_escuro) | franja(a, fundo))
    lab, n = ndi.label(fg); sizes = ndi.sum(fg, lab, range(1, n + 1)); cents = ndi.center_of_mass(fg, lab, range(1, n + 1))
    px = a[fg & ~dark]; cent, _ = kmeans2(px[::5], cores, minit='++', seed=5); pal = np.round(cent).astype(int)
    cls = ((a[..., None, :] - pal[None, None]) ** 2).sum(-1).argmin(-1)
    if grade:
        L, C = grade; caixas = [(i // C * H / L, (i // C + 1) * H / L, i % C * W / C, (i % C + 1) * W / C) for i in range(L * C)]
    else:
        colfg = fg.sum(0) > 0; runs = []; x = 0
        while x < W:
            if colfg[x]:
                x0 = x
                while x < W and colfg[x]: x += 1
                runs.append((x0, x))
            else: x += 1
        runs = [rr for rr in runs if rr[1] - rr[0] > 25]; caixas = [(0, H, x0, x1) for x0, x1 in runs]
    assert len(caixas) >= len([nm for nm in nomes if nm]), (len(caixas), len(nomes))
    quadros = {}
    for (y0, y1, x0, x1), nm in zip(caixas, nomes):
        if not nm: continue
        sc = (escalas or {}).get(nm, escala)
        ids = [k + 1 for k in range(n) if sizes[k] > 25 and y0 <= cents[k][0] < y1 and x0 <= cents[k][1] < x1]
        m = np.isin(lab, ids); ys, xs = np.nonzero(m); o = (slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1)); m = m[o]
        dk = dark[o] & m; col = m & ~dk; inner = ndi.binary_fill_holes(m) if tapa else m; h, w = m.shape; nh, nw = max(1, round(h * sc)), max(1, round(w * sc))
        ds = lambda z: np.asarray(Image.fromarray((z * 255).astype(np.uint8)).resize((nw, nh), Image.BOX)).astype(float) / 255
        I = ds(inner); D = ds(dk & inner); votes = np.stack([ds(col & (cls[o] == k)) for k in range(len(pal))], -1)
        body = I >= 0.5; out = np.zeros((nh + 2, nw + 2, 4), np.uint8)
        for y in range(nh):
            for xx in range(nw):
                if body[y, xx]: out[y + 1, xx + 1] = (*K, 255) if D[y, xx] / max(I[y, xx], 1e-6) > 0.55 else (*pal[votes[y, xx].argmax()], 255)
        bm = np.zeros((nh + 2, nw + 2), bool); bm[1:-1, 1:-1] = body
        ring = ndi.binary_dilation(bm, structure=ndi.generate_binary_structure(2, 1)) & ~bm; out[ring] = (*K, 255)
        quadros[nm] = out; print(nm, out.shape[1], 'x', out.shape[0])
    return quadros
def salva(quadros, saida, previa=None, fundo_previa=(201, 162, 192)):
    x = 0; rects = {}; hmax = max(q.shape[0] for q in quadros.values())
    for nm, q in quadros.items(): rects[nm] = [x, 0, q.shape[1], q.shape[0]]; x += q.shape[1] + 1
    sheet = Image.new('RGBA', (x, hmax), (0, 0, 0, 0))
    for nm, q in quadros.items(): sheet.alpha_composite(Image.fromarray(q, 'RGBA'), (rects[nm][0], 0))
    bio = io.BytesIO(); sheet.save(bio, 'PNG', optimize=True)
    json.dump({'rects': rects, 'src': 'data:image/png;base64,' + base64.b64encode(bio.getvalue()).decode()}, open(saida, 'w'))
    print(saida, sheet.size, len(bio.getvalue()), 'bytes')
    if previa:
        bg = Image.new('RGBA', sheet.size, (*fundo_previa, 255)); bg.alpha_composite(sheet); bg.resize((sheet.width * 5, sheet.height * 5), Image.NEAREST).save(previa)
