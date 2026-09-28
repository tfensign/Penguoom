const CACHE = "penguoom-v57";
const ASSETS = [
  "./",
  "./index.html",
  "./manifest.json",
  "./privacy.html",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/icon-512-maskable.png",
  "./icons/apple-touch-icon.png",
  "./icons/favicon.ico",
  "./fonts/audiowide-regular.woff2",
  "./textures/wall_ice_fortress.png",
  "./textures/wall_frozen_caverns.png",
  "./textures/wall_blizzard_wastes.png",
  "./textures/wall_emperors_keep.png",
  "./textures/wall_frozen_harbor.png",
  "./textures/wall_crystal_caverns.png",
  "./textures/wall_aurora_tundra.png",
  "./textures/wall_christmas_village.png",
  "./textures/wall_northern_lights_ruins.png",
  "./textures/wall_frozen_throne.png",
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(ASSETS)));
  // Stay in "waiting" (don't skipWaiting here) so the page can offer the
  // player a Reload prompt instead of swapping assets out from under them.
});

self.addEventListener("message", (e) => {
  if (e.data && e.data.type === "SKIP_WAITING") self.skipWaiting();
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (e) => {
  e.respondWith(
    caches.match(e.request).then((cached) => cached || fetch(e.request))
  );
});
