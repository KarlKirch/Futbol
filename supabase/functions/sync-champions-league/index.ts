import { createClient } from "npm:@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

const FEED_URL = "https://fixturedownload.com/feed/json/champions-league-2026";
const SYNC_KEY = "ucl_2026_27";
const FIXTURE_SYNC_MS = 15 * 60 * 1000;
const LOGO_SYNC_MS = 3 * 60 * 1000;
const LOGOS_PER_RUN = 24;

type FeedMatch = {
  MatchNumber: number;
  RoundNumber: number;
  DateUtc: string;
  Location?: string | null;
  HomeTeam: string;
  AwayTeam: string;
  HomeTeamScore?: number | null;
  AwayTeamScore?: number | null;
};

function normalizeTeam(name: string) {
  return String(name || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/\bfc\b/g, "")
    .replace(/[^a-z0-9]+/g, " ")
    .trim()
    .replace(/^b dortmund$/, "borussia dortmund")
    .replace(/^dortmund$/, "borussia dortmund")
    .replace(/^man city$/, "manchester city")
    .replace(/^man united$/, "manchester united")
    .replace(/^man utd$/, "manchester united")
    .replace(/^atleti$/, "atletico madrid")
    .replace(/^atletico de madrid$/, "atletico madrid")
    .replace(/^paris$/, "paris saint germain")
    .replace(/^psg$/, "paris saint germain")
    .replace(/^leipzig$/, "rb leipzig")
    .replace(/^bayern munchen$/, "bayern munich")
    .replace(/^slavia praha$/, "slavia prague")
    .replace(/^sporting cp$/, "sporting lisbon");
}

function logoSearchName(name: string) {
  const key = normalizeTeam(name);
  const aliases: Record<string, string> = {
    "borussia dortmund": "Borussia Dortmund",
    "manchester city": "Manchester City",
    "manchester united": "Manchester United",
    "atletico madrid": "Atletico Madrid",
    "paris saint germain": "Paris Saint-Germain",
    "rb leipzig": "RB Leipzig",
    "bayern munich": "Bayern Munich",
    "slavia prague": "Slavia Prague",
    "sporting lisbon": "Sporting Lisbon",
  };
  return aliases[key] || name;
}

function roundName(round: number) {
  if (round >= 1 && round <= 8) return `Liigafaas · ${round}. voor`;
  return `${round}. voor`;
}

function isoDate(value: string) {
  const normalized = String(value || "").replace(" ", "T");
  const date = new Date(normalized);
  if (Number.isNaN(date.getTime())) throw new Error(`Vigane mänguaeg: ${value}`);
  return date.toISOString();
}

