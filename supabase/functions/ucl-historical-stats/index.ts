type Fixture = {
  DateUtc?: string;
  HomeTeam?: string;
  AwayTeam?: string;
  HomeTeamScore?: number | null;
  AwayTeamScore?: number | null;
  RoundNumber?: number | null;
};

type Row = Fixture & {
  season: string;
  date_iso: string;
  competition: string;
  competition_key: string;
};

type LeagueConfig = {
  slug: string;
  name: string;
};

const CACHE_TTL = 6 * 60 * 60 * 1000;
const FETCH_TIMEOUT_MS = 5500;
const feedCache = new Map<string, { at: number; rows: Row[] }>();

const LEAGUES: LeagueConfig[] = [
  { slug: 'epl', name: 'Premier League' },
  { slug: 'la-liga', name: 'La Liga' },
  { slug: 'bundesliga', name: 'Bundesliga' },
  { slug: 'serie-a', name: 'Serie A' },
  { slug: 'ligue-1', name: 'Ligue 1' },
  { slug: 'eredivisie', name: 'Eredivisie' },
  { slug: 'primeira-liga', name: 'Primeira Liga' },
  { slug: 'turkish-super-lig', name: 'Turkish Super Lig' },
  { slug: 'scottish-premiership', name: 'Scottish Premiership' },
];

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

