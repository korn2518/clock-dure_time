/* 두레 전교 시보 HUD — 서비스 워커
   전략: 앱 셸은 프리캐시(설치 시) + 캐시 우선.
        HTML 문서는 네트워크 우선(빠른 갱신) → 실패 시 캐시.
        나머지 정적 자원은 캐시 우선 → 없으면 네트워크 후 저장.
   업데이트: VERSION 을 올리면 새 캐시가 만들어지고, 페이지에서 '새로고침'을 누를 때 교체됩니다. */

const VERSION = "v1.6.0";
const CACHE = `dure-hud-${VERSION}`;

/* 상대 경로로 두어 GitHub Pages 서브경로(/저장소이름/)에서도 그대로 동작합니다. */
const PRECACHE = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./assets/fonts/pretendard.css",
  "./assets/fonts/Pretendard-Regular.woff2",
  "./assets/fonts/Pretendard-Bold.woff2",
  "./assets/fonts/Pretendard-ExtraBold.woff2",
  "./assets/icons/icon.svg",
  "./assets/icons/icon-192.png",
  "./assets/icons/icon-512.png",
  "./assets/icons/icon-maskable-192.png",
  "./assets/icons/icon-maskable-512.png",
  "./assets/icons/apple-touch-icon.png",
  "./assets/icons/favicon-32.png",
  "./assets/icons/favicon.ico"
];

self.addEventListener("install", (e) => {
  e.waitUntil((async () => {
    const c = await caches.open(CACHE);
    // 하나가 실패해도 나머지는 캐시되도록 개별 처리
    await Promise.all(PRECACHE.map(async (u) => {
      try { await c.add(new Request(u, { cache: "reload" })); }
      catch (err) { console.warn("[sw] precache 실패:", u, err); }
    }));
  })());
});

self.addEventListener("activate", (e) => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter(k => k.startsWith("dure-hud-") && k !== CACHE)
                          .map(k => caches.delete(k)));
    if (self.registration.navigationPreload) {
      try { await self.registration.navigationPreload.enable(); } catch (err) {}
    }
    await self.clients.claim();
  })());
});

/* 페이지에서 즉시 업데이트를 요청할 때 */
self.addEventListener("message", (e) => {
  if (e.data === "SKIP_WAITING") self.skipWaiting();
  if (e.data === "GET_VERSION" && e.source) e.source.postMessage({ type: "VERSION", version: VERSION });
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;

  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;   // 외부 요청은 그대로 통과

  /* 문서(내비게이션): 네트워크 우선 → 오프라인이면 캐시된 index.html */
  if (req.mode === "navigate") {
    e.respondWith((async () => {
      try {
        const preload = await e.preloadResponse;
        if (preload) { putSafe(req, preload.clone()); return preload; }
        const net = await fetch(req);
        putSafe(req, net.clone());
        return net;
      } catch (err) {
        const c = await caches.open(CACHE);
        return (await c.match(req)) || (await c.match("./index.html")) || Response.error();
      }
    })());
    return;
  }

  /* 정적 자원: 캐시 우선 */
  e.respondWith((async () => {
    const c = await caches.open(CACHE);
    const hit = await c.match(req, { ignoreSearch: false });
    if (hit) return hit;
    try {
      const net = await fetch(req);
      if (net && net.ok && net.type === "basic") c.put(req, net.clone());
      return net;
    } catch (err) {
      const loose = await c.match(req, { ignoreSearch: true });
      if (loose) return loose;
      return new Response("오프라인입니다.", { status: 503, statusText: "Offline" });
    }
  })());
});

async function putSafe(req, res) {
  try {
    if (res && res.ok) { const c = await caches.open(CACHE); await c.put(req, res); }
  } catch (err) {}
}
