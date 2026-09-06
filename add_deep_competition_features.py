from pathlib import Path
import re

index_path = Path('index.html')
text = index_path.read_text(encoding='utf-8')
chat_path = Path('chat.js')
sw_path = Path('sw.js')

CSS_MARKER = '/* FUTBOL DEEP COMPETITION FEATURES */'
JS_MARKER = '// FUTBOL DEEP COMPETITION FEATURES'

# Favorite club must be available in the shared player list.
text = text.replace('.select("id,display_name");', '.select("id,display_name,favorite_team");')

# Explain the two mandatory season bonus questions in Rules.
if 'Hooaja boonusküsimused' not in text:
    rules = '''
      <div class="card">
        <h3>Hooaja boonusküsimused</h3>
        <ul class="rules-list">
          <li>Enne 1. vooru algust peab iga osaleja vastama <strong>kahele boonusküsimusele</strong>.</li>
          <li><strong>Champions League’i võitja</strong> õige ennustus annab hooaja lõpus <strong>10 punkti</strong>.</li>
          <li><strong>Champions League’i suurim väravakütt</strong> õige ennustus annab hooaja lõpus <strong>10 punkti</strong>.</li>
          <li>Boonusküsimustega on võimalik saada kokku kuni <strong>20 lisapunkti</strong> ning need lähevad üldtabeli kogusumma sisse.</li>
          <li>Vastuseid saab muuta kuni 1. vooru esimese valitud mängu alguseni. Seejärel lukustuvad mõlemad vastused automaatselt.</li>
          <li>Kui suurima väravaküti arvestuses jääb ametlikult esikohale mitu mängijat, saab admin märkida õigeks mitu nime ning kõik vastavad ennustused saavad 10 punkti.</li>
        </ul>
      </div>
'''
    text = text.replace('      <div id="paidRulesStatus"></div>', rules + '\n      <div id="paidRulesStatus"></div>', 1)

if CSS_MARKER not in text:
    css = r'''

    /* FUTBOL DEEP COMPETITION FEATURES */
    .prize-pool-card {
      overflow: hidden;
      border-color: #d9cfaa;
      background: linear-gradient(145deg, #fffdf6, #ffffff);
    }
    .prize-pool-top {
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      gap: 12px;
    }
    .prize-pool-kicker {
      color: #816617;
      font-size: 10px;
      font-weight: 950;
      letter-spacing: .8px;
      text-transform: uppercase;
    }
    .prize-pool-total {
      margin-top: 2px;
      color: #3d3212;
      font-size: 27px;
      line-height: 1;
      font-weight: 950;
    }
    .prize-paid-count {
      color: #77705d;
      font-size: 11px;
      font-weight: 800;
      text-align: right;
    }
    .prize-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 7px;
      margin-top: 12px;
    }
    .prize-box {
      padding: 9px 6px;
      border: 1px solid #eee5c8;
      border-radius: 11px;
      background: rgba(255,255,255,.8);
      text-align: center;
    }
    .prize-box strong { display:block; font-size:14px; color:#5e4a10; }
    .prize-box span { display:block; margin-top:2px; color:#8c8266; font-size:9px; font-weight:800; }
    .leader-prize-chip {
      display: inline-flex;
      margin: 3px 0 0 5px;
      padding: 2px 6px;
      border-radius: 999px;
      background: #fff4c9;
      color: #725809;
      font-size: 9px;
      font-weight: 950;
      vertical-align: 1px;
    }

    .bonus-card {
      border-color: #cbd5f4;
      background: linear-gradient(145deg, #f6f8ff, #ffffff);
    }
    .bonus-head {
      display:flex;
      justify-content:space-between;
      align-items:flex-start;
      gap:10px;
      margin-bottom:12px;
    }
    .bonus-title { color:#1d2f71; font-size:16px; font-weight:950; }
    .bonus-subtitle { margin-top:3px; color:#707992; font-size:11px; line-height:1.4; }
    .bonus-progress {
      flex:0 0 auto;
      padding:5px 8px;
      border-radius:999px;
      background:#fff0cf;
      color:#7b5710;
      font-size:10px;
      font-weight:950;
    }
    .bonus-progress.done { background:#dff3e6; color:#176b43; }
    .bonus-question { margin-top:10px; }
    .bonus-question label { display:flex; justify-content:space-between; gap:8px; margin-bottom:5px; font-size:12px; font-weight:900; }
    .bonus-points-pill { color:#334a9a; white-space:nowrap; }
    .bonus-deadline { margin-top:9px; color:#6f778a; font-size:10px; line-height:1.4; }
    .bonus-answer-status {
      display:grid;
      grid-template-columns:minmax(0,1fr) auto;
      gap:8px;
      align-items:center;
      padding:9px 0;
      border-top:1px solid #edf0f7;
      font-size:12px;
    }
    .bonus-answer-status:first-of-type { border-top:0; }
    .bonus-answer-points { font-weight:950; color:#263d83; }

    .favorite-card { margin-top:12px; }
    .favorite-row { display:grid; grid-template-columns:minmax(0,1fr) auto; gap:8px; align-items:center; margin-top:10px; }
    .favorite-team-icon {
      width:18px;
      height:18px;
      object-fit:contain;
      vertical-align:-4px;
      margin-left:5px;
    }
    .favorite-team-text { margin-left:5px; color:#6b7486; font-size:9px; font-weight:800; }

    .records-card { margin-top:12px; }
    .records-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px; margin-top:10px; }
    .record-box { padding:10px; border:1px solid #e3e7ef; border-radius:12px; background:#fafbfd; }
    .record-label { color:#7b8394; font-size:9px; font-weight:850; text-transform:uppercase; letter-spacing:.35px; }
    .record-value { margin-top:3px; color:#1c2d67; font-size:13px; font-weight:950; line-height:1.25; }
    .record-detail { margin-top:2px; color:#747d8f; font-size:10px; }

    .player-form-chart { margin:14px 0; }
    .player-form-row { display:grid; grid-template-columns:70px minmax(0,1fr) 34px; gap:8px; align-items:center; margin-top:6px; }
    .player-form-label { color:#616b7e; font-size:10px; font-weight:850; }
    .player-form-track { height:9px; overflow:hidden; border-radius:999px; background:#edf0f5; }
    .player-form-bar { height:100%; min-width:2px; border-radius:999px; background:#3553ae; }
    .player-form-points { color:#263d83; font-size:10px; font-weight:950; text-align:right; }

    .match-insight-shell { margin-top:10px; }
    .match-insight-btn { min-height:36px; padding:0 11px; border:1px solid #d8deee; border-radius:10px; background:#f7f8fc; color:#314475; font-size:11px; font-weight:900; }
    .match-insight-panel { margin-top:8px; padding:11px; border:1px solid #e1e5ef; border-radius:12px; background:#fafbfe; }
    .insight-team-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px; }
    .insight-team { padding:9px; border:1px solid #e5e8f1; border-radius:10px; background:white; }
    .insight-team-name { font-size:12px; font-weight:950; }
    .insight-stats { margin-top:5px; color:#687187; font-size:10px; line-height:1.45; }
    .form-pills { display:flex; flex-wrap:wrap; gap:4px; margin-top:7px; }
    .form-pill { width:22px; height:22px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; font-size:9px; font-weight:950; background:#edf0f5; color:#6d7584; }
    .form-pill.w { background:#dff3e6; color:#176b43; }
    .form-pill.d { background:#fff0cf; color:#7b5710; }
    .form-pill.l { background:#fde4e4; color:#9c2d2d; }
    .h2h-list { margin-top:10px; padding-top:9px; border-top:1px solid #e5e8f1; }
    .h2h-row { display:flex; justify-content:space-between; gap:8px; padding:4px 0; color:#596276; font-size:10px; }
    .insight-note { margin-top:8px; color:#8990a0; font-size:9px; line-height:1.4; }

    .round-report-card { border-color:#cfd9f5; background:linear-gradient(145deg,#f4f7ff,#fff); }
    .round-report-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:7px; margin-top:10px; }
    .round-report-stat { padding:8px; border:1px solid #e0e5f4; border-radius:10px; background:white; text-align:center; }
    .round-report-stat strong { display:block; color:#253d87; font-size:15px; }
    .round-report-stat span { display:block; margin-top:2px; color:#7b8397; font-size:9px; font-weight:800; }
    .round-report-modal-card { width:min(500px,100%); max-height:82vh; overflow:auto; padding:20px; border-radius:20px; background:white; box-shadow:0 18px 55px rgba(0,0,0,.28); }

    .admin-deep-card { border-color:#dce2f1; }
    .admin-answer-list { margin-top:7px; color:#737c8d; font-size:10px; line-height:1.45; }
    .admin-chat-row { padding:8px 0; border-top:1px solid #edf0f5; }
    .admin-chat-row:first-child { border-top:0; }
    .admin-chat-meta { color:#7b8395; font-size:9px; }
    .admin-chat-text { margin-top:3px; font-size:11px; line-height:1.35; }
    .admin-chat-actions { display:flex; flex-wrap:wrap; gap:5px; margin-top:6px; }

    .chat-message.announcement { align-self:stretch; max-width:100%; }
    .chat-message.announcement .chat-bubble { border-color:#d9c77f; background:#fff9df; color:#4d3d0c; }
    .chat-message.announcement.own .chat-bubble { border-color:#d9c77f; background:#fff9df; color:#4d3d0c; }
    .chat-pin-label { margin-left:5px; color:#8a6b0f; font-size:9px; font-weight:950; }
    .chat-admin-delete { margin-left:6px; border:0; background:transparent; color:#9b4141; font-size:9px; font-weight:850; cursor:pointer; }
    .chat-favorite-icon { width:14px; height:14px; object-fit:contain; vertical-align:-3px; margin-left:4px; }

    .bonus-history-cell { color:#8a6410; font-weight:950; background:#fffaf0; }

    @media (max-width:520px) {
      .prize-grid { grid-template-columns:repeat(3,1fr); }
      .records-grid { grid-template-columns:1fr; }
      .insight-team-grid { grid-template-columns:1fr; }
      .round-report-grid { grid-template-columns:repeat(3,1fr); }
      .favorite-row { grid-template-columns:1fr; }
    }
'''
    text = text.replace('  </style>', css + '\n  </style>', 1)

