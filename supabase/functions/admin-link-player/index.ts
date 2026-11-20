import { createClient } from "npm:@supabase/supabase-js@2.49.4";

const cors = {
  "Access-Control-Allow-Origin": "https://pumanubis.github.io",
  "Access-Control-Allow-Headers": "authorization, apikey, x-client-info, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Cache-Control": "no-store",
};
const send = (body: unknown, status = 200) => Response.json(body, { status, headers: cors });
const isUuid = (s: unknown) => typeof s === "string" && /^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$/i.test(s);
const db = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, {
  auth: { persistSession: false, autoRefreshToken: false },
});

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: cors });
  if (req.method !== "POST") return send({ error: "Método no permitido." }, 405);
  const jwt = req.headers.get("Authorization")?.match(/^Bearer\s+(\S+)$/i)?.[1];
  if (!jwt) return send({ error: "Inicia sesión como administrador." }, 401);
  try {
    const { data, error } = await db.auth.getUser(jwt);
    if (error || !data.user) return send({ error: "La sesión no es válida." }, 401);
    let body;
    try { body = await req.json(); } catch { return send({ error: "Solicitud no válida." }, 400); }
    const { game_id, team_id, username } = body || {};
    if (!isUuid(game_id) || !isUuid(team_id) || typeof username !== "string" || !/^[a-z0-9_-]{3,32}$/.test(username)) {
      return send({ error: "Verifica el nombre de usuario y el equipo." }, 400);
    }
    const result = await db.rpc("tactical_link_existing_player", {
      p_admin: data.user.id, p_game: game_id, p_team: team_id, p_username: username,
    });
    if (result.error) {
      const status = ({ "42501":403, "22023":400, "P0002":404, "23505":409 } as Record<string,number>)[result.error.code] ?? 500;
      return send({ error: status === 500 ? "No se pudo agregar al operador." : result.error.message }, status);
    }
    return send(result.data);
  } catch {
    return send({ error: "No se pudo agregar al operador." }, 500);
  }
});
