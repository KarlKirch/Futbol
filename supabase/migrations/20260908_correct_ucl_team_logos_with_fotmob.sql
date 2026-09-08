-- Keep current Champions League club crests deterministic and avoid ambiguous
-- name-only logo searches (for example Man Utd and Sabah).

do $$
declare
  r record;
begin
  for r in
    select * from (values
      ('aek athens','AEK Athens','8563'),
      ('arsenal','Arsenal','9825'),
      ('aston villa','Aston Villa','10252'),
      ('atletico madrid','Atleti','9906'),
      ('borussia dortmund','B. Dortmund','9789'),
      ('barcelona','Barcelona','8634'),
      ('bayern munich','Bayern München','9823'),
      ('bayern munchen','Bayern München','9823'),
      ('bodo glimt','Bodø/Glimt','8402'),
      ('club brugge','Club Brugge','8342'),
      ('como','Como','10171'),
      ('fenerbahce','Fenerbahçe','8695'),
      ('feyenoord','Feyenoord','10235'),
      ('galatasaray','Galatasaray','8637'),
      ('inter','Inter','8636'),
      ('lask','LASK','9977'),
      ('leipzig','Leipzig','178475'),
      ('rb leipzig','Leipzig','178475'),
      ('lens','Lens','8588'),
      ('lille','Lille','8639'),
      ('liverpool','Liverpool','8650'),
      ('manchester city','Man City','8456'),
      ('manchester united','Man Utd','10260'),
      ('man utd','Man Utd','10260'),
      ('napoli','Napoli','9875'),
      ('paris saint germain','Paris','9847'),
      ('porto','Porto','9773'),
      ('psv','PSV','8640'),
      ('real betis','Real Betis','8603'),
      ('real madrid','Real Madrid','8633'),
      ('roma','Roma','8686'),
      ('s bratislava','S. Bratislava','6019'),
      ('sabah','Sabah','951893'),
      ('shakhtar','Shakhtar','9728'),
      ('slavia praha','Slavia Praha','7787'),
      ('slavia prague','Slavia Praha','7787'),
      ('sporting lisbon','Sporting CP','9768'),
      ('sporting cp','Sporting CP','9768'),
      ('stuttgart','Stuttgart','10269'),
      ('viking','Viking','8478'),
      ('villarreal','Villarreal','10205')
    ) as v(team_key, team_name, fotmob_id)
  loop
    insert into public.team_assets(team_key, team_name, logo_url, updated_at)
    values (
      r.team_key,
      r.team_name,
      'https://images.fotmob.com/image_resources/logo/teamlogo/' || r.fotmob_id || '.png',
      now()
    )
    on conflict (team_key) do update
      set team_name = excluded.team_name,
          logo_url = excluded.logo_url,
          updated_at = now();
  end loop;

  for r in
    select * from (values
      ('AEK Athens','8563'),('Arsenal','9825'),('Aston Villa','10252'),('Atleti','9906'),
      ('B. Dortmund','9789'),('Barcelona','8634'),('Bayern München','9823'),('Bodø/Glimt','8402'),
      ('Club Brugge','8342'),('Como','10171'),('Fenerbahçe','8695'),('Feyenoord','10235'),
      ('Galatasaray','8637'),('Inter','8636'),('LASK','9977'),('Leipzig','178475'),
      ('Lens','8588'),('Lille','8639'),('Liverpool','8650'),('Man City','8456'),
      ('Man Utd','10260'),('Napoli','9875'),('Paris','9847'),('Porto','9773'),('PSV','8640'),
      ('Real Betis','8603'),('Real Madrid','8633'),('Roma','8686'),('S. Bratislava','6019'),
      ('Sabah','951893'),('Shakhtar','9728'),('Slavia Praha','7787'),('Sporting CP','9768'),
      ('Stuttgart','10269'),('Viking','8478'),('Villarreal','10205')
    ) as v(team_name, fotmob_id)
  loop
    update public.ucl_fixtures
      set home_logo_url = 'https://images.fotmob.com/image_resources/logo/teamlogo/' || r.fotmob_id || '.png'
      where home_team = r.team_name;
    update public.ucl_fixtures
      set away_logo_url = 'https://images.fotmob.com/image_resources/logo/teamlogo/' || r.fotmob_id || '.png'
      where away_team = r.team_name;
    update public.matches
      set home_logo_url = 'https://images.fotmob.com/image_resources/logo/teamlogo/' || r.fotmob_id || '.png'
      where home_team = r.team_name;
    update public.matches
      set away_logo_url = 'https://images.fotmob.com/image_resources/logo/teamlogo/' || r.fotmob_id || '.png'
      where away_team = r.team_name;
  end loop;
end
$$;
