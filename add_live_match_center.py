from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

CSS_MARKER = '/* FUTBOL FOTMOB LIVE MATCH CENTER */'
JS_MARKER = '// FUTBOL FOTMOB LIVE MATCH CENTER'

if CSS_MARKER not in text:
    css = r'''

    /* FUTBOL FOTMOB LIVE MATCH CENTER */
    .live-center { margin:0 0 16px; }
    .live-center-head { display:flex; align-items:center; justify-content:space-between; gap:12px; margin:2px 2px 10px; }
    .live-center-title { color:var(--dark); font-size:13px; font-weight:950; letter-spacing:1.35px; text-transform:uppercase; }
    .live-center-source { color:var(--muted); font-size:10px; font-weight:800; }
    .live-game-card { overflow:hidden; padding:0; border:1px solid #d8e2dc; border-radius:19px; background:#fff; box-shadow:0 8px 26px rgba(20,40,28,.09); }
    .live-game-card + .live-game-card { margin-top:11px; }
    .live-game-top { display:flex; align-items:center; justify-content:space-between; gap:10px; padding:11px 14px 8px; border-bottom:1px solid #edf1ee; }
    .live-status-pill { display:inline-flex; align-items:center; gap:6px; min-height:27px; padding:0 9px; border-radius:999px; background:#fff0f0; color:#b4232f; font-size:11px; font-weight:950; letter-spacing:.35px; }
    .live-status-pill.finished { background:#edf2ef; color:#58645d; }
    .live-status-dot { width:7px; height:7px; border-radius:50%; background:currentColor; box-shadow:0 0 0 4px rgba(180,35,47,.09); }
    .live-game-round { color:var(--muted); font-size:10px; font-weight:800; text-align:right; }
    .live-scoreboard { display:grid; grid-template-columns:minmax(0,1fr) auto minmax(0,1fr); align-items:center; gap:10px; padding:15px 13px 11px; }
    .live-team { min-width:0; text-align:center; }
    .live-team-logo { width:44px; height:44px; object-fit:contain; display:block; margin:0 auto 7px; }
    .live-team-name { font-size:13px; font-weight:900; line-height:1.2; overflow-wrap:anywhere; }
    .live-score { min-width:88px; color:var(--dark); font-size:34px; line-height:1; font-weight:950; letter-spacing:-1px; text-align:center; }
    .live-score-sep { padding:0 4px; color:#87918b; font-weight:700; }
    .live-scorers { display:grid; grid-template-columns:1fr 1fr; gap:12px; padding:0 14px 12px; color:#566159; font-size:10.5px; line-height:1.45; }
    .live-scorers-side:last-child { text-align:right; }
    .live-scorer-row + .live-scorer-row { margin-top:2px; }
    .live-own-prediction { margin:0 12px 12px; padding:9px 11px; border:1px solid #d6e8dc; border-radius:12px; background:#f4faf6; color:#285b3f; font-size:11px; font-weight:800; text-align:center; }
    .live-events { border-top:1px solid #edf1ee; }
    .live-events summary { padding:11px 14px; list-style:none; cursor:pointer; color:#46524a; font-size:11px; font-weight:900; }
    .live-events summary::-webkit-details-marker { display:none; }
    .live-events summary::after { content:'›'; float:right; font-size:18px; line-height:11px; transform:rotate(90deg); transition:transform .15s ease; }
    .live-events[open] summary::after { transform:rotate(-90deg); }
    .live-event-list { padding:0 14px 12px; }
    .live-event-row { display:grid; grid-template-columns:38px 24px minmax(0,1fr); gap:7px; align-items:start; padding:7px 0; border-top:1px solid #f0f3f1; font-size:11px; }
    .live-event-minute { color:#6d7770; font-weight:900; }
    .live-event-icon { text-align:center; font-weight:950; }
    .live-event-main { min-width:0; line-height:1.35; }
    .live-event-main strong { font-weight:900; }
    .live-event-meta { color:#7b857e; font-size:10px; }
    .live-inline-strip { margin:8px 0 10px; padding:9px 10px; border:1px solid #f0d3d6; border-radius:11px; background:#fff7f7; color:#8d2430; font-size:11px; font-weight:900; text-align:center; }
    .live-inline-strip.finished { border-color:#dde5e0; background:#f7f9f8; color:#566159; }
    article.card.live-match-active { border-color:#e4c7cb; box-shadow:0 7px 24px rgba(156,38,49,.08); }
    .live-data-note { padding:0 14px 10px; color:#8a948d; font-size:9px; text-align:center; }
    @media (max-width:420px) {
      .live-scoreboard { gap:5px; padding-left:8px; padding-right:8px; }
      .live-team-logo { width:40px; height:40px; }
      .live-team-name { font-size:12px; }
      .live-score { min-width:76px; font-size:31px; }
      .live-scorers { padding-left:10px; padding-right:10px; gap:8px; }
    }
'''
    text = text.replace('  </style>', css + '\n  </style>', 1)

