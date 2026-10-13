# Zé Gotinha's Revenge: guia de manutenção

Jogo do BACCHI LAB (seção "Jogos e sátiras"). Leia também o `CLAUDE.md` do repositório `bacchilab`, que traz as regras gerais dos apps do André.
Publicação: GitHub Pages, branch `main`, raiz. Endereço: https://andrebacchi.github.io/ze-gotinha-revenge/
Pré-visualização como artefato (privada, do André): https://claude.ai/artifact/F7Wzi36G24LKyR5uPZKEQG

Jogo de plataforma em estilo 16 bits (Mega Drive). O Zé Gotinha enfrenta a desinformação sobre vacinas.
Está em construção: fase 1 (Vila do Zap, chefão Tio do Zap, tema desinformação) e fase 2 em esboço no ramo `fase-2` (Arraial do Antigamente, chefão Barão do Sempre Foi Assim, tema apelo à tradição).
Cada fase tem um chefão que representa um obstáculo à vacinação.

## Estrutura

- `src/jogo.html` é a fonte: um arquivo só, com estilos, marcação, código e todas as artes em data URI. Não tem dependência além das fontes do Google.
  `sh build.sh` gera `index.html` e `sw.js` na raiz (arquivos gerados: não edite à mão). `sh build.sh artifact` gera `dist/artifact.html`, a versão de artefato
  (sem instalação nem service worker; o link do BACCHI LAB abre em nova aba). O build troca os marcadores `__PWA__`, `__VERSAO__`, `__QR__`, `__HUB__` e `__HUB_ALVO__`.
- `audio/`: músicas em MP3 (96 kbps). `titulo.mp3` toca na tela de título, `fase1.mp3` na fase, `chefe.mp3` em toda luta de chefe e `vitoria.mp3` (uma vez, sem laço) na comemoração do fim de fase. No artefato, publique os quatro como arquivos de apoio (`audio/...`).
- `src/qr.svg`: QR code do endereço do jogo (fixo; gerado com o `qrcode.js` do repositório `bacchilab`, nível M, margem de 2 módulos).
- `icons/`: ícones do app. `tools/icone.py` gera todos a partir do rosto do Zé (quadro parado do sprite, `tools/ze_2x.png` e `tools/head_1.png`) sobre o céu do jogo.
- `tools/arte/`: scripts usados para recortar e reduzir as artes (chroma key, redução por maioria, contorno refeito, empacotamento em data URI).
  Servem de referência: dependem das imagens originais, que ficam com o André e não estão no repositório.
- `tools/testes/`: testes com Playwright. `sh montar.sh` gera `page.html` (sem cartões nem abertura, para testar mecânica) e `page_intro.html` (jogo completo);
  depois `NODE_PATH=$(npm root -g) node t7.js` e os demais. O jogo expõe `window.__mg = { st, mode, keys, step, start, bossStart, tileAt, answer, introStart }`
  e respeita `window.__mgNoIntro` (pula abertura, cartões e a comemoração do fim) e `window.__mgNoSave` (não grava jogo salvo).

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
  O painel de mensagens fica embaixo do palco só no celular em pé (`pointer: coarse` com sobra de altura). No computador e no celular deitado (`.app.wide`) as mensagens e a pergunta
  do portão ficam sobre o jogo, como o André pediu. Palco de até 1600 px fora da tela cheia.
  **Tela cheia:** pílula "Tela cheia" no título, botão no canto do jogo e tecla F (`toggleFull()`, classe `.app.full`). Some onde o navegador não deixa (iPhone).
- **Fase:** `buildLevel()` monta o mapa com os auxiliares `hl`, `vl`, `set`, `pit`, `water`, `gota(s)`, `syr`, `mplat`, `E`, `Q`, `gate`.
  Blocos: `#` chão, `B` tijolo, `?` surpresa, `U` usado, `=` madeira (só segura por cima), `^` espinhos, `G` grade, `M`/`F` mito e fato, `~` água, `L` vitória-régia.
- **Artes:** cada conjunto tem um objeto com medidas e a folha em data URI (`ZE_ART`, `ZE_BIG`, `EXTRA_ART`, `JAC_ART`, `ITEM_ART`, `BOSS_ART`, `ENEMY_ART`, `SCENE_ART`, `BG_ART`, `AURA_ART`).
  Os desenhos feitos por código no começo continuam como reserva enquanto as imagens carregam.
