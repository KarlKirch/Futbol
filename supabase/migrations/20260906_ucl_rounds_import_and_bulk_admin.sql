alter table public.matches
  add column if not exists round_number integer,
  add column if not exists round_name text,
  add column if not exists external_match_id text,
  add column if not exists source text,
  add column if not exists venue text,
  add column if not exists home_logo_url text,
  add column if not exists away_logo_url text;

create unique index if not exists matches_external_match_id_uidx
  on public.matches(external_match_id)
  where external_match_id is not null;

create table if not exists public.team_assets (
  team_key text primary key,
  team_name text not null,
  logo_url text,
  updated_at timestamptz not null default now()
);

alter table public.team_assets enable row level security;

do $$
begin
  if not exists (
    select 1 from pg_policies
    where schemaname = 'public'
      and tablename = 'team_assets'
      and policyname = 'Authenticated can read team assets'
  ) then
    create policy "Authenticated can read team assets"
      on public.team_assets
      for select
      to authenticated
      using (true);
  end if;
end $$;

revoke all on public.team_assets from anon;
grant select on public.team_assets to authenticated;

create table if not exists private.competition_sync_state (
  sync_key text primary key,
  last_synced_at timestamptz,
  last_logo_sync_at timestamptz,
  last_result text,
  updated_at timestamptz not null default now()
);

revoke all on private.competition_sync_state from public, anon, authenticated;

create or replace function public.admin_create_match_v2(
  p_pin text,
  p_home_team text,
  p_away_team text,
  p_kickoff_at timestamptz,
  p_round_number integer default null,
  p_round_name text default null
)
returns uuid
language plpgsql
security definer
set search_path = pg_catalog, public, private
as $$
declare
  v_id uuid;
begin
  if not private.valid_admin_pin(p_pin) then
    raise exception 'Vale admin PIN' using errcode = '42501';
  end if;

  if btrim(coalesce(p_home_team, '')) = '' or btrim(coalesce(p_away_team, '')) = '' then
    raise exception 'Meeskonna nimi ei tohi olla tühi';
  end if;

  if lower(btrim(p_home_team)) = lower(btrim(p_away_team)) then
    raise exception 'Meeskonnad peavad olema erinevad';
  end if;

  if p_kickoff_at <= now() then
    raise exception 'Uue mängu algusaeg peab olema tulevikus';
  end if;

  insert into public.matches(
    home_team, away_team, kickoff_at, round_number, round_name, source
  ) values (
    btrim(p_home_team), btrim(p_away_team), p_kickoff_at,
    p_round_number, nullif(btrim(coalesce(p_round_name, '')), ''), 'manual'
  ) returning id into v_id;

  return v_id;
end;
$$;

create or replace function public.admin_update_match_v2(
  p_pin text,
  p_match_id uuid,
  p_home_team text,
  p_away_team text,
  p_kickoff_at timestamptz,
  p_round_number integer default null,
  p_round_name text default null
)
returns void
language plpgsql
security definer
set search_path = pg_catalog, public, private
as $$
declare
  v_current_kickoff timestamptz;
begin
  if not private.valid_admin_pin(p_pin) then
    raise exception 'Vale admin PIN' using errcode = '42501';
  end if;

  select kickoff_at into v_current_kickoff
  from public.matches
  where id = p_match_id;

  if not found then
    raise exception 'Mängu ei leitud';
  end if;

  if now() >= v_current_kickoff then
    raise exception 'Alanud mängu ei saa muuta';
  end if;

  if btrim(coalesce(p_home_team, '')) = '' or btrim(coalesce(p_away_team, '')) = '' then
    raise exception 'Meeskonna nimi ei tohi olla tühi';
  end if;

  if lower(btrim(p_home_team)) = lower(btrim(p_away_team)) then
    raise exception 'Meeskonnad peavad olema erinevad';
  end if;

  if p_kickoff_at <= now() then
    raise exception 'Mängu algusaeg peab olema tulevikus';
  end if;

  update public.matches
  set home_team = btrim(p_home_team),
      away_team = btrim(p_away_team),
      kickoff_at = p_kickoff_at,
      round_number = p_round_number,
      round_name = nullif(btrim(coalesce(p_round_name, '')), '')
  where id = p_match_id;
end;
$$;

create or replace function public.admin_bulk_create_matches(
  p_pin text,
  p_matches jsonb
)
returns integer
language plpgsql
security definer
set search_path = pg_catalog, public, private
as $$
declare
  v_item jsonb;
  v_count integer := 0;
  v_home text;
  v_away text;
  v_kickoff timestamptz;
  v_round_number integer;
  v_round_name text;
begin
  if not private.valid_admin_pin(p_pin) then
    raise exception 'Vale admin PIN' using errcode = '42501';
  end if;

  if jsonb_typeof(p_matches) <> 'array' then
    raise exception 'Mängude loend peab olema massiiv';
  end if;

  for v_item in select value from jsonb_array_elements(p_matches)
  loop
    v_home := btrim(coalesce(v_item->>'home_team', ''));
    v_away := btrim(coalesce(v_item->>'away_team', ''));
    v_kickoff := (v_item->>'kickoff_at')::timestamptz;
    v_round_number := nullif(v_item->>'round_number', '')::integer;
    v_round_name := nullif(btrim(coalesce(v_item->>'round_name', '')), '');

    if v_home = '' or v_away = '' then
      raise exception 'Meeskonna nimi ei tohi olla tühi';
    end if;
    if lower(v_home) = lower(v_away) then
      raise exception 'Meeskonnad peavad olema erinevad';
    end if;
    if v_kickoff <= now() then
      raise exception 'Uue mängu algusaeg peab olema tulevikus';
    end if;

    insert into public.matches(
      home_team, away_team, kickoff_at, round_number, round_name, source
    ) values (
      v_home, v_away, v_kickoff, v_round_number, v_round_name, 'manual'
    );
    v_count := v_count + 1;
  end loop;

  return v_count;
end;
$$;

revoke all on function public.admin_create_match_v2(text, text, text, timestamptz, integer, text) from public, anon;
revoke all on function public.admin_update_match_v2(text, uuid, text, text, timestamptz, integer, text) from public, anon;
revoke all on function public.admin_bulk_create_matches(text, jsonb) from public, anon;
grant execute on function public.admin_create_match_v2(text, text, text, timestamptz, integer, text) to authenticated;
grant execute on function public.admin_update_match_v2(text, uuid, text, text, timestamptz, integer, text) to authenticated;
grant execute on function public.admin_bulk_create_matches(text, jsonb) to authenticated;
