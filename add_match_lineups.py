from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

CSS_MARKER = '/* FUTBOL FOTMOB MATCH LINEUPS */'
JS_MARKER = '// FUTBOL FOTMOB MATCH LINEUPS'

if CSS_MARKER not in text:
    css = r'''

    /* FUTBOL FOTMOB MATCH LINEUPS */
    .match-lineups-inline { margin:10px 0 0; }
    .match-lineups-details { overflow:hidden; border:1px solid #dce7e0; border-radius:13px; background:#fbfdfc; }
    .match-lineups-details summary { padding:11px 13px; list-style:none; cursor:pointer; color:#34453a; font-size:11px; font-weight:950; }
    .match-lineups-details summary::-webkit-details-marker { display:none; }
    .match-lineups-details summary::after { content:'›'; float:right; font-size:18px; line-height:11px; transform:rotate(90deg); transition:transform .15s ease; }
    .match-lineups-details[open] summary::after { transform:rotate(-90deg); }
    .match-lineups-content { padding:0 11px 11px; border-top:1px solid #edf2ef; }
    .match-lineups-kicker { padding:8px 1px 7px; color:#748078; font-size:9.5px; font-weight:800; text-align:center; }
    .match-lineups-grid { display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr); gap:9px; }
    .lineup-team-card { min-width:0; padding:10px 9px; border:1px solid #e5ebe7; border-radius:11px; background:#fff; }
    .lineup-team-head { display:flex; align-items:flex-start; justify-content:space-between; gap:6px; padding-bottom:7px; border-bottom:1px solid #eff3f0; }
    .lineup-team-name { min-width:0; font-size:11px; font-weight:950; line-height:1.25; overflow-wrap:anywhere; }
    .lineup-formation { flex:0 0 auto; padding:3px 6px; border-radius:999px; background:#edf7f1; color:#286343; font-size:9px; font-weight:950; }
    .lineup-section-title { margin:8px 0 5px; color:#7a847e; font-size:8.5px; font-weight:950; letter-spacing:.5px; text-transform:uppercase; }
    .lineup-player-row { display:grid; grid-template-columns:22px minmax(0,1fr); gap:5px; align-items:center; min-height:24px; padding:2px 0; font-size:10.5px; }
    .lineup-shirt { width:20px; height:20px; display:flex; align-items:center; justify-content:center; border-radius:50%; background:#eef3f0; color:#415048; font-size:8.5px; font-weight:950; }
    .lineup-player-name { min-width:0; font-weight:800; line-height:1.2; overflow-wrap:anywhere; }
    .lineup-bench { color:#68746c; font-size:9.5px; line-height:1.45; }
    .live-game-card .match-lineups-details { margin:0; border-width:1px 0 0; border-radius:0; background:#fff; }
    .live-game-card .match-lineups-content { padding-left:13px; padding-right:13px; }
    @media (max-width:420px) {
      .match-lineups-grid { gap:6px; }
      .lineup-team-card { padding:8px 7px; }
      .lineup-team-name { font-size:10px; }
      .lineup-player-row { grid-template-columns:20px minmax(0,1fr); gap:4px; font-size:9.5px; }
      .lineup-shirt { width:18px; height:18px; font-size:8px; }
    }
'''
    text = text.replace('  </style>', css + '\n  </style>', 1)

