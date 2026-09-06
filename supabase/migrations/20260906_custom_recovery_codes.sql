create or replace function public.set_recovery_code(p_code text)
returns text
language plpgsql
security definer
set search_path = public, private, auth, extensions, pg_temp
as $$
declare
  v_uid uuid := auth.uid();
  v_clean_code text;
  v_hash text;
begin
  if v_uid is null then
    raise exception 'Kasutaja pole sisse logitud';
  end if;

  if not exists (select 1 from public.players where id = v_uid) then
    raise exception 'Mängijat ei leitud';
  end if;

  v_clean_code := upper(regexp_replace(coalesce(p_code, ''), '[^A-Z0-9]', '', 'g'));

  if length(v_clean_code) < 8 or length(v_clean_code) > 20 then
    raise exception 'Taastamiskood peab olema 8 kuni 20 märki';
  end if;

  v_hash := encode(extensions.digest(v_clean_code, 'sha256'::text), 'hex');

  if exists (
    select 1
    from private.player_recovery r
    where r.code_hash = v_hash
      and r.player_id <> v_uid
  ) then
    raise exception 'See taastamiskood on juba kasutusel';
  end if;

  insert into private.player_recovery(player_id, code_hash, updated_at)
  values (v_uid, v_hash, now())
  on conflict (player_id)
  do update set code_hash = excluded.code_hash, updated_at = now();

  return v_clean_code;
end;
$$;

revoke all on function public.set_recovery_code(text) from public;
grant execute on function public.set_recovery_code(text) to authenticated;
revoke execute on function public.set_recovery_code(text) from anon;

create or replace function public.restore_player(p_code text)
returns text
language plpgsql
security definer
set search_path = public, private, auth, extensions, pg_temp
as $$
declare
  v_new_uid uuid := auth.uid();
  v_old_uid uuid;
  v_name text;
  v_clean_code text;
begin
  if v_new_uid is null then
    raise exception 'Kasutaja pole sisse logitud';
  end if;

  if exists (select 1 from public.players where id = v_new_uid) then
    raise exception 'Praegusel seadmel on kasutaja juba seotud';
  end if;

  v_clean_code := upper(regexp_replace(coalesce(p_code, ''), '[^A-Z0-9]', '', 'g'));

  if length(v_clean_code) < 8 or length(v_clean_code) > 20 then
    raise exception 'Taastamiskood ei kehti';
  end if;

  select r.player_id, p.display_name
    into v_old_uid, v_name
  from private.player_recovery r
  join public.players p on p.id = r.player_id
  where r.code_hash = encode(extensions.digest(v_clean_code, 'sha256'::text), 'hex')
  limit 1;

  if v_old_uid is null then
    raise exception 'Taastamiskood ei kehti';
  end if;

  if v_old_uid = v_new_uid then
    return v_name;
  end if;

  insert into public.players(id, display_name)
  values (v_new_uid, '__restore__' || replace(v_new_uid::text, '-', ''));

  update public.predictions
  set user_id = v_new_uid
  where user_id = v_old_uid;

  update private.player_recovery
  set player_id = v_new_uid, updated_at = now()
  where player_id = v_old_uid;

  delete from auth.users
  where id = v_old_uid;

  update public.players
  set display_name = v_name
  where id = v_new_uid;

  return v_name;
end;
$$;
