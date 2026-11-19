-- The management service only needs to read the operation ID and state.
grant select (id, status) on table public.games to service_role;

create or replace function public.tactical_manage_player(
  p_admin uuid, p_game uuid, p_player uuid, p_action text, p_team uuid, p_username text
) returns jsonb language plpgsql security invoker set search_path = '' as $$
declare
  member public.game_players%rowtype;
  current_name text;
  game_state text;
  can_rename boolean;
begin
  if p_admin is null or not exists(select 1 from public.profiles where id=p_admin and role='admin') then
    raise exception using errcode='42501', message='Solo un administrador puede gestionar jugadores.';
  end if;
  if p_action is null or p_action not in ('read','edit','remove','restore') then
    raise exception using errcode='22023', message='Acción no válida.';
  end if;
  select status into game_state from public.games where id=p_game;
  if not found or game_state='finished' then
    raise exception using errcode='22023', message='La partida no existe o está finalizada.';
  end if;
  select * into member from public.game_players where id=p_player and game_id=p_game for update;
  if not found then
    raise exception using errcode='22023', message='El jugador no pertenece a esta partida.';
  end if;
  perform 1 from public.profiles where id=member.user_id and role='player' for update;
  if not found then
    raise exception using errcode='42501', message='El registro no corresponde a una cuenta de jugador.';
  end if;
  if p_action in ('remove','restore') then
    update public.game_players set status=case when p_action='remove' then 'inactive' else 'active' end
      where id=member.id and game_id=p_game returning * into member;
    return jsonb_build_object('success',true,'status',member.status);
  end if;
  select username into current_name from public.player_credentials where user_id=member.user_id;
  can_rename := current_name is not null and not exists(select 1 from public.game_players where user_id=member.user_id and game_id<>p_game);
  if p_action='read' then
    return jsonb_build_object('success',true,'username',current_name,'can_rename',can_rename);
  end if;
  if p_team is null or not exists(select 1 from public.teams where id=p_team and game_id=p_game) then
    raise exception using errcode='22023', message='El equipo no pertenece a esta partida.';
  end if;
  if p_username is not null and p_username is distinct from current_name then
    if not can_rename then raise exception using errcode='42501', message='El usuario no se puede cambiar desde esta partida.'; end if;
    if p_username !~ '^[a-z0-9_-]{3,32}$' then
      raise exception using errcode='22023', message='Verifica el nombre de usuario (3 a 32 caracteres).';
    end if;
    update public.player_credentials set username=p_username where user_id=member.user_id;
    update public.profiles set nickname=p_username where id=member.user_id and role='player';
    update public.game_players set team_id=p_team,callsign=p_username where id=member.id and game_id=p_game;
  else
    update public.game_players set team_id=p_team where id=member.id and game_id=p_game;
  end if;
  return jsonb_build_object('success',true);
exception when unique_violation then
  raise exception using errcode='23505', message='Ese nombre de usuario ya está en uso.';
end;
$$;
revoke all on function public.tactical_manage_player(uuid,uuid,uuid,text,uuid,text) from public, anon, authenticated;
grant execute on function public.tactical_manage_player(uuid,uuid,uuid,text,uuid,text) to service_role;
