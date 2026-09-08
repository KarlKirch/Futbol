import { createClient } from "npm:@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

const FEED_URLS = [
  "https://fixturedownload.com/feed/json/champions-league-2026",
  "https://fixturedownload.azurewebsites.net/feed/json/champions-league-2026",
];

const FOTMOB_TEAM_IDS: Record<string, string> = {
  "aek athens": "8563",
  "arsenal": "9825",
  "aston villa": "10252",
  "atletico madrid": "9906",
  "borussia dortmund": "9789",
  "barcelona": "8634",
  "bayern munich": "9823",
  "bodo glimt": "8402",
  "club brugge": "8342",
  "como": "10171",
  "fenerbahce": "8695",
  "feyenoord": "10235",
  "galatasaray": "8637",
  "inter": "8636",
  "lask": "9977",
  "rb leipzig": "178475",
  "lens": "8588",
  "lille": "8639",
  "liverpool": "8650",
  "manchester city": "8456",
  "manchester united": "10260",
  "napoli": "9875",
  "paris saint germain": "9847",
  "porto": "9773",
  "psv": "8640",
  "real betis": "8603",
  "real madrid": "8633",
  "roma": "8686",
  "s bratislava": "6019",
  "sabah": "951893",
  "shakhtar": "9728",
  "slavia prague": "7787",
  "sporting lisbon": "9768",
  "stuttgart": "10269",
  "viking": "8478",
  "villarreal": "10205",
};

function normalizeTeam(name: string) {
  return String(name || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "")
    .toLowerCase().replace(/\bfc\b/g, "").replace(/[^a-z0-9]+/g, " ").trim()
    .replace(/^man city$/, "manchester city")
    .replace(/^man utd$/, "manchester united")
    .replace(/^man united$/, "manchester united")
    .replace(/^inter milan$/, "inter")
    .replace(/^b dortmund$/, "borussia dortmund")
    .replace(/^dortmund$/, "borussia dortmund")
    .replace(/^atleti$/, "atletico madrid")
    .replace(/^atletico de madrid$/, "atletico madrid")
    .replace(/^paris$/, "paris saint germain")
    .replace(/^psg$/, "paris saint germain")
    .replace(/^leipzig$/, "rb leipzig")
    .replace(/^bayern munchen$/, "bayern munich")
    .replace(/^slavia praha$/, "slavia prague")
    .replace(/^sporting cp$/, "sporting lisbon");
}

function fotmobLogo(teamName: string) {
  const id = FOTMOB_TEAM_IDS[normalizeTeam(teamName)];
  return id ? `https://images.fotmob.com/image_resources/logo/teamlogo/${id}.png` : null;
}

function roundName(round: number) {
  if (round >= 1 && round <= 8) return `Liigafaas · ${round}. voor`;
  if (round === 9) return "Play-off · 1. mäng";
  if (round === 10) return "Play-off · 2. mäng";
  if (round === 11) return "1/8-finaal · 1. mäng";
  if (round === 12) return "1/8-finaal · 2. mäng";
  if (round === 13) return "Veerandfinaal · 1. mäng";
  if (round === 14) return "Veerandfinaal · 2. mäng";
  if (round === 15) return "Poolfinaal · 1. mäng";
  if (round === 16) return "Poolfinaal · 2. mäng";
  if (round === 17) return "Finaal";
  return `${round}. voor`;
}

function isoDate(value: string) {
  const d = new Date(String(value || "").replace(" ", "T"));
  if (Number.isNaN(d.getTime())) throw new Error(`Vigane mänguaeg: ${value}`);
  return d.toISOString();
}

async function fetchFeed() {
  let lastError = "";
  for (const url of FEED_URLS) {
    try {
      const response = await fetch(url, { headers: { "User-Agent": "Futbol-Champions-League/1.4" } });
      if (!response.ok) { lastError = `${url}: HTTP ${response.status}`; continue; }
      const body = await response.json();
      if (!Array.isArray(body)) { lastError = `${url}: vastus ei olnud loend`; continue; }
      return body;
    } catch (error) {
      lastError = error instanceof Error ? error.message : String(error);
    }
  }
  throw new Error(`Mängude allikat ei saanud laadida. ${lastError}`);
}

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });

  try {
    const supabaseUrl = Deno.env.get("SUPABASE_URL");
    const serviceRole = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
    if (!supabaseUrl || !serviceRole) throw new Error("Supabase serveri seaded puuduvad");

    const admin = createClient(supabaseUrl, serviceRole, {
      auth: { persistSession: false, autoRefreshToken: false },
    });

    const feed: any[] = await fetchFeed();
    const { data: assetsRaw } = await admin.from("team_assets").select("team_key,team_name,logo_url");
    const assets = new Map<string, string>();
    for (const row of assetsRaw || []) if (row.logo_url) assets.set(row.team_key, row.logo_url);

    let logosSynced = 0;
    const teams = new Map<string, string>();
    for (const m of feed) {
      teams.set(normalizeTeam(m.HomeTeam), String(m.HomeTeam || ""));
      teams.set(normalizeTeam(m.AwayTeam), String(m.AwayTeam || ""));
    }

    const canonicalRows = [...teams.entries()].flatMap(([key, teamName]) => {
      const logo = fotmobLogo(teamName);
      if (!logo) return [];
      assets.set(key, logo);
      return [{ team_key: key, team_name: teamName, logo_url: logo, updated_at: new Date().toISOString() }];
    });
    if (canonicalRows.length) {
      const { error: logoError } = await admin.from("team_assets").upsert(canonicalRows, { onConflict: "team_key" });
      if (logoError) throw logoError;
      logosSynced = canonicalRows.length;
    }

    const rows = feed.map((m: any) => {
      const round = Number(m.RoundNumber) || 0;
      return {
        home_team: String(m.HomeTeam || "").trim(),
        away_team: String(m.AwayTeam || "").trim(),
        kickoff_at: isoDate(m.DateUtc),
        round_number: round || null,
        round_name: roundName(round),
        external_match_id: `fixture-download:ucl-2026:${round}:${m.MatchNumber}`,
        source: "Fixture Download",
        venue: m.Location || null,
        home_logo_url: fotmobLogo(m.HomeTeam) || assets.get(normalizeTeam(m.HomeTeam)) || null,
        away_logo_url: fotmobLogo(m.AwayTeam) || assets.get(normalizeTeam(m.AwayTeam)) || null,
        home_score: m.HomeTeamScore === null || m.HomeTeamScore === undefined ? null : Number(m.HomeTeamScore),
        away_score: m.AwayTeamScore === null || m.AwayTeamScore === undefined ? null : Number(m.AwayTeamScore),
      };
    });

    const { data: syncResult, error: syncError } = await admin.rpc("sync_ucl_catalog", { p_rows: rows });
    if (syncError) throw syncError;

    await admin.from("competition_sync_state").upsert({
      sync_key: "ucl_2026_27",
      last_synced_at: new Date().toISOString(),
      last_logo_sync_at: new Date().toISOString(),
      last_result: JSON.stringify(syncResult || {}),
      updated_at: new Date().toISOString(),
    }, { onConflict: "sync_key" });

    return new Response(JSON.stringify({
      ok: true,
      catalog_synced: Number(syncResult?.catalog_upserted || 0),
      published_updated: Number(syncResult?.published_updated || 0),
      logos_synced: logosSynced,
      source: "Fixture Download + FotMob logos",
    }), { status: 200, headers: { ...corsHeaders, "Content-Type": "application/json" } });
  } catch (error) {
    return new Response(JSON.stringify({ ok: false, error: error instanceof Error ? error.message : String(error) }), {
      status: 200,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
