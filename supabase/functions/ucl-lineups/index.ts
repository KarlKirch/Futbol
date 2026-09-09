import { createClient } from "npm:@supabase/supabase-js@2";

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

const FETCH_TIMEOUT_MS = 9000;
const CACHE_TTL_MS = 45_000;
const resultCache = new Map<string, { at:number; value:any }>();
const teamPageCache = new Map<string, { at:number; value:any }>();

function jsonResponse(payload: unknown, status = 200) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { ...CORS_HEADERS, "Content-Type": "application/json", "Cache-Control": "no-store" },
  });
}

function normalize(value: string) {
  return String(value || "")
    .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
    .toLowerCase().replace(/&/g, " and ")
    .replace(/\b(fc|cf|ac|ssc|afc|fk|sk|sc|rcd|rc|sl|vfb)\b/g, " ")
    .replace(/[^a-z0-9]+/g, " ").replace(/\s+/g, " ").trim();
}

function canonical(value: string) {
  const s = normalize(value);
  const aliases: Record<string,string> = {
    "manchester city":"man city", "man city":"man city",
    "manchester united":"man united", "man utd":"man united", "man united":"man united",
    "atletico madrid":"atleti", "atletico de madrid":"atleti", "atleti":"atleti",
    "borussia dortmund":"dortmund", "b dortmund":"dortmund", "dortmund":"dortmund",
    "bayern munich":"bayern", "bayern munchen":"bayern", "bayern":"bayern",
    "paris saint germain":"paris", "psg":"paris", "paris":"paris",
    "porto":"porto", "fc porto":"porto",
    "rb leipzig":"leipzig", "leipzig":"leipzig",
    "slovan bratislava":"slovan bratislava", "s bratislava":"slovan bratislava",
    "shakhtar donetsk":"shakhtar", "shakhtar":"shakhtar",
    "slavia prague":"slavia praha", "slavia praha":"slavia praha",
    "sporting lisbon":"sporting cp", "sporting":"sporting cp", "sporting cp":"sporting cp",
    "internazionale":"inter", "inter milan":"inter", "inter":"inter",
    "bodo glimt":"bodo glimt",
  };
  return aliases[s] || s;
}

function assetKey(name:string) {
  return normalize(name)
    .replace(/^b dortmund$/, "borussia dortmund")
    .replace(/^man city$/, "manchester city")
    .replace(/^man utd$/, "manchester united")
    .replace(/^man united$/, "manchester united")
    .replace(/^atleti$/, "atletico madrid")
    .replace(/^paris$/, "paris saint germain")
    .replace(/^leipzig$/, "rb leipzig")
    .replace(/^bayern munchen$/, "bayern munich")
    .replace(/^slavia praha$/, "slavia prague")
    .replace(/^sporting cp$/, "sporting lisbon");
}

async function fetchText(url:string) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);
  try {
    const response = await fetch(url, {
      headers: {
        "Accept":"text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
        "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept-Language":"en-US,en;q=0.9",
      },
      redirect:"follow",
      signal:controller.signal,
    });
    if (!response.ok) throw new Error(`FotMob HTTP ${response.status}`);
    return await response.text();
  } finally {
    clearTimeout(timer);
  }
}

