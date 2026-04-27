const CACHE_NAME = 'holycode-v2';
const ASSETS = [
    '/static/css/style.css',
    '/static/js/app.js',
    '/static/manifest.json'
];

// Install
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS))
    );
    self.skipWaiting();
});

// Activate — delete old caches
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys =>
            Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
        )
    );
    self.clients.claim();
});

// Fetch — never cache dynamic routes
self.addEventListener('fetch', event => {
    const url = event.request.url;

    // Always fetch fresh for dynamic routes
    if (url.includes('/submit') ||
        url.includes('/like') ||
        url.includes('/explain') ||
        url.includes('/subscribe') ||
        url.includes('/submission') ||
        url.includes('/archive') ||
        url.includes('/card') ||
        url.includes('/ai-image') ||
        url.endsWith('/') ||
        url.endsWith('/holycode.onrender.com')) {
        event.respondWith(fetch(event.request).catch(() => caches.match(event.request)));
        return;
    }

    // Cache static assets only
    event.respondWith(
        caches.match(event.request).then(cached => cached || fetch(event.request))
    );
});

// Push notifications
self.addEventListener('push', event => {
    const data = event.data ? event.data.json() : {};
    const title = data.title || 'HolyCode';
    const options = {
        body: data.body || 'A new devotional is ready! ✦',
        icon: '/static/images/icon-192.png',
        badge: '/static/images/icon-192.png',
        data: { url: data.url || '/' }
    };
    event.waitUntil(self.registration.showNotification(title, options));
});

// Notification click
self.addEventListener('notificationclick', event => {
    event.notification.close();
    event.waitUntil(
        clients.openWindow(event.notification.data.url || '/')
    );
});
