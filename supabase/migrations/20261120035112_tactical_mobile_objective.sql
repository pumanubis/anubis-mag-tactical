create table public.tactical_mobile_objectives (
  game_id uuid primary key references public.games(id) on delete cascade,
  duration_minutes smallint not null check (duration_minutes in (20,30,40,50,60)),
  initial_lat double precision not null check (initial_lat between -90 and 90),
  initial_lng double precision not null check (initial_lng between -180 and 180),
  token_hash text not null check (token_hash ~ '^[a-f0-9]{64}$'),
  started_at timestamptz,
  ends_at timestamptz,
  closed_at timestamptz,
  last_lat double precision check (last_lat between -90 and 90),
  last_lng double precision check (last_lng between -180 and 180),
  last_fix_at timestamptz
);
alter table public.tactical_mobile_objectives enable row level security;
revoke all on public.tactical_mobile_objectives from public, anon, authenticated;
grant select, insert, update on public.tactical_mobile_objectives to service_role;

create schema if not exists tactical_internal;
revoke all on schema tactical_internal from public, anon, authenticated;

create function tactical_internal.tactical_mobile_game_closed() returns trigger
language plpgsql security definer set search_path = ''
as $$
begin
  update public.tactical_mobile_objectives
    set closed_at = clock_timestamp(), last_lat = null, last_lng = null, last_fix_at = null
    where game_id = new.id and closed_at is null;
  return new;
end;
$$;
revoke all on function tactical_internal.tactical_mobile_game_closed() from public, anon, authenticated;
create trigger tactical_mobile_game_closed after update of status on public.games
for each row when (new.status = 'finished' and old.status is distinct from new.status)
execute function tactical_internal.tactical_mobile_game_closed();

create function public.tactical_mobile_objective(
  p_user uuid, p_game uuid, p_action text, p_hash text,
  p_minutes integer, p_lat double precision, p_lng double precision
) returns jsonb
language plpgsql security invoker set search_path = ''
as $$
declare
  g public.games%rowtype;
  o public.tactical_mobile_objectives%rowtype;
  is_admin boolean := false;
  is_device boolean := p_action in ('device','activate','position');
  now_at timestamptz;
  mode text;
  visible_fix boolean;
begin
  if p_action is null or p_action not in ('read','prepare','device','activate','position','close') then
    raise exception 'Acción no válida.' using errcode = '22023';
  end if;
  if p_action in ('prepare','activate','position','close') then
    select * into g from public.games where id = p_game for share;
  else
    select * into g from public.games where id = p_game;
  end if;
  if g.id is null then
    raise exception 'Partida no disponible.' using errcode = '42501';
  end if;
  if not is_device then
    is_admin := p_user is not null and (g.created_by = p_user or exists
      (select 1 from public.profiles where id = p_user and role = 'admin'));
    if not coalesce(is_admin,false) and (p_action <> 'read' or not exists
      (select 1 from public.game_players where game_id = p_game and user_id = p_user and status = 'active')) then
      raise exception 'No tienes acceso a este objetivo.' using errcode = '42501';
    end if;
  end if;
  if p_action in ('prepare','activate','position','close') then
    select * into o from public.tactical_mobile_objectives where game_id = p_game for update;
  else
    select * into o from public.tactical_mobile_objectives where game_id = p_game;
  end if;
  now_at := clock_timestamp();
  if is_device and (o.game_id is null or p_hash is null or o.token_hash <> p_hash) then
    raise exception 'Este enlace ya no está autorizado.' using errcode = '42501';
  end if;
  if p_action = 'prepare' then
    if g.status not in ('waiting','active') or o.started_at is not null or o.closed_at is not null then
      raise exception 'El objetivo ya comenzó o se cerró y no se puede reiniciar.' using errcode = '22023';
    end if;
    if coalesce(p_minutes not in (20,30,40,50,60),true) or p_hash is null or p_hash !~ '^[a-f0-9]{64}$'
      or not coalesce(p_lat between -90 and 90 and p_lng between -180 and 180,false) then
      raise exception 'Revisa la duración y las coordenadas iniciales.' using errcode = '22023';
    end if;
    insert into public.tactical_mobile_objectives (game_id,duration_minutes,initial_lat,initial_lng,token_hash)
      values (p_game,p_minutes,p_lat,p_lng,p_hash)
      on conflict (game_id) do update set duration_minutes=excluded.duration_minutes,
        initial_lat=excluded.initial_lat, initial_lng=excluded.initial_lng,token_hash=excluded.token_hash
      where tactical_mobile_objectives.started_at is null and tactical_mobile_objectives.closed_at is null
      returning * into o;
    if o.game_id is null then
      raise exception 'El objetivo ya comenzó o se cerró.' using errcode = '22023';
    end if;
  elsif p_action = 'close' and o.game_id is not null and o.closed_at is null then
    update public.tactical_mobile_objectives
      set closed_at = now_at, last_lat = null, last_lng = null, last_fix_at = null
      where game_id = p_game returning * into o;
  elsif p_action = 'activate' and o.started_at is null and o.closed_at is null then
    if g.status <> 'active' then
      raise exception 'El administrador debe iniciar la partida primero.' using errcode = '22023';
    end if;
    if not coalesce(p_lat between -90 and 90 and p_lng between -180 and 180,false) then
      raise exception 'No hay una posición GPS válida.' using errcode = '22023';
    end if;
    update public.tactical_mobile_objectives
      set started_at = now_at, ends_at = now_at + make_interval(mins => o.duration_minutes),
          last_lat = p_lat, last_lng = p_lng, last_fix_at = now_at
      where game_id = p_game returning * into o;
  elsif p_action = 'position' and g.status = 'active' and o.closed_at is null and o.ends_at > now_at
        and (o.last_fix_at is null or o.last_fix_at < now_at - interval '2 seconds') then
    if not coalesce(p_lat between -90 and 90 and p_lng between -180 and 180,false) then
      raise exception 'No hay una posición GPS válida.' using errcode = '22023';
    end if;
    update public.tactical_mobile_objectives set last_lat=p_lat,last_lng=p_lng,last_fix_at=now_at
      where game_id = p_game returning * into o;
  end if;
  if o.game_id is null then return jsonb_build_object('objective',null); end if;
  mode := case when o.closed_at is not null or g.status = 'finished' or o.ends_at <= now_at then 'finished'
               when o.started_at is not null then 'live' else 'ready' end;
  visible_fix := mode = 'live' and g.status = 'active' and o.last_fix_at > now_at - interval '25 seconds';
  return jsonb_build_object('objective',jsonb_build_object(
    'status',mode,'game_active',g.status='active','minutes',o.duration_minutes,
    'remaining_ms',case when mode='live' then greatest(0, floor(extract(epoch from (o.ends_at-now_at))*1000)) else 0 end,
    'lat',case when mode='ready' then o.initial_lat when visible_fix then o.last_lat end,
    'lng',case when mode='ready' then o.initial_lng when visible_fix then o.last_lng end
  ));
end;
$$;
revoke all on function public.tactical_mobile_objective(uuid,uuid,text,text,integer,double precision,double precision)
from public, anon, authenticated;
grant execute on function public.tactical_mobile_objective(uuid,uuid,text,text,integer,double precision,double precision)
to service_role;
