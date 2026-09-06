create or replace function public.current_player_id()
returns uuid
language sql
stable
security definer
set search_path = pg_catalog, public, private
as $$
  select private.current_player_id();
$$;

revoke all on function public.current_player_id() from public, anon;
grant execute on function public.current_player_id() to authenticated;

drop policy if exists players_update_own on public.players;
create policy players_update_own on public.players for update to authenticated
using (id = public.current_player_id())
with check (id = public.current_player_id());

drop policy if exists predictions_read on public.predictions;
create policy predictions_read on public.predictions for select to authenticated
using (
  user_id = public.current_player_id()
  or exists (
    select 1 from public.matches m
    where m.id = predictions.match_id and now() >= m.kickoff_at
  )
);

drop policy if exists predictions_insert_own_before_kickoff on public.predictions;
create policy predictions_insert_own_before_kickoff on public.predictions for insert to authenticated
with check (
  user_id = public.current_player_id()
  and exists (
    select 1 from public.matches m
    where m.id = predictions.match_id and now() < m.kickoff_at
  )
);

drop policy if exists predictions_update_own_before_kickoff on public.predictions;
create policy predictions_update_own_before_kickoff on public.predictions for update to authenticated
using (
  user_id = public.current_player_id()
  and exists (
    select 1 from public.matches m
    where m.id = predictions.match_id and now() < m.kickoff_at
  )
)
with check (
  user_id = public.current_player_id()
  and exists (
    select 1 from public.matches m
    where m.id = predictions.match_id and now() < m.kickoff_at
  )
);

drop policy if exists chat_messages_insert_own on public.chat_messages;
create policy chat_messages_insert_own on public.chat_messages for insert to authenticated
with check (user_id = public.current_player_id());