- **Fluxo de arte combinado com o André:** eu escrevo o prompt em inglês, ele gera a imagem em outra ferramenta e devolve; eu recorto, reduzo e encaixo.
  Fundo magenta `#FF00FF` (verde ou amarelo quando o desenho tem rosa ou roxo). Detalhes finos somem na redução: olhos, símbolos e blocos de 16 px costumam ser refeitos à mão com as cores da arte.
- **Escudo e bolha de eco:** `AURA_ART` tem três linhas: `s` (escudo do Zé no tamanho original), `b` (sarado ou montado) e `eco` (bolha do chefão). Em cada uma, 3 quadros de laço e depois os de estourar.
  Os anéis foram refeitos pixel a pixel com as cores e o desenho das artes do André (`tools/arte/escudo.py`): reduzir um aro de 40 px de espessura para 5 px apaga sombra, brilho e cruz. Só os estilhaços do escudo vêm da redução direta.
  `auraFx()` toca os quadros de estourar como efeito solto (`st.fx` com `seq`). Quando o chefão se levanta, `b.bubIn` mostra os mesmos quadros de trás para frente. Sem a imagem carregada, vale o círculo desenhado por código.
- **Música:** `MUSIC` mapeia nome → arquivo e `music(nome)` troca a faixa (elemento `<audio>` em laço, volume 0,5). A do título só começa no primeiro toque ou tecla, porque o navegador não deixa antes.
  `bossStart()` chama `music('boss')` (a mesma faixa serve para todos os chefões, por decisão do André). Ao renascer volta a da fase. Ao vencer, silêncio na câmera lenta e a fanfarra (`music('vic')`) quando o Zé pousa para comemorar; ela segue tocando na tela seguinte até acabar.
  `vitoria.mp3` saiu de uma faixa de 2 minutos do gerador (original "Victory_Fanfare"): os 4 primeiros compassos (152 BPM, até 6,32 s) emendados no ataque do acorde final (122,32 s), que soa até o fim. O acorde cai no passo 379 depois do pouso, e `V_RISE_LEN` faz a câmera chegar ao céu nessa hora.
  As faixas vieram de um gerador e não fecham laço: foram aparadas e terminam com um fade de 2 segundos antes de recomeçar (`ffmpeg ... afade`).
  Sem internet: a página guarda os MP3 inteiros no cache `ze-gotinha-revenge-fixos-v1` e o `sw.js` responde os pedidos com `Range` cortando o arquivo guardado (`pedaco()`); sem isso o Safari não toca.
- **Efeitos sonoros:** `sfx('nome')`. Os que têm WAV em `SFX_WAV` tocam o arquivo, embutido em base64; os outros são sintetizados por oscilador (`SND`).
  Os WAV foram feitos pelo André no jsfxr (originais em `tools/sons/`): `gota`, `hurt` (levar dano), `jump`, `sus` (crescer com o SUS), `power` (pegar os demais itens), `bite` (mordida do jacaré),
  `bump` (batida em bloco, inclusive ao abrir um `?`), `tick` (contador da pergunta), `slam` (mergulho do chefão), `kill` (derrotar inimigo), `posto` (posto de vacinação),
  `shot` (lançar seringa), `hit` (golpe que não derrota), `mount` (montar no jacaré), `ok` e `bad` (acerto e erro no portão) e `pop` (escudo quebrando, ovo chocando, balão de fake news e explosões do chefão).
  Alguns nomes existem só para separar eventos que dividiam um som; `SFX_ALT` diz qual som sintetizado eles usam quando não há arquivo: `nope` ("Sem seringas") usa o `bump` sintetizado,
  e os cartões usam `cp`. Ainda sintetizados: `boss` (chegada do chefão e cada golpe que ele leva), `ploc` (seringa batendo na bolha de eco) e `cp` (cartão abrindo).
  O `win` sintetizado só toca com `__mgNoIntro`; no jogo, a vitória tem a fanfarra. Volumes acertados pela energia dos 100 ms mais fortes de cada arquivo, contra a mediana dos anteriores.
