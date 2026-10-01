
const CACHE_NAME = 'thinkinos-v2.0';
const ASSETS_TO_CACHE = [
    '/',
    '/desktop',
    '/login',
    '/portal',
    '/static/manifest.json',
    '/static/icons/icon-192.png',
    '/static/icons/icon-512.png'
];

// Instalação - cache dos assets principais
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('[SW] Cache aberto');
                return cache.addAll(ASSETS_TO_CACHE);
            })
            .catch((err) => console.log('[SW] Erro no cache:', err))
    );
    self.skipWaiting();
});

// Ativação - limpar caches antigos
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) => 
            Promise.all(
                keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
            )
        )
    );
    self.clients.claim();
});

// Fetch - estratégia: cache primeiro, depois rede
self.addEventListener('fetch', (event) => {
    // Ignorar requisições de API (sempre buscar da rede)
    if (event.request.url.includes('/api/')) {
        return;
    }
    
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                if (response) return response;
                return fetch(event.request).then((res) => {
                    if (res && res.status === 200 && res.type === 'basic') {
                        const resClone = res.clone();
                        caches.open(CACHE_NAME).then((cache) => {
                            cache.put(event.request, resClone);
                        });
                    }
                    return res;
                }).catch(() => caches.match('/desktop'));
            })
    );
});
