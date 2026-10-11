# Zé Gotinha's Revenge: guia de manutenção

Jogo do BACCHI LAB (seção "Jogos e sátiras"). Leia também o `CLAUDE.md` do repositório `bacchilab`, que traz as regras gerais dos apps do André.
Publicação: GitHub Pages, branch `main`, raiz. Endereço: https://andrebacchi.github.io/ze-gotinha-revenge/
Pré-visualização como artefato (privada, do André): https://claude.ai/artifact/F7Wzi36G24LKyR5uPZKEQG

Jogo de plataforma em estilo 16 bits (Mega Drive). O Zé Gotinha enfrenta a desinformação sobre vacinas.
Está em construção: hoje tem a fase 1 (Vila do Zap, chefão Tio do Zap); o André quer novas fases, cada uma com um chefão que represente um obstáculo à vacinação.

## Estrutura

- `src/jogo.html` é a fonte: um arquivo só, com estilos, marcação, código e todas as artes em data URI. Não tem dependência além das fontes do Google.
  `sh build.sh` gera `index.html` e `sw.js` na raiz (arquivos gerados: não edite à mão). `sh build.sh artifact` gera `dist/artifact.html`, a versão de artefato
  (sem instalação nem service worker; o link do BACCHI LAB abre em nova aba). O build troca os marcadores `__PWA__`, `__VERSAO__`, `__QR__`, `__HUB__` e `__HUB_ALVO__`.
- `src/qr.svg`: QR code do endereço do jogo (fixo; gerado com o `qrcode.js` do repositório `bacchilab`, nível M, margem de 2 módulos).
- `icons/`: ícones do app. `tools/icone.py` gera todos a partir do rosto do Zé (quadro parado do sprite, `tools/ze_2x.png` e `tools/head_1.png`) sobre o céu do jogo.
- `tools/arte/`: scripts usados para recortar e reduzir as artes (chroma key, redução por maioria, contorno refeito, empacotamento em data URI).
  Servem de referência: dependem das imagens originais, que ficam com o André e não estão no repositório.
- `tools/testes/`: testes com Playwright. `sh montar.sh` gera `page.html` (sem cartões nem abertura, para testar mecânica) e `page_intro.html` (jogo completo);
  depois `NODE_PATH=$(npm root -g) node t7.js` e os demais. O jogo expõe `window.__mg = { st, mode, keys, step, start, bossStart, tileAt, answer, introStart }`
  e respeita `window.__mgNoIntro` (pula abertura e cartões).

## Toda atualização

- Aumente `VERSAO` no `build.py`: aparece na tela de título e dá nome ao cache (`ze-gotinha-revenge-app-<versão>`).
- Rode `sh build.sh` e publique `index.html` e `sw.js` junto com a fonte. Para atualizar o artefato, publique `dist/artifact.html` no link acima.
- Teste em 390 px (celular em pé), 800 × 390 (deitado) e 1280 px, sem rolagem horizontal. O proxy da sessão bloqueia `fonts.googleapis.com` e `github.io`:
  teste com `python3 -m http.server` + Playwright e peça ao André para conferir o site no ar.
- Não dá para ver animação em movimento nem sentir a dificuldade pelos testes: diga isso ao André e peça para ele jogar.
- Commits com autor "André Demambre Bacchi".

## Como o jogo funciona

- **Tela:** canvas 2D com resolução interna de 320 × 180, ampliado por fator inteiro, sem suavização. Blocos de 16 px; a fase tem 176 × 14 blocos e o chão fica na linha 12.
  Laço fixo de 60 passos por segundo. Telas e cartões são HTML por cima do canvas.
- **Fase:** `buildLevel()` monta o mapa com os auxiliares `hl`, `vl`, `set`, `pit`, `water`, `gota(s)`, `syr`, `mplat`, `E`, `Q`, `gate`.
  Blocos: `#` chão, `B` tijolo, `?` surpresa, `U` usado, `=` madeira (só segura por cima), `^` espinhos, `G` grade, `M`/`F` mito e fato, `~` água, `L` vitória-régia.
