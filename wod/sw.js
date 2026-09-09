const CACHE='crossfit-v3';
const ASSETS=['./app.html','./index.html','./crossfit.webmanifest','./crossfit-icon.svg'];
self.addEventListener('install',event=>{event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(ASSETS)));self.skipWaiting()});
self.addEventListener('activate',event=>{event.waitUntil((async()=>{const keys=await caches.keys();await Promise.all(keys.filter(k=>(k.startsWith('wod-')||k.startsWith('crossfit-'))&&k!==CACHE).map(k=>caches.delete(k)));await self.clients.claim()})())});
self.addEventListener('fetch',event=>{const req=event.request,url=new URL(req.url);if(req.method!=='GET'||url.origin!==self.location.origin)return;if(req.mode==='navigate'){event.respondWith(fetch(req,{cache:'no-store'}).catch(()=>caches.match('./app.html')));return}event.respondWith(fetch(req,{cache:'no-store'}).then(res=>{if(res&&res.ok){const copy=res.clone();caches.open(CACHE).then(c=>c.put(req,copy))}return res}).catch(()=>caches.match(req)))});

self.addEventListener('push',event=>{
  let data={};
  try{data=event.data?event.data.json():{}}catch(_){data={}}
  event.waitUntil(self.registration.showNotification(data.title||'CrossFit',{
    body:data.body||'Sul on uus CrossFit teavitus.',
    icon:'./crossfit-icon.svg',
    badge:'./crossfit-icon.svg',
    tag:data.tag||'crossfit-notification',
    data:{url:data.url||'./app.html'}
  }));
});

self.addEventListener('notificationclick',event=>{
  event.notification.close();
  const target=event.notification.data?.url||'./app.html';
  event.waitUntil((async()=>{
    const windowClients=await clients.matchAll({type:'window',includeUncontrolled:true});
    for(const client of windowClients){
      if('focus'in client){await client.focus();if('navigate'in client)await client.navigate(target);return}
    }
    if(clients.openWindow)return clients.openWindow(target);
  })());
});
