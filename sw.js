const CACHE_NAME="anubis-tactical-v2";
const APP_FILES=["./","./index.html","./manifest.webmanifest","./anubis-mag-logo-oliva.png.png"];
const STATIC_HOSTS=["cdn.jsdelivr.net","unpkg.com","cdnjs.cloudflare.com","tile.openstreetmap.org"];
self.addEventListener("install",event=>{event.waitUntil(caches.open(CACHE_NAME).then(cache=>cache.addAll(APP_FILES)).then(()=>self.skipWaiting()));});
self.addEventListener("activate",event=>{event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith("anubis-tactical-")&&k!==CACHE_NAME).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));});
self.addEventListener("fetch",event=>{
 const req=event.request;
 if(req.method!=="GET")return;
 const url=new URL(req.url);
 const sameOrigin=url.origin===self.location.origin;
 const staticExternal=STATIC_HOSTS.includes(url.hostname);
 if(!sameOrigin&&!staticExternal)return;
 event.respondWith((async()=>{
  const cache=await caches.open(CACHE_NAME);
  const cached=await cache.match(req);
  if(cached)return cached;
  try{
   const response=await fetch(req);
   if(response.ok||response.type==="opaque")await cache.put(req,response.clone());
   return response;
  }catch{
   if(sameOrigin)return (await cache.match("./index.html"))||new Response("Sin conexión",{status:503});
   return new Response("Recurso no disponible sin conexión",{status:503});
  }
 })());
});