const STATIC_CACHE = "deckVault-static-v1";
const OFFLINE_CACHE = "deckVault-offline-v1";

// Install: only cache the offline fallback page and static assets
self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(OFFLINE_CACHE)
      .then((cache) => cache.addAll(["/offline"]))
      .then(() => self.skipWaiting())
  );
});

// Activate: clean up old caches
self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(
        keys.filter((k) => k !== STATIC_CACHE && k !== OFFLINE_CACHE)
            .map((k) => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const { request } = e;
  const url = new URL(request.url);

  // Never intercept non-GET or cross-origin requests
  if (request.method !== "GET" || url.origin !== self.location.origin) return;

  // Static assets (content-hashed, safe to cache forever)
  if (url.pathname.startsWith("/_astro/") || url.pathname.startsWith("/icons/")) {
    e.respondWith(
      caches.match(request).then((cached) => {
        if (cached) return cached;
        return fetch(request).then((res) => {
          const clone = res.clone();
          caches.open(STATIC_CACHE).then((cache) => cache.put(request, clone));
          return res;
        });
      })
    );
    return;
  }

  // Everything else (pages, API): network only, fall back to offline page if network fails
  e.respondWith(
    fetch(request).catch(() =>
      caches.match(request) || caches.match("/offline")
    )
  );
});