if JS_MARKER not in text:
    js = r'''

// FUTBOL FOTMOB LIVE MATCH CENTER
const liveMatchState = new Map();
let liveMatchRefreshPending = null;
let liveMatchPollTimer = null;
let liveMatchLastFetchAt = 0;

function liveRelevantMatches() {
  if (!Array.isArray(matches)) return [];
  const now = Date.now();
  return matches.filter(match => {
    const kickoff = new Date(match.kickoff_at).getTime();
    if (!Number.isFinite(kickoff)) return false;
    const state = liveMatchState.get(match.id);
    if (state?.started && !state?.finished) return true;
    if (state?.finished && now - kickoff < 5 * 60 * 60 * 1000) return true;
    return kickoff >= now - 6 * 60 * 60 * 1000 && kickoff <= now + 12 * 60 * 60 * 1000;
  }).slice(0, 24);
}

function liveStatusText(state) {
  if (!state) return '';
  const raw = String(state.live_time || '').trim();
  if (state.cancelled) return 'TÜHISTATUD';
  if (state.finished) return 'LÕPP';
  if (state.phase === 'ht') return 'HT';
  if (state.phase === 'et') return raw ? 'ET · ' + raw : 'ET';
  if (state.started) return raw ? 'LIVE · ' + raw : 'LIVE';
  return '';
}

function liveScoreText(state) {
  const home = state?.home_score;
  const away = state?.away_score;
  if (home === null || home === undefined || away === null || away === undefined) return '– : –';
  return Number(home) + ' : ' + Number(away);
}

function liveEventIcon(event) {
  const kind = String(event?.kind || '');
  if (kind === 'goal' || kind === 'penalty_goal') return '⚽';
  if (kind === 'own_goal') return 'OG';
  if (kind === 'yellow_card') return '🟨';
  if (kind === 'second_yellow') return '🟨';
  if (kind === 'red_card') return '🟥';
  if (kind === 'substitution') return '⇄';
  if (kind === 'penalty_miss') return '✕';
  if (kind === 'var') return 'VAR';
  return '•';
}

function liveEventDescription(event) {
  const kind = String(event?.kind || '');
  const player = esc(event?.player || '');
  if (kind === 'substitution') {
    const playerIn = esc(event?.player_in || '');
    const playerOut = esc(event?.player_out || event?.player || '');
    return '<strong>' + (playerIn || 'Vahetus') + '</strong>' + (playerOut ? '<div class="live-event-meta">sisse · ' + playerOut + ' välja</div>' : '');
  }
  let title = esc(event?.label || 'Sündmus');
  if (player) title = '<strong>' + player + '</strong> · ' + title;
  let meta = '';
  if (event?.assist) meta += 'Sööt: ' + esc(event.assist);
  if (event?.score) meta += (meta ? ' · ' : '') + 'Seis ' + esc(event.score);
  return title + (meta ? '<div class="live-event-meta">' + meta + '</div>' : '');
}

function liveEventsHtml(state) {
  const events = Array.isArray(state?.events) ? state.events : [];
  if (!events.length) return '';
  const keyEvents = events.filter(event => ['goal','penalty_goal','own_goal','yellow_card','second_yellow','red_card','substitution','penalty_miss','var'].includes(String(event?.kind || '')));
  if (!keyEvents.length) return '';
  const rows = keyEvents.slice().reverse().map(event =>
    '<div class="live-event-row">' +
      '<div class="live-event-minute">' + esc(event?.minute_text || '') + '</div>' +
      '<div class="live-event-icon">' + liveEventIcon(event) + '</div>' +
      '<div class="live-event-main">' + liveEventDescription(event) + '</div>' +
    '</div>'
  ).join('');
  return '<details class="live-events"><summary>Tähtsad sündmused · ' + keyEvents.length + '</summary><div class="live-event-list">' + rows + '</div></details>';
}

function liveScorersForSide(state, side) {
  const events = Array.isArray(state?.events) ? state.events : [];
  return events.filter(event => event?.side === side && ['goal','penalty_goal','own_goal'].includes(String(event?.kind || '')));
}

function liveScorersHtml(state) {
  const renderSide = side => {
    const rows = liveScorersForSide(state, side);
    if (!rows.length) return '<div class="live-scorers-side"></div>';
    return '<div class="live-scorers-side">' + rows.map(event => {
      const suffix = event.kind === 'penalty_goal' ? ' pen' : event.kind === 'own_goal' ? ' ov' : '';
      return '<div class="live-scorer-row">⚽ ' + esc(event.player || 'Värav') + ' ' + esc(event.minute_text || '') + esc(suffix) + '</div>';
    }).join('') + '</div>';
  };
  return '<div class="live-scorers">' + renderSide('home') + renderSide('away') + '</div>';
}

function provisionalPredictionHtml(match, state) {
  if (!state?.started || state?.home_score === null || state?.home_score === undefined || state?.away_score === null || state?.away_score === undefined) return '';
  const own = predictions.find(p => p.match_id === match.id && p.user_id === ownPlayerId());
  if (!own) return '';
  const ph = Number(own.home_score), pa = Number(own.away_score);
  const ah = Number(state.home_score), aa = Number(state.away_score);
  let points = 0;
  if (ph === ah && pa === aa) points = 3;
  else {
    const predicted = Math.sign(ph - pa);
    const actual = Math.sign(ah - aa);
    if (predicted === actual) points = 1;
  }
  const label = points === 3 ? 'hetkel täpne tulemus' : points === 1 ? 'hetkel õige mängutulemus' : 'hetkel 0 punkti';
  return '<div class="live-own-prediction">Sinu ennustus ' + ph + ':' + pa + ' · ' + label + (points ? ' · ' + points + ' p' : '') + '</div>';
}

function liveGameHtml(match, state) {
  const finished = !!state?.finished;
  const homeLogo = match.home_logo_url ? '<img class="live-team-logo" src="' + esc(match.home_logo_url) + '" alt="">' : '';
  const awayLogo = match.away_logo_url ? '<img class="live-team-logo" src="' + esc(match.away_logo_url) + '" alt="">' : '';
  return '<div class="live-game-card">' +
    '<div class="live-game-top"><span class="live-status-pill ' + (finished ? 'finished' : '') + '">' +
      (finished ? '' : '<span class="live-status-dot"></span>') + esc(liveStatusText(state)) + '</span>' +
      '<span class="live-game-round">' + esc(roundLabel(match)) + '</span></div>' +
    '<div class="live-scoreboard">' +
      '<div class="live-team">' + homeLogo + '<div class="live-team-name">' + esc(match.home_team) + '</div></div>' +
      '<div class="live-score">' + liveScoreText(state).replace(' : ', '<span class="live-score-sep">:</span>') + '</div>' +
      '<div class="live-team">' + awayLogo + '<div class="live-team-name">' + esc(match.away_team) + '</div></div>' +
    '</div>' +
    liveScorersHtml(state) +
    provisionalPredictionHtml(match, state) +
    liveEventsHtml(state) +
    '<div class="live-data-note">Live-andmed: FotMob · uuendub automaatselt</div>' +
  '</div>';
}

function renderLiveMatchCenter() {
  const container = document.getElementById('games');
  if (!container) return;
  let mount = document.getElementById('liveMatchCenter');
  if (mount) mount.remove();
  const candidates = matches.filter(match => {
    const state = liveMatchState.get(match.id);
    if (!state) return false;
    if (state.started && !state.finished && !state.cancelled) return true;
    if (state.finished) {
      const kickoff = new Date(match.kickoff_at).getTime();
      return Number.isFinite(kickoff) && Date.now() - kickoff < 5 * 60 * 60 * 1000;
    }
    return false;
  }).sort((a, b) => {
    const sa = liveMatchState.get(a.id), sb = liveMatchState.get(b.id);
    const liveA = sa?.started && !sa?.finished ? 0 : 1;
    const liveB = sb?.started && !sb?.finished ? 0 : 1;
    return liveA - liveB || new Date(a.kickoff_at) - new Date(b.kickoff_at);
  });
  if (!candidates.length) return;
  const anyLive = candidates.some(match => {
    const state = liveMatchState.get(match.id);
    return state?.started && !state?.finished;
  });
  mount = document.createElement('section');
  mount.id = 'liveMatchCenter';
  mount.className = 'live-center';
  mount.innerHTML = '<div class="live-center-head"><div class="live-center-title">' + (anyLive ? 'Champions League · LIVE' : 'Champions League · viimased tulemused') + '</div><div class="live-center-source">FotMob</div></div>' +
    candidates.map(match => liveGameHtml(match, liveMatchState.get(match.id))).join('');
  container.prepend(mount);
}

function decorateLiveMatchCards() {
  const container = document.getElementById('games');
  if (!container) return;
  container.querySelectorAll('article.card').forEach(card => {
    const matchId = card.dataset?.matchId || (typeof matchIdFromCardFix === 'function' ? matchIdFromCardFix(card) : '');
    card.querySelectorAll('.live-inline-strip').forEach(el => el.remove());
    card.classList.remove('live-match-active');
    if (!matchId) return;
    const state = liveMatchState.get(matchId);
    if (!state || (!state.started && !state.finished)) return;
    const strip = document.createElement('div');
    strip.className = 'live-inline-strip ' + (state.finished ? 'finished' : '');
    strip.textContent = liveStatusText(state) + ' · ' + liveScoreText(state);
    const teams = card.querySelector('.teams-logo-grid') || card.querySelector('.teams') || card.querySelector('.match-header');
    if (teams) teams.insertAdjacentElement('afterend', strip); else card.prepend(strip);
    if (state.started && !state.finished) card.classList.add('live-match-active');
  });
}

async function refreshLiveMatchCenter(force = false) {
  if (!currentUser || !currentPlayer || document.visibilityState === 'hidden') return;
  const relevant = liveRelevantMatches();
  if (!relevant.length) return;
  if (liveMatchRefreshPending) return liveMatchRefreshPending;
  if (!force && Date.now() - liveMatchLastFetchAt < 10000) return;
  liveMatchLastFetchAt = Date.now();
  liveMatchRefreshPending = (async () => {
    try {
      const result = await sb.functions.invoke('ucl-live', { body: { match_ids: relevant.map(match => match.id), force } });
      if (result.error || !result.data || result.data.ok === false) throw result.error || new Error(result.data?.error || 'Live-andmete laadimine ebaõnnestus');
      (result.data.matches || []).forEach(row => liveMatchState.set(row.match_id, row));
      renderLiveMatchCenter();
      decorateLiveMatchCards();
    } catch (error) {
      console.error('FotMob live center', error);
    } finally {
      liveMatchRefreshPending = null;
    }
  })();
  return liveMatchRefreshPending;
}

function ensureLiveMatchPolling() {
  if (!liveMatchPollTimer) {
    liveMatchPollTimer = window.setInterval(() => {
      if (document.visibilityState === 'visible') refreshLiveMatchCenter(false);
    }, 30000);
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'visible') refreshLiveMatchCenter(true);
    });
  }
}

const __liveCenterBaseRenderGames = renderGames;
renderGames = function() {
  __liveCenterBaseRenderGames();
  renderLiveMatchCenter();
  decorateLiveMatchCards();
  ensureLiveMatchPolling();
  window.setTimeout(() => refreshLiveMatchCenter(false), 0);
};
'''
    text = text.replace('\ninit();', js + '\n\ninit();', 1)

path.write_text(text, encoding='utf-8')
