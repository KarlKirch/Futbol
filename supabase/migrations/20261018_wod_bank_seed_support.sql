-- WOD bank seed support: allow metadata-first imports, then attach original images later.

alter table public.wod_bank_entries
  alter column image_path drop not null;

alter table public.wod_bank_entries
  add column if not exists source_filename text;