function currentSeasonYear() {
  const now = new Date();
  return now.getUTCMonth() >= 6 ? now.getUTCFullYear() : now.getUTCFullYear() - 1;
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
    .replace(/\b(fc|cf|ac|ssc|afc|fk|sk|sc|rcd|rc)\b/g, ' ')
    .replace(/[^a-z0-9]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

  const aliases: Record<string, string> = {
    'paris saint germain': 'paris', 'psg': 'paris', 'paris': 'paris',
    'manchester city': 'man city', 'man city': 'man city',
    'manchester united': 'man united', 'man united': 'man united',
    'tottenham hotspur': 'tottenham', 'spurs': 'tottenham', 'tottenham': 'tottenham',
    'b dortmund': 'dortmund', 'borussia dortmund': 'dortmund', 'dortmund': 'dortmund',
    'bayern munchen': 'bayern', 'bayern munich': 'bayern', 'bayern': 'bayern',
    'bayer 04 leverkusen': 'leverkusen', 'bayer leverkusen': 'leverkusen', 'leverkusen': 'leverkusen',
    'atletico': 'atleti', 'atletico de madrid': 'atleti', 'atletico madrid': 'atleti', 'atleti': 'atleti',
    'barcelona': 'barcelona', 'fc barcelona': 'barcelona',
    'villarreal': 'villarreal', 'villarreal cf': 'villarreal',
    'internazionale': 'inter', 'inter milan': 'inter', 'inter': 'inter',
    'ac milan': 'milan', 'milan': 'milan',
    'paris saint germain': 'paris',
    'losc lille': 'lille', 'losc': 'lille', 'lille': 'lille',
    'as monaco': 'monaco', 'monaco': 'monaco',
    'olympique de marseille': 'marseille', 'marseille': 'marseille',
    'sl benfica': 'benfica', 'benfica': 'benfica',
    'sporting lisbon': 'sporting cp', 'sporting': 'sporting cp', 'sporting cp': 'sporting cp',
    'club bruges': 'club brugge', 'club brugge': 'club brugge',
    'red star belgrade': 'crvena zvezda', 'crvena zvezda': 'crvena zvezda',
    'bodo glimt': 'bodo glimt', 'bodo glimt fk': 'bodo glimt',
    'fc copenhagen': 'copenhagen', 'copenhagen': 'copenhagen',
    'shakhtar donetsk': 'shakhtar', 'shakhtar': 'shakhtar',
    'gnk dinamo': 'dinamo zagreb', 'dinamo zagreb': 'dinamo zagreb',
  };

  return aliases[s] || s;
}

function parseDate(value?: string) {
  if (!value) return null;
  const cleaned = value.endsWith('Z') ? value : `${value}Z`;
  const iso = cleaned.includes('T') ? cleaned : cleaned.replace(' ', 'T');
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? null : d;
}

function scoreNumber(value: unknown) {
  if (value === null || value === undefined || value === '') return null;
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
}

function completed(row: Row) {
  const hs = scoreNumber(row.HomeTeamScore);
  const as = scoreNumber(row.AwayTeamScore);
  return hs !== null && as !== null && !!row.date_iso && new Date(row.date_iso).getTime() <= Date.now();
}

async function fetchJsonWithTimeout(url: string) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);
  try {
    const res = await fetch(url, {
      headers: { 'User-Agent': 'Futbol-Match-Stats/3.0', 'Accept': 'application/json' },
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

async function fetchFeed(slug: string, year: number, competition: string): Promise<Row[]> {
  const key = `${slug}-${year}`;
  const cached = feedCache.get(key);
  if (cached && Date.now() - cached.at < CACHE_TTL) return cached.rows;

  const urls = [
    `https://fixturedownload.com/feed/json/${slug}-${year}`,
    `https://fixturedownload.azurewebsites.net/feed/json/${slug}-${year}`,
  ];

  let rows: Row[] = [];
  for (const url of urls) {
    const data = await fetchJsonWithTimeout(url);
    if (!data) continue;
    rows = data.map((f: Fixture) => {
      const d = parseDate(f.DateUtc);
      return {
        ...f,
        season: seasonLabel(year),
        date_iso: d ? d.toISOString() : '',
        competition,
        competition_key: slug,
      };
    });
    break;
  }

  feedCache.set(key, { at: Date.now(), rows });
  return rows;
}

function containsTeam(rows: Row[], teamName: string) {
  const key = normalizeTeam(teamName);
  return rows.some(r => normalizeTeam(r.HomeTeam || '') === key || normalizeTeam(r.AwayTeam || '') === key);
}

async function findDomesticLeague(teamName: string, seasonYear: number) {
  const results = await Promise.all(
    LEAGUES.map(async config => ({ config, rows: await fetchFeed(config.slug, seasonYear, config.name) })),
  );
  return results.find(item => item.rows.length && containsTeam(item.rows, teamName)) || null;
}

function teamGames(rows: Row[], teamName: string) {
  const key = normalizeTeam(teamName);
  return rows
    .filter(r => completed(r) && (normalizeTeam(r.HomeTeam || '') === key || normalizeTeam(r.AwayTeam || '') === key))
    .sort((a, b) => new Date(b.date_iso).getTime() - new Date(a.date_iso).getTime());
}

function resultForTeam(row: Row, teamName: string) {
  const key = normalizeTeam(teamName);
  const home = normalizeTeam(row.HomeTeam || '') === key;
  const hs = Number(row.HomeTeamScore);
  const as = Number(row.AwayTeamScore);
  const gf = home ? hs : as;
  const ga = home ? as : hs;
  return gf > ga ? 'W' : gf === ga ? 'D' : 'L';
}

function recentMatches(rows: Row[], teamName: string) {
  const seen = new Set<string>();
  const games = teamGames(rows, teamName).filter(row => {
    const key = `${row.date_iso}|${normalizeTeam(row.HomeTeam || '')}|${normalizeTeam(row.AwayTeam || '')}|${row.HomeTeamScore}|${row.AwayTeamScore}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });

  return games.slice(0, 5).map(row => ({
    date: row.date_iso,
    competition: row.competition,
    home_team: row.HomeTeam,
    away_team: row.AwayTeam,
    home_score: Number(row.HomeTeamScore),
    away_score: Number(row.AwayTeamScore),
    result: resultForTeam(row, teamName),
  }));
}

function summaryForCompetition(rows: Row[], teamName: string) {
  const games = teamGames(rows, teamName);
  let wins = 0, draws = 0, losses = 0, gf = 0, ga = 0;
  for (const row of games) {
    const key = normalizeTeam(teamName);
    const home = normalizeTeam(row.HomeTeam || '') === key;
    const hs = Number(row.HomeTeamScore), as = Number(row.AwayTeamScore);
    const f = home ? hs : as, a = home ? as : hs;
    gf += f; ga += a;
    if (f > a) wins++; else if (f === a) draws++; else losses++;
  }
  return { played: games.length, wins, draws, losses, gf, ga, gd: gf - ga };
}

function leagueTable(rows: Row[], teamName: string, leagueName: string) {
  const table = new Map<string, {
    team: string; played: number; wins: number; draws: number; losses: number; gf: number; ga: number; points: number;
  }>();

  for (const row of rows) {
    if (!completed(row)) continue;
    const homeName = String(row.HomeTeam || '').trim();
    const awayName = String(row.AwayTeam || '').trim();
    if (!homeName || !awayName) continue;
    const hk = normalizeTeam(homeName), ak = normalizeTeam(awayName);
    const home = table.get(hk) || { team: homeName, played: 0, wins: 0, draws: 0, losses: 0, gf: 0, ga: 0, points: 0 };
    const away = table.get(ak) || { team: awayName, played: 0, wins: 0, draws: 0, losses: 0, gf: 0, ga: 0, points: 0 };
    const hs = Number(row.HomeTeamScore), as = Number(row.AwayTeamScore);

    home.played++; away.played++;
    home.gf += hs; home.ga += as;
    away.gf += as; away.ga += hs;
    if (hs > as) {
      home.wins++; home.points += 3; away.losses++;
    } else if (hs < as) {
      away.wins++; away.points += 3; home.losses++;
    } else {
      home.draws++; away.draws++; home.points++; away.points++;
    }
    table.set(hk, home);
    table.set(ak, away);
  }

  const sorted = Array.from(table.values()).sort((a, b) =>
    b.points - a.points ||
    (b.gf - b.ga) - (a.gf - a.ga) ||
    b.gf - a.gf ||
    a.team.localeCompare(b.team),
  );
  const targetKey = normalizeTeam(teamName);
  const index = sorted.findIndex(row => normalizeTeam(row.team) === targetKey);
  if (index < 0) return null;
  const row = sorted[index];
  return {
    league: leagueName,
    position: index + 1,
    teams: sorted.length,
    ...row,
    gd: row.gf - row.ga,
  };
}

function h2h(rows: Row[], homeTeam: string, awayTeam: string) {
  const a = normalizeTeam(homeTeam), b = normalizeTeam(awayTeam);
  return rows
    .filter(row => {
      if (!completed(row)) return false;
      const h = normalizeTeam(row.HomeTeam || ''), aw = normalizeTeam(row.AwayTeam || '');
      return (h === a && aw === b) || (h === b && aw === a);
    })
    .sort((x, y) => new Date(y.date_iso).getTime() - new Date(x.date_iso).getTime())
    .slice(0, 5)
    .map(row => ({
      season: row.season,
      date: row.date_iso,
      home_team: row.HomeTeam,
      away_team: row.AwayTeam,
      home_score: Number(row.HomeTeamScore),
      away_score: Number(row.AwayTeamScore),
    }));
}

async function teamSnapshot(teamName: string, domestic: Awaited<ReturnType<typeof findDomesticLeague>>, clCurrent: Row[], clPrevious: Row[], seasonYear: number) {
  let domesticPrevious: Row[] = [];
  let domesticCurrent: Row[] = [];
  let table = null;
  let leagueName: string | null = null;

  if (domestic) {
    domesticCurrent = domestic.rows;
    domesticPrevious = await fetchFeed(domestic.config.slug, seasonYear - 1, domestic.config.name);
    leagueName = domestic.config.name;
    table = leagueTable(domesticCurrent, teamName, domestic.config.name);
  }

  const combined = [...domesticCurrent, ...clCurrent, ...domesticPrevious, ...clPrevious];
  return {
    team: teamName,
    recent: recentMatches(combined, teamName),
    league: table,
    league_name: leagueName,
    ucl: summaryForCompetition(clCurrent, teamName),
  };
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

    const seasonYear = currentSeasonYear();
    const historyYears = Array.from({ length: 7 }, (_, i) => seasonYear - i);

    const [clHistoryRows, homeDomestic, awayDomestic] = await Promise.all([
      Promise.all(historyYears.map(year => fetchFeed('champions-league', year, 'Champions League')))
        .then(parts => parts.flat()),
      findDomesticLeague(home, seasonYear),
      findDomesticLeague(away, seasonYear),
    ]);

    const clCurrent = clHistoryRows.filter(row => row.season === seasonLabel(seasonYear));
    const clPrevious = clHistoryRows.filter(row => row.season === seasonLabel(seasonYear - 1));

    const [homeSnapshot, awaySnapshot] = await Promise.all([
      teamSnapshot(home, homeDomestic, clCurrent, clPrevious, seasonYear),
      teamSnapshot(away, awayDomestic, clCurrent, clPrevious, seasonYear),
    ]);

    return jsonResponse({
      ok: true,
      source: 'Fixture Download',
      season: seasonLabel(seasonYear),
      home: homeSnapshot,
      away: awaySnapshot,
      h2h: h2h(clHistoryRows, home, away),
      coverage_note: 'Hetkevorm koondab Fixture Downloadis saadaolevad koduliiga ja Champions League’i mängud. Kui mõne riigi karikasarja andmevoog puudub, võib üksik karikamäng vormireast puududa.',
    }, 200, { 'Cache-Control': 'public, max-age=900' });
  } catch (error) {
    return jsonResponse({ ok: false, error: error instanceof Error ? error.message : String(error) }, 500);
  }
});
