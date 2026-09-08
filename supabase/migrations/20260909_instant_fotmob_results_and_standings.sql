alter table public.matches
  add column if not exists result_source text,
  add column if not exists result_updated_at timestamptz;

do $$
begin
  if not exists (
    select 1 from pg_constraint
    where conname = 'matches_result_source_check'
      and conrelid = 'public.matches'::regclass
  ) then
    alter table public.matches
      add constraint matches_result_source_check
      check (result_source is null or result_source in ('admin','fotmob'));
  end if;
end
$$;

-- Preserve scores entered before automatic FotMob finalization as manual/admin results.
update public.matches
set result_source = 'admin',
    result_updated_at = coalesce(updated_at, finished_at, now())
where result_source is null
  and home_score is not null
  and away_score is not null;

create or replace function private.finalize_match_from_live_state()
returns trigger
language plpgsql
security definer
set search_path = pg_catalog, public, private
as $$
declare
  v_extra_time boolean := false;
begin
  if new.finished is true
     and coalesce(new.cancelled, false) is false
     and new.home_score is not null
     and new.away_score is not null then

    select coalesce(bool_or((e->>'minute')::integer > 90), false)
      into v_extra_time
    from jsonb_array_elements(coalesce(new.events, '[]'::jsonb)) e
    where coalesce(e->>'minute','') ~ '^[0-9]+$';

    update public.matches m
       set home_score = new.home_score::integer,
           away_score = new.away_score::integer,
           went_to_extra_time = v_extra_time,
           finished_at = coalesce(m.finished_at, new.source_updated_at, new.updated_at, now()),
           result_source = 'fotmob',
           result_updated_at = coalesce(new.source_updated_at, new.updated_at, now()),
           updated_at = now()
     where m.id = new.match_id
       and now() >= m.kickoff_at
       and coalesce(m.result_source, '') <> 'admin';
  end if;

  return new;
end;
$$;

drop trigger if exists trg_finalize_match_from_live_state on public.match_live_state;
create trigger trg_finalize_match_from_live_state
after insert or update of finished, cancelled, home_score, away_score, events, source_updated_at
on public.match_live_state
for each row
execute function private.finalize_match_from_live_state();

-- Promote matches that had already reached FT before this migration.
update public.matches m
   set home_score = l.home_score::integer,
       away_score = l.away_score::integer,
       went_to_extra_time = coalesce((
         select bool_or((e->>'minute')::integer > 90)
         from jsonb_array_elements(coalesce(l.events, '[]'::jsonb)) e
         where coalesce(e->>'minute','') ~ '^[0-9]+$'
       ), false),
       finished_at = coalesce(m.finished_at, l.source_updated_at, l.updated_at, now()),
       result_source = 'fotmob',
       result_updated_at = coalesce(l.source_updated_at, l.updated_at, now()),
       updated_at = now()
  from public.match_live_state l
 where l.match_id = m.id
   and l.finished is true
   and coalesce(l.cancelled, false) is false
   and l.home_score is not null
   and l.away_score is not null
   and m.result_source is null
   and now() >= m.kickoff_at;

create or replace function public.admin_set_result(
  p_pin text,
  p_match_id uuid,
  p_home_score integer,
  p_away_score integer,
  p_went_to_extra_time boolean default false
)
returns void
language plpgsql
security definer
set search_path = pg_catalog, public, private
as $$
declare
  v_kickoff timestamptz;
begin
  if not private.valid_admin_pin(p_pin) then
    raise exception 'Vale admin PIN' using errcode = '42501';
  end if;

  if p_home_score < 0 or p_away_score < 0 then
    raise exception 'Skoor ei saa olla negatiivne';
  end if;

  select m.kickoff_at into v_kickoff
  from public.matches m where m.id = p_match_id;

  if not found then
    raise exception 'Mängu ei leitud';
  end if;

  if now() < v_kickoff then
    raise exception 'Tulemust ei saa sisestada enne mängu algust';
  end if;

  update public.matches
     set home_score = p_home_score,
         away_score = p_away_score,
         went_to_extra_time = coalesce(p_went_to_extra_time, false),
         finished_at = coalesce(finished_at, now()),
         result_source = 'admin',
         result_updated_at = now(),
         updated_at = now()
   where id = p_match_id;
end;
$$;

do $$
begin
  if not exists (
    select 1
    from pg_publication_tables
    where pubname = 'supabase_realtime'
      and schemaname = 'public'
      and tablename = 'matches'
  ) then
    alter publication supabase_realtime add table public.matches;
  end if;
end
$$;

-- A prior 10-second live refresh job is authoritative; remove any duplicate minute job.
do $$
declare
  v_jobid bigint;
begin
  for v_jobid in select jobid from cron.job where jobname = 'futbol-live-score-refresh'
  loop
    perform cron.unschedule(v_jobid);
  end loop;
end
$$;
