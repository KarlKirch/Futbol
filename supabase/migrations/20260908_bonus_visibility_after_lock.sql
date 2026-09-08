create or replace function public.get_locked_bonus_answers()
returns table(
  question_key text,
  title text,
  points integer,
  player_id uuid,
  player_name text,
  answer_text text
)
language sql
stable
security definer
set search_path = pg_catalog, public, private
as $$
  select
    q.question_key,
    q.title,
    q.points,
    p.id,
    p.display_name,
    bp.answer_text
  from public.bonus_questions q
  cross join public.players p
  left join public.bonus_predictions bp
    on bp.question_key = q.question_key
   and bp.player_id = p.id
  where q.is_active
    and private.current_player_id() is not null
    and private.bonus_deadline() is not null
    and now() >= private.bonus_deadline()
  order by q.sort_order, q.question_key, lower(p.display_name), p.display_name;
$$;

revoke all on function public.get_locked_bonus_answers() from public, anon;
grant execute on function public.get_locked_bonus_answers() to authenticated;

create or replace function public.admin_get_bonus_missing(p_pin text)
returns table(
  question_key text,
  title text,
  missing_count integer,
  missing_names text[]
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
    q.question_key,
    q.title,
    count(p.id) filter (where bp.player_id is null)::integer as missing_count,
    coalesce(
      array_agg(p.display_name order by lower(p.display_name), p.display_name)
        filter (where bp.player_id is null),
      array[]::text[]
    ) as missing_names
  from public.bonus_questions q
  cross join public.players p
  left join public.bonus_predictions bp
    on bp.question_key = q.question_key
   and bp.player_id = p.id
  where q.is_active
  group by q.question_key, q.title, q.sort_order
  order by q.sort_order, q.question_key;
end;
$$;

revoke all on function public.admin_get_bonus_missing(text) from public, anon;
grant execute on function public.admin_get_bonus_missing(text) to authenticated;