async function resolveLogo(teamName: string) {
  try {
    const search = encodeURIComponent(logoSearchName(teamName));
    const response = await fetch(`https://www.thesportsdb.com/api/v1/json/123/searchteams.php?t=${search}`);
    if (!response.ok) return null;
    const data = await response.json();
    const teams = Array.isArray(data?.teams) ? data.teams : [];
    const soccer = teams.find((team: any) => String(team?.strSport || "").toLowerCase() === "soccer") || teams[0];
    return soccer?.strBadge || null;
  } catch {
    return null;
  }
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

    const now = Date.now();
    const { data: state } = await admin
      .schema("private")
      .from("competition_sync_state")
      .select("last_synced_at,last_logo_sync_at")
      .eq("sync_key", SYNC_KEY)
      .maybeSingle();

    const lastFixture = state?.last_synced_at ? new Date(state.last_synced_at).getTime() : 0;
    const lastLogo = state?.last_logo_sync_at ? new Date(state.last_logo_sync_at).getTime() : 0;
    const shouldFetchFixtures = !lastFixture || now - lastFixture >= FIXTURE_SYNC_MS;
    const shouldFetchLogos = !lastLogo || now - lastLogo >= LOGO_SYNC_MS;

    let feed: FeedMatch[] = [];
    let fixtureCount = 0;
    let logoCount = 0;

    if (shouldFetchFixtures || shouldFetchLogos) {
      const response = await fetch(FEED_URL, {
        headers: { "User-Agent": "Futbol-Champions-League/1.0" },
      });
      if (!response.ok) throw new Error(`Mängude allikas vastas ${response.status}`);
      const body = await response.json();
      if (!Array.isArray(body)) throw new Error("Mängude allika vastus ei olnud loend");
      feed = body as FeedMatch[];
    }

    const { data: assetsRaw } = await admin.from("team_assets").select("team_key,team_name,logo_url");
    const assets = new Map<string, { team_name: string; logo_url: string | null }>();
    for (const row of assetsRaw || []) assets.set(row.team_key, { team_name: row.team_name, logo_url: row.logo_url });

    if (shouldFetchLogos && feed.length) {
      const uniqueTeams = new Map<string, string>();
      for (const match of feed) {
        uniqueTeams.set(normalizeTeam(match.HomeTeam), match.HomeTeam);
        uniqueTeams.set(normalizeTeam(match.AwayTeam), match.AwayTeam);
      }

      const missing = [...uniqueTeams.entries()]
        .filter(([key]) => !assets.get(key)?.logo_url)
        .slice(0, LOGOS_PER_RUN);

      await admin.schema("private").from("competition_sync_state").upsert({
        sync_key: SYNC_KEY,
        last_logo_sync_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }, { onConflict: "sync_key" });

      for (let i = 0; i < missing.length; i += 6) {
        const batch = missing.slice(i, i + 6);
        const resolved = await Promise.all(batch.map(async ([key, teamName]) => ({
          key,
          teamName,
          badge: await resolveLogo(teamName),
        })));

        const upserts = resolved.filter(item => item.badge).map(item => ({
          team_key: item.key,
          team_name: item.teamName,
          logo_url: item.badge,
          updated_at: new Date().toISOString(),
        }));

        if (upserts.length) {
          await admin.from("team_assets").upsert(upserts, { onConflict: "team_key" });
          for (const item of upserts) {
            assets.set(item.team_key, { team_name: item.team_name, logo_url: item.logo_url });
            logoCount++;
          }
        }
      }
    }

    if (shouldFetchFixtures && feed.length) {
      const { data: existingRaw, error: existingError } = await admin
        .from("matches")
        .select("id,home_team,away_team,kickoff_at,external_match_id")
        .gte("kickoff_at", "2026-09-01T00:00:00Z");
      if (existingError) throw existingError;

      const byExternal = new Map<string, any>();
      const byNatural = new Map<string, any>();
      for (const row of existingRaw || []) {
        if (row.external_match_id) byExternal.set(row.external_match_id, row);
        const key = `${new Date(row.kickoff_at).toISOString()}|${normalizeTeam(row.home_team)}|${normalizeTeam(row.away_team)}`;
        byNatural.set(key, row);
      }

      const upsertRows: any[] = [];
      const manualUpdates: Array<{ id: string; row: any }> = [];

      for (const match of feed) {
        const kickoff = isoDate(match.DateUtc);
        const externalId = `fixture-download:ucl-2026:${match.MatchNumber}`;
        const homeKey = normalizeTeam(match.HomeTeam);
        const awayKey = normalizeTeam(match.AwayTeam);
        const naturalKey = `${kickoff}|${homeKey}|${awayKey}`;
        const existing = byExternal.get(externalId) || byNatural.get(naturalKey);

        const row = {
          home_team: match.HomeTeam,
          away_team: match.AwayTeam,
          kickoff_at: kickoff,
          round_number: Number(match.RoundNumber) || null,
          round_name: roundName(Number(match.RoundNumber) || 0),
          external_match_id: externalId,
          source: "Fixture Download",
          venue: match.Location || null,
          home_logo_url: assets.get(homeKey)?.logo_url || null,
          away_logo_url: assets.get(awayKey)?.logo_url || null,
          home_score: match.HomeTeamScore === null || match.HomeTeamScore === undefined ? null : Number(match.HomeTeamScore),
          away_score: match.AwayTeamScore === null || match.AwayTeamScore === undefined ? null : Number(match.AwayTeamScore),
          went_to_extra_time: false,
          updated_at: new Date().toISOString(),
        };

        if (existing?.id && !existing.external_match_id) manualUpdates.push({ id: existing.id, row });
        else upsertRows.push(row);
      }

      for (const item of manualUpdates) {
        const { error } = await admin.from("matches").update(item.row).eq("id", item.id);
        if (error) throw error;
      }

      for (let i = 0; i < upsertRows.length; i += 100) {
        const { error } = await admin
          .from("matches")
          .upsert(upsertRows.slice(i, i + 100), { onConflict: "external_match_id" });
        if (error) throw error;
      }

      fixtureCount = feed.length;
      await admin.schema("private").from("competition_sync_state").upsert({
        sync_key: SYNC_KEY,
        last_synced_at: new Date().toISOString(),
        last_result: `Synced ${fixtureCount} fixtures`,
        updated_at: new Date().toISOString(),
      }, { onConflict: "sync_key" });
    }

    return new Response(JSON.stringify({
      ok: true,
      fixtures_synced: fixtureCount,
      logos_synced: logoCount,
      cached: !shouldFetchFixtures,
      source: "Fixture Download",
    }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  } catch (error) {
    return new Response(JSON.stringify({
      ok: false,
      error: error instanceof Error ? error.message : String(error),
    }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
