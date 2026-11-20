create function public.tactical_link_existing_player(p_admin uuid,p_game uuid,p_team uuid,p_username text)
returns jsonb language plpgsql security invoker set search_path = '' as $$
declare
  account_id uuid;
  operation_status text;
  membership_id uuid;
  membership_status text;
begin
  if p_admin is null or not exists(select 1 from public.profiles where id=p_admin and role='admin') then
    raise exception 'Solo un administrador puede agregar operadores.' using errcode='42501';
  end if;
  if p_game is null or p_team is null or p_username is null or p_username !~ '^[a-z0-9_-]{3,32}$' then
    raise exception 'Verifica el nombre de usuario y el equipo.' using errcode='22023';
  end if;
  select status into operation_status from public.games where id=p_game;
  if operation_status is null or operation_status not in ('waiting','active') then
    raise exception 'La partida no existe o ya fue finalizada.' using errcode='22023';
  end if;
  if not exists(select 1 from public.teams where id=p_team and game_id=p_game) then
    raise exception 'El equipo no corresponde a la partida seleccionada.' using errcode='22023';
  end if;
  select c.user_id into account_id from public.player_credentials c
    join public.profiles p on p.id=c.user_id and p.role='player'
    where lower(c.username)=p_username;
  if account_id is null then
    raise exception 'No hay un operador registrado con ese usuario. Si es nuevo, usa Registrar nuevo.' using errcode='P0002';
  end if;
  insert into public.game_players(game_id,team_id,user_id,callsign,status)
    values (p_game,p_team,account_id,p_username,'active')
    on conflict (game_id,user_id) do nothing returning id into membership_id;
  if membership_id is not null then
    return jsonb_build_object('success',true,'username',p_username,'player_id',membership_id);
  end if;
  select status into membership_status from public.game_players
    where game_id=p_game and user_id=account_id;
  if membership_status='inactive' then
    raise exception 'Ese operador fue retirado de esta partida. Usa Restaurar en la lista de jugadores.' using errcode='23505';
  end if;
  raise exception 'Ese operador ya está en esta partida. Usa Editar jugador si quieres cambiar su equipo.' using errcode='23505';
end;
$$;
revoke all on function public.tactical_link_existing_player(uuid,uuid,uuid,text) from public, anon, authenticated;
grant execute on function public.tactical_link_existing_player(uuid,uuid,uuid,text) to service_role;
