create table if not exists private.player_devices (
  auth_user_id uuid primary key references auth.users(id) on delete cascade,
  player_id uuid not null references public.players(id) on delete cascade,
  linked_at timestamptz not null default now()
);

alter table private.player_devices enable row level security;
revoke all on private.player_devices from public, anon, authenticated;

insert into private.player_devices(auth_user_id, player_id)
select p.id, p.id
from public.players p
on conflict (auth_user_id) do nothing;

create or replace function private.current_player_id_for_auth(p_auth_uid uuid)
returns uuid
language sql
stable
security definer
set search_path = pg_catalog, public, private
as $$
  select coalesce(
    (select d.player_id from private.player_devices d where d.auth_user_id = p_auth_uid),
    (select p.id from public.players p where p.id = p_auth_uid)
  );
$$;

create or replace function private.current_player_id()
returns uuid
language sql
stable
security definer
set search_path = pg_catalog, public, private
as $$
  select private.current_player_id_for_auth(auth.uid());
$$;

revoke all on function private.current_player_id_for_auth(uuid) from public, anon, authenticated;
revoke all on function private.current_player_id() from public, anon, authenticated;

create or replace function private.ensure_player_device()
returns trigger
language plpgsql
security definer
set search_path = pg_catalog, private
as $$
begin
  insert into private.player_devices(auth_user_id, player_id)
  values (new.id, new.id)
  on conflict (auth_user_id) do update set player_id = excluded.player_id;
  return new;
end;
$$;

drop trigger if exists players_create_device_link on public.players;
create trigger players_create_device_link
after insert on public.players
for each row execute function private.ensure_player_device();

create or replace function public.get_current_player()
returns table(id uuid, display_name text, created_at timestamptz)
language sql
stable
security definer
set search_path = pg_catalog, public, private
as $$
  select p.id, p.display_name, p.created_at
  from public.players p
  where p.id = private.current_player_id();
$$;

revoke all on function public.get_current_player() from public, anon;
grant execute on function public.get_current_player() to authenticated;

drop policy if exists players_update_own on public.players;
create policy players_update_own on public.players for update to authenticated
using (id = private.current_player_id())
with check (id = private.current_player_id());

drop policy if exists predictions_read on public.predictions;
create policy predictions_read on public.predictions for select to authenticated
using (
  user_id = private.current_player_id()
  or exists (
    select 1 from public.matches m
    where m.id = predictions.match_id and now() >= m.kickoff_at
  )
);

drop policy if exists predictions_insert_own_before_kickoff on public.predictions;
create policy predictions_insert_own_before_kickoff on public.predictions for insert to authenticated
with check (
  user_id = private.current_player_id()
  and exists (
    select 1 from public.matches m
    where m.id = predictions.match_id and now() < m.kickoff_at
  )
);

drop policy if exists predictions_update_own_before_kickoff on public.predictions;
create policy predictions_update_own_before_kickoff on public.predictions for update to authenticated
using (
  user_id = private.current_player_id()
  and exists (
    select 1 from public.matches m
    where m.id = predictions.match_id and now() < m.kickoff_at
  )
)
with check (
  user_id = private.current_player_id()
  and exists (
    select 1 from public.matches m
    where m.id = predictions.match_id and now() < m.kickoff_at
  )
);

drop policy if exists chat_messages_insert_own on public.chat_messages;
create policy chat_messages_insert_own on public.chat_messages for insert to authenticated
with check (user_id = private.current_player_id());

create or replace function public.has_recovery_code()
returns boolean
language sql
security definer
set search_path = pg_catalog, public, private
as $$
  select exists(
    select 1 from private.player_recovery r
    where r.player_id = private.current_player_id()
  );
$$;

revoke all on function public.has_recovery_code() from public, anon;
grant execute on function public.has_recovery_code() to authenticated;

create or replace function public.set_recovery_code(p_code text)
returns text
language plpgsql
security definer
set search_path = pg_catalog, public, private, extensions
as $$
declare
  v_player_id uuid := private.current_player_id();
  v_clean_code text;
  v_hash text;
begin
  if auth.uid() is null then raise exception 'Kasutaja pole sisse logitud'; end if;
  if v_player_id is null then raise exception 'Mängijat ei leitud'; end if;

  v_clean_code := upper(regexp_replace(coalesce(p_code, ''), '[^A-Z0-9]', '', 'g'));
  if length(v_clean_code) < 8 or length(v_clean_code) > 20 then
    raise exception 'Taastamiskood peab olema 8 kuni 20 märki';
  end if;

  v_hash := encode(extensions.digest(v_clean_code, 'sha256'::text), 'hex');
  if exists (
    select 1 from private.player_recovery r
    where r.code_hash = v_hash and r.player_id <> v_player_id
  ) then
    raise exception 'See taastamiskood on juba kasutusel';
  end if;

  insert into private.player_recovery(player_id, code_hash, updated_at)
  values (v_player_id, v_hash, now())
  on conflict (player_id)
  do update set code_hash = excluded.code_hash, updated_at = now();

  return v_clean_code;
