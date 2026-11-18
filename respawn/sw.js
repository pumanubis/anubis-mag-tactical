const CACHE="tactical-respawn-trial-app-v1";
const QR_CACHE="tactical-respawn-trial-qr";
const QR_URL="https://cdn.jsdelivr.net/npm/jsqr@1.4.0/dist/jsQR.js";
const APP_FILES=["./","./index.html","./qrgen.js","./v6admin.js","../anubis-mag-logo-oliva.png.png"];
const base=new URL(self.registration.scope);
const files=new Set(APP_FILES.map(path=>new URL(path,base).href));
self.addEventListener("install", event=>{
  event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(APP_FILES)).then(()=>self.skipWaiting()));
});
self.addEventListener("activate", event=>{
  event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(key=>key.startsWith("tactical-respawn-trial-app-")&&key!==CACHE).map(key=>caches.delete(key)))).then(()=>self.clients.claim()));
});
self.addEventListener("fetch", event=>{
  if(event.request.method!=="GET")return;
  const url=new URL(event.request.url);
  const isQR=url.href===QR_URL;
  url.search="";
  url.hash="";
  if(!isQR&&!files.has(url.href))return;
  event.respondWith((async()=>{
    const cache=await caches.open(isQR?QR_CACHE:CACHE);
    const key=url.href;
    const cached=await cache.match(key);
    if(cached&&event.request.mode!=="navigate")return cached;
    try{
      const response=await fetch(event.request);
      if(response.ok||response.type==="opaque")await cache.put(key,response.clone());
      return response;
    }catch{return cached||new Response("Recurso no disponible sin conexión",{status:503});}
  })());
});