- **Juice** (sugestão de um colega do André): o Zé estica no pulo (`p.jT`) e espreme no pouso conforme a queda (`p.landT`, `p.landK`), escalado a partir dos pés; queda alta e freada levantam poeira (`dust()`).
  Golpes congelam o jogo por alguns quadros (`hitstop()`: 2 a 4 em inimigos, 5 no chefão, 12 no golpe final, 5 a 7 no Zé). O tremor de câmera tem intensidade (`shake(duração, amplitude)`) e também sobe e desce.
  Inimigo, chefão e Zé tremem no lugar ao levar golpe (`e.fl`, `b.hurtT`, `p.hurtT`). Pulo coiote (7 quadros), pulo antecipado (8) e pulo curto ao soltar o botão já existiam.
  Com "reduzir movimento" no sistema não há tremor nem pausa; com `__mgNoIntro` também não há pausa, para os testes de mecânica.
- **Controle (gamepad):** `pollPad()` lê `navigator.getGamepads()` a cada quadro (padrão Xbox/PlayStation/GameSir): direcional ou alavanca andam, A pula, X ou B lançam, Start pausa.
  Nos menus (`padLayer()`, `padMenu()`), o direcional percorre os botões da camada visível, A confirma e B volta; no título, A sem foco começa. Só mexe em `keys` quando o controle muda, então teclado e controle convivem.
  Com o controle em uso, `body.pad-on` esconde os botões de toque e a tela de controles mostra os botões do controle; tocar na tela ou desligar o controle traz os botões de volta.
  Golpes fortes vibram o controle (`rumble()`). O navegador só enxerga o controle depois do primeiro botão apertado. Testado com controle simulado (`t63.js`) e conferido pelo André com um GameSir no celular (13/10/2026).
- **Estado:** tudo em `st`. Placar só no aparelho (localStorage `mg-placar`, `mg-nome`, `mg-mudo`).

## Regras do jogo (decisões do André)

- **Modos:** escolhidos em "Modo de jogo" ao começar um jogo novo (`DIFF`, `DF()`, `st.diff`). Normal é a fase e o chefão como foram feitos. Fácil: chefão com 8 de vida em vez de 12,
  mais lento, com menos tiros e mais tempo cansado; 15 segundos nas perguntas; escudo de imunidade a cada vida; sem os boatos que caem na segunda metade da luta. O placar marca "· fácil".
  "Jogar de novo" e "Recomeçar a fase" mantêm o modo da partida.
- **Jogo salvo:** ao tocar uma bandeira (posto), o jogo grava em localStorage `mg-salvo` a fase, a bandeira, o modo, o tempo, inimigos, power-ups, portões e cartões já vistos.
  Um jogo novo grava a partida no começo da fase. A tela de título mostra CONTINUAR (com fase, posto e modo) e NOVO JOGO; sem jogo salvo, PRESS START leva à escolha do modo.
  Ao continuar, inimigos e itens antes da bandeira ficam resolvidos e os portões para trás, abertos (`applySave()`). Vencer a fase apaga o jogo salvo.
  A pausa tem "Tela inicial" (`goTitle()`): volta ao título com a música dele; o progresso depois da última bandeira se perde, e a pausa avisa em qual posto o jogo fica guardado.

- **Vida como no Mario:** no tamanho original, um golpe derruba. O SUS deixa o Zé "sarado" (não escreva "bombado" nos textos): ele aguenta um golpe e volta ao tamanho original. O escudo de imunidade é uma proteção extra, gasta antes do SUS.
- **Gotas** são coletáveis e valem pontos; qualquer morte zera as gotas juntadas.
- **Seringas:** no máximo 3; repostas pela fase e nos postos. A dose de reforço dá tiro triplo sem gastar por 10 segundos.
  O Zé sarado dobra os joelhos ao lançar (o tronco é desenhado 6 px mais baixo, por cima das pernas) e a seringa sai a 16 px do chão: antes saía a 22 e passava por cima dos inimigos, que têm 16 de altura.
- **Jacaré (montaria):** nasce do ovo no ninho. Atravessa a água nadando (o Zé sozinho se afoga). Qualquer golpe, em terra ou na água, faz o jacaré fugir: ele corre, não para na beirada,
  nada se cair na água e some se cair no buraco (o ovo volta ao ninho). Pulo de novo no ar, montado, é o pulo duplo: o Zé salta mais alto e desce, e o jacaré fica parado esperando.
  Há três plataformas altas que só o pulo duplo alcança (conferido por força bruta em `tools/testes/t37.js`). Com um jacaré, outro ovo vira bônus.
- **Mito ou fato:** três portões. A afirmação aparece, o jogador tem 10 segundos (15 no fácil) e responde batendo a cabeça no bloco M ou F. Erro ou tempo esgotado soltam boatos e trocam a afirmação.
  O resultado pausa o jogo com um cartão de explicação.