- **Artes:** cada conjunto tem um objeto com medidas e a folha em data URI (`ZE_ART`, `ZE_BIG`, `EXTRA_ART`, `JAC_ART`, `ITEM_ART`, `BOSS_ART`, `ENEMY_ART`, `SCENE_ART`, `BG_ART`).
  Os desenhos feitos por código no começo continuam como reserva enquanto as imagens carregam.
- **Fluxo de arte combinado com o André:** eu escrevo o prompt em inglês, ele gera a imagem em outra ferramenta e devolve; eu recorto, reduzo e encaixo.
  Fundo magenta `#FF00FF` (verde ou amarelo quando o desenho tem rosa ou roxo). Detalhes finos somem na redução: olhos, símbolos e blocos de 16 px costumam ser refeitos à mão com as cores da arte.
- **Estado:** tudo em `st`. Placar só no aparelho (localStorage `mg-placar`, `mg-nome`, `mg-mudo`).

## Regras do jogo (decisões do André)

- **Vida como no Mario:** no tamanho original, um golpe derruba. O SUS deixa o Zé "sarado" (não escreva "bombado" nos textos): ele aguenta um golpe e volta ao tamanho original. O escudo de imunidade é uma proteção extra, gasta antes do SUS.
- **Gotas** são coletáveis e valem pontos; qualquer morte zera as gotas juntadas.
- **Seringas:** no máximo 3; repostas pela fase e nos postos. A dose de reforço dá tiro triplo sem gastar por 10 segundos.
- **Jacaré (montaria):** nasce do ovo no ninho. Atravessa a água nadando (o Zé sozinho se afoga). Qualquer golpe, em terra ou na água, faz o jacaré fugir: ele corre, não para na beirada,
  nada se cair na água e some se cair no buraco (o ovo volta ao ninho). Pulo de novo no ar, montado, é o pulo duplo: o Zé salta mais alto e desce, e o jacaré fica parado esperando.
  Há três plataformas altas que só o pulo duplo alcança (conferido por força bruta em `tools/testes/t37.js`). Com um jacaré, outro ovo vira bônus.
- **Mito ou fato:** três portões. A afirmação aparece, o jogador tem 10 segundos e responde batendo a cabeça no bloco M ou F. Erro ou tempo esgotado soltam boatos e trocam a afirmação.
  O resultado pausa o jogo com um cartão de explicação.
- **Cartões de apresentação:** na primeira vez que cada inimigo, item, o jacaré e o portão aparecem, o jogo congela, dá zoom e explica. Voltam a cada partida nova.
- **Abertura da fase:** a câmera desce do céu com o nome da fase. A tela de título não mostra nome de fase nem controles; os controles ficam no botão CONTROLES.
- **Fim:** ao vencer o chefão aparece "Em construção" (novas fases em breve) e depois a pontuação.
- **Pontuação:** gotas 10, boato 50, fake news 80, vírus 100, chefão 1000, power-up 100, portão 600/200/50 conforme os erros, tempo até 2000. Inimigos soltos por erro e os da arena não pontuam.
- **Textos:** na voz do André: diretos, ironia seca, fato concreto com data e lugar, sem travessão, sem rótulo solto abrindo frase e sem contraste de fórmula ("não X, mas Y").
  Os fatos das explicações do mito ou fato foram escritos sem checar fonte na hora e aguardam revisão dele.
- **Personagem:** o Zé Gotinha é do Ministério da Saúde (criado por Darlan Rosa). A tela de resultado traz o aviso de jogo educativo independente, sem vínculo oficial.

## Pendências e ideias em aberto

- Músicas: o André vai gerar três faixas em estilo 16 bits (fase, título e luta de chefe, esta para todos os chefões). Ainda não há música no jogo, só efeitos sintetizados.
- Placar online: hoje é só no aparelho. Fora do artefato dá para usar um banco externo (sugestão feita: Firebase); o André ainda não decidiu.
- Cartões de apresentação só na primeira partida do aparelho (oferecido, sem resposta).
- Revisão do André: textos do bestiário e das explicações; se 10 segundos bastam para as afirmações mais longas; dificuldade do golpe sobre a água.
- Novas fases: ainda sem roteiro. O código tem `PHASE = { n: 1, name: 'VILA DO ZAP' }` e uma fase só em `buildLevel()`.