if JS_MARKER not in text:
    js = r'''

// FUTBOL FOTMOB MATCH LINEUPS
const matchLineupState = new Map();
const matchLineupOpen = new Set();
let matchLineupPending = null;
let matchLineupPollTimer = null;
let matchLineupLastFetchAt = 0;

function rememberMatchLineupOpen(matchId, open) {
  if (open) matchLineupOpen.add(String(matchId));
  else matchLineupOpen.delete(String(matchId));
}

function lineupRelevantMatches() {
  if (!Array.isArray(matches)) return [];
  const now = Date.now();
  return matches.filter(match => {
    const kickoff = new Date(match.kickoff_at).getTime();
    if (!Number.isFinite(kickoff)) return false;
    const live = (typeof liveMatchState !== 'undefined' && liveMatchState?.get) ? liveMatchState.get(match.id) : null;
    if (live?.started && !live?.finished) return true;
    return kickoff >= now - 5 * 60 * 60 * 1000 && kickoff <= now + 4 * 60 * 60 * 1000;
  }).slice(0, 24);
}

function lineupPlayerRowsHtml(players) {
  const rows = Array.isArray(players) ? players : [];
  return rows.map(player => {
    const number = String(player?.shirt_number ?? '').trim();
    return '<div class="lineup-player-row">' +
      '<span class="lineup-shirt">' + esc(number || '·') + '</span>' +
      '<span class="lineup-player-name">' + esc(player?.name || '') + '</span>' +
    '</div>';
  }).join('');
}

function lineupTeamHtml(team, fallbackName) {
  const starters = Array.isArray(team?.starters) ? team.starters : [];
  const subs = Array.isArray(team?.substitutes) ? team.substitutes : [];
  const formation = String(team?.formation || '').trim();
  const bench = subs.map(player => {
    const number = String(player?.shirt_number ?? '').trim();
    return (number ? number + ' ' : '') + String(player?.name || '');
  }).filter(Boolean).join(', ');
  return '<div class="lineup-team-card">' +
    '<div class="lineup-team-head"><div class="lineup-team-name">' + esc(team?.team_name || fallbackName || '') + '</div>' +
      (formation ? '<span class="lineup-formation">' + esc(formation) + '</span>' : '') + '</div>' +
    '<div class="lineup-section-title">Algkoosseis</div>' +
    lineupPlayerRowsHtml(starters) +
    (bench ? '<div class="lineup-section-title">Varumängijad</div><div class="lineup-bench">' + esc(bench) + '</div>' : '') +
  '</div>';
}

function matchLineupsDetailsHtml(match, state) {
  if (!state?.available || !state?.home || !state?.away) return '';
  const open = matchLineupOpen.has(String(match.id)) ? ' open' : '';
  return '<details class="match-lineups-details"' + open + ' ontoggle="rememberMatchLineupOpen(\'' + esc(match.id) + '\', this.open)">' +
    '<summary>Koosseisud</summary>' +
    '<div class="match-lineups-content">' +
      '<div class="match-lineups-kicker">FotMobi ametlik algkoosseis</div>' +
      '<div class="match-lineups-grid">' +
        lineupTeamHtml(state.home, match.home_team) +
        lineupTeamHtml(state.away, match.away_team) +
      '</div>' +
    '</div>' +
  '</details>';
}

function lineupMatchIdFromCard(card) {
  if (!card) return '';
  if (typeof matchIdFromCardFix === 'function') return matchIdFromCardFix(card);
  if (card.dataset?.matchId) return card.dataset.matchId;
  const scoreInput = card.querySelector('[id^="ph-"]');
  return scoreInput?.id ? scoreInput.id.slice(3) : '';
}

function decorateMatchCardsWithLineups() {
  const container = document.getElementById('games');
  if (!container) return;
  container.querySelectorAll('article.card').forEach(card => {
    card.querySelectorAll('.match-lineups-inline').forEach(node => node.remove());
    const matchId = lineupMatchIdFromCard(card);
    if (!matchId) return;
    const state = matchLineupState.get(matchId);
    const match = matches.find(row => String(row.id) === String(matchId));
    if (!match || !state?.available) return;
    const wrapper = document.createElement('div');
    wrapper.className = 'match-lineups-inline';
    wrapper.innerHTML = matchLineupsDetailsHtml(match, state);
    const teams = card.querySelector('.teams-logo-grid') || card.querySelector('.teams');
    if (teams) teams.insertAdjacentElement('afterend', wrapper);
    else {
      const score = card.querySelector('.score-entry');
      if (score) score.insertAdjacentElement('beforebegin', wrapper);
      else card.appendChild(wrapper);
    }
  });
}

const __lineupBaseLiveGameHtml = (typeof liveGameHtml === 'function') ? liveGameHtml : null;
if (__lineupBaseLiveGameHtml) {
  liveGameHtml = function(match, state) {
    let html = __lineupBaseLiveGameHtml(match, state);
    const lineup = matchLineupState.get(match.id);
    if (!lineup?.available) return html;
    const block = matchLineupsDetailsHtml(match, lineup);
    const marker = '<div class="live-data-note">';
    if (html.includes(marker)) html = html.replace(marker, block + marker);
    else html += block;
    return html;
  };
}

async function refreshMatchLineups(force) {
  if (!currentUser || !currentPlayer || typeof sb === 'undefined') return;
  if (matchLineupPending) return matchLineupPending;
  const relevant = lineupRelevantMatches();
  if (!relevant.length) return;
  const now = Date.now();
  if (!force && now - matchLineupLastFetchAt < 45 * 1000) return;
  matchLineupLastFetchAt = now;
  matchLineupPending = (async () => {
    try {
      const result = await sb.functions.invoke('ucl-lineups', {
        body: { match_ids: relevant.map(match => match.id), force: !!force }
      });
      if (result.error || result.data?.ok === false) throw result.error || new Error(result.data?.error || 'Koosseisude laadimine ebaõnnestus');
      (result.data?.matches || []).forEach(row => {
        if (row?.match_id) matchLineupState.set(String(row.match_id), row);
      });
      decorateMatchCardsWithLineups();
      if (typeof renderLiveMatchCenter === 'function') renderLiveMatchCenter();
    } catch (error) {
      console.error('FotMob lineups error', error);
    } finally {
      matchLineupPending = null;
    }
  })();
  return matchLineupPending;
}

const __lineupBaseRenderGames = renderGames;
renderGames = function() {
  __lineupBaseRenderGames();
  decorateMatchCardsWithLineups();
};

const __lineupBaseLoadAll = loadAll;
loadAll = async function() {
  await __lineupBaseLoadAll();
  window.setTimeout(() => refreshMatchLineups(false), 80);
};

function ensureMatchLineupPolling() {
  if (matchLineupPollTimer) return;
  matchLineupPollTimer = window.setInterval(() => {
    if (currentUser && currentPlayer && document.visibilityState === 'visible') refreshMatchLineups(false);
  }, 60 * 1000);
}
ensureMatchLineupPolling();
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible' && currentUser && currentPlayer) refreshMatchLineups(true);
});
'''
    text = text.replace('\ninit();', js + '\n\ninit();', 1)

path.write_text(text, encoding='utf-8')