if JS_MARKER not in text:
    js = r'''

// FUTBOL DEEP COMPETITION FEATURES
let prizePoolInfo = null;
let bonusQuestionsState = [];
let bonusScoreRows = [];
let uclTeamOptionsState = [];
let competitionRecordsState = null;
let latestRoundReportState = null;
let adminBonusState = [];
let adminChatRowsState = [];
let matchInsightsCache = new Map();
let deepAdminLoading = false;

function euroText(value) {
  const n = Number(value || 0);
  return (Number.isInteger(n) ? String(n) : n.toFixed(2).replace('.', ',')) + ' €';
}

function bonusScoreMap() {
  return new Map((bonusScoreRows || []).map(row => [row.player_id, Number(row.bonus_points || 0)]));
}

function playerByIdDeep(playerId) {
  return (players || []).find(p => p.id === playerId) || null;
}

function teamLogoUrlDeep(teamName) {
  const row = (uclTeamOptionsState || []).find(t => String(t.team_name || '').toLowerCase() === String(teamName || '').toLowerCase());
  return row?.logo_url || '';
}

function favoriteClubMini(playerId) {
  const player = playerByIdDeep(playerId);
  const team = player?.favorite_team;
  if (!team) return '';
  const logo = teamLogoUrlDeep(team);
  return logo
    ? '<img class="favorite-team-icon" src="' + esc(logo) + '" alt="" title="' + esc(team) + '">'
    : '<span class="favorite-team-text" title="Lemmikklubi">' + esc(team) + '</span>';
}

function chatFavoriteMini(playerId) {
  const player = playerByIdDeep(playerId);
  const team = player?.favorite_team;
  if (!team) return '';
  const logo = teamLogoUrlDeep(team);
  return logo
    ? '<img class="chat-favorite-icon" src="' + esc(logo) + '" alt="" title="' + esc(team) + '">'
    : '';
}

async function loadDeepCompetitionData() {
  if (!currentUser || !currentPlayer) return;

  const [prize, bonus, scores, teams, records] = await Promise.all([
    sb.rpc('get_prize_pool'),
    sb.rpc('get_bonus_questions'),
    sb.rpc('get_bonus_scores'),
    sb.rpc('get_ucl_team_options'),
    sb.rpc('get_competition_records')
  ]);

  if (!prize.error) prizePoolInfo = Array.isArray(prize.data) ? (prize.data[0] || null) : prize.data;
  if (!bonus.error) bonusQuestionsState = bonus.data || [];
  if (!scores.error) bonusScoreRows = scores.data || [];
  if (!teams.error) uclTeamOptionsState = teams.data || [];
  if (!records.error) competitionRecordsState = records.data || null;

  const playerRefresh = await sb.from('players').select('id,display_name,favorite_team');
  if (!playerRefresh.error) players = playerRefresh.data || players;

  await loadLatestRoundReportDeep();
}

function completedRoundNumbersDeep() {
  const rounds = [...new Set((matches || []).map(m => Number(m.round_number)).filter(Boolean))];
  return rounds.filter(n => {
    const rows = matches.filter(m => Number(m.round_number) === n);
    return rows.length > 0 && rows.every(m => isFinished(m));
  }).sort((a,b) => a-b);
}

async function loadLatestRoundReportDeep() {
  const rounds = completedRoundNumbersDeep();
  if (!rounds.length) {
    latestRoundReportState = null;
    return;
  }
  const round = rounds[rounds.length - 1];
  const result = await sb.rpc('get_my_round_report', { p_round_number: round });
  latestRoundReportState = result.error ? null : (result.data || null);
}

function prizePoolCardHtmlDeep() {
  if (!prizePoolInfo) return '';
  return '<div class="card prize-pool-card" id="deepPrizePool">' +
    '<div class="prize-pool-top"><div><div class="prize-pool-kicker">Auhinnafond</div><div class="prize-pool-total">' + euroText(prizePoolInfo.total_amount) + '</div></div>' +
    '<div class="prize-paid-count">' + Number(prizePoolInfo.paid_count || 0) + ' / ' + Number(prizePoolInfo.total_players || 0) + ' osalejat tasunud</div></div>' +
    '<div class="prize-grid">' +
      '<div class="prize-box"><strong>' + euroText(prizePoolInfo.first_prize) + '</strong><span>🥇 1. koht · 50%</span></div>' +
      '<div class="prize-box"><strong>' + euroText(prizePoolInfo.second_prize) + '</strong><span>🥈 2. koht · 30%</span></div>' +
      '<div class="prize-box"><strong>' + euroText(prizePoolInfo.third_prize) + '</strong><span>🥉 3. koht · 20%</span></div>' +
    '</div></div>';
}

function bonusCompleteDeep() {
  const active = bonusQuestionsState || [];
  return active.length > 0 && active.every(q => String(q.my_answer || '').trim());
}

function bonusHomeCardHtmlDeep() {
  if (!bonusQuestionsState.length) return '';
  const locked = bonusQuestionsState.some(q => q.is_locked);
  if (locked) return '';

  const answered = bonusQuestionsState.filter(q => String(q.my_answer || '').trim()).length;
  const winner = bonusQuestionsState.find(q => q.question_key === 'ucl_winner');
  const scorer = bonusQuestionsState.find(q => q.question_key === 'top_scorer');
  const deadline = bonusQuestionsState[0]?.deadline;

  let winnerOptions = '<option value="">Vali meeskond</option>';
  (uclTeamOptionsState || []).forEach(row => {
    const selected = String(winner?.my_answer || '').toLowerCase() === String(row.team_name || '').toLowerCase();
    winnerOptions += '<option value="' + esc(row.team_name) + '" ' + (selected ? 'selected' : '') + '>' + esc(row.team_name) + '</option>';
  });

  return '<div class="card bonus-card" id="deepBonusHome">' +
    '<div class="bonus-head"><div><div class="bonus-title">Boonusennustused enne 1. vooru</div>' +
    '<div class="bonus-subtitle">Mõlemale küsimusele peab vastama enne esimese vooru algust. Õige vastus annab 10 punkti.</div></div>' +
    '<span class="bonus-progress ' + (answered === bonusQuestionsState.length ? 'done' : '') + '">' + answered + '/' + bonusQuestionsState.length + ' vastatud</span></div>' +
    '<div class="bonus-question"><label><span>Champions League’i võitja</span><span class="bonus-points-pill">+10 p</span></label>' +
      '<select id="bonus-ucl_winner" class="input">' + winnerOptions + '</select></div>' +
    '<div class="bonus-question"><label><span>Suurim väravakütt</span><span class="bonus-points-pill">+10 p</span></label>' +
      '<input id="bonus-top_scorer" class="input" maxlength="120" autocomplete="off" placeholder="Näiteks Kylian Mbappé" value="' + esc(scorer?.my_answer || '') + '"></div>' +
    '<button class="btn btn-block" type="button" onclick="saveBonusPredictionsDeep()">' + (answered === bonusQuestionsState.length ? 'Uuenda boonuse vastuseid' : 'Salvesta mõlemad vastused') + '</button>' +
    '<div class="bonus-deadline">' + (deadline ? 'Vastused lukustuvad ' + formatDate(deadline) + ' kell ' + formatTime(deadline) + '.' : 'Lukustusaeg tekib automaatselt, kui 1. vooru mängud on avaldatud.') + '</div>' +
  '</div>';
}

async function saveBonusPredictionsDeep() {
  const winner = String(document.getElementById('bonus-ucl_winner')?.value || '').trim();
  const scorer = String(document.getElementById('bonus-top_scorer')?.value || '').trim();
  if (!winner || !scorer) {
    toast('Vasta mõlemale boonusküsimusele.');
    return;
  }
  const rows = [
    { question_key:'ucl_winner', player_id:ownPlayerId(), answer_text:winner },
    { question_key:'top_scorer', player_id:ownPlayerId(), answer_text:scorer }
  ];
  const result = await sb.from('bonus_predictions').upsert(rows, { onConflict:'question_key,player_id' });
  if (result.error) {
    toast(friendlyError(result.error));
    return;
  }
  toast('Boonusennustused salvestatud.');
  await loadAll();
}

function bonusRulesStatusHtmlDeep() {
  if (!bonusQuestionsState.length) return '';
  const locked = bonusQuestionsState.some(q => q.is_locked);
  if (!locked && !bonusCompleteDeep()) return '';
  let rows = '';
  bonusQuestionsState.forEach(q => {
    const result = q.is_resolved
      ? ('Õige: ' + esc(q.correct_answer || '–'))
      : (locked ? 'Vastus lukus' : 'Salvestatud');
    rows += '<div class="bonus-answer-status"><div><strong>' + esc(q.title) + '</strong><div class="hint" style="text-align:left;margin-top:2px">Sinu vastus: ' + esc(q.my_answer || '–') + ' · ' + result + '</div></div>' +
      '<div class="bonus-answer-points">' + (q.is_resolved ? ('+' + Number(q.my_points || 0) + ' p') : '+10 p') + '</div></div>';
  });
  return '<div class="recovery-card bonus-card"><div class="recovery-card-title">Minu hooaja boonused</div>' + rows + '</div>';
}

function favoriteSettingsHtmlDeep() {
  const own = playerByIdDeep(ownPlayerId());
  let options = '<option value="">Lemmikklubi valimata</option>';
  (uclTeamOptionsState || []).forEach(row => {
    const selected = String(own?.favorite_team || '').toLowerCase() === String(row.team_name || '').toLowerCase();
    options += '<option value="' + esc(row.team_name) + '" ' + (selected ? 'selected' : '') + '>' + esc(row.team_name) + '</option>';
  });
  return '<div class="recovery-card favorite-card"><div class="recovery-card-title">Minu lemmikklubi</div>' +
    '<div class="recovery-card-text">Lemmikklubi kuvatakse sinu profiilis, tabelis ja chatis. See ei mõjuta punktiarvestust.</div>' +
    '<div class="favorite-row"><select id="favoriteTeamSelect" class="input">' + options + '</select>' +
    '<button class="btn btn-secondary btn-small" type="button" onclick="saveFavoriteTeamDeep()">Salvesta</button></div></div>';
}

async function saveFavoriteTeamDeep() {
  const team = String(document.getElementById('favoriteTeamSelect')?.value || '').trim();
  const result = await sb.rpc('set_favorite_team', { p_team: team || null });
  if (result.error) {
    toast(friendlyError(result.error));
    return;
  }
  toast(team ? 'Lemmikklubi salvestatud.' : 'Lemmikklubi eemaldatud.');
  await loadAll();
}

function roundReportCardHtmlDeep() {
  const r = latestRoundReportState;
  if (!r) return '';
  const move = Number(r.rank_change || 0);
  const rankText = r.rank_after ? String(r.rank_after) + '. koht' : '–';
  const moveText = move > 0 ? '↑ ' + move : (move < 0 ? '↓ ' + Math.abs(move) : '–');
  return '<div class="card round-report-card" id="deepRoundReport"><div class="round-summary-kicker">Viimase vooru raport</div>' +
    '<div class="round-summary-title">' + esc(r.round_name || (r.round_number + '. voor')) + '</div>' +
    '<div class="round-report-grid">' +
      '<div class="round-report-stat"><strong>' + Number(r.points || 0) + ' p</strong><span>Vooru punktid</span></div>' +
      '<div class="round-report-stat"><strong>' + Number(r.exact_scores || 0) + '</strong><span>Täpsed skoorid</span></div>' +
      '<div class="round-report-stat"><strong>' + esc(rankText) + '</strong><span>Tabelis · ' + esc(moveText) + '</span></div>' +
    '</div>' +
    '<div class="hint" style="text-align:left;margin-top:9px">Vooru parim: <strong>' + esc(r.round_winner || '–') + '</strong>' + (r.round_winner_points != null ? ' · ' + Number(r.round_winner_points) + ' p' : '') + '</div></div>';
}

function recordsCardHtmlDeep() {
  const r = competitionRecordsState;
  if (!r || !Object.values(r).some(Boolean)) return '';
  const item = (label, data, suffix='', detail='') => {
    if (!data) return '';
    return '<div class="record-box"><div class="record-label">' + esc(label) + '</div><div class="record-value">' + esc(data.player_name || '–') + '</div><div class="record-detail">' + esc(String(data.value ?? 0) + suffix + (detail ? ' · ' + detail : '')) + '</div></div>';
  };
  return '<div class="card records-card"><h3>Hooaja rekordid</h3><div class="records-grid">' +
    item('Enim täpseid skoore', r.most_exact, ' täpset') +
    item('Parim voor', r.best_round, ' p', r.best_round?.round_number ? competitionRoundShort(r.best_round.round_number) : '') +
    item('Parim täpsus', r.best_accuracy, '%') +
    item('Pikim punktiseeria', r.longest_streak, ' mängu') +
    item('Suurim tõus', r.biggest_rise, ' kohta', r.biggest_rise?.round_number ? competitionRoundShort(r.biggest_rise.round_number) : '') +
  '</div></div>';
}

const __deepBaseRenderPlayerSummary = renderPlayerSummary;
renderPlayerSummary = function() {
  __deepBaseRenderPlayerSummary();
  const container = document.getElementById('playerSummary');
  if (!container) return;
  container.querySelectorAll('#deepPrizePool,#deepBonusHome,#deepRoundReport').forEach(el => el.remove());
  const anchor = container.querySelector('.player-summary');
  if (!anchor) return;
  anchor.insertAdjacentHTML('afterend', prizePoolCardHtmlDeep() + bonusHomeCardHtmlDeep() + roundReportCardHtmlDeep());
};

const __deepBaseRenderRecoverySettings = renderRecoverySettings;
renderRecoverySettings = function() {
  __deepBaseRenderRecoverySettings();
  const container = document.getElementById('recoverySettings');
  if (!container) return;
  container.insertAdjacentHTML('beforeend', bonusRulesStatusHtmlDeep() + favoriteSettingsHtmlDeep());
};

function prizeForRankDeep(rank) {
  if (!prizePoolInfo) return null;
  if (Number(rank) === 1) return prizePoolInfo.first_prize;
  if (Number(rank) === 2) return prizePoolInfo.second_prize;
  if (Number(rank) === 3) return prizePoolInfo.third_prize;
  return null;
}

renderLeaderboard = function() {
  const container = document.getElementById('leaderboard');
  if (!container) return;
  if (!leaderboard.length) {
    container.innerHTML = '<div class="card"><div class="notice">Ametlik tabel on veel tühi. Tabelisse jõuavad makse kinnitanud osalejad.</div></div>';
    return;
  }

  const rounds = typeof leaderboardVisibleRounds === 'function' ? leaderboardVisibleRounds() : [];
  const latestRound = rounds.length ? rounds[rounds.length - 1] : null;
  const roundMaps = new Map(rounds.map(n => [n, roundStatMap(n)]));
  const bonusMap = bonusScoreMap();
  const showBonus = bonusQuestionsState.some(q => q.is_resolved);
  const leaderPoints = Math.max(...leaderboard.map(item => Number(item.total_points || 0)));

  let html = (latestRound ? roundSummaryHtml(latestRound) : '') +
    '<div class="leaderboard-toolbar"><div><div class="leaderboard-toolbar-title">Üldtabel</div>' +
    '<div class="leaderboard-table-note">Voorude punktid täienevad jooksvalt. Hooaja lõpus lisanduvad õigete boonusküsimuste punktid kogusummale.</div></div></div>' +
    '<div class="card table-wrap"><table class="leaderboard-plus leaderboard-dynamic"><thead><tr><th>Koht</th><th>Mängija</th>';

  rounds.forEach(n => {
    html += '<th class="num round-history-head ' + (n === latestRound ? 'latest' : '') + '">' + esc(competitionRoundShort(n)) + '</th>';
  });
  if (showBonus) html += '<th class="num">Boonus</th>';
  html += '<th class="num">Kokku</th><th class="num">Liidrist</th><th class="num">±</th></tr></thead><tbody>';

  leaderboard.forEach(row => {
    const rank = Number(row.rank_no);
    const medal = rank === 1 ? '🥇' : rank === 2 ? '🥈' : rank === 3 ? '🥉' : '';
    const isSelf = row.player_id === ownPlayerId();
    const total = Number(row.total_points || 0);
    const gap = Math.max(0, leaderPoints-total);
    const prize = prizeForRankDeep(rank);
    html += '<tr class="' + (isSelf ? 'leaderboard-self' : '') + '"><td class="rank">' + (medal ? '<span class="rank-medal">'+medal+'</span>' : '') + row.rank_no + '</td>' +
      '<td><button class="player-name-btn" onclick="openPlayerStats(\''+row.player_id+'\')">'+esc(row.player_name)+'</button>' + favoriteClubMini(row.player_id) +
      (prize != null ? '<span class="leader-prize-chip">' + euroText(prize) + '</span>' : '') +
      '<div class="leader-player-meta">'+Number(row.exact_scores||0)+' täpset · '+Number(row.predictions_count||0)+' ennustust</div></td>';
    rounds.forEach(n => {
      const stat = roundMaps.get(n)?.get(row.player_id) || {points:0};
      html += '<td class="num round-history-cell ' + (n===latestRound?'latest':'') + '">'+Number(stat.points||0)+'</td>';
    });
    if (showBonus) html += '<td class="num bonus-history-cell">'+Number(bonusMap.get(row.player_id)||0)+'</td>';
    html += '<td class="num leader-total-cell">'+total+'</td><td class="num leader-gap-cell">'+(gap===0?'–':'−'+gap)+'</td>' +
      '<td class="num">'+(latestRound ? rankMoveHtml(row.player_id,latestRound) : '<span class="rank-move same">–</span>')+'</td></tr>';
  });
  container.innerHTML = html + '</tbody></table></div>' + recordsCardHtmlDeep();
};

openPlayerStats = function(playerId) {
  const player = playerByIdDeep(playerId);
  const boardRow = leaderboard.find(row => row.player_id === playerId);
  const name = player?.display_name || boardRow?.player_name || 'Mängija';
  const rows = predictions.filter(p => p.user_id === playerId).map(p => ({prediction:p,match:matches.find(m=>m.id===p.match_id)}))
    .filter(x => x.match && isFinished(x.match)).sort((a,b)=>new Date(b.match.kickoff_at)-new Date(a.match.kickoff_at));
  let matchPoints=0, exact=0, correct=0, wrong=0;
  rows.forEach(x => { const pts=Number(calculatePoints(x.prediction,x.match)||0); matchPoints+=pts; if(pts===3) exact++; else if(pts===1) correct++; else wrong++; });
  const avg = rows.length ? (matchPoints/rows.length).toFixed(2).replace('.',',') : '0,00';
  const accuracy = rows.length ? Math.round(100*(exact+correct)/rows.length) : 0;
  const bonus = Number(bonusScoreMap().get(playerId)||0);
  const total = Number(boardRow?.total_points ?? (matchPoints+bonus));
  const rounds = typeof scoredRounds === 'function' ? scoredRounds() : [];
  const series = rounds.map(n => ({n,points:Number(roundStatMap(n).get(playerId)?.points||0)}));
  const maxRound = Math.max(1,...series.map(x=>x.points));
  const bestRound = series.reduce((best,x)=>x.points>(best?.points??-1)?x:best,null);
  let formHtml = '';
  series.forEach(x => { formHtml += '<div class="player-form-row"><div class="player-form-label">'+esc(competitionRoundShort(x.n))+'</div><div class="player-form-track"><div class="player-form-bar" style="width:'+Math.max(2,Math.round(100*x.points/maxRound))+'%"></div></div><div class="player-form-points">'+x.points+' p</div></div>'; });

  const finishedAsc = matches.filter(isFinished).sort((a,b)=>new Date(a.kickoff_at)-new Date(b.kickoff_at));
  let currentStreak=0;
  finishedAsc.forEach(m => {
    const p = predictions.find(x=>x.user_id===playerId && x.match_id===m.id);
    const pts = p ? Number(calculatePoints(p,m)||0) : 0;
    currentStreak = pts>0 ? currentStreak+1 : 0;
  });

  let recent='';
  rows.slice(0,5).forEach(x => {
    const pts=Number(calculatePoints(x.prediction,x.match)||0);
    recent += '<div class="recent-stat-row"><div><strong>'+esc(x.match.home_team)+' – '+esc(x.match.away_team)+'</strong><div class="match-date">'+formatDate(x.match.kickoff_at)+'</div></div><div class="recent-stat-score">'+x.prediction.home_score+' : '+x.prediction.away_score+' · +'+pts+' p</div></div>';
  });

  const fav = player?.favorite_team;
  const content=document.getElementById('statsContent');
  content.innerHTML = '<h2 style="padding-right:42px">'+esc(name)+favoriteClubMini(playerId)+'</h2>' +
    (fav ? '<div class="hint" style="text-align:left;margin-top:-8px;margin-bottom:10px">Lemmikklubi: <strong>'+esc(fav)+'</strong></div>' : '') +
    '<div class="stats-grid">' +
      '<div class="stats-box"><span class="stats-value">'+total+'</span><span class="stats-label">Punktid kokku</span></div>' +
      '<div class="stats-box"><span class="stats-value">'+(boardRow?.rank_no||'–')+'</span><span class="stats-label">Koht tabelis</span></div>' +
      '<div class="stats-box"><span class="stats-value">'+exact+'</span><span class="stats-label">Täpsed skoorid</span></div>' +
      '<div class="stats-box"><span class="stats-value">'+accuracy+'%</span><span class="stats-label">Punktiga ennustusi</span></div>' +
      '<div class="stats-box"><span class="stats-value">'+avg+'</span><span class="stats-label">Punkti / mäng</span></div>' +
      '<div class="stats-box"><span class="stats-value">'+currentStreak+'</span><span class="stats-label">Hetke punktiseeria</span></div>' +
      '<div class="stats-box"><span class="stats-value">'+(bestRound?.points||0)+'</span><span class="stats-label">Parim voor</span></div>' +
      '<div class="stats-box"><span class="stats-value">'+bonus+'</span><span class="stats-label">Boonuspunktid</span></div>' +
    '</div>' +
    (series.length ? '<h3>Vorm voorude kaupa</h3><div class="player-form-chart">'+formHtml+'</div>' : '') +
    (recent ? '<h3>Viimased mängud</h3>'+recent : '<div class="notice">Lõppenud mängude statistikat veel pole.</div>');
  document.getElementById('statsModal').classList.remove('hidden');
};

function decorateMatchInsightsDeep() {
  document.querySelectorAll('#games article[data-match-id]').forEach(card => {
    if (card.querySelector('.match-insight-shell')) return;
    const id=card.dataset.matchId;
    const teams=card.querySelector('.teams');
    if (!id || !teams) return;
    teams.insertAdjacentHTML('afterend','<div class="match-insight-shell"><button class="match-insight-btn" type="button" onclick="toggleMatchInsightsDeep(\''+id+'\')">Statistika</button><div id="insight-'+id+'" class="match-insight-panel hidden"></div></div>');
  });
}

function formPillsDeep(form) {
  if (!Array.isArray(form) || !form.length) return '<div class="insight-stats">Varasemaid CL tulemusi pole.</div>';
  return '<div class="form-pills">'+form.map(x=>'<span class="form-pill '+String(x.result||'').toLowerCase()+'" title="'+esc(x.opponent||'')+' '+Number(x.gf||0)+':'+Number(x.ga||0)+'">'+esc(x.result||'–')+'</span>').join('')+'</div>';
}

function insightTeamDeep(team, stats, form) {
  return '<div class="insight-team"><div class="insight-team-name">'+esc(team)+'</div>' + formPillsDeep(form) +
    '<div class="insight-stats">Mänge '+Number(stats?.played||0)+' · V '+Number(stats?.wins||0)+' · Vi '+Number(stats?.draws||0)+' · K '+Number(stats?.losses||0)+'<br>Väravad '+Number(stats?.gf||0)+':'+Number(stats?.ga||0)+'</div></div>';
}

function renderMatchInsightsDeep(data) {
  let h2h='';
  if (Array.isArray(data?.h2h) && data.h2h.length) {
    h2h='<div class="h2h-list"><strong style="font-size:10px">Omavahelised CL mängud sel hooajal</strong>' + data.h2h.map(x=>'<div class="h2h-row"><span>'+esc(x.home_team)+' – '+esc(x.away_team)+'</span><strong>'+Number(x.home_score||0)+' : '+Number(x.away_score||0)+'</strong></div>').join('')+'</div>';
  }
  return '<div class="insight-team-grid">'+insightTeamDeep(data.home_team,data.home_stats,data.home_form)+insightTeamDeep(data.away_team,data.away_stats,data.away_form)+'</div>'+h2h+
    '<div class="insight-note">Statistika põhineb Futboli Champions League 2026/27 andmebaasis enne seda mängu olnud tulemustel.</div>';
}

async function toggleMatchInsightsDeep(matchId) {
  const mount=document.getElementById('insight-'+matchId);
  if (!mount) return;
  const opening=mount.classList.contains('hidden');
  mount.classList.toggle('hidden');
  if (!opening) return;
  if (matchInsightsCache.has(matchId)) {
    mount.innerHTML=renderMatchInsightsDeep(matchInsightsCache.get(matchId));
    return;
  }
  mount.innerHTML='<div class="hint">Laen statistikat…</div>';
  const result=await sb.rpc('get_match_insights',{p_match_id:matchId});
  if (result.error) {
    mount.innerHTML='<div class="hint">Statistika laadimine ebaõnnestus.</div>';
    return;
  }
  matchInsightsCache.set(matchId,result.data||{});
  mount.innerHTML=renderMatchInsightsDeep(result.data||{});
}

const __deepBaseRenderGames = renderGames;
renderGames = function() {
  __deepBaseRenderGames();
  decorateMatchInsightsDeep();
};

const __deepBaseSavePrediction = savePrediction;
savePrediction = async function(matchId) {
  const match=matches.find(m=>m.id===matchId);
  if (match && Number(match.round_number)===1 && bonusQuestionsState.length && !bonusQuestionsState.some(q=>q.is_locked) && !bonusCompleteDeep()) {
    toast('Vasta enne 1. vooru mõlemale boonusküsimusele.');
    document.getElementById('deepBonusHome')?.scrollIntoView({behavior:'smooth',block:'center'});
    return;
  }
  return __deepBaseSavePrediction(matchId);
};

if (typeof savePredictionGroup === 'function') {
  const __deepBaseSavePredictionGroup = savePredictionGroup;
  savePredictionGroup = async function(ids) {
    const hasRoundOne=(ids||[]).some(id=>Number(matches.find(m=>m.id===id)?.round_number)===1);
    if (hasRoundOne && bonusQuestionsState.length && !bonusQuestionsState.some(q=>q.is_locked) && !bonusCompleteDeep()) {
      toast('Vasta enne 1. vooru mõlemale boonusküsimusele.');
      document.getElementById('deepBonusHome')?.scrollIntoView({behavior:'smooth',block:'center'});
      return;
    }
    return __deepBaseSavePredictionGroup(ids);
  };
}

const __deepBaseFriendlyError = friendlyError;
friendlyError = function(error) {
  const msg=String(error?.message||error||'');
  if (msg.includes('Vasta enne 1. vooru mõlemale boonusküsimusele')) return 'Enne 1. vooru ennustamist vasta mõlemale boonusküsimusele.';
  if (msg.includes('Boonusennustused on lukus')) return 'Boonusennustused on juba lukus.';
  return __deepBaseFriendlyError(error);
};

function showRoundReportModalDeep() {
  const r=latestRoundReportState;
  if (!r || document.getElementById('roundReportModalDeep')) return;
  const modal=document.createElement('div');
  modal.id='roundReportModalDeep';
  modal.className='modal-backdrop';
  modal.innerHTML='<div class="round-report-modal-card"><div class="round-summary-kicker">Voor on lõppenud</div><h2>'+esc(r.round_name||'Voor')+'</h2>' +
    '<div class="round-report-grid"><div class="round-report-stat"><strong>'+Number(r.points||0)+' p</strong><span>Sinu punktid</span></div><div class="round-report-stat"><strong>'+Number(r.exact_scores||0)+'</strong><span>Täpsed skoorid</span></div><div class="round-report-stat"><strong>'+(r.rank_after ? r.rank_after+'.' : '–')+'</strong><span>Koht tabelis</span></div></div>' +
    '<div class="notice" style="margin-top:12px">Vooru võitja: <strong>'+esc(r.round_winner||'–')+'</strong>'+(r.round_winner_points!=null?' · '+Number(r.round_winner_points)+' p':'')+'</div>' +
    (r.best_prediction ? '<div class="hint" style="text-align:left;margin-top:10px">Sinu parim ennustus: <strong>'+esc(r.best_prediction.home_team)+' – '+esc(r.best_prediction.away_team)+' '+Number(r.best_prediction.predicted_home)+':'+Number(r.best_prediction.predicted_away)+'</strong> · +'+Number(r.best_prediction.points||0)+' p</div>' : '') +
    '<button class="btn btn-block" type="button" onclick="document.getElementById(\'roundReportModalDeep\')?.remove()">Sulge</button></div>';
  document.body.appendChild(modal);
}

function maybeShowRoundReportDeep() {
  const r=latestRoundReportState;
  if (!r || !ownPlayerId()) return;
  const key='futbol-round-report-seen:'+ownPlayerId()+':'+r.round_number;
  if (localStorage.getItem(key)==='1') return;
  localStorage.setItem(key,'1');
  showRoundReportModalDeep();
  if ('Notification' in window && Notification.permission==='granted' && navigator.serviceWorker) {
    navigator.serviceWorker.ready.then(reg=>reg.showNotification('Futbol – '+(r.round_name||'voor')+' läbi',{body:'Said '+Number(r.points||0)+' punkti, täpseid skoore '+Number(r.exact_scores||0)+'. Koht tabelis: '+(r.rank_after||'–')+'.',icon:'./app-icon.svg',badge:'./app-icon.svg',tag:'futbol-round-report-'+r.round_number,data:{url:'./'}})).catch(()=>{});
  }
}

async function loadAdminDeepData() {
  if (!adminVerified || !adminPin || deepAdminLoading) return;
  deepAdminLoading=true;
  try {
    const [bonus, chat] = await Promise.all([
      sb.rpc('admin_get_bonus_questions',{p_pin:adminPin}),
      sb.from('chat_messages').select('id,user_id,message,created_at,is_announcement,pinned').order('created_at',{ascending:false}).limit(30)
    ]);
    if (!bonus.error) adminBonusState=bonus.data||[];
    if (!chat.error) adminChatRowsState=chat.data||[];
  } finally { deepAdminLoading=false; }
}

function adminBonusCardHtmlDeep() {
  let body='';
  adminBonusState.forEach(q=>{
    const suggestions=(q.question_key==='ucl_winner' ? (uclTeamOptionsState||[]).map(t=>t.team_name) : (q.answers||[]).map(a=>a.answer));
    const listId='bonus-list-'+q.question_key;
    body += '<div style="padding:10px 0;border-top:1px solid #edf0f5"><strong>'+esc(q.title)+'</strong><div class="hint" style="text-align:left">Vastanud '+Number(q.answered_count||0)+' / '+Number(q.total_players||0)+' · '+Number(q.points||10)+' p</div>' +
      '<input id="admin-bonus-'+q.question_key+'" class="input" list="'+listId+'" placeholder="Õige vastus; viigi korral eralda nimed komaga" value="'+esc(q.correct_answer||'')+'" style="margin-top:7px">' +
      '<datalist id="'+listId+'">'+suggestions.map(v=>'<option value="'+esc(v)+'"></option>').join('')+'</datalist>' +
      '<div class="admin-chat-actions"><button class="btn btn-small" onclick="adminSetBonusDeep(\''+q.question_key+'\')">Kinnita õige vastus</button>' +
      (q.resolved_at ? '<button class="btn btn-secondary btn-small" onclick="adminClearBonusDeep(\''+q.question_key+'\')">Tühista tulemus</button>' : '') + '</div>' +
      '<div class="admin-answer-list">Populaarsed vastused: '+((q.answers||[]).slice(0,6).map(a=>esc(a.answer)+' ('+Number(a.count||0)+')').join(', ')||'–')+'</div></div>';
  });
  return '<div class="card admin-deep-card" id="adminBonusDeep"><h3>Boonusküsimused</h3><div class="hint" style="text-align:left">Hooaja lõpus kinnita õiged vastused. Suurima väravaküti viigi korral sisesta mitu nime komaga.</div>'+body+'</div>';
}

async function adminSetBonusDeep(key) {
  const raw=String(document.getElementById('admin-bonus-'+key)?.value||'').trim();
  const answers=raw.split(',').map(v=>v.trim()).filter(Boolean);
  if (!answers.length) { toast('Sisesta vähemalt üks õige vastus.'); return; }
  const result=await sb.rpc('admin_set_bonus_results',{p_pin:adminPin,p_question_key:key,p_correct_answers:answers});
  if (result.error) { toast(friendlyError(result.error)); return; }
  toast('Boonuse õige vastus kinnitatud.');
  await loadAll();
}

async function adminClearBonusDeep(key) {
  if (!window.confirm('Kas tühistada selle boonusküsimuse tulemus?')) return;
  const result=await sb.rpc('admin_set_bonus_results',{p_pin:adminPin,p_question_key:key,p_correct_answers:[]});
  if (result.error) { toast(friendlyError(result.error)); return; }
  toast('Boonuse tulemus tühistatud.');
  await loadAll();
}

function adminChatCardHtmlDeep() {
  const rows=adminChatRowsState.slice(0,15).map(m=>'<div class="admin-chat-row"><div class="admin-chat-meta">'+esc(playerName(m.user_id))+' · '+formatDate(m.created_at)+' '+formatTime(m.created_at)+(m.pinned?' · 📌 kinnitatud':'')+'</div><div class="admin-chat-text">'+esc(m.message)+'</div><div class="admin-chat-actions"><button class="btn btn-secondary btn-small" onclick="adminToggleChatPinDeep('+m.id+','+(!m.pinned)+')">'+(m.pinned?'Vabasta':'Kinnita üles')+'</button><button class="btn btn-danger btn-small" onclick="adminDeleteChatMessageDeep('+m.id+')">Kustuta</button></div></div>').join('');
  return '<div class="card admin-deep-card" id="adminChatDeep"><h3>Chati teadaanne ja modereerimine</h3><textarea id="adminAnnouncementText" class="input" maxlength="500" rows="3" style="height:auto;padding-top:10px" placeholder="Kirjuta administraatori teadaanne…"></textarea><label style="display:block;margin-top:8px;font-size:11px"><input id="adminAnnouncementPinned" type="checkbox" checked> Kinnita teadaanne chati ülaossa</label><button class="btn btn-block" onclick="adminPostAnnouncementDeep()">Avalda teadaanne</button><div style="margin-top:12px">'+(rows||'<div class="hint">Chatis pole veel sõnumeid.</div>')+'</div></div>';
}

async function adminPostAnnouncementDeep() {
  const message=String(document.getElementById('adminAnnouncementText')?.value||'').trim();
  const pinned=!!document.getElementById('adminAnnouncementPinned')?.checked;
  if (!message) { toast('Kirjuta teadaanne.'); return; }
  const result=await sb.rpc('admin_post_chat_announcement',{p_pin:adminPin,p_message:message,p_pinned:pinned});
  if (result.error) { toast(friendlyError(result.error)); return; }
  toast('Teadaanne avaldatud.');
  await loadAdminDeepData();
  renderAdmin();
  if (window.futbolReloadChat) window.futbolReloadChat();
}

async function adminDeleteChatMessageDeep(id) {
  if (!adminVerified || !adminPin) return;
  if (!window.confirm('Kas kustutada see chati sõnum?')) return;
  const result=await sb.rpc('admin_delete_chat_message',{p_pin:adminPin,p_message_id:id});
  if (result.error) { toast(friendlyError(result.error)); return; }
  toast('Sõnum kustutatud.');
  await loadAdminDeepData();
  renderAdmin();
  if (window.futbolReloadChat) window.futbolReloadChat();
}

async function adminToggleChatPinDeep(id,pinned) {
  const result=await sb.rpc('admin_set_chat_pinned',{p_pin:adminPin,p_message_id:id,p_pinned:pinned});
  if (result.error) { toast(friendlyError(result.error)); return; }
  await loadAdminDeepData();
  renderAdmin();
  if (window.futbolReloadChat) window.futbolReloadChat();
}

const __deepBaseRenderAdmin = renderAdmin;
renderAdmin = function() {
  __deepBaseRenderAdmin();
  if (!adminVerified) return;
  const area=document.getElementById('adminArea');
  if (!area) return;
  const marker=area.querySelector('.admin-player-note') || area.firstElementChild;
  const html=adminBonusCardHtmlDeep()+adminChatCardHtmlDeep();
  if (marker) marker.insertAdjacentHTML('afterend',html); else area.insertAdjacentHTML('afterbegin',html);
};

const __deepBaseAdminLogin = adminLogin;
adminLogin = async function() {
  await __deepBaseAdminLogin();
  if (adminVerified) {
    await loadDeepCompetitionData();
    await loadAdminDeepData();
    renderAdmin();
  }
};

const __deepBaseAdminLogout = adminLogout;
adminLogout = function() {
  adminBonusState=[];
  adminChatRowsState=[];
  __deepBaseAdminLogout();
};

const __deepBaseLoadAll = loadAll;
loadAll = async function() {
  await __deepBaseLoadAll();
  await loadDeepCompetitionData();
  if (adminVerified) await loadAdminDeepData();
  renderPlayerSummary();
  renderGames();
  renderLeaderboard();
  renderRecoverySettings();
  if (adminVerified) renderAdmin();
  maybeShowRoundReportDeep();
};
'''
    text = text.replace('\n\ninit();', js + '\n\ninit();', 1)

