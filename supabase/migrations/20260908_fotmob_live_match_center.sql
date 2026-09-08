create table if not exists public.match_live_state (
  match_id uuid primary key references public.matches(id) on delete cascade,
  fotmob_match_id bigint,
  page_url text,
  phase text not null default 'scheduled',
  live_time text,
  started boolean not null default false,
  finished boolean not null default false,
  cancelled boolean not null default false,
  home_score smallint,
  away_score smallint,
  events jsonb not null default '[]'::jsonb,
  source text not null default 'FotMob',
  source_updated_at timestamptz,
  last_error text,
  updated_at timestamptz not null default now()
);

create unique index if not exists match_live_state_fotmob_match_id_uidx
  on public.match_live_state(fotmob_match_id)
  where fotmob_match_id is not null;

alter table public.match_live_state enable row level security;

drop policy if exists "authenticated can read live match state" on public.match_live_state;
create policy "authenticated can read live match state"
  on public.match_live_state
  for select
  to authenticated
  using (auth.uid() is not null);

grant select on public.match_live_state to authenticated;
revoke insert, update, delete on public.match_live_state from anon, authenticated;
revoke all on public.match_live_state from anon;
