const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
};

const CACHE_TTL = 5 * 60 * 1000;
const FETCH_TIMEOUT_MS = 9000;
const teamResolveCache = new Map<string, { at:number; value:ResolvedTeam }>();
const teamPageCache = new Map<string, { at:number; value:any }>();
const searchCache = new Map<string, { at:number; value:any }>();

type ResolvedTeam = { id:string; name:string; leagueId:number|null; leagueName:string|null };

const SEARCH_ALIASES: Record<string,string> = {
  'atleti': 'Atlético Madrid',
  'b dortmund': 'Borussia Dortmund',
  'bayern munchen': 'Bayern Munich',
  'bodo glimt': 'Bodø/Glimt',
  'leipzig': 'RB Leipzig',
  'man city': 'Manchester City',
  'man utd': 'Manchester United',
  'paris': 'Paris Saint-Germain',
  'porto': 'FC Porto',
  's bratislava': 'Slovan Bratislava',
  'shakhtar': 'Shakhtar Donetsk',
  'slavia praha': 'Slavia Prague',
  'stuttgart': 'VfB Stuttgart',
  'viking': 'Viking FK',
};

function jsonResponse(payload:unknown, status=200) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { ...CORS_HEADERS, 'Content-Type':'application/json', 'Cache-Control':'private, max-age=180' },
  });
}

function normalize(value:string) {
  return String(value || '')
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .toLowerCase().replace(/&/g, ' and ')
    .replace(/\b(fc|cf|ac|ssc|afc|fk|sk|sc|rcd|rc|sl|vfb)\b/g, ' ')
    .replace(/[^a-z0-9]+/g, ' ').replace(/\s+/g, ' ').trim();
}

function canonical(value:string) {
  const s = normalize(value);
  const aliases:Record<string,string> = {
    'manchester city':'man city','man city':'man city',
    'manchester united':'man united','man utd':'man united','man united':'man united',
    'atletico madrid':'atleti','atletico de madrid':'atleti','atleti':'atleti',
    'borussia dortmund':'dortmund','b dortmund':'dortmund','dortmund':'dortmund',
    'bayern munich':'bayern','bayern munchen':'bayern','bayern':'bayern',
    'paris saint germain':'paris','psg':'paris','paris':'paris',
    'porto':'porto','fc porto':'porto',
    'rb leipzig':'leipzig','leipzig':'leipzig',
    'slovan bratislava':'slovan bratislava','s bratislava':'slovan bratislava',
    'shakhtar donetsk':'shakhtar','shakhtar':'shakhtar',
    'slavia prague':'slavia praha','slavia praha':'slavia praha',
    'viking':'viking','viking fk':'viking',
    'club bruges':'club brugge','club brugge':'club brugge',
    'sporting lisbon':'sporting cp','sporting':'sporting cp','sporting cp':'sporting cp',
    'internazionale':'inter','inter milan':'inter','inter':'inter',
    'bodo glimt':'bodo glimt',
  };
  return aliases[s] || s;
}

function isSeniorMens(name:string) {
  const s = String(name || '').toLowerCase();
  return !/(\(w\)| women| u21| u23| u19| youth| reserves| ii$| b$)/i.test(s);
}

async function fetchWithTimeout(url:string, asJson=false) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);
  try {
    const res = await fetch(url, {
      headers: {
        'Accept': asJson ? 'application/json' : 'text/html,application/xhtml+xml',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/152 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
      },
      redirect:'follow', signal:controller.signal,
    });
    if (!res.ok) throw new Error(`Source HTTP ${res.status}`);
    return asJson ? await res.json() : await res.text();
  } finally {
    clearTimeout(timer);
  }
}

async function fotmobSearch(term:string, hits=20) {
  const key = `${term}|${hits}`;
  const cached = searchCache.get(key);
  if (cached && Date.now()-cached.at < CACHE_TTL) return cached.value;
  const url = `https://apigw.fotmob.com/searchapi/suggest?term=${encodeURIComponent(term)}&lang=en&hits=${hits}`;
  const value = await fetchWithTimeout(url, true);
  searchCache.set(key,{at:Date.now(),value});
  return value;
}

