create or replace function public.admin_issue_player_recovery_code(p_pin text, p_player_id uuid)
returns text
language plpgsql
security definer
set search_path = pg_catalog, public, private, extensions
as $$
declare
  v_code text;
  v_hash text;
  v_try integer := 0;
begin
  if not private.valid_admin_pin(p_pin) then
    raise exception 'Vale admin PIN';
  end if;

  if not exists (select 1 from public.players p where p.id = p_player_id) then
    raise exception 'Mängijat ei leitud';
  end if;

  loop
    v_try := v_try + 1;
    v_code := upper(encode(extensions.gen_random_bytes(6), 'hex'));
    v_hash := encode(extensions.digest(v_code, 'sha256'::text), 'hex');
    exit when not exists (
      select 1 from private.player_recovery r
      where r.code_hash = v_hash and r.player_id <> p_player_id
    );
    if v_try >= 10 then
      raise exception 'Taastamiskoodi loomine ebaõnnestus';
    end if;
  end loop;

  insert into private.player_recovery(player_id, code_hash, updated_at)
  values (p_player_id, v_hash, now())
  on conflict (player_id)
  do update set code_hash = excluded.code_hash, updated_at = now();

  return v_code;
end;
$$;

revoke all on function public.admin_issue_player_recovery_code(text, uuid) from public, anon;
grant execute on function public.admin_issue_player_recovery_code(text, uuid) to authenticated;
