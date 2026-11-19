import { createClient } from "npm:@supabase/supabase-js@2.49.4";
const cors={"Access-Control-Allow-Origin":"https://pumanubis.github.io","Access-Control-Allow-Headers":"authorization, apikey, x-client-info, content-type","Access-Control-Allow-Methods":"POST, OPTIONS"};
const reply=(body:unknown,status=200)=>new Response(JSON.stringify(body),{status,headers:{...cors,"Content-Type":"application/json"}});
const uuid=(value:unknown)=>typeof value==="string"&&/^[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}$/i.test(value);
Deno.serve(async(req)=>{
 if(req.method==="OPTIONS")return new Response("ok",{headers:cors});
 if(req.method!=="POST")return reply({error:"Método no permitido."},405);
 const auth=req.headers.get("authorization");
 if(!auth?.match(/^Bearer\s+\S+$/i))return reply({error:"Inicia sesión como administrador."},401);
 try{
  const db=createClient(Deno.env.get("SUPABASE_URL")!,Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,{auth:{autoRefreshToken:false,persistSession:false}});
  const {data:{user},error:authError}=await db.auth.getUser(auth.replace(/^Bearer\s+/i,""));
  if(authError||!user)return reply({error:"La sesión no es válida."},401);
  let b;
  try{b=await req.json();}catch{return reply({error:"Solicitud no válida."},400);}
  if(!b||!uuid(b.game_id)||!uuid(b.player_id)||!["read","edit","remove","restore"].includes(b.action)||(b.action==="edit"&&!uuid(b.team_id)))return reply({error:"No se reconoció el jugador, el equipo o la partida."},400);
  if(b.username!=null&&(typeof b.username!=="string"||!/^[a-z0-9_-]{3,32}$/.test(b.username)))return reply({error:"Verifica el nombre de usuario."},400);
  const {data,error}=await db.rpc("tactical_manage_player",{p_admin:user.id,p_game:b.game_id,p_player:b.player_id,p_action:b.action,p_team:b.action==="edit"?b.team_id:null,p_username:b.action==="edit"?b.username??null:null});
  if(error){
   const status=error.code==="42501"?403:error.code==="23505"?409:error.code==="22023"?400:500;
   return reply({error:status===500?"No se pudo gestionar el jugador.":error.message},status);
  }
  return reply(data);
 }catch{return reply({error:"No se pudo gestionar el jugador."},500);}
});