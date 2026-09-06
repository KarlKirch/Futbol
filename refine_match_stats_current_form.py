from pathlib import Path
import re

index_path = Path('index.html')
sw_path = Path('sw.js')
text = index_path.read_text(encoding='utf-8')
sw = sw_path.read_text(encoding='utf-8') if sw_path.exists() else ''

CSS_MARKER = '/* FUTBOL CURRENT FORM MATCH STATS */'
JS_MARKER = '// FUTBOL CURRENT FORM MATCH STATS'

if CSS_MARKER not in text:
    css = r'''

    /* FUTBOL CURRENT FORM MATCH STATS */
    .current-stats-head {
      display:flex;
      justify-content:space-between;
      align-items:flex-start;
      gap:10px;
      margin-bottom:12px;
    }
    .current-stats-title { color:#1d316f; font-size:14px; font-weight:950; }
    .current-stats-subtitle { margin-top:2px; color:#778198; font-size:10px; line-height:1.4; }
    .current-stats-season { flex:0 0 auto; color:#6f7890; font-size:9px; font-weight:850; }
    .current-team-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; }
    .current-team-card { padding:11px; border:1px solid #dde3ef; border-radius:12px; background:white; }
    .current-team-name { color:#1d2f68; font-size:13px; font-weight:950; }
    .current-form-strip { display:flex; flex-wrap:wrap; gap:5px; margin:8px 0 10px; }
    .current-form-pill { width:27px; height:27px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; font-size:9px; font-weight:950; }
    .current-form-pill.w { background:#dff3e6; color:#176b43; }
    .current-form-pill.d { background:#fff0cf; color:#7b5710; }
    .current-form-pill.l { background:#fde4e4; color:#9c2d2d; }
    .current-recent-title, .current-season-title { margin-top:10px; color:#44516d; font-size:9px; font-weight:950; text-transform:uppercase; letter-spacing:.35px; }
    .current-match-row { display:grid; grid-template-columns:26px minmax(0,1fr) auto; gap:7px; align-items:center; padding:7px 0; border-bottom:1px solid #eff1f5; }
    .current-match-row:last-child { border-bottom:0; }
    .current-result-badge { width:25px; height:25px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:8px; font-weight:950; }
    .current-result-badge.w { background:#dff3e6; color:#176b43; }
    .current-result-badge.d { background:#fff0cf; color:#7b5710; }
    .current-result-badge.l { background:#fde4e4; color:#9c2d2d; }
    .current-match-main { min-width:0; }
    .current-match-opponent { color:#26334d; font-size:10px; font-weight:900; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .current-match-meta { margin-top:2px; color:#858da0; font-size:8px; }
    .current-match-score { color:#1f2d4e; font-size:11px; font-weight:950; white-space:nowrap; }
    .current-summary-box { margin-top:7px; padding:9px; border:1px solid #e4e8f0; border-radius:10px; background:#fafbfe; }
    .current-summary-primary { color:#20346f; font-size:12px; font-weight:950; }
    .current-summary-secondary { margin-top:3px; color:#667187; font-size:9px; line-height:1.45; }
    .current-h2h { margin-top:12px; padding-top:10px; border-top:1px solid #dfe4ee; }
    .current-h2h-title { color:#334777; font-size:10px; font-weight:950; }
    .current-h2h-row { display:grid; grid-template-columns:62px minmax(0,1fr) auto; gap:7px; padding:6px 0; border-bottom:1px solid #f0f2f6; color:#5e687d; font-size:9px; }
    .current-coverage-note { margin-top:9px; color:#8b92a0; font-size:8px; line-height:1.45; }
    .match-insight-panel.stats-persistent-loading { min-height:64px; display:flex; align-items:center; justify-content:center; }

    @media (max-width:520px) {
      .current-team-grid { grid-template-columns:1fr; }
    }
'''
    text = text.replace('  </style>', css + '\n  </style>', 1)

