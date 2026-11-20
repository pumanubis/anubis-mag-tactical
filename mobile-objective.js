/* Objective-phone mode and independent Tactical map/list overlay. */
(() => {
 const $ = id => document.getElementById(id);
 const time = ms => {
  const seconds = Math.ceil(Math.max(0,ms)/1000);
  return String(Math.floor(seconds/60)).padStart(2,"0")+":"+String(seconds%60).padStart(2,"0");
 };
 const label = state => ({ready:"Por encontrar",live:"En movimiento",finished:"Finalizado"})[state];
 const stamp = (objective, at) => objective && { ...objective, deadline: at + Number(objective.remaining_ms || 0) };
 const stateOf = o => o?.status === "live" && performance.now() >= o.deadline ? "finished" : o?.status;

 async function request(opts, action, body, key) {
  const started = performance.now();
  const auth = key ? null : (await opts.db.auth.getSession()).data?.session?.access_token;
  const response = await fetch(opts.url+"/functions/v1/tactical-mobile-objective", {
   method:"POST", cache:"no-store", credentials:"omit",
   headers:{"Content-Type":"application/json",apikey:opts.key,...(auth ? {Authorization:"Bearer "+auth} : {})},
   body:JSON.stringify({action,...body,...(key ? {token:key} : {})}), signal:AbortSignal.timeout(10000)
  });
  const result = await response.json();
  if(!response.ok){const e=new Error(result.error || "No se pudo conectar con el objetivo móvil.");e.status=response.status;throw e;}
  return { ...result, objective:stamp(result.objective,started) };
 }

 function tactical(opts) {
  let view=null, gameId=null, objective=null, marker=null, map=null, generation=0, lastSync=0, busy=false, centered=false;
  let adminSync=false,picking=false;
  function detach() {
   ++generation; view=gameId=objective=map=null; lastSync=0; busy=false; adminSync=false; picking=false; centered=false;
   marker?.remove(); marker=null; $("mobilePlayer").hidden=true; $("mobilePlayer").parentElement.classList.remove("mobile-present"); $("mobileLinkBox").hidden=true;
   $("mobileAdminStatus").textContent=""; $("mobilePrivateLink").value="";
   $("mobileAdminSave").disabled=false;
   $("mobileAdminClose").disabled=false;
   $("mobileInitialLat").value=""; $("mobileInitialLng").value=""; $("mobileMinutes").value="30";
  }
  function objectivePoint(){
   const state=stateOf(objective);
   if(state!=="ready" && state!=="live")return null;
   if(state==="live" && (performance.now()-lastSync>16000 || !navigator.onLine))return null;
   return Number.isFinite(objective.lat) && Number.isFinite(objective.lng) ? [objective.lat,objective.lng] : null;
  }
  function compassTarget(){
   if(view!=="player" || !objective?.game_active)return null;
   const p=objectivePoint();
   return p ? {name:"Objetivo móvil",p} : null;
  }
  function draw() {
   const state=stateOf(objective), live=state==="live", point=objectivePoint();
   if(view==="player") {
    const visible=!!state;
    $("mobilePlayer").hidden=!visible;
    $("mobilePlayer").parentElement.classList.toggle("mobile-present",visible);
    if(visible) {
     $("mobilePlayerState").textContent=label(state);
     const p=opts.position();
     const dist=p && point ? " · "+Math.round(opts.distance(p,point))+" m" : "";
     $("mobilePlayerInfo").textContent=state==="ready" ? "Busca el celular en el punto marcado. Actívalo en ese mismo dispositivo"+dist+"."
      : live ? time(objective.deadline-performance.now())+" restantes · "+(!point ? "Ubicación temporalmente no disponible" : "Ubicación en directo"+dist)
      : "Terminó el seguimiento. El árbitro confirma quién tenía el celular.";
    }
   }
   if(view==="admin") {
    $("mobileAdminState").textContent=state ? label(state)+(live ? " · "+time(objective.deadline-performance.now()) : "") : "Sin configurar";
    $("mobileAdminSave").disabled=adminSync || !!state && state!=="ready" || opts.game()?.status==="finished";
    $("mobilePickPoint").disabled=$("mobileAdminSave").disabled;
    $("mobileAdminClose").hidden=!state || state==="finished";
    if(state==="finished")$("mobileLinkBox").hidden=true;
   }
   const nextMap=view && opts.map(view);
   if(view==="player")opts.refreshCompass?.();
   if(view==="player")$("mobileShowPoint").hidden=!point || !nextMap;
   if(map!==nextMap || !point || !marker || !nextMap?.hasLayer(marker)){marker?.remove();marker=null;map=nextMap;}
   if(point && map && window.L){
    if(!marker)marker=L.marker(point,{icon:L.divIcon({className:"mobile-map-icon",html:"📱",iconSize:[36,36],iconAnchor:[18,18]})}).addTo(map);
    else marker.setLatLng(point);
    const content="Objetivo móvil · "+label(state);
    if(marker.getTooltip())marker.setTooltipContent(content);else marker.bindTooltip(content,{direction:"top",offset:[0,-12]});
    if(!centered && state==="ready" && map.getZoom()<11){map.setView(point,15);centered=true;}
   }
  }
  async function poll() {
   if(!gameId || busy || adminSync || !navigator.onLine || document.hidden || (view==="admin" && $("gameAdmin").classList.contains("hidden")))return;
   const version=generation;busy=true;
   try {
    const result=await request(opts,"read",{game_id:gameId});
    if(version!==generation)return;
    if(!objective && result.objective?.status==="ready" && view==="admin" && !$("mobileInitialLat").value && !$("mobileInitialLng").value) {
     $("mobileInitialLat").value=result.objective.lat; $("mobileInitialLng").value=result.objective.lng; $("mobileMinutes").value=result.objective.minutes;
    }
    objective=result.objective; lastSync=performance.now();
    if(view==="admin" && ["No se pudo consultar el objetivo móvil.","Sin conexión al módulo. Vuelve a intentarlo."].includes($("mobileAdminStatus").textContent))$("mobileAdminStatus").textContent="";
   } catch(e) {
    if(version!==generation)return;
    if(e.status===401 || e.status===403)objective=null;
    if(view==="admin" && !$("mobileAdminStatus").textContent)$("mobileAdminStatus").textContent=e.status ? e.message : "Sin conexión al módulo. Vuelve a intentarlo.";
   } finally {if(version===generation){busy=false; draw();}}
  }
  function attach(nextView, nextId) {
   if(view===nextView && gameId===nextId){draw();return;}
   detach();view=nextView;gameId=nextId;draw();void poll();
  }
  async function manage(action, data) {
   if(!gameId || view!=="admin" || adminSync)return;
   const version=++generation, id=gameId;
   adminSync=true;busy=false;$("mobileAdminClose").disabled=true;draw();
   $("mobileAdminStatus").textContent="Guardando…";
   try {
    const result=await request(opts,action,{game_id:id,...data});
    if(version!==generation)return;
    objective=result.objective;lastSync=performance.now();
    if(result.token) {
     const link=new URL(location.pathname,location.origin);
     link.searchParams.set("modo","objetivo");
     link.hash="objetivo="+id+"."+result.token;
     $("mobilePrivateLink").value=link.href;
     $("mobileLinkBox").hidden=false;
    }
    $("mobileAdminStatus").textContent=action==="close" ? "Objetivo finalizado. Respawn y los objetivos virtuales no cambiaron." : "Abre el enlace privado solo en el celular del campo.";
   } catch(e) {
    if(version===generation)$("mobileAdminStatus").textContent=e.status ? e.message : "No se pudo guardar. Revisa la conexión e inténtalo de nuevo.";
   } finally {
    if(version===generation){adminSync=false;$("mobileAdminClose").disabled=false;draw();void poll();}
   }
  }
  function pick(point) {
   if(!picking || view!=="admin")return false;
   picking=false;$("mobileInitialLat").value=point.lat.toFixed(7);$("mobileInitialLng").value=point.lng.toFixed(7);
   $("mobileAdminStatus").textContent="Punto elegido. Guarda para preparar el celular.";
   $("mobileAdminForm").scrollIntoView({block:"center"});
   return true;
  }
  $("mobilePickPoint").addEventListener("click",()=>{
   if(view!=="admin" || !opts.map(view))return;
   picking=true;$("mobileAdminStatus").textContent="Toca el punto inicial en el mapa de operaciones.";
   $("adminMap").scrollIntoView({block:"center"});
  });
  $("mobileShowPoint").addEventListener("click",()=>{
   if(view!=="player" || !marker || !map || stateOf(objective)==="finished")return;
   map.setView(marker.getLatLng(),Math.max(map.getZoom(),16));marker.openTooltip();
   $("playerMap").scrollIntoView({block:"center"});
  });
  $("mobileAdminForm").addEventListener("submit",e=>{
   e.preventDefault();
   if($("mobileLinkBox").hidden===false || objective?.status==="ready"){
    if(!confirm("¿Guardar y reemplazar el enlace anterior del celular objetivo?"))return;
   }
   void manage("prepare",{lat:Number($("mobileInitialLat").value),lng:Number($("mobileInitialLng").value),minutes:Number($("mobileMinutes").value)});
  });
  $("mobileAdminClose").addEventListener("click",()=>{
   if(confirm("¿Finalizar el objetivo móvil? El GPS y el pitido se apagarán. No se puede reiniciar."))void manage("close",{});
  });
  $("mobileCopyLink").addEventListener("click",async()=>{
   try{await navigator.clipboard.writeText($("mobilePrivateLink").value);$("mobileAdminStatus").textContent="Enlace copiado. Ábrelo solo en el celular del campo.";}
   catch{$("mobilePrivateLink").select();$("mobileAdminStatus").textContent="Copia el enlace seleccionado y ábrelo en el celular del campo.";}
  });
  setInterval(draw,1000);
  setInterval(poll,5000);
  window.addEventListener("online",poll);
  document.addEventListener("visibilitychange",poll);
  return {attach,detach,draw,poll,pick,compassTarget};
 }

 function device(opts) {
  $("login").classList.add("hidden");
  $("mobileDevice").classList.remove("hidden");
  const button=$("mobileActivate"), output=$("mobileDeviceStatus"), clock=$("mobileDeviceClock");
  const valid=v=>/^[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}\.[a-f0-9]{64}$/i.test(v);
  let paired="";
  try{paired=sessionStorage.getItem("anubis-mobile-device")||"";}catch{}
  if(!valid(paired)){output.textContent="Abre el enlace privado que preparó el administrador.";return;}
  const [game_id,key]=paired.split(".");
  let objective=null, enabled=false, working=false, stopped=false, wakePending=false, wakeLock=null, audio=null, watchId=null, lastFix=null, lastBeep=-Infinity, gpsMessage="";
  function finish() {
   stopped=true; enabled=false; button.hidden=true;
   if(watchId!==null)navigator.geolocation.clearWatch(watchId);
   watchId=null;lastFix=null;
   if(audio && audio.state!=="closed")audio.close().catch(()=>{});
   if(wakeLock)wakeLock.release().catch(()=>{});
   wakeLock=null;
  }
  function show() {
   if(stopped)return;
   const state=stateOf(objective), live=state==="live";
   button.hidden=!state || state==="finished" || (state==="ready" && !objective.game_active) || (live && enabled && audio?.state==="running");
   button.disabled=working;
   button.textContent=live?"REANUDAR GPS Y PITIDO":"ACTIVAR OBJETIVO";
   if(state==="finished") {
    clock.textContent="00:00"; output.textContent="Objetivo finalizado. GPS y pitido apagados."; finish();
   } else if(live) {
    clock.textContent=time(objective.deadline-performance.now());
    output.textContent=enabled && audio?.state==="running" ? (gpsMessage || "En movimiento · GPS y pitido activos.") : "El tiempo sigue corriendo. Pulsa para reanudar el GPS y el pitido.";
   } else if(state==="ready") {
    clock.textContent=time(objective.minutes*60000);
    output.textContent=working?"Obteniendo la ubicación del celular…":gpsMessage || (objective.game_active?"Pulsa el botón cuando encuentres el celular.":"Esperando a que el administrador inicie la partida.");
   }
  }
  function accept(next){
   if(!next || stopped)return;
   if(next.status==="live" && objective?.status==="live")next.deadline=Math.min(next.deadline,objective.deadline);
   objective=next;show();
  }
  async function lock() {
   if(!enabled || stopped || document.hidden || wakeLock || wakePending || !navigator.wakeLock)return;
   wakePending=true;
   try {
    const acquired=await navigator.wakeLock.request("screen");
    if(!enabled || stopped){await acquired.release();return;}
    wakeLock=acquired;
    acquired.addEventListener("release",()=>{if(wakeLock===acquired)wakeLock=null;});
   } catch {} finally {wakePending=false;}
  }
  function beep() {
   if(!enabled || stateOf(objective)!=="live" || audio?.state!=="running" || performance.now()-lastBeep<4600)return;
   const left=(objective.deadline-performance.now())/1000;
   if(left<.66)return;
   lastBeep=performance.now();
   // A descending triple chime, distinct from Respawn's two rising square-wave bursts.
   for(const [offset,hz,duration] of [[0,1560,.11],[.18,1170,.11],[.36,880,.24]]){
    const o=audio.createOscillator(),g=audio.createGain(),t=audio.currentTime+offset;
    o.type="triangle";o.frequency.setValueAtTime(hz,t);
    g.gain.setValueAtTime(.0001,t);g.gain.linearRampToValueAtTime(.36,t+.012);
    g.gain.exponentialRampToValueAtTime(.0001,t+duration);
    o.connect(g);g.connect(audio.destination);o.start(t);o.stop(t+duration+.01);
   }
  }
  function unavailable(e){
   if(e?.status===403){output.textContent="El enlace dejó de estar autorizado. Pide uno nuevo al administrador.";finish();return;}
   gpsMessage=e?.status ? e.message : "Sin conexión con Tactical. El contador no se reinicia.";
   if(objective?.status==="live"){output.textContent=gpsMessage;}else if(!objective)output.textContent=gpsMessage;
  }
  let polling=false, fixPending=false, operation=0;
  function refreshStationaryFix(){
   if(fixPending || !enabled || stopped || lastFix && Date.now()-lastFix.timestamp<12000)return;
   fixPending=true;
   navigator.geolocation.getCurrentPosition(p=>{
    fixPending=false;if(enabled && !stopped && (!lastFix || p.timestamp>lastFix.timestamp))lastFix=p;
   },()=>{fixPending=false;},{enableHighAccuracy:true,maximumAge:2000,timeout:8000});
  }
  async function poll() {
   if(stopped || working || polling || document.hidden)return;
   polling=true;const version=operation;
   try {
    if(stateOf(objective)==="live")refreshStationaryFix();
    const fresh=enabled && stateOf(objective)==="live" && lastFix && Date.now()-lastFix.timestamp<18000;
    const body=fresh ? {lat:lastFix.coords.latitude,lng:lastFix.coords.longitude} : {};
    const response=await request(opts,fresh?"position":"device",{game_id,...body},key);
    if(working || version!==operation)return;
    gpsMessage=fresh || !enabled ? "" : "Esperando una posición GPS reciente.";
    accept(response.objective);
   } catch(e){if(!working && version===operation)unavailable(e);} finally{polling=false;}
  }
  function track() {
   if(watchId!==null)return;
   watchId=navigator.geolocation.watchPosition(p=>{lastFix=p;},()=>{
    lastFix=null;gpsMessage="GPS sin señal. Revisa el permiso de ubicación.";
   },{enableHighAccuracy:true,maximumAge:0,timeout:12000});
  }
  button.addEventListener("click",async()=>{
   if(stopped || working || !objective || stateOf(objective)==="finished")return;
   if(!navigator.geolocation || !(window.AudioContext||window.webkitAudioContext)){
    gpsMessage="Este navegador no permite usar GPS o audio.";show();return;
   }
   ++operation;working=true;gpsMessage="";show();
   try{
    if(!audio || audio.state==="closed")audio=new (window.AudioContext||window.webkitAudioContext)();
    await Promise.race([audio.resume(),new Promise((_,reject)=>setTimeout(()=>reject(new Error("Audio bloqueado")),2000))]);
    if(audio.state!=="running")throw new Error("Audio bloqueado");
    if(stateOf(objective)==="ready"){
     const p=await new Promise((resolve,reject)=>navigator.geolocation.getCurrentPosition(resolve,()=>reject(new Error("Da permiso de ubicación e inténtalo de nuevo.")),{enableHighAccuracy:true,maximumAge:0,timeout:14000}));
     const res=await request(opts,"activate",{game_id,lat:p.coords.latitude,lng:p.coords.longitude},key);
     lastFix=p;accept(res.objective);
    }
    if(stateOf(objective)==="live" && !stopped){enabled=true;track();void lock();beep();}
   }catch(e){if(e.status===403)unavailable(e);else gpsMessage=e.message==="Audio bloqueado"?"El audio está bloqueado. Revisa el volumen y vuelve a pulsar.":e.message;}
   finally{working=false;show();void poll();}
  });
  setInterval(()=>{show();beep();},250);
  setInterval(poll,5000);
  document.addEventListener("visibilitychange",()=>{show();void lock();void poll();});
  window.addEventListener("online",poll);
  window.addEventListener("pagehide",()=>{if(watchId!==null)navigator.geolocation.clearWatch(watchId);watchId=null;enabled=false;lastFix=null;if(audio?.state==="running")audio.suspend().catch(()=>{});});
  void poll();
 }
 window.AnubisMobileObjective={tactical,device};
})();
