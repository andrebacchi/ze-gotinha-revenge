#!/bin/sh
# Monta as páginas de teste a partir de src/jogo.html: page.html (sem cartões nem abertura, para os testes de mecânica)
# e page_intro.html (jogo completo). Depois: NODE_PATH=$(npm root -g) node t7.js (e os demais).
cd "$(dirname "$0")" && R=../.. && (cd $R && python3 build.py artifact >/dev/null)
HEAD='<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>body{margin:0;font:14px system-ui}img{max-width:100%}[hidden]{display:none!important}</style></head><body>'
{ printf '%s' "$HEAD"; printf '<script>window.__mgNoIntro=1</script>'; cat "$R/dist/artifact.html"; printf '</body></html>'; } > page.html
{ printf '%s' "$HEAD"; cat "$R/dist/artifact.html"; printf '</body></html>'; } > page_intro.html
