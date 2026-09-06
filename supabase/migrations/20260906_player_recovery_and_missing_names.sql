create table if not exists private.player_recovery (
  player_id uuid primary key references public.players(id) on delete cascade,
  code_hash text not null unique,
  updated_at timestamptz not null default now()
);

alter table private.player_recovery enable row level security;
revoke all on private.player_recovery from public, anon, authenticated;

create or replace function public.has_recovery_code()
returns boolean
language sql
security definer
set search_path = public, private, auth, pg_temp
as $$
  select exists(
    select 1 from private.player_recovery r where r.player_id = auth.uid()
  );
$$;

revoke all on function public.has_recovery_code() from public;
grant execute on function public.has_recovery_code() to authenticated;

create or replace function public.create_recovery_code()
returns text
language plpgsql
security definer
set search_path = public, private, auth, pg_temp
as $$
declare
  v_uid uuid := auth.uid();
  v_code text;
  v_hash text;
begin
  if v_uid is null then raise exception 'Kasutaja pole sisse logitud'; end if;
  if not exists (select 1 from public.players where id = v_uid) then
    raise exception 'Mängijat ei leitud';
  end if;

  loop
    v_code := upper(substr(replace(gen_random_uuid()::text, '-', ''), 1, 12));
    v_hash := encode(digest(v_code, 'sha256'), 'hex');
    exit when not exists (select 1 from private.player_recovery where code_hash = v_hash);
  end loop;

  insert into private.player_recovery(player_id, code_hash, updated_at)
  values (v_uid, v_hash, now())
  on conflict (player_id)
  do update set code_hash = excluded.code_hash, updated_at = now();

  return substr(v_code,1,4) || '-' || substr(v_code,5,4) || '-' || substr(v_code,9,4);
end;
$$;

revoke all on function public.create_recovery_code() from public;
grant execute on function public.create_recovery_code() to authenticated;

create or replace function public.restore_player(p_code text)
returns text
language plpgsql
security definer
set search_path = public, private, auth, pg_temp
as $$
declare
  v_new_uid uuid := auth.uid();
  v_old_uid uuid;
  v_name text;
  v_clean_code text;
begin
  if v_new_uid is null then raise exception 'Kasutaja pole sisse logitud'; end if;
  if exists (select 1 from public.players where id = v_new_uid) then
    raise exception 'Praegusel seadmel on kasutaja juba seotud';
  end if;

  v_clean_code := upper(regexp_replace(coalesce(p_code, ''), '[^A-Z0-9]', '', 'g'));
  if length(v_clean_code) <> 12 then raise exception 'Taastamiskood ei kehti'; end if;

  select r.player_id, p.display_name into v_old_uid, v_name
  from private.player_recovery r
  join public.players p on p.id = r.player_id
  where r.code_hash = encode(digest(v_clean_code, 'sha256'), 'hex')
  limit 1;

  if v_old_uid is null then raise exception 'Taastamiskood ei kehti'; end if;
  if v_old_uid = v_new_uid then return v_name; end if;

  insert into public.players(id, display_name)
  values (v_new_uid, '__restore__' || replace(v_new_uid::text, '-', ''));

  update public.predictions set user_id = v_new_uid where user_id = v_old_uid;
  update private.player_recovery set player_id = v_new_uid, updated_at = now() where player_id = v_old_uid;
  delete from auth.users where id = v_old_uid;
  update public.players set display_name = v_name where id = v_new_uid;

  return v_name;
end;
$$;

revoke all on function public.restore_player(text) from public;
grant execute on function public.restore_player(text) to authenticated;

drop function if exists public.admin_get_prediction_counts(text);

create function public.admin_get_prediction_counts(p_pin text)
returns table(match_id uuid, predictions_count bigint, players_count bigint, missing_names text[])
language plpgsql
security definer
set search_path = public, private, auth, pg_temp
as $$
begin
  if not private.valid_admin_pin(p_pin) then raise exception 'Vale admin PIN'; end if;

  return query
  select
    m.id,
    (select count(*) from public.predictions pr where pr.match_id = m.id)::bigint,
    (select count(*) from public.players)::bigint,
    coalesce(
      (
        select array_agg(p.display_name order by lower(p.display_name))
        from public.players p
        where not exists (
          select 1 from public.predictions pr2
          where pr2.match_id = m.id and pr2.user_id = p.id
        )
      ),
      array[]::text[]
    )
  from public.matches m;
end;
$$;

revoke all on function public.admin_get_prediction_counts(text) from public;
grant execute on function public.admin_get_prediction_counts(text) to authenticated;
