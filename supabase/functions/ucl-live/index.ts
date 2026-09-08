import { createClient } from "npm:@supabase/supabase-js@2";

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

const FETCH_TIMEOUT_MS = 9000;
const teamPageCache = new Map<string, { at: number; value: any }>();

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
  const aliases: Record<string, string> = {
    "manchester city": "man city", "man city": "man city",
    "manchester united": "man united", "man utd": "man united", "man united": "man united",
    "atletico madrid": "atleti", "atletico de madrid": "atleti", "atleti": "atleti",
    "borussia dortmund": "dortmund", "b dortmund": "dortmund", "dortmund": "dortmund",
    "bayern munich": "bayern", "bayern munchen": "bayern", "bayern": "bayern",
    "paris saint germain": "paris", "psg": "paris", "paris": "paris",
    "porto": "porto", "fc porto": "porto",
    "rb leipzig": "leipzig", "leipzig": "leipzig",
    "slovan bratislava": "slovan bratislava", "s bratislava": "slovan bratislava",
    "shakhtar donetsk": "shakhtar", "shakhtar": "shakhtar",
    "slavia prague": "slavia praha", "slavia praha": "slavia praha",
    "sporting lisbon": "sporting cp", "sporting": "sporting cp", "sporting cp": "sporting cp",
    "internazionale": "inter", "inter milan": "inter", "inter": "inter",
    "bodo glimt": "bodo glimt",
  };
  return aliases[s] || s;
}

async function fetchText(url: string) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);
  try {
    const response = await fetch(url, {
      headers: {
        "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
      },
      redirect: "follow",
      signal: controller.signal,
    });
    if (!response.ok) throw new Error(`FotMob HTTP ${response.status}`);
    return await response.text();
  } finally {
    clearTimeout(timer);
  }
}

