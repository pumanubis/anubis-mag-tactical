-- ANUBIS MAG TACTICAL
-- Habilita partidas de 2, 3 o 4 equipos y un cuarto color.
-- Ejecutar únicamente en el proyecto Supabase anubis-mag-tactical.
-- Es una modificación aditiva de restricciones; no elimina datos.

begin;

alter table public.games
  drop constraint if exists games_team_count_check;

alter table public.games
  add constraint games_team_count_check
  check (team_count = any (array[2, 3, 4]));

alter table public.teams
  drop constraint if exists teams_color_check;

alter table public.teams
  add constraint teams_color_check
  check (color = any (array['red', 'blue', 'green', 'yellow']));

commit;
