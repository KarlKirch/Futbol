const CACHE_NAME = "futbol-champions-v10";
const STATIC_ASSETS = [
  "./",
  "./index.html",
  "./chat.js?v=6",
  "./manifest.webmanifest",
  "./app-icon.svg",
  "./favicon.ico"
];

const SCOPE_PATH = new URL(self.registration.scope).pathname;
const WOD_PATH = new URL("./wod/", self.registration.scope).pathname;
const ROOT_PATH = SCOPE_PATH.endsWith("/") ? SCOPE_PATH : SCOPE_PATH + "/";
const ROOT_INDEX_PATH = ROOT_PATH + "index.html";

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener("activate", event => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key)));
    await self.clients.claim();
  })());
});

self.addEventListener("fetch", event => {
  const request = event.request;
  const url = new URL(request.url);

  if (request.method !== "GET" || url.origin !== self.location.origin) {
    return;
  }

  // WOD is a separate app. Futbol's service worker must never cache,
  // rewrite or provide an offline fallback for anything under /wod/.
  if (url.pathname.startsWith(WOD_PATH)) {
    return;
  }

  if (request.mode === "navigate") {
    const isFutbolRoot = url.pathname === ROOT_PATH || url.pathname === ROOT_INDEX_PATH;

    if (!isFutbolRoot) {
      return;
    }

    event.respondWith(
      fetch(request, { cache: "no-store" })
        .then(response => {
          if (response && response.ok) {
            const copy = response.clone();
            caches.open(CACHE_NAME).then(cache => cache.put("./index.html", copy));
          }
          return response;
        })
        .catch(() => caches.match("./index.html"))
    );
    return;
  }

  event.respondWith(
    fetch(request, { cache: "no-store" })
      .then(response => {
        if (response && response.ok) {
          const copy = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(request, copy));
        }
        return response;
      })
      .catch(() => caches.match(request))
  );
});

self.addEventListener("push", event => {
  let data = {};

  try {
    data = event.data ? event.data.json() : {};
  } catch (_) {
    data = {};
  }

  event.waitUntil(
    self.registration.showNotification(
      data.title || "Futbol – Champions League",
      {
        body: data.body || "Sul on ennustusi tegemata.",
        icon: "./app-icon.svg",
        badge: "./app-icon.svg",
        tag: data.tag || "futbol-prediction-reminder",
        data: {
          url: data.url || "./"
        }
      }
    )
  );
});

self.addEventListener("notificationclick", event => {
  event.notification.close();
  const target = event.notification.data && event.notification.data.url
    ? event.notification.data.url
    : "./";

  event.waitUntil((async () => {
    const windowClients = await clients.matchAll({
      type: "window",
      includeUncontrolled: true
    });

    for (const client of windowClients) {
      if ("focus" in client) {
        await client.focus();
        if ("navigate" in client) {
          await client.navigate(target);
        }
        return;
      }
    }

    if (clients.openWindow) {
      return clients.openWindow(target);
    }
  })());
});
