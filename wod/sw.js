const CACHE='wod-v3';
const ASSETS=['./app.html','./index.html','./crossfit.webmanifest','./manifest.webmanifest','./crossfit-icon.svg','./icon.svg'];
self.addEventListener('install',event=>{event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(ASSETS)));self.skipWaiting()});
self.addEventListener('activate',event=>{event.waitUntil((async()=>{const keys=await caches.keys();await Promise.all(keys.filter(k=>k.startsWith('wod-')&&k!==CACHE).map(k=>caches.delete(k)));await self.clients.claim()})())});
self.addEventListener('fetch',event=>{const req=event.request,url=new URL(req.url);if(req.method!=='GET'||url.origin!==self.location.origin)return;if(req.mode==='navigate'){event.respondWith(fetch(req,{cache:'no-store'}).catch(()=>caches.match('./app.html')));return}event.respondWith(fetch(req,{cache:'no-store'}).then(res=>{if(res&&res.ok){const copy=res.clone();caches.open(CACHE).then(c=>c.put(req,copy))}return res}).catch(()=>caches.match(req)))});
