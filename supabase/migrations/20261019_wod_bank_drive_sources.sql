-- Store Google Drive source metadata for historical WOD imports.
alter table public.wod_bank_entries
  add column if not exists source_drive_file_id text,
  add column if not exists source_drive_url text;

create index if not exists wod_bank_entries_source_drive_file_id_idx
  on public.wod_bank_entries(source_drive_file_id);
