create table if not exists private.player_payments (
  player_id uuid primary key references public.players(id) on delete cascade,
  payment_code text not null unique,
  paid_at timestamptz,
  updated_at timestamptz not null default now()
);

alter table private.player_payments enable row level security;
revoke all on private.player_payments from public, anon, authenticated;

insert into private.settings(key, value) values
  ('entry_fee_amount', '10.00'),
  ('entry_payee', 'Oliver Ossipov'),
  ('entry_iban', 'EE597700771005156592')
on conflict (key) do update set value = excluded.value;

create or replace function private.ensure_player_payment()
returns trigger
language plpgsql
security definer
set search_path = pg_catalog, private
as $$
begin
  insert into private.player_payments(player_id, payment_code)
  values (new.id, upper(substr(md5(new.id::text), 1, 6)))
  on conflict (player_id) do nothing;
  return new;
end;
$$;

insert into private.player_payments(player_id, payment_code)
select p.id, upper(substr(md5(p.id::text), 1, 6))
from public.players p
on conflict (player_id) do nothing;

drop trigger if exists players_create_payment on public.players;
create trigger players_create_payment
after insert on public.players
for each row execute function private.ensure_player_payment();

create or replace function private.entry_deadline()
returns timestamptz
language sql
stable
security definer
set search_path = pg_catalog, public, private
as $$
  select coalesce(
    nullif((select s.value from private.settings s where s.key = 'entry_deadline'), '')::timestamptz,
    (select min(m.kickoff_at) from public.matches m)
  );
$$;

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
  where pl.id = auth.uid();
$$;

revoke all on function public.get_my_payment_info() from public, anon;
grant execute on function public.get_my_payment_info() to authenticated;

create or replace function public.admin_get_payments(p_pin text)
returns table(
  player_id uuid,
  player_name text,
  payment_code text,
  payment_description text,
  is_paid boolean,
  paid_at timestamptz,
  entry_deadline timestamptz
)
language plpgsql
stable
security definer
set search_path = pg_catalog, public, private
as $$
begin
  if not private.valid_admin_pin(p_pin) then
    raise exception 'Vale admin PIN';
  end if;

  return query
  select
    pl.id,
    pl.display_name,
    pp.payment_code,
    'FUTBOL 2026 ' || pl.display_name || ' ' || pp.payment_code,
    pp.paid_at is not null,
    pp.paid_at,
    private.entry_deadline()
  from public.players pl
  join private.player_payments pp on pp.player_id = pl.id
  order by (pp.paid_at is not null) asc, lower(pl.display_name) asc;
end;
$$;

revoke all on function public.admin_get_payments(text) from public, anon;
grant execute on function public.admin_get_payments(text) to authenticated;

create or replace function public.admin_set_player_paid(p_pin text, p_player_id uuid, p_paid boolean)
returns boolean
language plpgsql
security definer
set search_path = pg_catalog, public, private
as $$
begin
  if not private.valid_admin_pin(p_pin) then
    raise exception 'Vale admin PIN';
  end if;

  update private.player_payments
  set paid_at = case when p_paid then coalesce(paid_at, now()) else null end,
      updated_at = now()
  where player_id = p_player_id;

  if not found then
    raise exception 'Mängijat ei leitud';
  end if;

  return p_paid;
end;
$$;

revoke all on function public.admin_set_player_paid(text, uuid, boolean) from public, anon;
grant execute on function public.admin_set_player_paid(text, uuid, boolean) to authenticated;

create or replace function public.get_leaderboard()
returns table(
  rank_no bigint,
  player_id uuid,
  player_name text,
  total_points bigint,
  exact_scores bigint,
  predictions_count bigint
)
language sql
stable
security definer
set search_path = pg_catalog, public, private
as $$
with scored as (
  select
    p.user_id,
    sum(public.calculate_points(p.home_score, p.away_score, m.home_score, m.away_score))::bigint as total_points,
    count(*)::bigint as predictions_count,
    count(*) filter (
      where p.home_score = m.home_score and p.away_score = m.away_score
    )::bigint as exact_scores
  from public.predictions p
  join public.matches m on m.id = p.match_id
  join private.player_payments pay on pay.player_id = p.user_id and pay.paid_at is not null
  where m.home_score is not null
    and m.away_score is not null
    and now() >= m.kickoff_at
  group by p.user_id
),
ranking as (
  select
    pl.id as player_id,
    pl.display_name as player_name,
    coalesce(s.total_points, 0)::bigint as total_points,
    coalesce(s.exact_scores, 0)::bigint as exact_scores,
    coalesce(s.predictions_count, 0)::bigint as predictions_count
  from public.players pl
  join private.player_payments pay on pay.player_id = pl.id and pay.paid_at is not null
  left join scored s on s.user_id = pl.id
)
select
  row_number() over (
    order by total_points desc, exact_scores desc, player_name asc
  ) as rank_no,
  player_id,
  player_name,
  total_points,
  exact_scores,
  predictions_count
from ranking
order by total_points desc, exact_scores desc, player_name asc;
$$;

revoke all on function public.get_leaderboard() from public, anon;
grant execute on function public.get_leaderboard() to authenticated;