async function resolveTeam(inputName:string):Promise<ResolvedTeam> {
  const cacheKey = canonical(inputName);
  const cached = teamResolveCache.get(cacheKey);
  if (cached && Date.now()-cached.at < CACHE_TTL) return cached.value;

  const query = SEARCH_ALIASES[normalize(inputName)] || inputName;
  const data = await fotmobSearch(query, 25);
  const options:any[] = [];
  for (const group of (data?.teamSuggest || [])) {
    for (const option of (group?.options || [])) options.push(option);
  }
  const senior = options.filter(o => isSeniorMens(String(o?.text || '').split('|')[0]));
  if (!senior.length) throw new Error(`Klubi ei leitud: ${inputName}`);

  const target = canonical(query);
  senior.sort((a,b) => {
    const an = String(a?.text || '').split('|')[0];
    const bn = String(b?.text || '').split('|')[0];
    const ac = canonical(an), bc = canonical(bn);
    const aScore = ac===target ? 0 : ac.includes(target)||target.includes(ac) ? 1 : 2;
    const bScore = bc===target ? 0 : bc.includes(target)||target.includes(bc) ? 1 : 2;
    return aScore-bScore || Number(b?.score||0)-Number(a?.score||0);
  });
  const best = senior[0];
  const display = String(best.text || '').split('|')[0];
  const value:ResolvedTeam = {
    id:String(best?.payload?.id || ''),
    name:display,
    leagueId:best?.payload?.leagueId == null ? null : Number(best.payload.leagueId),
    leagueName:best?.payload?.leagueName || null,
  };
  if (!value.id) throw new Error(`Klubi ID puudub: ${inputName}`);
  teamResolveCache.set(cacheKey,{at:Date.now(),value});
  return value;
}

