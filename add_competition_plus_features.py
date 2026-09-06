from pathlib import Path

path = Path("index.html")
text = path.read_text(encoding="utf-8")

CSS_MARKER = "/* FUTBOL COMPETITION PLUS UX */"
JS_MARKER = "// FUTBOL COMPETITION PLUS UX"

# Give rendered match cards a stable match id for the final DOM decorators.
text = text.replace(
    "html += '<article class=\"card\">' +",
    "html += '<article class=\"card\" data-match-id=\"' + match.id + '\">' +"
)
text = text.replace(
    "html += '<article class=\"card\">';",
    "html += '<article class=\"card\" data-match-id=\"' + match.id + '\">';"
)

if CSS_MARKER not in text:
    css = r'''

    /* FUTBOL COMPETITION PLUS UX */
    #nav-admin { display: none !important; }
    .bottom-nav-inner { grid-template-columns: repeat(3, 1fr) !important; }

    .admin-access-btn {
      flex: 0 0 auto;
      width: 38px;
      height: 38px;
      padding: 0;
      border: 1px solid rgba(255,255,255,.22);
      border-radius: 50%;
      background: rgba(255,255,255,.09);
      color: white;
      font-size: 18px;
      font-weight: 900;
    }
    .admin-access-btn.verified {
      background: rgba(95, 125, 255, .28);
      border-color: rgba(255,255,255,.38);
    }

    .admin-player-note {
      margin-bottom: 12px;
      padding: 10px 12px;
      border: 1px solid #d7def6;
      border-radius: 12px;
      background: #f4f6ff;
      color: #344577;
      font-size: 12px;
      line-height: 1.45;
    }

    .round-filter-btn.knockout-round {
      border-color: #c8cff8;
      background: #f3f2ff;
      color: #40338d;
    }
    .round-filter-btn.knockout-round.active {
      background: #332777;
      color: white;
      border-color: #332777;
    }
    .round-filter-btn.final-round {
      border-color: #d5b96a;
      background: #fff9e9;
      color: #775b10;
    }
    .round-filter-btn.final-round.active {
      background: #806616;
      color: white;
      border-color: #806616;
    }

    .match-time-title {
      flex-wrap: wrap;
    }
    .match-time-status {
      flex: 0 0 auto;
      padding: 4px 8px;
      border-radius: 999px;
      background: #f5f7fb;
      color: #667087;
      font-size: 11px;
      font-weight: 850;
    }
    .match-time-status.done {
      background: #eaf7ef;
      color: #176b43;
    }
    .match-time-save-all {
      flex: 0 0 auto;
      min-height: 32px;
      padding: 0 10px;
      border: 0;
      border-radius: 9px;
      background: #243b83;
      color: white;
      font-size: 11px;
      font-weight: 900;
    }

    .crowd-stats {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 7px;
      margin: 10px 0;
    }
    .crowd-stat {
      padding: 8px 9px;
      border: 1px solid #e1e5f2;
      border-radius: 10px;
      background: #fafbff;
      color: #4e5870;
      font-size: 11px;
      line-height: 1.35;
    }
    .crowd-stat strong { color: #233a82; }

    .prediction-comparison {
      margin-top: 9px;
      border: 1px solid var(--border);
      border-radius: 12px;
      background: #fbfcfb;
      overflow: hidden;
    }
    .prediction-comparison summary {
      padding: 10px 12px;
      color: var(--text);
      font-size: 12px;
      font-weight: 900;
      cursor: pointer;
    }
    .prediction-comparison .prediction-list {
      margin: 0;
      padding: 0 12px 10px;
    }

    .leaderboard-toolbar {
      display: flex;
      align-items: end;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 10px;
    }
    .leaderboard-toolbar-title {
      color: var(--text);
      font-size: 13px;
      font-weight: 900;
    }
    .leaderboard-toolbar .input {
      width: auto;
      min-width: 145px;
      height: 40px;
      padding-right: 28px;
      font-size: 12px;
      font-weight: 800;
    }

    .round-summary-card {
      overflow: hidden;
      border-color: #cfd8f7;
      background: linear-gradient(145deg, #f7f8ff, #ffffff);
    }
    .round-summary-kicker {
      color: #4b55a6;
      font-size: 11px;
      font-weight: 950;
      letter-spacing: .7px;
      text-transform: uppercase;
    }
    .round-summary-title {
      margin-top: 4px;
      color: #182451;
      font-size: 19px;
      font-weight: 950;
    }
    .round-summary-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px;
      margin-top: 12px;
    }
    .round-summary-item {
      padding: 10px;
      border: 1px solid #e0e4f5;
      border-radius: 11px;
      background: rgba(255,255,255,.78);
    }
    .round-summary-label {
      color: #737b91;
      font-size: 10px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: .4px;
    }
    .round-summary-value {
      display: block;
      margin-top: 3px;
      color: #1d2f71;
      font-size: 14px;
      font-weight: 950;
    }

    .leaderboard-plus th { white-space: nowrap; }
    .leaderboard-plus .leader-player-meta {
      margin-top: 3px;
      color: var(--muted);
      font-size: 10px;
      font-weight: 650;
    }
    .round-points-cell {
      color: #324fb2;
      font-weight: 950;
    }
    .leader-total-cell {
      color: var(--text);
      font-size: 15px;
      font-weight: 950;
    }
    .rank-move {
      display: inline-block;
      min-width: 30px;
      text-align: center;
      font-size: 11px;
      font-weight: 950;
    }
    .rank-move.up { color: #157347; }
    .rank-move.down { color: #a33b3b; }
    .rank-move.same { color: #8a9290; }

    .push-reminder-card {
      margin-top: 14px;
      padding: 14px;
      border: 1px solid #d9e0f7;
      border-radius: 16px;
      background: #f8f9ff;
    }
    .push-reminder-title {
      color: #1c2e69;
      font-size: 14px;
      font-weight: 950;
    }
    .push-reminder-text {
      margin-top: 4px;
      color: #687188;
      font-size: 12px;
      line-height: 1.45;
    }
    .push-reminder-status {
      display: inline-block;
      margin-top: 9px;
      padding: 5px 9px;
      border-radius: 999px;
      background: #eaf7ef;
      color: #176b43;
      font-size: 11px;
      font-weight: 900;
    }

    @media (max-width: 520px) {
      .topbar-inner { gap: 9px; }
      .admin-access-btn { width: 34px; height: 34px; font-size: 16px; }
      .crowd-stats { grid-template-columns: 1fr; }
      .leaderboard-toolbar { align-items: stretch; flex-direction: column; }
      .leaderboard-toolbar .input { width: 100%; }
      .leaderboard-plus th:nth-child(5),
      .leaderboard-plus td:nth-child(5) { width: 42px; }
      .round-summary-grid { grid-template-columns: 1fr 1fr; }
    }
'''
    text = text.replace("  </style>", css + "\n  </style>", 1)

