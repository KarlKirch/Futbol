alter table public.push_subscriptions
  add column if not exists chat_enabled boolean not null default false;

create index if not exists push_subscriptions_chat_enabled_idx
  on public.push_subscriptions (user_id)
  where chat_enabled = true;

create table if not exists private.chat_push_log (
  message_id bigint primary key references public.chat_messages(id) on delete cascade,
  sent_at timestamptz not null default now()
);

revoke all on table private.chat_push_log from public, anon, authenticated;

create or replace function public.server_claim_chat_push(p_message_id bigint)
returns boolean
language plpgsql
security definer
set search_path = pg_catalog, public, private
as $$
begin
  insert into private.chat_push_log(message_id)
  values (p_message_id)
  on conflict (message_id) do nothing;
  return found;
end;
$$;

revoke all on function public.server_claim_chat_push(bigint) from public, anon, authenticated;
grant execute on function public.server_claim_chat_push(bigint) to service_role;