end;
$$;

revoke all on function public.set_recovery_code(text) from public, anon;
grant execute on function public.set_recovery_code(text) to authenticated;

create or replace function public.restore_player(p_code text)
returns text
language plpgsql
security definer
set search_path = pg_catalog, public, private, extensions
as $$
declare
  v_auth_uid uuid := auth.uid();
  v_source_player uuid := private.current_player_id();
  v_target_player uuid;
  v_target_name text;
  v_clean_code text;
  v_source_paid_at timestamptz;
begin
  if v_auth_uid is null then raise exception 'Kasutaja pole sisse logitud'; end if;

  v_clean_code := upper(regexp_replace(coalesce(p_code, ''), '[^A-Z0-9]', '', 'g'));
  if length(v_clean_code) < 8 or length(v_clean_code) > 20 then
    raise exception 'Taastamiskood ei kehti';
  end if;

  select r.player_id, p.display_name into v_target_player, v_target_name
  from private.player_recovery r
  join public.players p on p.id = r.player_id
  where r.code_hash = encode(extensions.digest(v_clean_code, 'sha256'::text), 'hex')
  limit 1;

  if v_target_player is null then raise exception 'Taastamiskood ei kehti'; end if;

  if v_source_player is null then
    insert into private.player_devices(auth_user_id, player_id, linked_at)
    values (v_auth_uid, v_target_player, now())
    on conflict (auth_user_id) do update set player_id = excluded.player_id, linked_at = now();
    return v_target_name;
  end if;

  if v_source_player = v_target_player then
    insert into private.player_devices(auth_user_id, player_id, linked_at)
    values (v_auth_uid, v_target_player, now())
    on conflict (auth_user_id) do update set player_id = excluded.player_id, linked_at = now();
    return v_target_name;
  end if;

  insert into public.predictions(match_id, user_id, home_score, away_score, created_at, updated_at)
  select p.match_id, v_target_player, p.home_score, p.away_score, p.created_at, p.updated_at
  from public.predictions p
  where p.user_id = v_source_player
  on conflict (match_id, user_id) do nothing;

  delete from public.predictions where user_id = v_source_player;
  update public.chat_messages set user_id = v_target_player where user_id = v_source_player;

  select paid_at into v_source_paid_at from private.player_payments where player_id = v_source_player;
  if v_source_paid_at is not null then
    update private.player_payments
    set paid_at = coalesce(paid_at, v_source_paid_at), updated_at = now()
    where player_id = v_target_player;
  end if;

  delete from private.player_recovery where player_id = v_source_player;
  delete from private.player_payments where player_id = v_source_player;
  update private.player_devices set player_id = v_target_player, linked_at = now() where player_id = v_source_player;

  insert into private.player_devices(auth_user_id, player_id, linked_at)
  values (v_auth_uid, v_target_player, now())
  on conflict (auth_user_id) do update set player_id = excluded.player_id, linked_at = now();

  delete from public.players where id = v_source_player;
  return v_target_name;
end;
$$;

revoke all on function public.restore_player(text) from public, anon;
grant execute on function public.restore_player(text) to authenticated;

create or replace function public.link_player_device(p_code text)
returns text
language sql
security definer
set search_path = pg_catalog, public
as $$ select public.restore_player(p_code); $$;

revoke all on function public.link_player_device(text) from public, anon;
grant execute on function public.link_player_device(text) to authenticated;

create or replace function public.get_my_payment_info()
returns table(
  amount numeric,
  payee text,
  iban text,
  payment_code text,
  payment_description text,
  is_paid boolean,
  paid_at timestamptz,
  entry_deadline timestamptz,
  deadline_passed boolean
)
language sql
stable
security definer
set search_path = pg_catalog, public, private
as $$
  select
    coalesce((select s.value::numeric from private.settings s where s.key = 'entry_fee_amount'), 10.00::numeric),
    coalesce((select s.value from private.settings s where s.key = 'entry_payee'), 'Oliver Ossipov'),
    coalesce((select s.value from private.settings s where s.key = 'entry_iban'), 'EE597700771005156592'),
    pp.payment_code,
    'FUTBOL 2026 ' || pl.display_name || ' ' || pp.payment_code,
    pp.paid_at is not null,
    pp.paid_at,
    private.entry_deadline(),
    private.entry_deadline() is not null and now() >= private.entry_deadline()
  from public.players pl
  join private.player_payments pp on pp.player_id = pl.id
  where pl.id = private.current_player_id();
$$;

revoke all on function public.get_my_payment_info() from public, anon;
grant execute on function public.get_my_payment_info() to authenticated;
