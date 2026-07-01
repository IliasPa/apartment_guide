/*
  sw.js — offline support for the apartment guide
  - Precaches the app shell (pages, css, js, shared datasets, icons) on install
  - Caches per-property content/images at runtime as a guest visits their pages,
    so a repeat visit (or a spotty-wifi moment mid-stay) still works
  - Navigations and JSON/CSS/JS: network-first, falling back to cache when offline
  - Images: cache-first (they rarely change once published)
*/

const VERSION = "v1";
const STATIC_CACHE = "apt-guide-static-" + VERSION;
const RUNTIME_CACHE = "apt-guide-runtime-" + VERSION;

const APP_SHELL = [
  "./",
  "index.html",
  "manifest.json",
  "pages/accommodation.html",
  "pages/neighborhood.html",
  "pages/restaurants.html",
  "pages/attractions.html",
  "pages/beaches.html",
  "pages/phrases.html",
  "pages/emergency.html",
  "pages/contacts.html",
  "assets/css/styles.css",
  "assets/js/app.js",
  "assets/images/favicon.png",
  "assets/images/hero.svg",
  "assets/images/icon-192.png",
  "assets/images/icon-512.png",
  "assets/images/flag-gb.svg",
  "assets/images/flag-gr.svg",
  "assets/images/phone.svg",
  "assets/images/whatsapp.svg",
  "assets/images/viber.svg",
  "assets/images/messenger.svg",
  "assets/images/messenger0.svg",
  "assets/images/placeholder.svg",
  "data/content.en.json",
  "data/content.gr.json",
  "data/properties.json",
  "data/phrases.json",
  "dataset/attractions.json",
  "dataset/beaches.json",
  "dataset/restaurants.json",
  "dataset/images/attractions/placeholder.svg",
  "dataset/images/beaches/placeholder.svg",
  "dataset/images/restaurants/placeholder.svg",
];

// third-party resources worth caching for offline (opaque, can't inspect status)
const CROSS_ORIGIN_SHELL = [
  "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css",
];

const IMAGE_RE = /\.(png|jpe?g|svg|webp|gif)$/i;

self.addEventListener("install", (event) => {
  event.waitUntil(
    (async () => {
      const cache = await caches.open(STATIC_CACHE);
      await cache.addAll(APP_SHELL);
      await Promise.all(
        CROSS_ORIGIN_SHELL.map(async (url) => {
          try {
            const res = await fetch(url, { mode: "no-cors" });
            await cache.put(url, res);
          } catch (e) {
            /* offline install or blocked request; skip */
          }
        }),
      );
      self.skipWaiting();
    })(),
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    (async () => {
      const names = await caches.keys();
      await Promise.all(
        names
          .filter((n) => n !== STATIC_CACHE && n !== RUNTIME_CACHE)
          .map((n) => caches.delete(n)),
      );
      await self.clients.claim();
    })(),
  );
});

async function networkFirst(request) {
  const cache = await caches.open(RUNTIME_CACHE);
  try {
    const fresh = await fetch(request);
    if (fresh && fresh.ok) cache.put(request, fresh.clone());
    return fresh;
  } catch (e) {
    const cached =
      (await cache.match(request)) || (await caches.match(request));
    if (cached) return cached;
    if (request.mode === "navigate") {
      const fallback = await caches.match("index.html");
      if (fallback) return fallback;
    }
    throw e;
  }
}

async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) return cached;
  const cache = await caches.open(RUNTIME_CACHE);
  try {
    const fresh = await fetch(request);
    if (fresh && fresh.ok) cache.put(request, fresh.clone());
    return fresh;
  } catch (e) {
    throw e;
  }
}

self.addEventListener("fetch", (event) => {
  const request = event.request;
  if (request.method !== "GET") return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return; // let cross-origin (weather API, maps, CDN) pass through as normal

  if (IMAGE_RE.test(url.pathname)) {
    event.respondWith(cacheFirst(request));
    return;
  }

  event.respondWith(networkFirst(request));
});