function extractPageProps(html:string) {
  const match = html.match(/<script[^>]*id=["']__NEXT_DATA__["'][^>]*>([\s\S]*?)<\/script>/i);
  if (!match) throw new Error("FotMob __NEXT_DATA__ puudub");
  const root = JSON.parse(match[1]);
  return root?.props?.pageProps || {};
}

function unwrapTeamPage(pageProps:any, teamId:string) {
  const fallback = pageProps?.fallback || {};
  const direct = fallback[`team-${teamId}`];
  if (direct) return direct;
  for (const value of Object.values(fallback) as any[]) {
    if (String(value?.details?.id || "") === String(teamId)) return value;
  }
  if (String(pageProps?.details?.id || "") === String(teamId)) return pageProps;
  throw new Error("FotMobi meeskonna plokk puudub");
}

function unwrapMatchPage(pageProps:any, matchId:string) {
  if (String(pageProps?.general?.matchId || "") === String(matchId)) return pageProps;
  const fallback = pageProps?.fallback || {};
  for (const key of [`match-${matchId}`, `matchDetails-${matchId}`, String(matchId)]) {
    if (fallback[key] && String(fallback[key]?.general?.matchId || matchId) === String(matchId)) return fallback[key];
  }
  for (const value of Object.values(fallback) as any[]) {
    if (String(value?.general?.matchId || "") === String(matchId)) return value;
  }
  for (const value of Object.values(pageProps || {}) as any[]) {
    if (value && typeof value === "object" && String(value?.general?.matchId || "") === String(matchId)) return value;
  }
  return pageProps;
}

async function loadTeamPage(teamId:string) {
  const cached = teamPageCache.get(teamId);
  if (cached && Date.now() - cached.at < 60_000) return cached.value;
  const html = await fetchText(`https://www.fotmob.com/teams/${teamId}/overview`);
  const value = unwrapTeamPage(extractPageProps(html), teamId);
  teamPageCache.set(teamId, { at:Date.now(), value });
  return value;
}

function fixtureList(page:any) {
  for (const list of [page?.fixtures?.allFixtures?.fixtures, page?.fixtures?.allFixtures?.allMatches, page?.fixtures?.allMatches]) {
    if (Array.isArray(list)) return list;
  }
  return [];
}

function parseDate(value:any) {
  const t = new Date(String(value || "")).getTime();
  return Number.isFinite(t) ? t : 0;
}

function findFixture(page:any, match:any) {
  const kickoff = parseDate(match.kickoff_at);
  const home = canonical(match.home_team), away = canonical(match.away_team);
  let best:any = null, bestDiff = Number.POSITIVE_INFINITY;
  for (const fixture of fixtureList(page)) {
    if (canonical(fixture?.home?.name || "") !== home || canonical(fixture?.away?.name || "") !== away) continue;
    const fixtureTime = parseDate(fixture?.status?.utcTime);
    const diff = Math.abs(fixtureTime - kickoff);
    if (!kickoff || !fixtureTime) { if (!best) best = fixture; continue; }
    if (diff < bestDiff) { best = fixture; bestDiff = diff; }
  }
  return best;
}

function cleanPageUrl(value:any) {
  return String(value || "").trim().split("#")[0];
}

async function loadMatchDetails(pageUrl:string, matchId:string) {
  if (!pageUrl) throw new Error("FotMobi mängu URL puudub");
  const url = pageUrl.startsWith("http") ? pageUrl : `https://www.fotmob.com${pageUrl}`;
  return unwrapMatchPage(extractPageProps(await fetchText(url)), matchId);
}

function playerRow(player:any) {
  if (!player || typeof player !== "object") return null;
  const name = String(player?.name || player?.fullName || player?.playerName || "").trim();
  if (!name) return null;
  const rawNumber = player?.shirtNumber ?? player?.shirt ?? player?.shirtNo ?? null;
  return {
    id: player?.id ?? player?.playerId ?? null,
    name,
    shirt_number: rawNumber == null ? null : String(rawNumber),
    position: String(player?.position || player?.role || "").trim() || null,
  };
}

function uniquePlayers(rows:any[]) {
  const out:any[] = [], seen = new Set<string>();
  for (const row of rows) {
    const p = playerRow(row);
    if (!p) continue;
    const key = String(p.id || "") + "|" + p.name.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(p);
  }
  return out;
}

function parseNewTeam(team:any, fallbackName:string) {
  if (!team || typeof team !== "object") return null;
  const starters = uniquePlayers(Array.isArray(team?.starters) ? team.starters : []);
  const substitutes = uniquePlayers(Array.isArray(team?.subs) ? team.subs : (Array.isArray(team?.bench) ? team.bench : []));
  if (!starters.length && !substitutes.length) return null;
  return {
    team_name: String(team?.name || fallbackName || ""),
    formation: String(team?.formation || "").trim() || null,
    starters,
    substitutes,
  };
}

function parseLegacyTeam(team:any, fallbackName:string) {
  if (!team || typeof team !== "object") return null;
  let starterRows:any[] = [];
  if (Array.isArray(team?.players)) {
    for (const row of team.players) {
      if (Array.isArray(row)) starterRows.push(...row);
      else if (row) starterRows.push(row);
    }
  }
  if (!starterRows.length && Array.isArray(team?.optaLineup?.starting)) starterRows = team.optaLineup.starting;
  const starters = uniquePlayers(starterRows);
  const substitutes = uniquePlayers(Array.isArray(team?.bench) ? team.bench : []);
  if (!starters.length && !substitutes.length) return null;
  return {
    team_name: String(team?.teamName || fallbackName || ""),
    formation: String(team?.formation || "").trim() || null,
    starters,
    substitutes,
  };
}

function matchLineups(details:any, match:any) {
  const lineup = details?.content?.lineup || {};
  let home = parseNewTeam(lineup?.homeTeam, match.home_team);
  let away = parseNewTeam(lineup?.awayTeam, match.away_team);

  if (!home || !away) {
    const legacy = Array.isArray(lineup?.lineup) ? lineup.lineup : [];
    const homeId = String(details?.general?.homeTeam?.id || "");
    const awayId = String(details?.general?.awayTeam?.id || "");
    for (const team of legacy) {
      const id = String(team?.teamId || team?.id || "");
      const parsed = parseLegacyTeam(team, id === homeId ? match.home_team : match.away_team);
      if (!parsed) continue;
      if (!home && (id === homeId || canonical(parsed.team_name) === canonical(match.home_team))) home = parsed;
      else if (!away && (id === awayId || canonical(parsed.team_name) === canonical(match.away_team))) away = parsed;
    }
  }

  const available = !!(home?.starters?.length && away?.starters?.length);
  return { available, home: home || null, away: away || null };
}

Deno.serve(async (req:Request) => {
  if (req.method === "OPTIONS") return new Response("ok", { status:200, headers:CORS_HEADERS });
  if (req.method !== "POST") return jsonResponse({ ok:false, error:"Method not allowed" }, 405);

  try {
    const supabaseUrl = Deno.env.get("SUPABASE_URL");
    const serviceRole = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
    if (!supabaseUrl || !serviceRole) throw new Error("Supabase serveri seaded puuduvad");
    const admin = createClient(supabaseUrl, serviceRole, { auth:{ persistSession:false, autoRefreshToken:false } });
    const body = await req.json().catch(() => ({}));
    const requested = Array.isArray(body?.match_ids)
      ? body.match_ids.map((x:any) => String(x || "")).filter((x:string) => /^[0-9a-f-]{36}$/i.test(x)).slice(0, 30)
      : [];
    if (!requested.length) return jsonResponse({ ok:true, source:"FotMob", matches:[] });

    const { data:matches, error:matchError } = await admin
      .from("matches")
      .select("id,home_team,away_team,kickoff_at")
      .in("id", requested)
      .order("kickoff_at", { ascending:true });
    if (matchError) throw matchError;
    if (!matches?.length) return jsonResponse({ ok:true, source:"FotMob", matches:[] });

    const ids = matches.map((m:any) => m.id);
    const [{ data:liveRows }, { data:assets }] = await Promise.all([
      admin.from("match_live_state").select("match_id,fotmob_match_id,page_url").in("match_id", ids),
      admin.from("team_assets").select("team_key,logo_url"),
    ]);
    const liveMap = new Map((liveRows || []).map((r:any) => [r.match_id, r]));
    const teamIds = new Map<string,string>();
    for (const asset of assets || []) {
      const m = String(asset?.logo_url || "").match(/teamlogo\/(\d+)\.png/i);
      if (m) teamIds.set(String(asset.team_key), m[1]);
    }

    const output:any[] = [];
    for (const match of matches) {
      const cached = resultCache.get(match.id);
      if (body?.force !== true && cached && Date.now() - cached.at < CACHE_TTL_MS) {
        output.push(cached.value);
        continue;
      }

      let fotmobId = String(liveMap.get(match.id)?.fotmob_match_id || "");
      let pageUrl = cleanPageUrl(liveMap.get(match.id)?.page_url);
      try {
        if (!pageUrl || !fotmobId) {
          const teamId = teamIds.get(assetKey(match.home_team));
          if (!teamId) throw new Error(`FotMobi klubi ID puudub: ${match.home_team}`);
          const fixture = findFixture(await loadTeamPage(teamId), match);
          if (!fixture) throw new Error("FotMobi mängu ei leitud");
          fotmobId = String(fixture?.id || "");
          pageUrl = cleanPageUrl(fixture?.pageUrl);
        }
        if (!pageUrl) throw new Error("FotMobi mängu URL puudub");
        const details = await loadMatchDetails(pageUrl, fotmobId);
        const parsed = matchLineups(details, match);
        const row = {
          match_id:match.id,
          fotmob_match_id:fotmobId ? Number(fotmobId) : null,
          available:parsed.available,
          home:parsed.home,
          away:parsed.away,
          source:"FotMob",
          updated_at:new Date().toISOString(),
          last_error:null,
        };
        resultCache.set(match.id, { at:Date.now(), value:row });
        output.push(row);
      } catch (error) {
        const row = {
          match_id:match.id,
          fotmob_match_id:fotmobId ? Number(fotmobId) : null,
          available:false,
          home:null,
          away:null,
          source:"FotMob",
          updated_at:new Date().toISOString(),
          last_error:error instanceof Error ? error.message : String(error),
        };
        resultCache.set(match.id, { at:Date.now(), value:row });
        output.push(row);
      }
    }

    return jsonResponse({ ok:true, source:"FotMob", matches:output });
  } catch (error) {
    console.error("ucl-lineups", error);
    return jsonResponse({ ok:false, error:error instanceof Error ? error.message : String(error) }, 502);
  }
});
