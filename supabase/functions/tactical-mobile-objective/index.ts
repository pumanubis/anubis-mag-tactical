import { createClient } from "npm:@supabase/supabase-js@2.49.4";

const cors = {
  "Access-Control-Allow-Origin": "https://pumanubis.github.io",
  "Access-Control-Allow-Headers": "authorization, apikey, x-client-info, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Cache-Control": "no-store",
};
const json = (value: unknown, status = 200) => new Response(JSON.stringify(value), {
  status, headers: { ...cors, "Content-Type": "application/json" },
});
const hex = (bytes: Uint8Array) => Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join("");
const hash = async (key: string) => hex(new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(key))));
const validCoord = (v: unknown, max: number) => typeof v === "number" && Number.isFinite(v) && Math.abs(v) <= max;
const db = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, {
  auth: { persistSession: false, autoRefreshToken: false },
});

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: cors });
  if (req.method !== "POST") return json({ error: "Método no permitido." }, 405);
  try {
    let body;
    try {
      const raw = await req.text();
      if (raw.length > 2048) return json({ error: "Solicitud demasiado grande." }, 413);
      body = JSON.parse(raw);
    } catch { return json({ error: "Solicitud no válida." }, 400); }
    const { action, game_id, token, minutes, lat, lng } = body || {};
    if (!["read","prepare","device","activate","position","close"].includes(action)
        || typeof game_id !== "string" || !/^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$/i.test(game_id)) {
      return json({ error: "No se reconoció la acción o la partida." }, 400);
    }
    if (["prepare","activate","position"].includes(action) && (!validCoord(lat,90) || !validCoord(lng,180))) {
      return json({ error: "Revisa las coordenadas." }, 400);
    }
    if (action === "prepare" && ![20,30,40,50,60].includes(minutes)) return json({ error: "Duración no válida." }, 400);
    let userId = null;
    let deviceKey = null;
    if (["device","activate","position"].includes(action)) {
      if (typeof token !== "string" || !/^[a-f0-9]{64}$/.test(token)) return json({ error: "Este enlace no está autorizado." }, 403);
      deviceKey = token;
    } else {
      const bearer = req.headers.get("authorization")?.match(/^Bearer\s+(\S+)$/i)?.[1];
      if (!bearer) return json({ error: "Inicia sesión en Tactical." }, 401);
      const { data, error } = await db.auth.getUser(bearer);
      if (error || !data.user) return json({ error: "Tu sesión no es válida." }, 401);
      userId = data.user.id;
      if (action === "prepare") deviceKey = hex(crypto.getRandomValues(new Uint8Array(32)));
    }
    const { data, error } = await db.rpc("tactical_mobile_objective", {
      p_user: userId, p_game: game_id, p_action: action, p_hash: deviceKey ? await hash(deviceKey) : null,
      p_minutes: action === "prepare" ? minutes : null,
      p_lat: ["prepare","activate","position"].includes(action) ? lat : null,
      p_lng: ["prepare","activate","position"].includes(action) ? lng : null,
    });
    if (error) {
      const status = error.code === "42501" ? 403 : error.code === "22023" ? 400 : 500;
      return json({ error: status === 500 ? "No se pudo consultar el objetivo móvil." : error.message }, status);
    }
    return json(action === "prepare" ? { ...data, token: deviceKey } : data);
  } catch {
    return json({ error: "No se pudo consultar el objetivo móvil." }, 500);
  }
});
