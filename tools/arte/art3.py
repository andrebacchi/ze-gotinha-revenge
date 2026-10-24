# Ajuda comum dos recortes da fase 3 (itens, objetos, cenário). Cada objeto sai de uma janela da folha, com escala própria e paleta própria:
# máscara do desenho (por dentro do contorno), redução por média, cor por maioria dentro da paleta do objeto e contorno de 1 px refeito.
import json, base64, io
from PIL import Image
import numpy as np, scipy.ndimage as ndi
from scipy.cluster.vq import kmeans2
K = (11, 16, 48)

class Folha:
    def __init__(self, path, fundo):   # fundo: 'ciano' ou 'magenta'
        self.a = np.asarray(Image.open(path).convert('RGB')).astype(float); a = self.a; r, g, b = a[..., 0], a[..., 1], a[..., 2]
        self.H, self.W = a.shape[:2]
        self.bg = ((g > 180) & (b > 180) & (r < 120)) if fundo == 'ciano' else ((r > 180) & (b > 180) & (g < 110))
        self.fg = ndi.binary_opening(~self.bg, iterations=1)
        self.lum = 0.3 * r + 0.59 * g + 0.11 * b
        franja = ((g > r + 70) & (b > r + 70) & (self.lum > 120)) if fundo == 'ciano' else ((r > g + 35) & (b > g + 35))
        self.dark = self.fg & ((self.lum < 40) | franja)
        self.franja = franja
        self.lab, n = ndi.label(self.fg); self.objs = ndi.find_objects(self.lab); self.area = ndi.sum(self.fg, self.lab, range(1, n + 1))

    def ids(self, x0, y0, x1, y1):
        out = []
        for k, o in enumerate(self.objs):
            if self.area[k] > 150 and x0 <= (o[1].start + o[1].stop) / 2 < x1 and y0 <= (o[0].start + o[0].stop) / 2 < y1: out.append(k + 1)
        return out

    def recorta(self, x0, y0, x1, y1, esc, ncol=18, clip=None, ref=None):
        ids = self.ids(x0, y0, x1, y1); assert ids, (x0, y0, x1, y1)
        ys = slice(min(self.objs[k - 1][0].start for k in ids), max(self.objs[k - 1][0].stop for k in ids))
        xs = slice(min(self.objs[k - 1][1].start for k in ids), max(self.objs[k - 1][1].stop for k in ids))
        m = np.isin(self.lab[ys, xs], ids)
        if clip is not None:
            Y, X = np.mgrid[ys, xs]; m &= clip(X, Y)
        return self.reduz(m, (ys, xs), esc, ncol)

    def reduz(self, m, o, SC, ncol):
        a = self.a[o]; dk = self.dark[o] & m; col = m & ~dk
        px = a[col]; assert len(px) > 20
        cent, _ = kmeans2(px[::max(1, len(px) // 4000)], ncol, minit='++', seed=3); pal = np.round(cent).astype(int)
        pal = np.array([p for p in pal if not (p[1] > p[0] + 70 and p[2] > p[0] + 70 and p[1] > 170)])
        cls = ((a[..., None, :] - pal[None, None]) ** 2).sum(-1).argmin(-1)
        inner = ndi.binary_fill_holes(m); h, w = m.shape; nh, nw = max(1, round(h * SC)), max(1, round(w * SC))
        ds = lambda z: np.asarray(Image.fromarray((z * 255).astype(np.uint8)).resize((nw, nh), Image.BOX)).astype(float) / 255
        I = ds(inner); D = ds(dk & inner); votes = np.stack([ds(col & (cls == k)) for k in range(len(pal))], -1)
        body = I >= 0.5; out = np.zeros((nh + 2, nw + 2, 4), np.uint8)
        for y in range(nh):
            for x in range(nw):
                if body[y, x]: out[y + 1, x + 1] = (*K, 255) if D[y, x] / max(I[y, x], 1e-6) > 0.6 else (*pal[votes[y, x].argmax()], 255)
        bm = np.zeros((nh + 2, nw + 2), bool); bm[1:-1, 1:-1] = body
        out[ndi.binary_dilation(bm, structure=ndi.generate_binary_structure(2, 1)) & ~bm] = (*K, 255)
        return out

    def quadro(self, x0, y0, x1, y1, w=16, h=16, ncol=8):   # bloco quadrado reduzido por média (amostras da máquina e pote premium)
        ids = self.ids(x0, y0, x1, y1); assert len(ids) == 1, ids; o = self.objs[ids[0] - 1]
        crop = self.a[o]; msk = self.fg[o]
        im = np.asarray(Image.fromarray(crop.astype(np.uint8)).resize((w, h), Image.BOX)).astype(float)
        al = np.asarray(Image.fromarray((msk * 255).astype(np.uint8)).resize((w, h), Image.BOX)) >= 128
        px = crop[msk][::3]; cent, _ = kmeans2(px, ncol, minit='++', seed=4)
        q = cent[((im[..., None, :] - cent[None, None]) ** 2).sum(-1).argmin(-1)]
        out = np.zeros((h, w, 4), np.uint8); out[..., :3] = np.round(q); out[..., 3] = al * 255
        out[(out[..., :3].astype(int).sum(-1) < 150) & al] = (*K, 255)
        return out

def empacota(frames, nome, extra=None):
    Wt = sum(f.shape[1] + 1 for f in frames.values()); Ht = max(f.shape[0] for f in frames.values())
    sheet = Image.new('RGBA', (Wt, Ht), (0, 0, 0, 0)); rects = {}; x = 0
    for nm, f in frames.items(): sheet.alpha_composite(Image.fromarray(f, 'RGBA'), (x, 0)); rects[nm] = [x, 0, f.shape[1], f.shape[0]]; x += f.shape[1] + 1
    bio = io.BytesIO(); sheet.save(bio, 'PNG', optimize=True)
    d = {'rects': rects, 'src': 'data:image/png;base64,' + base64.b64encode(bio.getvalue()).decode()}
    if extra: d['info'] = extra
    json.dump(d, open(nome + '_art.json', 'w')); print(nome, 'bytes', len(bio.getvalue()), {k: v[2:] for k, v in rects.items()})
    bgc = Image.new('RGBA', sheet.size, (60, 70, 110, 255)); bgc.alpha_composite(sheet); bgc.resize((sheet.width * 4, sheet.height * 4), Image.NEAREST).save('preview_' + nome + '.png')