if JS_MARKER not in text:
    js = r'''

// FUTBOL COMPETITION PLUS UX
const FUTBOL_VAPID_PUBLIC = 'BJYpdEsob-TJHXH5cn27pxwAgHZRVKTetdZraQO5LVmcwQYUzkYR3bQ0wc57jxlxWajOTYfOfanDlWJmTI-cRzY';
let leaderboardRoundView = null;
let pushSubscriptionCheckedUser = null;

function competitionRoundTitle(number) {
  const n = Number(number);
  if (n >= 1 && n <= 8) return 'Liigafaas · ' + n + '. voor';
  if (n === 9) return 'Play-off · 1. mäng';
  if (n === 10) return 'Play-off · 2. mäng';
  if (n === 11) return '1/8-finaal · 1. mäng';
  if (n === 12) return '1/8-finaal · 2. mäng';
  if (n === 13) return 'Veerandfinaal · 1. mäng';
  if (n === 14) return 'Veerandfinaal · 2. mäng';
  if (n === 15) return 'Poolfinaal · 1. mäng';
  if (n === 16) return 'Poolfinaal · 2. mäng';
  if (n === 17) return 'Finaal';
  return n ? n + '. voor' : 'Voor määramata';
}

function competitionRoundShort(number) {
  const n = Number(number);
  if (n >= 1 && n <= 8) return n + '. voor';
  if (n === 9) return 'Play-off 1';
  if (n === 10) return 'Play-off 2';
  if (n === 11) return '1/8 · 1';
  if (n === 12) return '1/8 · 2';
  if (n === 13) return '1/4 · 1';
  if (n === 14) return '1/4 · 2';
  if (n === 15) return '1/2 · 1';
  if (n === 16) return '1/2 · 2';
  if (n === 17) return 'Finaal';
  return n + '. voor';
}

roundLabel = function(match) {
  const n = Number(match?.round_number);
  return n ? competitionRoundTitle(n) : (match?.round_name || 'Voor määramata');
};

uclRoundName = function(number) {
  return competitionRoundTitle(number);
};

roundSelectOptions = function(selected, includeBlank = false, rounds = null) {
  const available = Array.isArray(rounds) && rounds.length ? rounds : [1,2,3,4,5,6,7,8];
  let html = includeBlank ? '<option value="">Vali voor</option>' : '';
  available.forEach(n => {
    html += '<option value="' + n + '" ' + (Number(selected) === Number(n) ? 'selected' : '') + '>' + esc(competitionRoundTitle(n)) + '</option>';
  });
  return html;
};

roundFilterHtml = function(active, onclickName) {
  const rounds = availableRoundNumbers();
  let html = '<div class="round-filter-bar">';
  html += '<button class="round-filter-btn ' + (active === 'next' ? 'active' : '') + '" onclick="' + onclickName + '(\'next\')">Järgmine</button>';
  rounds.forEach(n => {
    const cls = n === 17 ? ' final-round' : (n > 8 ? ' knockout-round' : '');
    html += '<button class="round-filter-btn' + cls + ' ' + (String(active) === String(n) ? 'active' : '') + '" onclick="' + onclickName + '(\'' + n + '\')">' + esc(competitionRoundShort(n)) + '</button>';
  });
  html += '<button class="round-filter-btn ' + (active === 'all' ? 'active' : '') + '" onclick="' + onclickName + '(\'all\')">Kõik</button>';
  html += '</div>';
  return html;
};

function ensureAdminAccessUI() {
  const navAdmin = document.getElementById('nav-admin');
  if (navAdmin) navAdmin.style.display = 'none';
  const inner = document.querySelector('.bottom-nav-inner');
  if (inner) inner.style.gridTemplateColumns = 'repeat(3, 1fr)';

  const topbar = document.querySelector('.topbar-inner');
  if (topbar && !document.getElementById('adminAccessButton')) {
    const button = document.createElement('button');
    button.id = 'adminAccessButton';
    button.type = 'button';
    button.className = 'admin-access-btn' + (adminVerified ? ' verified' : '');
    button.title = 'Admin';
    button.setAttribute('aria-label', 'Admin');
    button.textContent = '⚙';
    button.onclick = () => showTab('admin');
    topbar.appendChild(button);
  } else if (document.getElementById('adminAccessButton')) {
    document.getElementById('adminAccessButton').classList.toggle('verified', !!adminVerified);
  }
}

function decorateAdminPlayerMode() {
  if (!adminVerified) return;
  const area = document.getElementById('adminArea');
  if (!area || area.querySelector('.admin-player-note')) return;
  area.insertAdjacentHTML('afterbegin',
    '<div class="admin-player-note"><strong>Admin on ka mängija.</strong> Ennustamiseks mine Mängud vaatesse. Admini õigused ei ava teiste skoore enne mängu algust; enne tähtaega näed ainult seda, kes on ennustanud.</div>'
  );
}

function matchCardsAfterTimeHeader(header) {
  const cards = [];
  let node = header.nextElementSibling;
  while (node) {
    if (node.classList.contains('match-time-title') || node.classList.contains('match-day-title') || node.classList.contains('match-group-title') || node.classList.contains('round-section-title')) break;
    if (node.tagName === 'ARTICLE' && node.classList.contains('card')) cards.push(node);
    node = node.nextElementSibling;
  }
  return cards;
}

async function savePredictionGroup(ids) {
  if (!currentUser || !Array.isArray(ids) || !ids.length) return;
  const rows = [];
  for (const matchId of ids) {
    const match = matches.find(m => m.id === matchId);
    if (!match || isStarted(match)) continue;
    const homeEl = document.getElementById('ph-' + matchId);
    const awayEl = document.getElementById('pa-' + matchId);
    if (!homeEl || !awayEl || homeEl.value === '' || awayEl.value === '') {
      toast('Sisesta enne kõik selle kellaaja skoorid.');
      return;
    }
    const home = Number(homeEl.value);
    const away = Number(awayEl.value);
    if (!Number.isInteger(home) || !Number.isInteger(away) || home < 0 || away < 0 || home > 30 || away > 30) {
      toast('Kontrolli skoorid üle. Lubatud on täisarv 0–30.');
      return;
    }
    rows.push({
      match_id: matchId,
      user_id: currentUser.id,
      home_score: home,
      away_score: away,
      updated_at: new Date().toISOString()
    });
  }
  if (!rows.length) return;
  const result = await sb.from('predictions').upsert(rows, { onConflict: 'match_id,user_id' });
  if (result.error) {
    toast(friendlyError(result.error));
    return;
  }
  toast(rows.length + ' ennustust salvestatud.');
  await loadAll();
}

function crowdStatsHtml(match, rows) {
  if (!rows.length) return '';
  let home = 0, draw = 0, away = 0;
  const scores = new Map();
  rows.forEach(p => {
    if (p.home_score > p.away_score) home += 1;
    else if (p.home_score < p.away_score) away += 1;
    else draw += 1;
    const key = p.home_score + ':' + p.away_score;
    scores.set(key, (scores.get(key) || 0) + 1);
  });
  const total = rows.length;
  const pct = value => Math.round((value / total) * 100);
  const popular = [...scores.entries()].sort((a,b) => b[1] - a[1] || a[0].localeCompare(b[0]))[0];
  return '<div class="crowd-stats">' +
    '<div class="crowd-stat"><strong>Ennustuste jaotus</strong><br>Koduvõit ' + pct(home) + '% · viik ' + pct(draw) + '% · võõrsil ' + pct(away) + '%</div>' +
    '<div class="crowd-stat"><strong>Populaarseim skoor</strong><br>' + esc(popular[0]) + ' · ' + popular[1] + ' ennustajat</div>' +
  '</div>';
}

function decorateGameCompetitionUX() {
  const container = document.getElementById('games');
  if (!container) return;

  container.querySelectorAll('article.card[data-match-id]').forEach(card => {
    const matchId = card.dataset.matchId;
    const match = matches.find(m => m.id === matchId);
    if (!match) return;

    if (Number(match.round_number) > 8) card.classList.add('knockout-match');
    if (Number(match.round_number) === 17) card.classList.add('final-match');

    if (!isStarted(match)) return;
    const visible = predictions
      .filter(p => p.match_id === matchId)
      .sort((a,b) => playerName(a.user_id).localeCompare(playerName(b.user_id), 'et'));

    const list = card.querySelector('.prediction-list');
    if (!list) return;
    if (!card.querySelector('.crowd-stats') && visible.length) {
      list.insertAdjacentHTML('beforebegin', crowdStatsHtml(match, visible));
    }
    if (!list.closest('.prediction-comparison')) {
      const details = document.createElement('details');
      details.className = 'prediction-comparison';
      const summary = document.createElement('summary');
      summary.textContent = 'Kõigi ennustused (' + visible.length + ')';
      list.parentNode.insertBefore(details, list);
      details.appendChild(summary);
      details.appendChild(list);
    }
  });

  container.querySelectorAll('.match-time-title').forEach(header => {
    const cards = matchCardsAfterTimeHeader(header);
    const ids = cards.map(card => card.dataset.matchId).filter(Boolean);
    const openIds = ids.filter(id => {
      const m = matches.find(x => x.id === id);
      return m && !isStarted(m);
    });
    const predicted = ids.filter(id => predictions.some(p => p.match_id === id && currentUser && p.user_id === currentUser.id)).length;

    if (!header.querySelector('.match-time-status')) {
      const status = document.createElement('span');
      status.className = 'match-time-status' + (ids.length && predicted === ids.length ? ' done' : '');
      status.textContent = openIds.length ? (predicted + '/' + ids.length + ' ennustatud') : 'Lukus';
      header.appendChild(status);
    }

    if (openIds.length > 1 && !header.querySelector('.match-time-save-all')) {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'match-time-save-all';
      button.textContent = 'Salvesta kõik';
      button.onclick = () => savePredictionGroup(openIds);
      header.appendChild(button);
    }
  });
}

function roundStatMap(roundNumber) {
  const matchRows = matches.filter(m => Number(m.round_number) === Number(roundNumber) && isFinished(m));
  const ids = new Set(matchRows.map(m => m.id));
  const map = new Map();
  predictions.filter(p => ids.has(p.match_id)).forEach(pred => {
    const match = matchRows.find(m => m.id === pred.match_id);
    if (!match) return;
    const pts = Number(calculatePoints(pred, match) || 0);
    const stat = map.get(pred.user_id) || { points: 0, exact: 0, predicted: 0 };
    stat.points += pts;
    stat.exact += pts === 3 ? 1 : 0;
    stat.predicted += 1;
    map.set(pred.user_id, stat);
  });
  return map;
}

function rankingThroughRound(roundNumber) {
  const maxRound = Number(roundNumber);
  const usable = matches.filter(m => isFinished(m) && Number(m.round_number) <= maxRound);
  const ids = new Set(usable.map(m => m.id));
  const stats = new Map(players.map(p => [p.id, { points: 0, exact: 0 }]));
  predictions.filter(p => ids.has(p.match_id)).forEach(pred => {
    const match = usable.find(m => m.id === pred.match_id);
    if (!match) return;
    const pts = Number(calculatePoints(pred, match) || 0);
    const stat = stats.get(pred.user_id) || { points: 0, exact: 0 };
    stat.points += pts;
    stat.exact += pts === 3 ? 1 : 0;
    stats.set(pred.user_id, stat);
  });
  const rows = players.map(p => ({
    id: p.id,
    name: p.display_name,
    points: (stats.get(p.id) || {}).points || 0,
    exact: (stats.get(p.id) || {}).exact || 0,
  })).sort((a,b) => b.points - a.points || b.exact - a.exact || a.name.localeCompare(b.name, 'et'));
  const rank = new Map();
  rows.forEach((row, index) => rank.set(row.id, index + 1));
  return rank;
}

function scoredRounds() {
  return [...new Set(matches.filter(isFinished).map(m => Number(m.round_number)).filter(n => Number.isInteger(n) && n > 0))].sort((a,b) => a-b);
}

function defaultLeaderboardRound() {
  const rounds = scoredRounds();
  if (leaderboardRoundView && rounds.includes(Number(leaderboardRoundView))) return Number(leaderboardRoundView);
  return rounds.length ? rounds[rounds.length - 1] : (focusRoundNumber() || 1);
}

function setLeaderboardRoundView(value) {
  leaderboardRoundView = Number(value) || null;
  renderLeaderboard();
}

function rankMoveHtml(playerId, roundNumber) {
  const n = Number(roundNumber);
  const currentRanks = rankingThroughRound(n);
  const previousRounds = scoredRounds().filter(r => r < n);
  if (!previousRounds.length) return '<span class="rank-move same">–</span>';
  const previousRanks = rankingThroughRound(previousRounds[previousRounds.length - 1]);
  const current = currentRanks.get(playerId);
  const previous = previousRanks.get(playerId);
  if (!current || !previous) return '<span class="rank-move same">–</span>';
  const diff = previous - current;
  if (diff > 0) return '<span class="rank-move up">↑' + diff + '</span>';
  if (diff < 0) return '<span class="rank-move down">↓' + Math.abs(diff) + '</span>';
  return '<span class="rank-move same">–</span>';
}

function roundSummaryHtml(roundNumber) {
  const n = Number(roundNumber);
  const roundMatches = matches.filter(m => Number(m.round_number) === n);
  if (!roundMatches.length || roundMatches.some(m => !isFinished(m))) return '';
  const stats = roundStatMap(n);
  const rows = players.map(p => {
    const s = stats.get(p.id) || { points: 0, exact: 0, predicted: 0 };
    return { id: p.id, name: p.display_name, ...s };
  }).filter(r => r.predicted > 0).sort((a,b) => b.points - a.points || b.exact - a.exact || a.name.localeCompare(b.name, 'et'));
  if (!rows.length) return '';

  const best = rows[0];
  const winners = rows.filter(r => r.points === best.points && r.exact === best.exact).map(r => r.name).join(' & ');
  const maxExact = Math.max(...rows.map(r => r.exact));
  const exactNames = maxExact > 0 ? rows.filter(r => r.exact === maxExact).map(r => r.name).join(' & ') : '–';
  const currentRanks = rankingThroughRound(n);
  const prevRounds = scoredRounds().filter(r => r < n);
  let climber = '–';
  if (prevRounds.length) {
    const prevRanks = rankingThroughRound(prevRounds[prevRounds.length - 1]);
    const moves = rows.map(r => ({ name: r.name, move: (prevRanks.get(r.id) || 0) - (currentRanks.get(r.id) || 0) })).sort((a,b) => b.move - a.move);
    if (moves.length && moves[0].move > 0) climber = moves[0].name + ' ↑' + moves[0].move;
  }
  const average = rows.reduce((sum,r) => sum + r.points, 0) / rows.length;

  return '<div class="card round-summary-card">' +
    '<div class="round-summary-kicker">Vooru kokkuvõte</div>' +
    '<div class="round-summary-title">' + esc(competitionRoundTitle(n)) + '</div>' +
    '<div class="round-summary-grid">' +
      '<div class="round-summary-item"><span class="round-summary-label">Vooru parim</span><span class="round-summary-value">' + esc(winners) + ' · ' + best.points + ' p</span></div>' +
      '<div class="round-summary-item"><span class="round-summary-label">Täpsed skoorid</span><span class="round-summary-value">' + esc(exactNames) + (maxExact ? ' · ' + maxExact : '') + '</span></div>' +
      '<div class="round-summary-item"><span class="round-summary-label">Suurim tõus</span><span class="round-summary-value">' + esc(climber) + '</span></div>' +
      '<div class="round-summary-item"><span class="round-summary-label">Keskmine</span><span class="round-summary-value">' + average.toFixed(1) + ' p</span></div>' +
    '</div>' +
  '</div>';
}

renderLeaderboard = function() {
  const container = document.getElementById('leaderboard');
  if (!container) return;
  if (!leaderboard.length) {
    container.innerHTML = '<div class="card"><div class="notice">Tabel on veel tühi.</div></div>';
    return;
  }

  const round = defaultLeaderboardRound();
  leaderboardRoundView = round;
  const rounds = scoredRounds();
  const roundStats = roundStatMap(round);
  let options = '';
  (rounds.length ? rounds : [round]).forEach(n => {
    options += '<option value="' + n + '" ' + (Number(n) === Number(round) ? 'selected' : '') + '>' + esc(competitionRoundTitle(n)) + '</option>';
  });

  let html = roundSummaryHtml(round) +
    '<div class="leaderboard-toolbar">' +
      '<div><div class="leaderboard-toolbar-title">Üldtabel</div><div class="hint" style="text-align:left;margin-top:2px">Vooru veergu saad allolevast valikust muuta.</div></div>' +
      '<select class="input" onchange="setLeaderboardRoundView(this.value)">' + options + '</select>' +
    '</div>' +
    '<div class="card table-wrap"><table class="leaderboard-plus"><thead><tr>' +
      '<th>Koht</th><th>Mängija</th><th class="num">Voor</th><th class="num">Kokku</th><th class="num">±</th>' +
    '</tr></thead><tbody>';

  leaderboard.forEach(row => {
    const rank = Number(row.rank_no);
    const medal = rank === 1 ? '🥇' : rank === 2 ? '🥈' : rank === 3 ? '🥉' : '';
    const isSelf = currentUser && row.player_id === currentUser.id;
    const rs = roundStats.get(row.player_id) || { points: 0, exact: 0, predicted: 0 };
    html += '<tr class="' + (isSelf ? 'leaderboard-self' : '') + '">' +
      '<td class="rank">' + (medal ? '<span class="rank-medal">' + medal + '</span>' : '') + row.rank_no + '</td>' +
      '<td><button class="player-name-btn" onclick="openPlayerStats(\'' + row.player_id + '\')">' + esc(row.player_name) + '</button>' +
        '<div class="leader-player-meta">' + Number(row.exact_scores || 0) + ' täpset · ' + Number(row.predictions_count || 0) + ' ennustust</div></td>' +
      '<td class="num round-points-cell">' + Number(rs.points || 0) + '</td>' +
      '<td class="num leader-total-cell">' + Number(row.total_points || 0) + '</td>' +
      '<td class="num">' + rankMoveHtml(row.player_id, round) + '</td>' +
    '</tr>';
  });
  container.innerHTML = html + '</tbody></table></div>';
};

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const raw = atob(base64);
  return Uint8Array.from([...raw].map(char => char.charCodeAt(0)));
}

function pushSupported() {
  return 'serviceWorker' in navigator && 'PushManager' in window && typeof Notification !== 'undefined';
}

async function storePushSubscription(subscription) {
  if (!currentUser || !subscription) return;
  const json = subscription.toJSON();
  const result = await sb.from('push_subscriptions').upsert({
    user_id: currentUser.id,
    endpoint: subscription.endpoint,
    p256dh: json.keys?.p256dh || '',
    auth: json.keys?.auth || '',
    updated_at: new Date().toISOString()
  }, { onConflict: 'endpoint' });
  if (result.error) throw result.error;
}

async function enablePredictionReminders() {
  if (!pushSupported()) {
    toast('See brauser ei toeta taustateavitusi.');
    return;
  }
  const permission = await Notification.requestPermission();
  if (permission !== 'granted') {
    renderPushReminderSettings();
    return;
  }
  try {
    const registration = await navigator.serviceWorker.ready;
    let subscription = await registration.pushManager.getSubscription();
    if (!subscription) {
      subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(FUTBOL_VAPID_PUBLIC)
      });
    }
    await storePushSubscription(subscription);
    pushSubscriptionCheckedUser = currentUser?.id || null;
    toast('Ennustuste meeldetuletused on sisse lülitatud.');
    renderPushReminderSettings();
  } catch (error) {
    toast('Teavituste sisselülitamine ebaõnnestus: ' + friendlyError(error));
  }
}

async function disablePredictionReminders() {
  if (!pushSupported()) return;
  try {
    const registration = await navigator.serviceWorker.ready;
    const subscription = await registration.pushManager.getSubscription();
    if (subscription) {
      await sb.from('push_subscriptions').delete().eq('endpoint', subscription.endpoint);
      await subscription.unsubscribe();
    }
    pushSubscriptionCheckedUser = null;
    toast('Ennustuste meeldetuletused on välja lülitatud.');
    renderPushReminderSettings();
  } catch (error) {
    toast(friendlyError(error));
  }
}

async function ensurePushSubscriptionSilent() {
  if (!currentUser || !pushSupported() || Notification.permission !== 'granted') return;
  if (pushSubscriptionCheckedUser === currentUser.id) return;
  try {
    const registration = await navigator.serviceWorker.ready;
    const subscription = await registration.pushManager.getSubscription();
    if (subscription) await storePushSubscription(subscription);
    pushSubscriptionCheckedUser = currentUser.id;
  } catch (_) {}
}

function renderPushReminderSettings() {
  const recovery = document.getElementById('recoverySettings');
  if (!recovery) return;
  let mount = document.getElementById('pushReminderSettings');
  if (!mount) {
    mount = document.createElement('div');
    mount.id = 'pushReminderSettings';
    recovery.insertAdjacentElement('afterend', mount);
  }

  if (!pushSupported()) {
    mount.innerHTML = '<div class="push-reminder-card"><div class="push-reminder-title">Ennustuste meeldetuletused</div><div class="push-reminder-text">Sinu brauser ei toeta praegu veebirakenduse taustateavitusi.</div></div>';
    return;
  }

  if (Notification.permission === 'granted') {
    mount.innerHTML = '<div class="push-reminder-card"><div class="push-reminder-title">Ennustuste meeldetuletused</div>' +
      '<div class="push-reminder-text">Kui sul on umbes tund enne valitud Champions League’i mängude algust mõni ennustus tegemata, saad seadmesse meeldetuletuse.</div>' +
      '<span class="push-reminder-status">Teavitused lubatud</span>' +
      '<div><button class="btn btn-secondary btn-small" style="margin-top:9px" type="button" onclick="disablePredictionReminders()">Lülita välja</button></div></div>';
  } else {
    const denied = Notification.permission === 'denied';
    mount.innerHTML = '<div class="push-reminder-card"><div class="push-reminder-title">Ennustuste meeldetuletused</div>' +
      '<div class="push-reminder-text">Luba teavitus, et Futbol tuletaks umbes tund enne mängude algust meelde, kui mõni ennustus on veel tegemata.' + (denied ? ' Brauseris on teavitused praegu blokeeritud; luba need esmalt selle lehe saidiseadetes.' : '') + '</div>' +
      (denied ? '' : '<button class="btn btn-secondary btn-small" style="margin-top:9px" type="button" onclick="enablePredictionReminders()">Luba meeldetuletused</button>') + '</div>';
  }
}

const __plusBaseRenderGames = renderGames;
renderGames = function() {
  __plusBaseRenderGames();
  decorateGameCompetitionUX();
  ensureAdminAccessUI();
};

const __plusBaseRenderAdmin = renderAdmin;
renderAdmin = function() {
  __plusBaseRenderAdmin();
  ensureAdminAccessUI();
  decorateAdminPlayerMode();
};

const __plusBaseRenderRecoverySettings = renderRecoverySettings;
renderRecoverySettings = function() {
  __plusBaseRenderRecoverySettings();
  renderPushReminderSettings();
  ensurePushSubscriptionSilent();
};

const __plusBaseAdminLogin = adminLogin;
adminLogin = async function() {
  await __plusBaseAdminLogin();
  ensureAdminAccessUI();
  decorateAdminPlayerMode();
};

const __plusBaseAdminLogout = adminLogout;
adminLogout = function() {
  __plusBaseAdminLogout();
  ensureAdminAccessUI();
};

ensureAdminAccessUI();
'''
    anchor = "\ninit();"
    pos = text.rfind(anchor)
    if pos == -1:
        raise SystemExit("init anchor not found")
    text = text[:pos] + js + text[pos:]

path.write_text(text, encoding="utf-8")
print("Added competition plus UX, leaderboard upgrades, admin privacy and push reminder UI")