function parseNextData(html:string, teamId:string) {
  const match = html.match(/<script[^>]*id=["']__NEXT_DATA__["'][^>]*>([\s\S]*?)<\/script>/i);
  if (!match) throw new Error('FotMobi meeskonna andmeid ei leitud');
  const root = JSON.parse(match[1]);
  const fallback = root?.props?.pageProps?.fallback || {};
  const direct = fallback[`team-${teamId}`];
  if (direct) return direct;
  for (const value of Object.values(fallback) as any[]) {
    if (String(value?.details?.id || '') === String(teamId)) return value;
  }
  throw new Error('FotMobi meeskonna plokk puudub');
}

async function loadTeamPage(team:ResolvedTeam) {
  const cached = teamPageCache.get(team.id);
  if (cached && Date.now()-cached.at < CACHE_TTL) return cached.value;
  const html = await fetchWithTimeout(`https://www.fotmob.com/teams/${team.id}/overview`, false) as string;
  const value = parseNextData(html, team.id);
  teamPageCache.set(team.id,{at:Date.now(),value});
  return value;
}

function currentSeasonLabel(page:any) {
  const raw = String(page?.details?.latestSeason || '');
  const m = raw.match(/(\d{4})\D+(\d{4})/);
  return m ? `${m[1]}/${m[2].slice(-2)}` : raw;
}

function finishedFixtures(page:any) {
  const fixtures = page?.fixtures?.allFixtures?.fixtures;
  return Array.isArray(fixtures)
    ? fixtures.filter((f:any) => f?.status?.finished === true && f?.status?.cancelled !== true)
        .sort((a:any,b:any) => new Date(b?.status?.utcTime||0).getTime()-new Date(a?.status?.utcTime||0).getTime())
    : [];
}

function resultForFixture(f:any, teamId:string) {
  if (typeof f?.result === 'number') return f.result > 0 ? 'W' : f.result < 0 ? 'L' : 'D';
  const home = String(f?.home?.id)===teamId;
  const hs=Number(f?.home?.score), as=Number(f?.away?.score);
  const gf=home?hs:as, ga=home?as:hs;
  return gf>ga?'W':gf<ga?'L':'D';
}

function scoreText(f:any) {
  const basic = String(f?.status?.scoreStr || '').trim();
  const note = String(f?.status?.reason?.short || '').trim();
  if (basic) return note && !/^FT$/i.test(note) ? `${basic} (${note})` : basic;
  return `${Number(f?.home?.score||0)} - ${Number(f?.away?.score||0)}`;
}

function recentFive(page:any, team:ResolvedTeam) {
  return finishedFixtures(page).slice(0,5).map((f:any) => ({
    date:f?.status?.utcTime || null,
    competition:f?.tournament?.name || '',
    home_team:f?.home?.name || '',
    away_team:f?.away?.name || '',
    home_score:Number(f?.home?.score ?? 0),
    away_score:Number(f?.away?.score ?? 0),
    score_text:scoreText(f),
    is_home:String(f?.home?.id)===team.id,
    result:resultForFixture(f,team.id),
  }));
}

function primaryLeagueTable(page:any, team:ResolvedTeam) {
  const tables = Array.isArray(page?.table) ? page.table : [];
  const primary = Number(page?.details?.primaryLeagueId || team.leagueId || 0);
  const block = tables.find((x:any) => Number(x?.data?.leagueId||0)===primary && Array.isArray(x?.data?.table?.all))
    || tables.find((x:any) => Array.isArray(x?.data?.table?.all));
  if (!block) return null;
  const rows = block.data.table.all;
  const idx = rows.findIndex((r:any) => String(r?.id)===team.id);
  if (idx<0) return null;
  const r=rows[idx];
  const score = String(r?.scoresStr || '0-0').match(/(-?\d+)\s*[-:]\s*(-?\d+)/);
  const gf=score?Number(score[1]):0, ga=score?Number(score[2]):0;
  return {
    league:block?.data?.leagueName || team.leagueName || 'Koduliiga',
    position:Number(r?.idx)>0?Number(r.idx):idx+1,
    teams:rows.length,
    team:r?.name || team.name,
    played:Number(r?.played||0), wins:Number(r?.wins||0), draws:Number(r?.draws||0), losses:Number(r?.losses||0),
    gf, ga, gd:Number(r?.goalConDiff ?? gf-ga), points:Number(r?.pts||0),
  };
}

function currentUcl(page:any, team:ResolvedTeam) {
  const season = currentSeasonLabel(page);
  let wins=0,draws=0,losses=0,gf=0,ga=0,played=0;
  for (const f of finishedFixtures(page)) {
    if (!/champions league/i.test(String(f?.tournament?.name||''))) continue;
    const date = new Date(f?.status?.utcTime||0);
    const startYear = Number(season.slice(0,4));
    if (Number.isFinite(startYear) && date.getUTCFullYear()<startYear) continue;
    played++;
    const home=String(f?.home?.id)===team.id;
    const hs=Number(f?.home?.score||0), as=Number(f?.away?.score||0);
    gf += home?hs:as; ga += home?as:hs;
    const result=resultForFixture(f,team.id);
    if(result==='W')wins++; else if(result==='D')draws++; else losses++;
  }
  return {played,wins,draws,losses,gf,ga,gd:gf-ga};
}

function snapshot(inputName:string, team:ResolvedTeam, page:any) {
  return {
    team:inputName,
    resolved_name:team.name,
    recent:recentFive(page,team),
    league:primaryLeagueTable(page,team),
    league_name:page?.details?.primaryLeagueName || team.leagueName || null,
    ucl:currentUcl(page,team),
  };
}

async function headToHead(a:ResolvedTeam,b:ResolvedTeam) {
  const data = await fotmobSearch(`${a.name} ${b.name}`, 50);
  const rows:any[]=[];
  for (const group of (data?.matchSuggest||[])) {
    for (const option of (group?.options||[])) {
      const p=option?.payload||{};
      const home=String(p.homeTeamId||''), away=String(p.awayTeamId||'');
      if (!((home===a.id&&away===b.id)||(home===b.id&&away===a.id))) continue;
      if (p.homeScore==null || p.awayScore==null || !p.matchDate) continue;
      const when=new Date(p.matchDate);
      if(Number.isNaN(when.getTime())||when.getTime()>Date.now()) continue;
      rows.push({date:p.matchDate,competition:p.leagueName||'',home_team:p.homeName||'',away_team:p.awayName||'',home_score:Number(p.homeScore),away_score:Number(p.awayScore)});
    }
  }
  const seen=new Set<string>();
  return rows.sort((x,y)=>new Date(y.date).getTime()-new Date(x.date).getTime())
    .filter(r=>{const k=`${r.date}|${r.home_team}|${r.away_team}`;if(seen.has(k))return false;seen.add(k);return true;})
    .slice(0,5);
}

Deno.serve(async (req:Request) => {
  if(req.method==='OPTIONS') return new Response('ok',{status:200,headers:CORS_HEADERS});
  if(req.method!=='POST') return jsonResponse({ok:false,error:'Method not allowed'},405);
  try {
    const body=await req.json().catch(()=>({}));
    const home=String(body?.home_team||'').trim(), away=String(body?.away_team||'').trim();
    if(!home||!away||home.length>100||away.length>100) return jsonResponse({ok:false,error:'Vigased meeskonnad'},400);

    const [homeTeam,awayTeam]=await Promise.all([resolveTeam(home),resolveTeam(away)]);
    const [homePage,awayPage]=await Promise.all([loadTeamPage(homeTeam),loadTeamPage(awayTeam)]);
    const h2h=await headToHead(homeTeam,awayTeam).catch(()=>[]);
    const season=currentSeasonLabel(homePage)||currentSeasonLabel(awayPage);

    return jsonResponse({
      ok:true,
      source:'FotMob',
      season,
      home:snapshot(home,homeTeam,homePage),
      away:snapshot(away,awayTeam,awayPage),
      h2h,
      coverage_note:'Allikas: FotMob. Viimased 5 mängu hõlmavad kõiki FotMobi esimese meeskonna mängukavas kajastatud lõppenud kohtumisi eri sarjades, sh liiga-, karika-, Euroopa- ja sõprusmänge.',
    });
  } catch(error) {
    console.error('ucl-historical-stats',error);
    return jsonResponse({ok:false,error:error instanceof Error?error.message:String(error)},502);
  }
});