function extractPageProps(html: string) {
  const match = html.match(/<script[^>]*id=["']__NEXT_DATA__["'][^>]*>([\s\S]*?)<\/script>/i);
  if (!match) throw new Error("FotMob __NEXT_DATA__ puudub");
  const root = JSON.parse(match[1]);
  return root?.props?.pageProps || {};
}

function unwrapTeamPage(pageProps: any, teamId: string) {
  const fallback = pageProps?.fallback || {};
  const direct = fallback[`team-${teamId}`];
  if (direct) return direct;
  for (const value of Object.values(fallback) as any[]) {
    if (String(value?.details?.id || "") === String(teamId)) return value;
  }
  if (String(pageProps?.details?.id || "") === String(teamId)) return pageProps;
  throw new Error("FotMobi meeskonna plokk puudub");
}

function unwrapMatchPage(pageProps: any, matchId: string) {
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

async function loadTeamPage(teamId: string) {
  const cached = teamPageCache.get(teamId);
  if (cached && Date.now() - cached.at < 12_000) return cached.value;
  const html = await fetchText(`https://www.fotmob.com/teams/${teamId}/overview`);
  const value = unwrapTeamPage(extractPageProps(html), teamId);
  teamPageCache.set(teamId, { at: Date.now(), value });
  return value;
}

function fixtureList(page: any) {
  for (const list of [page?.fixtures?.allFixtures?.fixtures, page?.fixtures?.allFixtures?.allMatches, page?.fixtures?.allMatches]) {
    if (Array.isArray(list)) return list;
  }
  return [];
}

function parseDate(value: any) {
  const t = new Date(String(value || "")).getTime();
  return Number.isFinite(t) ? t : 0;
}

function findFixture(page: any, match: any) {
  const kickoff = parseDate(match.kickoff_at);
  const home = canonical(match.home_team);
  const away = canonical(match.away_team);
  let best: any = null;
  let bestDiff = Number.POSITIVE_INFINITY;
  for (const f of fixtureList(page)) {
    if (canonical(f?.home?.name || "") !== home || canonical(f?.away?.name || "") !== away) continue;
    const fixtureTime = parseDate(f?.status?.utcTime);
    const diff = Math.abs(fixtureTime - kickoff);
    if (!kickoff || !fixtureTime) { if (!best) best = f; continue; }
    if (diff < bestDiff) { best = f; bestDiff = diff; }
  }
  if (best && bestDiff <= 8 * 60 * 60 * 1000) return best;
  return best;
}

function cleanPageUrl(value: any) {
  return String(value || "").trim().split("#")[0];
}

async function loadMatchDetails(pageUrl: string, matchId: string) {
  if (!pageUrl) throw new Error("FotMobi mängu URL puudub");
  const url = pageUrl.startsWith("http") ? pageUrl : `https://www.fotmob.com${pageUrl}`;
  return unwrapMatchPage(extractPageProps(await fetchText(url)), matchId);
}

function numberOrNull(value: any) {
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
}

function parseScoreStr(value: any) {
  const m = String(value || "").match(/(-?\d+)\s*[-:]\s*(-?\d+)/);
  return m ? [Number(m[1]), Number(m[2])] : [null, null];
}

function scorePair(fixture: any, details: any) {
  const teams = details?.header?.teams;
  if (Array.isArray(teams) && teams.length >= 2) {
    const a = numberOrNull(teams[0]?.score), b = numberOrNull(teams[1]?.score);
    if (a !== null && b !== null) return [a, b];
  }
  for (const score of [details?.header?.status?.score, fixture?.status?.score]) {
    if (score) {
      const a = numberOrNull(score.home), b = numberOrNull(score.away);
      if (a !== null && b !== null) return [a, b];
    }
  }
  const a = numberOrNull(fixture?.home?.score), b = numberOrNull(fixture?.away?.score);
  if (a !== null && b !== null) return [a, b];
  return parseScoreStr(details?.header?.status?.scoreStr || fixture?.status?.scoreStr);
}

function statusSnapshot(fixture: any, details: any) {
  const s = details?.header?.status || fixture?.status || {};
  const finished = s?.finished === true;
  const cancelled = s?.cancelled === true;
  const started = s?.started === true || (!finished && !cancelled && !!s?.liveTime?.short);
  let liveTime = String(s?.liveTime?.short || s?.reason?.short || "").trim();
  if (finished && !liveTime) liveTime = "FT";
  const low = liveTime.toLowerCase();
  let phase = "scheduled";
  if (cancelled) phase = "cancelled";
  else if (finished) phase = "ft";
  else if (started && /ht|half/.test(low)) phase = "ht";
  else if (started && /et|extra/.test(low)) phase = "et";
  else if (started) phase = "live";
  return { started, finished, cancelled, liveTime, phase };
}

function eventMinute(ev: any) {
  return numberOrNull(ev?.time ?? ev?.min) || 0;
}

function eventMinuteText(ev: any) {
  const raw = ev?.timeStr ?? ev?.min;
  if (typeof raw === "string" && raw.trim()) return raw.replace(/\s*\+\s*/g, "+").replace(/'$/, "") + "'";
  const n = eventMinute(ev), added = numberOrNull(ev?.minAdded);
  return added && added > 0 ? `${n}+${added}'` : `${n}'`;
}

function playerName(ev: any) {
  if (ev?.player?.name) return String(ev.player.name);
  if (ev?.fullName) return String(ev.fullName);
  if (ev?.nameStr) return String(ev.nameStr);
  return [ev?.firstName, ev?.lastName].filter(Boolean).join(" ").trim();
}

function matchEvents(details: any) {
  const raw = details?.content?.matchFacts?.events?.events || details?.content?.matchFacts?.events?.incidents || [];
  const rows: any[] = [];
  if (Array.isArray(raw)) {
    for (const ev of raw) {
      const type = String(ev?.type || ""), low = type.toLowerCase();
      if (!type || low === "half" || low === "addedtime") continue;
      const base: any = {
        id: String(ev?.eventId || `${eventMinute(ev)}-${type}-${playerName(ev)}`),
        minute: eventMinute(ev), minute_text: eventMinuteText(ev),
        side: ev?.isHome === true ? "home" : "away",
        player: playerName(ev), kind: "other", label: type,
      };
      if (low.includes("goal")) {
        base.kind = ev?.ownGoal === true ? "own_goal" : ev?.isPenalty === true ? "penalty_goal" : "goal";
        base.label = ev?.ownGoal === true ? "Omavärav" : ev?.isPenalty === true ? "Penaltivärav" : "Värav";
        base.assist = String(ev?.assistInput || ev?.assistStr || "").trim();
        const score = Array.isArray(ev?.newScore) ? ev.newScore : [ev?.homeScore, ev?.awayScore];
        if (score.length >= 2) base.score = `${Number(score[0] || 0)}:${Number(score[1] || 0)}`;
      } else if (low === "card" || low.includes("card")) {
        const card = String(ev?.card || "").toLowerCase();
        base.kind = card.includes("red") ? "red_card" : card.includes("second") ? "second_yellow" : "yellow_card";
        base.label = card.includes("red") ? "Punane kaart" : card.includes("second") ? "Teine kollane" : "Kollane kaart";
      } else if (low.includes("substitution")) {
        base.kind = "substitution"; base.label = "Vahetus";
        const swap = Array.isArray(ev?.swap) ? ev.swap : [];
        if (swap.length >= 2) {
          base.player_in = String(swap[0]?.name || "");
          base.player_out = String(swap[1]?.name || "");
          base.player = base.player_out;
        }
      } else if (low.includes("penalty") && (low.includes("miss") || low.includes("saved"))) {
        base.kind = "penalty_miss"; base.label = "Penalti ei läinud sisse";
      } else if (low.includes("var")) {
        base.kind = "var"; base.label = "VAR";
      } else continue;
      rows.push(base);
    }
  }

  const shots = details?.content?.shotmap?.shots;
  if (Array.isArray(shots)) {
    for (const shot of shots) {
      const situation = String(shot?.situation || "").toLowerCase();
      const eventType = String(shot?.eventType || "").toLowerCase();
      if (situation !== "penalty" || eventType === "goal") continue;
      const p = String(shot?.playerName || [shot?.firstName, shot?.lastName].filter(Boolean).join(" ") || "");
      const minute = numberOrNull(shot?.min) || 0;
      const duplicate = rows.some(r => r.kind === "penalty_miss" && r.minute === minute && (!p || !r.player || r.player === p));
      if (duplicate) continue;
      rows.push({
        id: `shot-${String(shot?.id || `${minute}-${p}`)}`,
        minute, minute_text: eventMinuteText(shot),
        side: String(shot?.teamId || "") === String(details?.general?.homeTeam?.id || "") ? "home" : "away",
        player: p, kind: "penalty_miss",
        label: eventType.includes("saved") ? "Penalti tõrjuti" : "Penalti mööda",
      });
    }
  }
  rows.sort((a, b) => (a.minute || 0) - (b.minute || 0));
  return rows.slice(-80);
}

function refreshMs(match: any, state: any) {
  if (state?.finished) return 15 * 60 * 1000;
  if (state?.started) return 18 * 1000;
  const delta = parseDate(match.kickoff_at) - Date.now();
  if (delta <= 20 * 60 * 1000 && delta >= -5 * 60 * 60 * 1000) return 20 * 1000;
  if (delta <= 6 * 60 * 60 * 1000 && delta >= -6 * 60 * 60 * 1000) return 60 * 1000;
  return 10 * 60 * 1000;
}

function assetKey(name: string) {
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

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") return new Response("ok", { status: 200, headers: CORS_HEADERS });
  if (req.method !== "POST") return jsonResponse({ ok: false, error: "Method not allowed" }, 405);
  try {
    const supabaseUrl = Deno.env.get("SUPABASE_URL"), serviceRole = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
    if (!supabaseUrl || !serviceRole) throw new Error("Supabase serveri seaded puuduvad");
    const admin = createClient(supabaseUrl, serviceRole, { auth: { persistSession: false, autoRefreshToken: false } });
    const body = await req.json().catch(() => ({}));
    const requested = Array.isArray(body?.match_ids)
      ? body.match_ids.map((x: any) => String(x || "")).filter((x: string) => /^[0-9a-f-]{36}$/i.test(x)).slice(0, 40)
      : [];

    let query = admin.from("matches").select("id,home_team,away_team,kickoff_at,home_logo_url,away_logo_url");
    if (requested.length) query = query.in("id", requested);
    else query = query.gte("kickoff_at", new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString())
      .lte("kickoff_at", new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString());
    const { data: matches, error: matchError } = await query.order("kickoff_at", { ascending: true });
    if (matchError) throw matchError;
    if (!matches?.length) return jsonResponse({ ok: true, source: "FotMob", matches: [] });

    const ids = matches.map((m: any) => m.id);
    const [{ data: states }, { data: assets }] = await Promise.all([
      admin.from("match_live_state").select("*").in("match_id", ids),
      admin.from("team_assets").select("team_key,logo_url"),
    ]);
    const stateMap = new Map((states || []).map((s: any) => [s.match_id, s]));
    const teamIds = new Map<string, string>();
    for (const a of assets || []) {
      const m = String(a.logo_url || "").match(/teamlogo\/(\d+)\.png/i);
      if (m) teamIds.set(String(a.team_key), m[1]);
    }

    const output: any[] = [];
    for (const match of matches) {
      const previous: any = stateMap.get(match.id) || null;
      const age = previous?.updated_at ? Date.now() - new Date(previous.updated_at).getTime() : Number.POSITIVE_INFINITY;
      if (body?.force !== true && previous && age < refreshMs(match, previous)) { output.push(previous); continue; }

      let fixture: any = null, details: any = null;
      let fotmobId = previous?.fotmob_match_id ? String(previous.fotmob_match_id) : "";
      let pageUrl = cleanPageUrl(previous?.page_url), lastError = "";
      try {
        const teamId = teamIds.get(assetKey(match.home_team));
        if (!teamId) throw new Error(`FotMobi klubi ID puudub: ${match.home_team}`);
        const teamPage = await loadTeamPage(teamId);
        fixture = findFixture(teamPage, match);
        if (!fixture && !fotmobId) throw new Error("FotMobi mängu ei leitud");
        if (fixture) {
          fotmobId = String(fixture?.id || fotmobId || "");
          pageUrl = cleanPageUrl(fixture?.pageUrl || pageUrl);
        }

        const fixtureStatus = statusSnapshot(fixture, null);
        const kickoffDelta = Date.now() - parseDate(match.kickoff_at);
        if (pageUrl && (fixtureStatus.started || fixtureStatus.finished || kickoffDelta > -15 * 60 * 1000)) {
          try { details = await loadMatchDetails(pageUrl, fotmobId); }
          catch (error) { lastError = error instanceof Error ? error.message : String(error); }
        }

        const status = statusSnapshot(fixture, details);
        const [homeScore, awayScore] = scorePair(fixture, details);
        const row = {
          match_id: match.id,
          fotmob_match_id: fotmobId ? Number(fotmobId) : null,
          page_url: pageUrl || null,
          phase: status.phase,
          live_time: status.liveTime || null,
          started: status.started,
          finished: status.finished,
          cancelled: status.cancelled,
          home_score: homeScore,
          away_score: awayScore,
          events: details ? matchEvents(details) : (Array.isArray(previous?.events) ? previous.events : []),
          source: "FotMob",
          source_updated_at: new Date().toISOString(),
          last_error: lastError || null,
          updated_at: new Date().toISOString(),
        };
        const { error: upsertError } = await admin.from("match_live_state").upsert(row, { onConflict: "match_id" });
        if (upsertError) throw upsertError;
        output.push(row);
      } catch (error) {
        const message = error instanceof Error ? error.message : String(error);
        const row = previous ? { ...previous, last_error: message, updated_at: new Date().toISOString() } : {
          match_id: match.id, fotmob_match_id: fotmobId ? Number(fotmobId) : null, page_url: pageUrl || null,
          phase: "scheduled", live_time: null, started: false, finished: false, cancelled: false,
          home_score: null, away_score: null, events: [], source: "FotMob", source_updated_at: null,
          last_error: message, updated_at: new Date().toISOString(),
        };
        await admin.from("match_live_state").upsert(row, { onConflict: "match_id" });
        output.push(row);
      }
    }
    return jsonResponse({ ok: true, source: "FotMob", matches: output });
  } catch (error) {
    console.error("ucl-live", error);
    return jsonResponse({ ok: false, error: error instanceof Error ? error.message : String(error) }, 502);
  }
});
