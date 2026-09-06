type Fixture = {
  DateUtc?: string;
  HomeTeam?: string;
  AwayTeam?: string;
  HomeTeamScore?: number | null;
  AwayTeamScore?: number | null;
  RoundNumber?: number | null;
};

type Row = Fixture & { season: string; date_iso: string };

const YEARS = [2026, 2025, 2024, 2023, 2022, 2021, 2020];
const CACHE_TTL = 6 * 60 * 60 * 1000;
const FETCH_TIMEOUT_MS = 6500;
let cache: { at: number; rows: Row[]; seasons: string[] } | null = null;

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
};

function jsonResponse(payload: unknown, status = 200, extra: Record<string, string> = {}) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: {
      ...CORS_HEADERS,
      'Content-Type': 'application/json',
      ...extra,
    },
  });
}

function seasonLabel(year: number) {
  return `${year}/${String((year + 1) % 100).padStart(2, '0')}`;
}

function normalizeTeam(value: string) {
  const s = String(value || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/&/g, ' and ')
    .replace(/[^a-z0-9]+/g, ' ')
    .trim();

  const aliases: Record<string, string> = {
    'paris saint germain': 'paris', 'psg': 'paris', 'paris': 'paris',
    'manchester city': 'man city', 'man city': 'man city',
    'manchester united': 'man united', 'man united': 'man united',
    'b dortmund': 'dortmund', 'borussia dortmund': 'dortmund', 'dortmund': 'dortmund',
    'bayern munchen': 'bayern', 'bayern munich': 'bayern', 'bayern': 'bayern',
    'atletico': 'atleti', 'atletico de madrid': 'atleti', 'atletico madrid': 'atleti', 'atleti': 'atleti',
    'internazionale': 'inter', 'inter milan': 'inter', 'inter': 'inter',
    'ac milan': 'milan', 'milan': 'milan',
    'shakhtar donetsk': 'shakhtar', 'shakhtar': 'shakhtar',
    'gnk dinamo': 'dinamo zagreb', 'dinamo zagreb': 'dinamo zagreb',
    'losc': 'lille', 'lille': 'lille',
    'fc copenhagen': 'copenhagen', 'copenhagen': 'copenhagen',
    'sporting lisbon': 'sporting cp', 'sporting': 'sporting cp', 'sporting cp': 'sporting cp',
    'club bruges': 'club brugge', 'club brugge': 'club brugge',
    'red star belgrade': 'crvena zvezda', 'crvena zvezda': 'crvena zvezda',
    'bodo glimt': 'bodo glimt', 'bodo glimt fk': 'bodo glimt',
  };
  return aliases[s] || s;
}

function parseDate(value?: string) {
  if (!value) return null;
  const iso = value.includes('T') ? value : value.replace(' ', 'T');
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? null : d;
}

async function fetchJsonWithTimeout(url: string) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);
  try {
    const res = await fetch(url, {
      headers: { 'User-Agent': 'Futbol-UCL-Stats/2.0', 'Accept': 'application/json' },
      signal: controller.signal,
    });
    if (!res.ok) return null;
    const data = await res.json();
    return Array.isArray(data) ? data : null;
  } catch (_) {
    return null;
  } finally {
    clearTimeout(timer);
  }
}

async function fetchSeason(year: number): Promise<Row[]> {
  const urls = [
    `https://fixturedownload.com/feed/json/champions-league-${year}`,
    `https://fixturedownload.azurewebsites.net/feed/json/champions-league-${year}`,
  ];

  for (const url of urls) {
    const data = await fetchJsonWithTimeout(url);
    if (!data) continue;
    return data.map((f: Fixture) => {
      const d = parseDate(f.DateUtc);
      return { ...f, season: seasonLabel(year), date_iso: d ? d.toISOString() : '' };
    });
  }
  return [];
}

async function loadRows() {
  if (cache && Date.now() - cache.at < CACHE_TTL) return cache;
  const results = await Promise.all(YEARS.map(async y => ({ y, rows: await fetchSeason(y) })));
  const rows = results.flatMap(x => x.rows);
  const seasons = results.filter(x => x.rows.length).map(x => seasonLabel(x.y));
  cache = { at: Date.now(), rows, seasons };
  return cache;
}

function completed(row: Row) {
  return Number.isFinite(Number(row.HomeTeamScore)) &&
    Number.isFinite(Number(row.AwayTeamScore)) &&
    !!row.date_iso &&
    new Date(row.date_iso).getTime() <= Date.now();
}

