create or replace function private.capture_entry_deadline()
returns trigger
language plpgsql
security definer
set search_path = pg_catalog, public, private
as $$
declare
  current_deadline timestamptz;
begin
  select nullif(s.value, '')::timestamptz
  into current_deadline
  from private.settings s
  where s.key = 'entry_deadline';

  if current_deadline is null or new.kickoff_at < current_deadline then
    insert into private.settings(key, value)
    values ('entry_deadline', new.kickoff_at::text)
    on conflict (key) do update set value = excluded.value;
  end if;

  return new;
end;
$$;

drop trigger if exists matches_capture_entry_deadline on public.matches;
create trigger matches_capture_entry_deadline
after insert on public.matches
for each row execute function private.capture_entry_deadline();

insert into private.settings(key, value)
select 'entry_deadline', min(m.kickoff_at)::text
from public.matches m
having count(*) > 0
on conflict (key) do nothing;
