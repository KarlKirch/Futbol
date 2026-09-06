create or replace function public.admin_delete_player(
  p_pin text,
  p_player_id uuid
)
returns boolean
language plpgsql
security definer
set search_path = public, private, auth, pg_temp
as $$
declare
  v_deleted integer := 0;
begin
  if not private.valid_admin_pin(p_pin) then
    raise exception 'Vale admin PIN';
  end if;

  if p_player_id = auth.uid() then
    raise exception 'Enda kasutajat ei saa kustutada';
  end if;

  delete from auth.users
  where id = p_player_id;

  get diagnostics v_deleted = row_count;

  if v_deleted = 0 then
    raise exception 'Kasutajat ei leitud';
  end if;

  return true;
end;
$$;

revoke all on function public.admin_delete_player(text, uuid) from public;
grant execute on function public.admin_delete_player(text, uuid) to authenticated;
