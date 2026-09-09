create table if not exists public.player_presence (
  player_id uuid primary key references public.players(id) on delete cascade,
  last_seen timestamptz not null default now()
);

alter table public.player_presence enable row level security;

revoke all on public.player_presence from public, anon;
grant select, insert, update on public.player_presence to authenticated;

drop policy if exists player_presence_select_authenticated on public.player_presence;
create policy player_presence_select_authenticated
on public.player_presence
for select
to authenticated
using (true);

drop policy if exists player_presence_insert_own on public.player_presence;
create policy player_presence_insert_own
on public.player_presence
for insert
to authenticated
with check (player_id = auth.uid());

drop policy if exists player_presence_update_own on public.player_presence;
create policy player_presence_update_own
on public.player_presence
for update
to authenticated
using (player_id = auth.uid())
with check (player_id = auth.uid());

create index if not exists player_presence_last_seen_idx on public.player_presence(last_seen desc);