- **Cartões de apresentação:** na primeira vez que cada inimigo, item, o jacaré e o portão aparecem, o jogo congela, dá zoom e explica. Voltam a cada partida nova.
- **Abertura da fase:** a câmera desce do céu com o nome da fase. A tela de título não mostra nome de fase nem controles; os controles ficam no botão CONTROLES.
- **Fim:** o golpe final deixa o jogo em câmera lenta (`SLOW_STEPS` passos a `SLOW_RATE`, uns 2 segundos). Depois o Zé comemora (preparo, salto e pose com a seringa, em `EXTRA_ART.vn` e `.vb`),
  aparece "Fase 1 completa" e a câmera sobe para o céu, o inverso da abertura (`stepVictory()`, constantes `V_*`). Pulo, seringa ou Enter encerram depois da pose.
  Em seguida vêm a tela "Em construção" (novas fases em breve) e a pontuação. O tempo da partida para no golpe final. Com `window.__mgNoIntro` a comemoração é pulada (contador `winT`), para os testes de mecânica.
- **Pontuação:** gotas 10, boato 50, fake news 80, vírus 100, chefão 1000, power-up 100, portão 600/200/50 conforme os erros, tempo até 2000. Inimigos soltos por erro e os da arena não pontuam.
- **Textos:** na voz do André: diretos, ironia seca, fato concreto com data e lugar, sem travessão, sem rótulo solto abrindo frase e sem contraste de fórmula ("não X, mas Y").
  Os fatos das explicações do mito ou fato foram escritos sem checar fonte na hora e aguardam revisão dele.
- **Personagem:** o Zé Gotinha é do Ministério da Saúde (criado por Darlan Rosa). A tela de resultado traz o aviso de jogo educativo independente, sem vínculo oficial.

## Várias fases

- `PHASES` guarda cada fase (largura `lw`, nome, chefão, tema, perguntas `qs`, chave do placar). `buildLevel(n)` chama `buildLevel1()` ou `buildLevel2()` e acerta `PHASE` e `LW` (largura variável).
- Fase 1 continua com os números fixos de antes (arena 153 a 175, `s.arena`). A fase 2 não tem arena: o chefão é no ar.
- Vencer uma fase libera a seguinte (`mg-fases`) e grava o jogo salvo no começo dela; a tela depois da vitória diz "Fase 2 liberada" e o placar ganha o botão Próxima fase.
  Com mais de uma fase liberada, a tela de modo mostra a escolha de fase e o título ganha o botão FASES (abre a escolha já na fase mais nova; CONTINUAR segue o jogo salvo). Na pré-visualização (artefato, `ESBOCO`) a fase 2 já vem liberada.
