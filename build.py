#!/usr/bin/env python3
"""Monta o jogo a partir de src/.
  python3 build.py            -> index.html e sw.js (site completo, para o GitHub Pages)
  python3 build.py artifact   -> dist/artifact.html (página para publicar como artefato, sem instalação)
O jogo é um arquivo só: código, estilos e todas as artes (em data URI) ficam em src/jogo.html.
A cada atualização publicada, aumente VERSAO: ela aparece na tela de título e renova o cache de quem instalou."""
import os, re, sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
VERSAO = '1.43'
SITE = 'https://andrebacchi.github.io/ze-gotinha-revenge/'
HUB = 'https://andrebacchi.github.io/bacchilab/'
TITULO = "Zé Gotinha's Revenge"
DESCRICAO = 'Jogo de plataforma em 16 bits: o Zé Gotinha enfrenta boatos, fake news e o Tio do Zap para libertar a Vila do Zap da desinformação sobre vacinas.'
ARTEFATO = len(sys.argv) > 1 and sys.argv[1] == 'artifact'

def ler(nome):
    with open(os.path.join(RAIZ, 'src', nome), encoding='utf-8') as f:
        return f.read()

def gravar(caminho, texto):
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(texto)
    print(os.path.relpath(caminho, RAIZ), f'{len(texto.encode()) / 1024:.0f} KB')

qr = re.sub(r'>\s+<', '><', ler('qr.svg').strip()).replace('<svg ', '<svg role="img" aria-label="QR code para andrebacchi.github.io/ze-gotinha-revenge" ')
miolo = (ler('jogo.html')
         .replace('__PWA__', 'false' if ARTEFATO else 'true')
         .replace('__VERSAO__', VERSAO)
         .replace('__QR__', qr)
         .replace('__HUB_ALVO__', ' target="_blank" rel="noopener"' if ARTEFATO else '')
         .replace('__HUB__', HUB))
assert not re.search(r'__[A-Z_]+__', re.sub(r"data:image/[^'\"]+", '', miolo)), 'sobrou marcador sem substituir em jogo.html'

if ARTEFATO:
    os.makedirs(os.path.join(RAIZ, 'dist'), exist_ok=True)
    gravar(os.path.join(RAIZ, 'dist', 'artifact.html'), miolo)
else:
    cabeca, resto = miolo.split('<style>', 1)
    estilo, resto = resto.split('</style>', 1)
    gravar(os.path.join(RAIZ, 'index.html'), f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="{DESCRICAO}">
<meta name="theme-color" content="#0a0f2c">
<meta property="og:title" content="{TITULO}">
<meta property="og:description" content="{DESCRICAO}">
<meta property="og:image" content="{SITE}icons/icon-512.png">
<link rel="manifest" href="manifest.json">
<link rel="icon" type="image/png" href="icons/favicon-64.png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="{TITULO}">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{cabeca}<style>
html,body{{margin:0}}
[hidden]{{display:none!important}}
img{{max-width:100%}}
{estilo}</style>
</head>
<body>
{resto}</body>
</html>
''')
    gravar(os.path.join(RAIZ, 'sw.js'), ler('sw.js').replace('__VERSAO__', VERSAO))
