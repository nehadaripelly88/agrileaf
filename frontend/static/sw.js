// AgriLeaf Service Worker — Offline PWA Support
const CACHE = 'agrileaf-v1';
const ASSETS = [
    '/',
    '/static/css/style.css',
    '/static/js/main.js',
    '/static/js/i18n.js',
    '/static/js/weather.js',
    'https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css'
];

self.addEventListener('install', e => {
    e.waitUntil(
        caches.open(CACHE).then(cache => cache.addAll(ASSETS).catch(() => {}))
    );
    self.skipWaiting();
});

self.addEventListener('activate', e => {
    e.waitUntil(
        caches.keys().then(keys =>
            Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
        )
    );
    self.clients.claim();
});

self.addEventListener('fetch', e => {
    // Don't cache POST requests (analyze)
    if (e.request.method !== 'GET') return;
    // Don't cache API calls
    if (e.request.url.includes('/analyze') || e.request.url.includes('/history') || e.request.url.includes('/model_status')) return;

    e.respondWith(
        caches.match(e.request).then(cached => {
            if (cached) return cached;
            return fetch(e.request).then(res => {
                if (res && res.status === 200) {
                    const clone = res.clone();
                    caches.open(CACHE).then(cache => cache.put(e.request, clone));
                }
                return res;
            }).catch(() => cached);
        })
    );
});