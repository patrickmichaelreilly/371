/* Offline-first service worker (Milestone 4).
   - App shell (index.html, verovio, manifest, icons, chorale list) is
     precached on install and served network-first with cache fallback so
     updates land when online but everything works offline.
   - Chorale bundles (chorales/NNN.json.gz) are immutable-ish and large:
     cache-first, populated as the player visits chorales. */
const VERSION = 'v1';
const SHELL_CACHE = `shell-${VERSION}`;
const DATA_CACHE = `data-${VERSION}`;
const SHELL = [
  '.',
  'index.html',
  'vendor/verovio-toolkit-wasm.js',
  'manifest.webmanifest',
  'chorales/index.json',
  'icon-192.png',
  'icon-512.png',
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(SHELL_CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(k => k !== SHELL_CACHE && k !== DATA_CACHE)
          .map(k => caches.delete(k))
    )).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET' || url.origin !== location.origin) return;

  if (url.pathname.endsWith('.json.gz')) {
    /* chorale bundles: cache-first */
    e.respondWith(
      caches.open(DATA_CACHE).then(async c => {
        const hit = await c.match(e.request);
        if (hit) return hit;
        const res = await fetch(e.request);
        if (res.ok) c.put(e.request, res.clone());
        return res;
      })
    );
    return;
  }

  /* shell + manifest: network-first, cache fallback for offline */
  e.respondWith(
    fetch(e.request).then(res => {
      if (res.ok) {
        const clone = res.clone();
        caches.open(SHELL_CACHE).then(c => c.put(e.request, clone));
      }
      return res;
    }).catch(() => caches.match(e.request, { ignoreSearch: true }))
  );
});
