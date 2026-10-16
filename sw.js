/* Zé Gotinha's Revenge: funciona sem internet depois da primeira visita.
   Este arquivo é gerado pelo build (python3 build.py) a partir de src/sw.js; a versão vem de VERSAO no build.py. */
const APP = 'ze-gotinha-revenge-app-1.56';   // página e ícones: troca a cada versão
const FIXOS = 'ze-gotinha-revenge-fixos-v1';       // fontes e músicas: raramente mudam
// Todos os apps dividem andrebacchi.github.io: apague só os caches deste jogo.
const PREFIXO = 'ze-gotinha-revenge-';
const NUCLEO = ['./', 'index.html', 'manifest.json', 'icons/icon-192.png', 'icons/icon-512.png', 'icons/favicon-64.png', 'icons/apple-touch-icon.png'];
const ESCOPO = new URL(self.registration.scope).pathname;

self.addEventListener('install', e => {
  e.waitUntil(caches.open(APP).then(c => c.addAll(NUCLEO)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(ks => Promise.all(ks.filter(k => k.startsWith(PREFIXO) && k !== APP && k !== FIXOS).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});
const guardar = (cache, req, resp) => { if (resp && (resp.ok || resp.type === 'opaque')) { const copia = resp.clone(); caches.open(cache).then(c => c.put(req, copia)); } return resp; };
async function pedaco(req, resp) {
  const faixa = /bytes=(\d+)-(\d*)/.exec(req.headers.get('range') || ''); if (!faixa) return resp;
  const dados = await resp.arrayBuffer(), ini = +faixa[1], fim = faixa[2] ? Math.min(+faixa[2], dados.byteLength - 1) : dados.byteLength - 1;
  return new Response(dados.slice(ini, fim + 1), { status: 206, headers: { 'Content-Type': resp.headers.get('Content-Type') || 'audio/mpeg', 'Content-Range': `bytes ${ini}-${fim}/${dados.byteLength}`, 'Content-Length': String(fim - ini + 1), 'Accept-Ranges': 'bytes' } });
}
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  const fonte = url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com';
  if (!fonte && (url.origin !== location.origin || !url.pathname.startsWith(ESCOPO))) return;
  if (!fonte && url.pathname.slice(ESCOPO.length).startsWith('audio/')) {
    // músicas: o jogo guarda o arquivo inteiro; aqui o pedaço pedido pelo player (Range) é cortado do que está guardado
    e.respondWith(caches.match(url.href).then(tem => tem ? pedaco(req, tem) : fetch(req)));
    return;
  }
  if (fonte) {   // fontes: o que já está guardado responde na hora
    e.respondWith(caches.match(req).then(tem => tem || fetch(req).then(r => guardar(FIXOS, req, r))));
    return;
  }
  // página e ícones: rede primeiro (para ver a versão nova logo), cache se estiver sem internet
  // cache: 'no-cache' faz o navegador conferir com o servidor (o GitHub Pages deixa a página 10 minutos no cache HTTP)
  e.respondWith(fetch(req, { cache: 'no-cache' }).then(r => guardar(APP, req, r))
    .catch(() => caches.match(req).then(tem => tem || (req.mode === 'navigate' ? caches.match('./') : Response.error()))));
});