function teamSummary(rows: Row[], teamName: string) {
  const key = normalizeTeam(teamName);
  const games = rows
    .filter(r => completed(r) && (normalizeTeam(r.HomeTeam || '') === key || normalizeTeam(r.AwayTeam || '') === key))
    .sort((a, b) => new Date(b.date_iso).getTime() - new Date(a.date_iso).getTime());

  let wins = 0, draws = 0, losses = 0, gf = 0, ga = 0;
  const bySeason = new Map<string, { matches: number; wins: number; draws: number; losses: number; gf: number; ga: number }>();

  const recent = games.slice(0, 10).map(r => {
    const home = normalizeTeam(r.HomeTeam || '') === key;
    const hs = Number(r.HomeTeamScore), as = Number(r.AwayTeamScore);
    const f = home ? hs : as, a = home ? as : hs;
    const result = f > a ? 'W' : f === a ? 'D' : 'L';
    return {
      season: r.season,
      date: r.date_iso,
      home_team: r.HomeTeam,
      away_team: r.AwayTeam,
      home_score: hs,
      away_score: as,
      result,
    };
  });

  for (const r of games) {
    const home = normalizeTeam(r.HomeTeam || '') === key;
    const hs = Number(r.HomeTeamScore), as = Number(r.AwayTeamScore);
    const f = home ? hs : as, a = home ? as : hs;
    gf += f; ga += a;
    if (f > a) wins++; else if (f === a) draws++; else losses++;
    const s = bySeason.get(r.season) || { matches: 0, wins: 0, draws: 0, losses: 0, gf: 0, ga: 0 };
    s.matches++; s.gf += f; s.ga += a;
    if (f > a) s.wins++; else if (f === a) s.draws++; else s.losses++;
    bySeason.set(r.season, s);
  }

  return {
    team: teamName,
    matches: games.length,
    wins,
    draws,
    losses,
    goals_for: gf,
    goals_against: ga,
    win_rate: games.length ? Math.round((wins / games.length) * 100) : 0,
    recent,
    seasons: Array.from(bySeason.entries())
      .map(([season, s]) => ({ season, ...s }))
      .sort((a, b) => b.season.localeCompare(a.season)),
  };
}

function h2h(rows: Row[], homeTeam: string, awayTeam: string) {
  const a = normalizeTeam(homeTeam), b = normalizeTeam(awayTeam);
  return rows
    .filter(r => {
      if (!completed(r)) return false;
      const h = normalizeTeam(r.HomeTeam || ''), aw = normalizeTeam(r.AwayTeam || '');
      return (h === a && aw === b) || (h === b && aw === a);
    })
    .sort((x, y) => new Date(y.date_iso).getTime() - new Date(x.date_iso).getTime())
    .map(r => ({
      season: r.season,
      date: r.date_iso,
      home_team: r.HomeTeam,
      away_team: r.AwayTeam,
      home_score: Number(r.HomeTeamScore),
      away_score: Number(r.AwayTeamScore),
    }));
}

Deno.serve(async (req: Request) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { status: 200, headers: CORS_HEADERS });
  }
  if (req.method !== 'POST') {
    return jsonResponse({ ok: false, error: 'Method not allowed' }, 405);
  }

  try {
    const body = await req.json().catch(() => ({}));
    const home = String(body?.home_team || '').trim();
    const away = String(body?.away_team || '').trim();
    if (!home || !away || home.length > 100 || away.length > 100) {
      return jsonResponse({ ok: false, error: 'Vigased meeskonnad' }, 400);
    }

    const loaded = await loadRows();
    if (!loaded.rows.length) {
      return jsonResponse({ ok: false, error: 'Ajalooliste hooaegade andmeid ei õnnestunud laadida' }, 503);
    }

    const payload = {
      ok: true,
      source: 'Fixture Download',
      seasons_loaded: loaded.seasons,
      range_label: loaded.seasons.length
        ? `${loaded.seasons[loaded.seasons.length - 1]}–${loaded.seasons[0]}`
        : '',
      home: teamSummary(loaded.rows, home),
      away: teamSummary(loaded.rows, away),
      h2h: h2h(loaded.rows, home, away).slice(0, 20),
    };

    return jsonResponse(payload, 200, { 'Cache-Control': 'public, max-age=21600' });
  } catch (error) {
    return jsonResponse({ ok: false, error: error instanceof Error ? error.message : String(error) }, 500);
  }
});