index_path.write_text(text, encoding='utf-8')

# Chat: announcements stay at the top, favorite club icon is visible, and admin can moderate.
if chat_path.exists():
    chat = chat_path.read_text(encoding='utf-8')
    chat = chat.replace(".select('id,user_id,message,created_at')", ".select('id,user_id,message,created_at,is_announcement,pinned')")

    old_render = '''    box.innerHTML = chatMessages.map(function (item) {
      var own = currentUser && item.user_id === (currentPlayer?.id || currentUser.id);
      var name = own ? 'Sina' : playerName(item.user_id);
      return '<div class="chat-message ' + (own ? 'own' : '') + '">' +
        '<div class="chat-meta"><span class="chat-name">' + esc(name) + '</span><span class="chat-time"> · ' + esc(chatTimestamp(item.created_at)) + '</span></div>' +
        '<div class="chat-bubble">' + esc(item.message) + '</div>' +
      '</div>';
    }).join('');'''
    new_render = '''    var pinnedMessages = chatMessages.filter(function (item) { return !!item.pinned; });
    var regularMessages = chatMessages.filter(function (item) { return !item.pinned; });
    box.innerHTML = pinnedMessages.concat(regularMessages).map(function (item) {
      var own = currentUser && item.user_id === (currentPlayer?.id || currentUser.id);
      var name = own ? 'Sina' : playerName(item.user_id);
      var favorite = (typeof chatFavoriteMini === 'function') ? chatFavoriteMini(item.user_id) : '';
      var adminDelete = (typeof adminVerified !== 'undefined' && adminVerified)
        ? '<button class="chat-admin-delete" type="button" onclick="adminDeleteChatMessageDeep(' + item.id + ')">Kustuta</button>' : '';
      return '<div class="chat-message ' + (own ? 'own ' : '') + (item.is_announcement ? 'announcement' : '') + '">' +
        '<div class="chat-meta"><span class="chat-name">' + esc(name) + '</span>' + favorite + (item.pinned ? '<span class="chat-pin-label">📌 TEADAANNE</span>' : '') + '<span class="chat-time"> · ' + esc(chatTimestamp(item.created_at)) + '</span>' + adminDelete + '</div>' +
        '<div class="chat-bubble">' + esc(item.message) + '</div>' +
      '</div>';
    }).join('');'''
    if old_render in chat:
        chat = chat.replace(old_render, new_render, 1)

    old_sub = """        .on('postgres_changes', {
          event: 'INSERT',
          schema: 'public',
          table: 'chat_messages'
        }, function (payload) { appendChatMessage(payload.new, true); })
        .subscribe();"""
    new_sub = """        .on('postgres_changes', {
          event: 'INSERT',
          schema: 'public',
          table: 'chat_messages'
        }, function (payload) { appendChatMessage(payload.new, true); })
        .on('postgres_changes', {
          event: 'UPDATE',
          schema: 'public',
          table: 'chat_messages'
        }, function () { loadChatMessages(false); })
        .on('postgres_changes', {
          event: 'DELETE',
          schema: 'public',
          table: 'chat_messages'
        }, function () { loadChatMessages(false); })
        .subscribe();"""
    if old_sub in chat:
        chat = chat.replace(old_sub, new_sub, 1)

    if 'window.futbolReloadChat' not in chat:
        chat = chat.replace("  if (document.readyState === 'loading') {", "  window.futbolReloadChat = function () { loadChatMessages(false); };\n\n  if (document.readyState === 'loading') {", 1)

    chat_path.write_text(chat, encoding='utf-8')

# Force installed phones to pick up the new index/chat version.
if sw_path.exists():
    sw = sw_path.read_text(encoding='utf-8')
    sw = sw.replace('futbol-champions-v4', 'futbol-champions-v5')
    sw = sw.replace('./chat.js?v=4', './chat.js?v=5')
    sw_path.write_text(sw, encoding='utf-8')

text = index_path.read_text(encoding='utf-8')
text = text.replace('./chat.js?v=4', './chat.js?v=5')
index_path.write_text(text, encoding='utf-8')