if JS_MARKER not in text:
    js = r'''

// FUTBOL CURRENT FORM MATCH STATS
const persistentStatsOpen = new Set();
const currentMatchStatsCache = new Map();
const currentMatchStatsPending = new Map();

function statsResultClass(value) {
  const r = String(value || '').toLowerCase();
  return r === 'w' ? 'w' : r === 'd' ? 'd' : 'l';
}

function statsResultText(value) {
  const r = String(value || '').toLowerCase();
  return r === 'w' ? 'V' : r === 'd' ? 'Vi' : 'K';
}

function statsShortDate(value) {
  if (!value) return '';
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return '';
  return new Intl.DateTimeFormat('et-EE', { day:'2-digit', month:'2-digit', year:'2-digit', timeZone:'Europe/Tallinn' }).format(d);
}

function teamRecentStatsHtml(team) {
  const recent = Array.isArray(team?.recent) ? team.recent : [];
  if (!recent.length) return '<div class="hint" style="text-align:left;margin-top:8px">Viimaste mängude andmeid ei leitud.</div>';
  const strip = recent.map(row => '<span class="current-form-pill ' + statsResultClass(row.result) + '" title="' + esc(row.home_team + ' ' + row.home_score + ':' + row.away_score + ' ' + row.away_team) + '">' + statsResultText(row.result) + '</span>').join('');
  const rows = recent.map(row => {
    const own = String(team?.team || '').toLowerCase();
    const homeIsOwn = String(row.home_team || '').toLowerCase() === own;
    const opponent = homeIsOwn ? row.away_team : row.home_team;
    const venue = homeIsOwn ? 'Kodus' : 'Võõrsil';
    return '<div class="current-match-row">' +
      '<span class="current-result-badge ' + statsResultClass(row.result) + '">' + statsResultText(row.result) + '</span>' +
      '<div class="current-match-main"><div class="current-match-opponent">' + esc(opponent || '') + '</div>' +
      '<div class="current-match-meta">' + esc(statsShortDate(row.date)) + ' · ' + esc(row.competition || '') + ' · ' + venue + '</div></div>' +
      '<div class="current-match-score">' + Number(row.home_score) + ':' + Number(row.away_score) + '</div>' +
    '</div>';
  }).join('');
  return '<div class="current-form-strip">' + strip + '</div><div class="current-recent-title">Viimased 5 ametlikku mängu</div>' + rows;
}

function teamSeasonStatsHtml(team, season) {
  let league = '';
  if (team?.league) {
    const row = team.league;
    league = '<div class="current-season-title">' + esc(row.league || team.league_name || 'Koduliiga') + ' · ' + esc(season || '') + '</div>' +
      '<div class="current-summary-box"><div class="current-summary-primary">' + Number(row.position || 0) + '. koht · ' + Number(row.points || 0) + ' p · ' + Number(row.played || 0) + ' mängu</div>' +
      '<div class="current-summary-secondary">' + Number(row.wins || 0) + ' V · ' + Number(row.draws || 0) + ' Vi · ' + Number(row.losses || 0) + ' K · väravad ' + Number(row.gf || 0) + ':' + Number(row.ga || 0) + ' · vv ' + (Number(row.gd || 0) >= 0 ? '+' : '') + Number(row.gd || 0) + '</div></div>';
  } else {
    league = '<div class="current-season-title">Koduliiga · ' + esc(season || '') + '</div><div class="hint" style="text-align:left;margin-top:6px">Selle klubi liigatabeli andmeid ei ole praegu allikas saadaval.</div>';
  }

  const ucl = team?.ucl || {};
  const cl = '<div class="current-season-title">Champions League · ' + esc(season || '') + '</div>' +
    '<div class="current-summary-box"><div class="current-summary-primary">' + Number(ucl.played || 0) + ' mängu · ' + Number(ucl.wins || 0) + ' V · ' + Number(ucl.draws || 0) + ' Vi · ' + Number(ucl.losses || 0) + ' K</div>' +
    '<div class="current-summary-secondary">Väravad ' + Number(ucl.gf || 0) + ':' + Number(ucl.ga || 0) + '</div></div>';
  return league + cl;
}

function currentTeamStatsHtml(team, season) {
  return '<div class="current-team-card"><div class="current-team-name">' + esc(team?.team || '') + '</div>' + teamRecentStatsHtml(team) + teamSeasonStatsHtml(team, season) + '</div>';
}

function currentH2hHtml(data) {
  const h2h = Array.isArray(data?.h2h) ? data.h2h : [];
  if (!h2h.length) return '';
  return '<div class="current-h2h"><div class="current-h2h-title">Omavahelised Champions League’i mängud</div>' +
    h2h.map(row => '<div class="current-h2h-row"><span>' + esc(row.season || '') + '</span><span>' + esc(row.home_team || '') + ' – ' + esc(row.away_team || '') + '</span><strong>' + Number(row.home_score) + ':' + Number(row.away_score) + '</strong></div>').join('') +
  '</div>';
}

function currentMatchStatsHtml(data) {
  return '<div class="current-stats-head"><div><div class="current-stats-title">Hetkevorm ja hooaja seis</div>' +
    '<div class="current-stats-subtitle">Viimased tulemused, koduliiga hetkeseis ja käimasoleva CL hooaja statistika.</div></div>' +
    '<div class="current-stats-season">' + esc(data?.season || '') + '</div></div>' +
    '<div class="current-team-grid">' + currentTeamStatsHtml(data?.home, data?.season) + currentTeamStatsHtml(data?.away, data?.season) + '</div>' +
    currentH2hHtml(data) +
    '<div class="current-coverage-note">' + esc(data?.coverage_note || '') + '</div>';
}

async function loadPersistentMatchStats(matchId) {
  if (currentMatchStatsCache.has(matchId)) return currentMatchStatsCache.get(matchId);
  if (currentMatchStatsPending.has(matchId)) return currentMatchStatsPending.get(matchId);
  const match = matches.find(m => m.id === matchId);
  if (!match) throw new Error('Mängu ei leitud');

  const promise = sb.functions.invoke('ucl-historical-stats', {
    body: { home_team: match.home_team, away_team: match.away_team }
  }).then(result => {
    if (result.error || !result.data || result.data.ok === false) {
      throw result.error || new Error(result.data?.error || 'Statistika laadimine ebaõnnestus');
    }
    currentMatchStatsCache.set(matchId, result.data);
    return result.data;
  }).finally(() => currentMatchStatsPending.delete(matchId));

  currentMatchStatsPending.set(matchId, promise);
  return promise;
}

function renderPersistentStatsPanel(matchId) {
  const mount = document.getElementById('insight-' + matchId);
  const button = mount?.parentElement?.querySelector('.match-insight-btn');
  if (!mount) return;
  const isOpen = persistentStatsOpen.has(matchId);
  mount.classList.toggle('hidden', !isOpen);
  if (button) button.textContent = isOpen ? '📊 Sulge statistika' : '📊 Mängu statistika';
  if (!isOpen) return;

  if (currentMatchStatsCache.has(matchId)) {
    mount.classList.remove('stats-persistent-loading');
    mount.innerHTML = currentMatchStatsHtml(currentMatchStatsCache.get(matchId));
    return;
  }

  mount.classList.add('stats-persistent-loading');
  mount.innerHTML = '<div class="hint">Laen hetkevormi ja hooaja statistikat…</div>';
  loadPersistentMatchStats(matchId).then(data => {
    if (!persistentStatsOpen.has(matchId)) return;
    const currentMount = document.getElementById('insight-' + matchId);
    if (!currentMount) return;
    currentMount.classList.remove('stats-persistent-loading');
    currentMount.innerHTML = currentMatchStatsHtml(data);
  }).catch(() => {
    if (!persistentStatsOpen.has(matchId)) return;
    const currentMount = document.getElementById('insight-' + matchId);
    if (!currentMount) return;
    currentMount.classList.remove('stats-persistent-loading');
    currentMount.innerHTML = '<div class="hint">Statistika laadimine ebaõnnestus. Proovi uuesti.</div>';
  });
}

toggleMatchInsightsDeep = function(matchId) {
  if (persistentStatsOpen.has(matchId)) persistentStatsOpen.delete(matchId);
  else persistentStatsOpen.add(matchId);
  renderPersistentStatsPanel(matchId);
};

const __currentFormStatsBaseRenderGames = renderGames;
renderGames = function() {
  __currentFormStatsBaseRenderGames();
  document.querySelectorAll('#games .match-insight-panel').forEach(panel => {
    const id = String(panel.id || '').replace(/^insight-/, '');
    if (id) renderPersistentStatsPanel(id);
  });
};
'''
    pos = text.rfind('\n\ninit();')
    if pos == -1:
        raise SystemExit('init anchor not found')
    text = text[:pos] + js + text[pos:]

# Force installed clients to refresh the shell after this interaction change.
if sw:
    sw = re.sub(r'const CACHE_NAME = "futbol-champions-v\d+";', 'const CACHE_NAME = "futbol-champions-v8";', sw)

index_path.write_text(text, encoding='utf-8')
if sw_path.exists():
    sw_path.write_text(sw, encoding='utf-8')
print('Refined match statistics to current form and persistent panels')
