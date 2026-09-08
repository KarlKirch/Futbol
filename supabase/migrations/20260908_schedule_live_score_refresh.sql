insert into private.settings(key, value)
values ('live_cron_token', replace(gen_random_uuid()::text, '-', ''))
on conflict (key) do nothing;

create or replace function public.check_live_cron_token(p_token text)
returns boolean
language sql
stable
security definer
set search_path = pg_catalog, public, private
as $$
  select coalesce(
    p_token is not null
    and length(p_token) >= 24
    and p_token = (select value from private.settings where key = 'live_cron_token'),
    false
  );
$$;

revoke all on function public.check_live_cron_token(text) from public, anon, authenticated;
grant execute on function public.check_live_cron_token(text) to service_role;

create or replace function private.trigger_live_refresh()
returns void
language plpgsql
security definer
set search_path = pg_catalog, public, private, net
as $$
declare
  v_token text;
begin
  if not exists (
    select 1
    from public.matches m
    left join public.match_live_state l on l.match_id = m.id
    where m.kickoff_at between now() - interval '4 hours' and now() + interval '20 minutes'
      and coalesce(l.finished, false) = false
      and (l.updated_at is null or l.updated_at < now() - interval '7 seconds')
  ) then
    return;
  end if;

  select value into v_token
  from private.settings
  where key = 'live_cron_token';

  if v_token is null or length(v_token) < 24 then
    return;
  end if;

  perform net.http_post(
    url := 'https://aanxpugvehwtcwwpefwx.supabase.co/functions/v1/ucl-live-cron',
    headers := jsonb_build_object(
      'Content-Type', 'application/json',
      'x-cron-token', v_token
    ),
    body := '{}'::jsonb,
    timeout_milliseconds := 8000
  );
end;
$$;

revoke all on function private.trigger_live_refresh() from public;

do $$
declare
  v_jobid bigint;
begin
  for v_jobid in select jobid from cron.job where jobname = 'futbol-live-refresh'
  loop
    perform cron.unschedule(v_jobid);
  end loop;
end $$;

select cron.schedule(
  'futbol-live-refresh',
  '10 seconds',
  'select private.trigger_live_refresh();'
);