- Placar por fase: fase 1 em `mg-placar`, fase 2 em `mg-placar-2`, com abas no placar da tela inicial.
- Testes da fase 2: `t70.js` (capturas de cada trecho), `t71.js` (as duas balanças se resolvem), `t72.js` (robô atravessa a mina no vagonete, normal e fácil),
  `t73.js` (força bruta nos sinos), `t74.js` (travessia do rio pela roda d'água), `t75.js` (decolagem, chefão e vitória), `t76.js` (telas de fase no computador e no celular), `t77.js` (botão FASES no título com jogo salvo).
  `t56.js` e `t57.js` são de antes da tela de modo e já falhavam na versão publicada.

## Fase 2: Arraial do Antigamente (esboço)

Arraial colonial com cara de Minas. Tema: técnicas que se mantiveram só pela tradição. Sprites, cenário e fundo são provisórios, desenhados em código (`SPR2`, `SKY2`, `LAYERS2`);
o fluxo de troca é o mesmo da fase 1. Artes já trocadas: Barão (`BARAO_ART`, 6 quadros: flutuar, arremessar, investida, exposto, dor, derrota; `tools/arte/barao.py`, fundo verde, escala 0,145);
humores, sanguessuga, boticário e frasco (`ATLAS2.hum` e `.bot`, recortados com `tools/arte/fase2.py`, escalas 0,058 e 0,1: o André pediu a cabeça do boticário do tamanho da do Zé; área de golpe 18 × 40; olhos dos humores agachados refeitos à mão);
morcego, miasma, pedra, retrato e poeira (`ATLAS2.mina`, fundo ciano); passarola, balão do Barão, vagonete e sino (`ATLAS2.vei`, recortados com `tapa=False` para as cordas ficarem vazadas;
ao carregar saem os recortes `pbasket` e `cfront`, a frente do cesto e do vagonete desenhada por cima do tronco do Zé);
blocos do cenário (`ATLAS2.til`, `tools/arte/tiles2.py`: recorta por dentro do contorno, troca a franja arroxeada pela cor vizinha e sobe o trilho para o topo do bloco)
e balança (`ATLAS2.bal`: evidência, tradição, prato desenhado inteiro sobre a balança, porta desenhada inteira a partir do bloco D de cima à esquerda, bloco ↺, lampião).
Falta: fundo (céu, nuvens/serra/muro e casario). As paredes repetidas mostram uma emenda leve entre blocos.
Ordem combinada das folhas: Barão · humores e sanguessuga · boticário e frasco · morcego, pedra, miasma, retrato · passarola, balão do Barão, vagonete, sino · blocos do cenário · balança · fundo. A música da fase ainda é a da fase 1; a de chefe e a de vitória valem para todas.
- **Trechos:** ruas e telhados (casarões `W`/`T`, telhas soltas `C` que caem 24 quadros depois do pisão e voltam em 5 s, varal `V`, muro com caco de vidro) · igreja em obra (sinos em pêndulo
  sobre o vão, boticário no balcão, andaime que sobe e desce, balança 1) · mina no vagonete (102 a 188) · rio com jacaré, miasmas e roda d'água · balança 2 · portão 3 e passarola. Postos em 57, 100, 202, 271, 286.
- **Balança da evidência** (no máximo duas, decisão do André): blocos empurráveis (`s.blocks`); evidência (lupa) pesa 1, tradição (moldura dourada) pesa zero. O prato `P` conta as evidências apoiadas nele,
  direto ou em pilha (`onPan`). Duas evidências abrem a porta `D`. O bloco cai quando o meio dele passa da beirada e encaixa no vão. Tradição que cai num buraco fundo é descartada; evidência volta ao lugar.
  O bloco `O` recoloca os blocos. Balança 1: as tradições vão para o fundo do prato e as evidências descem do andaime (a que cai no prato precisa ser empurrada até o fim antes da segunda).
  Balança 2: uma tradição vira aterro do buraco raso e outra vira degrau para a tábua da evidência alta. Montado no jacaré não empurra.
- **Vagonete:** anda sozinho (`cartV`: 2 no normal, 1,85 no fácil; mais lento atrapalhava o pulo). O jogador só pula (pulo de 5,3, como montado). Buraco derruba; caixote é golpe e quebra.
  Pedras do teto caem quando o Zé chega a 96 px; morcegos acordam a 150 px, cruzam o caminho e somem. Posições acertadas para o encontro cair em trecho livre (robô do `t72.js` passa sem morrer no normal).
- **Inimigos novos:** sanguessuga (chão ou teto), os quatro humores (saltam), boticário (frascos em arco, 2 de vida), miasma (não morre, só desvia), morcego, pedra; voltam boato, fake news e vírus.
- **Perguntas:** `QS2`, sobre tradição. Os fatos aguardam a revisão do André.
- **Chefão no ar:** a passarola (Bartolomeu de Gusmão, 1709) decola com câmera subindo. No ar: setas movem, pulo esquenta o ar (segurar sobe sem parar), seringa normal; telhado embaixo machuca.
  O Barão tem camadas de poeira dos séculos (3 no normal, 2 no fácil): cada seringa arranca uma; sem poeira ele fica exposto e aí seringa tira 1 e pisão 2 de vida (12 no normal, 8 no fácil).
  Ataques: retratos de antepassados teleguiados e investida horizontal com aviso. Na segunda metade, SUS uma vez e retratos-inimigos. Seringas chegam em balõezinhos.
  Morrer no ar volta ao posto 5, no chão. Vitória: o balão vai ao centro, "Fase 2 completa" e sobe.

## Pendências e ideias em aberto

- Fase 2: artes definitivas (prompts a escrever depois que o André aprovar o esboço), música da fase, revisão das perguntas e dos cartões, sentir a dificuldade jogando.

- Placar online: hoje é só no aparelho. Fora do artefato dá para usar um banco externo (sugestão feita: Firebase); o André ainda não decidiu.
- Cartões de apresentação só na primeira partida do aparelho (oferecido, sem resposta).
- Revisão do André: textos do bestiário e das explicações; se 10 segundos bastam para as afirmações mais longas; dificuldade do golpe sobre a água.
