from pathlib import Path
import re

path = Path("index.html")
text = path.read_text(encoding="utf-8")


def replace_once(old, new, label):
    global text
    if old not in text:
        raise SystemExit(label + " anchor not found")
    text = text.replace(old, new, 1)


# Head / PWA metadata
if 'rel="manifest"' not in text:
    replace_once(
        '  <title>Futbol</title>\n<link rel="icon" href="./favicon.ico">',
        '  <title>Futbol – Champions League</title>\n'
        '  <link rel="icon" href="./favicon.ico">\n'
        '  <link rel="manifest" href="./manifest.webmanifest">\n'
        '  <link rel="apple-touch-icon" href="./app-icon.svg">\n'
        '  <meta name="apple-mobile-web-app-capable" content="yes">\n'
        '  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">\n'
        '  <meta name="apple-mobile-web-app-title" content="Futbol CL">',
        "head",
    )
else:
    text = text.replace('<title>Futbol</title>', '<title>Futbol – Champions League</title>', 1)

# Branding CSS and feature CSS
if ".brand-subtitle {" not in text:
    css_anchor = "    .player-label {\n"
    css = '''    .brand-subtitle {
      display: block;
      margin-top: 1px;
      color: #cddbd2;
      font-size: 10px;
      font-weight: 800;
      letter-spacing: 2px;
      line-height: 1.1;
    }

    .welcome-subtitle {
      margin: -2px 0 10px;
      color: var(--green);
      font-size: 12px;
      font-weight: 900;
      letter-spacing: 2.2px;
    }

    .recovery-entry {
      margin-top: 14px;
      padding-top: 14px;
      border-top: 1px solid var(--border);
    }

    .recovery-entry-title {
      font-size: 13px;
      font-weight: 850;
      color: var(--text);
    }

    .recovery-entry .input {
      margin-top: 9px;
      text-transform: uppercase;
      text-align: center;
      letter-spacing: 1.4px;
      font-weight: 850;
    }

    .recovery-card,
    .install-card {
      padding: 14px;
      margin-bottom: 14px;
      border: 1px solid var(--border);
      border-radius: 16px;
      background: white;
      box-shadow: var(--shadow);
    }

    .recovery-card-title,
    .install-card-title {
      font-size: 14px;
      font-weight: 900;
    }

    .recovery-card-text,
    .install-card-text {
      margin-top: 4px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.45;
    }

    .recovery-actions,
    .install-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 10px;
    }

    .recovery-code-box {
      margin-top: 10px;
      padding: 12px;
      border: 1px dashed #9fbbaa;
      border-radius: 12px;
      background: var(--green-soft);
      color: var(--dark);
      text-align: center;
      font-size: 20px;
      font-weight: 950;
      letter-spacing: 2px;
    }

    .player-name-btn {
      padding: 0;
      border: 0;
      background: transparent;
      color: inherit;
      font: inherit;
      font-weight: inherit;
      text-decoration: underline;
      text-decoration-color: #b8cbbf;
      text-underline-offset: 3px;
      cursor: pointer;
    }

    .modal-backdrop {
      position: fixed;
      z-index: 200;
      inset: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 18px;
      background: rgba(9, 25, 16, 0.62);
    }

    .stats-modal {
      position: relative;
      width: min(520px, 100%);
      max-height: min(82vh, 720px);
      overflow-y: auto;
      padding: 20px;
      border-radius: 20px;
      background: white;
      box-shadow: 0 18px 55px rgba(0,0,0,.25);
    }

    .modal-close {
      position: absolute;
      top: 10px;
      right: 10px;
      width: 38px;
      height: 38px;
      border: 0;
      border-radius: 50%;
      background: #edf2ef;
      color: var(--dark);
      font-size: 22px;
      line-height: 1;
    }

    .stats-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 8px;
      margin: 14px 0;
    }

    .stats-box {
      padding: 12px 8px;
      border: 1px solid var(--border);
      border-radius: 13px;
      text-align: center;
    }

    .stats-value {
      display: block;
      color: var(--green);
      font-size: 21px;
      font-weight: 950;
    }

    .stats-label {
      display: block;
      margin-top: 3px;
      color: var(--muted);
      font-size: 11px;
      font-weight: 700;
    }

    .recent-stat-row {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 10px;
      padding: 9px 0;
      border-bottom: 1px solid #edf1ee;
      font-size: 13px;
    }

    .recent-stat-score {
      font-weight: 900;
      white-space: nowrap;
    }

    .admin-count-wrap {
      margin-top: 8px;
    }

    .missing-predictions {
      margin-top: 7px;
      padding: 8px 10px;
      border: 1px solid var(--border);
      border-radius: 11px;
      background: #fafcfb;
      font-size: 12px;
    }

    .missing-predictions summary {
      color: var(--muted);
      font-weight: 800;
      cursor: pointer;
    }

    .missing-names {
      margin-top: 7px;
      line-height: 1.45;
      color: var(--text);
    }

'''
    if css_anchor not in text:
        raise SystemExit("branding CSS anchor not found")
    text = text.replace(css_anchor, css + css_anchor, 1)

# Welcome and top branding
text = text.replace(
    '<div class="welcome-logo">FUTBOL</div>',
    '<div class="welcome-logo">FUTBOL</div>\n      <div class="welcome-subtitle">CHAMPIONS LEAGUE</div>',
    1,
)
text = text.replace(
    'Ennusta sõpradega jalgpallimängude tulemusi\n        ja kogu punkte.',
    "Ennusta sõpradega Champions League'i mängude tulemusi\n        ja kogu punkte.",
    1,
)
text = text.replace(
    '''      <div class="brand">\n        FUTBOL\n      </div>''',
    '''      <div class="brand">\n        FUTBOL\n        <span class="brand-subtitle">CHAMPIONS LEAGUE</span>\n      </div>''',
    1,
)

# Recovery UI at the name gate
if 'id="recoveryPanel"' not in text:
    old = '''      <div id="nameError" class="error"></div>\n\n    </div>'''
    new = '''      <div id="nameError" class="error"></div>\n\n      <div class="recovery-entry">\n        <div class="recovery-entry-title">Kasutasid Futboli varem teises telefonis või brauseris?</div>\n        <button class="btn btn-secondary btn-block" type="button" onclick="toggleRecoveryPanel()">Taasta varasem kasutaja</button>\n        <div id="recoveryPanel" class="hidden">\n          <input id="recoveryInput" class="input" maxlength="14" autocomplete="off" placeholder="XXXX-XXXX-XXXX" oninput="formatRecoveryInput(this)">\n          <button class="btn btn-block" type="button" onclick="restorePlayer()">Taasta kasutaja</button>\n          <div id="recoveryError" class="error"></div>\n        </div>\n      </div>\n\n    </div>'''
    replace_once(old, new, "recovery gate")

# Stats modal
if 'id="statsModal"' not in text:
    replace_once(
        '<div id="toast" class="hidden"></div>',
        '''<div id="statsModal" class="modal-backdrop hidden" onclick="closeStatsOnBackdrop(event)">\n  <div class="stats-modal" role="dialog" aria-modal="true" aria-label="Mängija statistika">\n    <button class="modal-close" type="button" onclick="closePlayerStats()" aria-label="Sulge">×</button>\n    <div id="statsContent"></div>\n  </div>\n</div>\n\n<div id="toast" class="hidden"></div>''',
        "stats modal",
    )

# State variables
if "let hasRecoveryCodeState" not in text:
    replace_once(
        'let gamesFilter = "all";\nlet adminPredictionCounts = [];',
        'let gamesFilter = "all";\nlet adminPredictionCounts = [];\nlet hasRecoveryCodeState = false;\nlet latestRecoveryCode = "";\nlet deferredInstallPrompt = null;',
        "state vars",
    )

# Friendly recovery errors
if 'msg.includes("Taastamiskood ei kehti")' not in text:
    anchor = '  if (msg.includes("Alanud mängu ei saa muuta")) {'
    block = '''  if (msg.includes("Taastamiskood ei kehti")) {\n    return "Taastamiskood ei kehti. Kontrolli koodi ja proovi uuesti.";\n  }\n\n  if (msg.includes("Praegusel seadmel on kasutaja juba seotud")) {\n    return "Selles brauseris on kasutaja juba seotud.";\n  }\n\n'''
    if anchor not in text:
        raise SystemExit("friendly error anchor not found")
    text = text.replace(anchor, block + anchor, 1)

# Check recovery status during normal refreshes
if 'const recoveryStatusResult' not in text:
    anchor = '''  if (!boardResult.error) {\n\n    leaderboard =\n      boardResult.data || [];\n  }\n\n  renderPlayerSummary();'''
    replacement = '''  if (!boardResult.error) {\n\n    leaderboard =\n      boardResult.data || [];\n  }\n\n  const recoveryStatusResult = await sb.rpc("has_recovery_code");\n  if (!recoveryStatusResult.error) {\n    hasRecoveryCodeState = Boolean(recoveryStatusResult.data);\n  }\n\n  renderPlayerSummary();'''
    replace_once(anchor, replacement, "recovery status")

# Replace player summary and add recovery/install helpers
start = text.find("function renderPlayerSummary() {\n")
end = text.find("async function shareFutbol() {\n")
if start == -1 or end == -1 or end <= start:
    raise SystemExit("player summary boundaries not found")

new_summary = r'''function isStandaloneMode() {
  return window.matchMedia("(display-mode: standalone)").matches ||
    window.navigator.standalone === true;
}

function renderPlayerSummary() {

  const container = document.getElementById("playerSummary");

  if (!container || !currentUser) {
    return;
  }

  const row = leaderboard.find(item => item.player_id === currentUser.id);
  const points = row ? Number(row.total_points || 0) : 0;
  const rank = row ? row.rank_no : "–";
  const exact = row ? Number(row.exact_scores || 0) : 0;

  const upcoming = matches.filter(match => !isStarted(match));
  const predictedUpcoming = upcoming.filter(match =>
    predictions.some(
      p => p.match_id === match.id && p.user_id === currentUser.id
    )
  );
  const missing = Math.max(0, upcoming.length - predictedUpcoming.length);

  let reminder = "";

  if (upcoming.length > 0) {
    reminder = missing > 0
      ? '<div class="prediction-reminder">Sul on veel <strong>' + missing +
        '</strong> mängu ennustamata.</div>'
      : '<div class="prediction-reminder done">Kõik tulevased mängud on ennustatud ✓</div>';
  }

  let recoveryCard =
    '<div class="recovery-card">' +
      '<div class="recovery-card-title">Kasutaja taastamine</div>';

  if (latestRecoveryCode) {
    recoveryCard +=
      '<div class="recovery-card-text">Salvesta see kood turvaliselt. Sellega saad oma nime, punktid ja ennustused uues telefonis või brauseris taastada.</div>' +
      '<div class="recovery-code-box">' + esc(latestRecoveryCode) + '</div>' +
      '<div class="recovery-actions">' +
        '<button class="btn btn-small" type="button" onclick="copyRecoveryCode()">Kopeeri kood</button>' +
        '<button class="btn btn-secondary btn-small" type="button" onclick="createRecoveryCode()">Loo uus kood</button>' +
      '</div>';
  } else if (hasRecoveryCodeState) {
    recoveryCard +=
      '<div class="recovery-card-text">Taastamiskood on loodud. Kui oled selle kaotanud, loo uus kood. Uue koodi loomisel vana kood enam ei kehti.</div>' +
      '<div class="recovery-actions">' +
        '<button class="btn btn-secondary btn-small" type="button" onclick="createRecoveryCode()">Loo uus taastamiskood</button>' +
      '</div>';
  } else {
    recoveryCard +=
      '<div class="recovery-card-text">Loo ühekordne taastamiskood, et saaksid telefoni või brauseri vahetamisel oma Futboli kasutaja tagasi.</div>' +
      '<div class="recovery-actions">' +
        '<button class="btn btn-small" type="button" onclick="createRecoveryCode()">Loo taastamiskood</button>' +
      '</div>';
  }

  recoveryCard += '</div>';

  const installCard = isStandaloneMode()
    ? ""
    : '<div class="install-card">' +
        '<div class="install-card-title">Lisa Futbol avakuvale</div>' +
        '<div class="install-card-text">Futbol avaneb telefonis nagu eraldi rakendus. Play Store’i või App Store’i pole vaja.</div>' +
        '<div class="install-actions"><button class="btn btn-secondary btn-small" type="button" onclick="installFutbol()">Lisa avakuvale</button></div>' +
      '</div>';

  container.innerHTML =
    '<div class="player-summary">' +
      '<div class="summary-stat">' +
        '<span class="summary-value">' + points + '</span>' +
        '<span class="summary-label">Minu punktid</span>' +
      '</div>' +
      '<div class="summary-stat">' +
        '<span class="summary-value">' + rank + '</span>' +
        '<span class="summary-label">Koht tabelis</span>' +
      '</div>' +
      '<div class="summary-stat">' +
        '<span class="summary-value">' + exact + '</span>' +
        '<span class="summary-label">Täpsed skoorid</span>' +
      '</div>' +
    '</div>' +
    reminder +
    '<div class="share-card">' +
      '<div class="share-top">' +
        '<div class="share-card-text">' +
          '<div class="share-card-title">Kutsu sõbrad Champions League’i ennustama</div>' +
          '<div class="share-card-subtitle">Jaga Futboli linki otse telefonist</div>' +
        '</div>' +
        '<button class="share-btn" onclick="shareFutbol()">Jaga</button>' +
      '</div>' +
      '<div class="share-apps">' +
        '<button class="share-app-btn" onclick="shareViaApp(\'whatsapp\')">WhatsApp</button>' +
        '<button class="share-app-btn" onclick="shareViaApp(\'messenger\')">Messenger</button>' +
        '<button class="share-app-btn" onclick="shareViaApp(\'viber\')">Viber</button>' +
        '<button class="share-app-btn" onclick="shareViaApp(\'instagram\')">Instagram</button>' +
        '<button class="share-app-btn" onclick="shareViaApp(\'telegram\')">Telegram</button>' +
        '<button class="share-app-btn" onclick="shareViaApp(\'facebook\')">Facebook</button>' +
        '<button class="share-app-btn" onclick="copyFutbolLink()">Kopeeri link</button>' +
      '</div>' +
    '</div>' +
    recoveryCard +
    installCard;
}

function toggleRecoveryPanel() {
  const panel = document.getElementById("recoveryPanel");
  if (panel) panel.classList.toggle("hidden");
}

function formatRecoveryInput(input) {
  const raw = String(input.value || "")
    .toUpperCase()
    .replace(/[^A-Z0-9]/g, "")
    .slice(0, 12);

  input.value = [raw.slice(0, 4), raw.slice(4, 8), raw.slice(8, 12)]
    .filter(Boolean)
    .join("-");
}

async function restorePlayer() {
  const input = document.getElementById("recoveryInput");
  const errorBox = document.getElementById("recoveryError");

  if (!input || !errorBox) return;

  errorBox.textContent = "";
  const code = input.value.trim();

  if (!code) {
    errorBox.textContent = "Sisesta taastamiskood.";
    return;
  }

  const result = await sb.rpc("restore_player", { p_code: code });

  if (result.error) {
    errorBox.textContent = friendlyError(result.error);
    return;
  }

  currentPlayer = {
    id: currentUser.id,
    display_name: result.data
  };

  hasRecoveryCodeState = true;
  latestRecoveryCode = "";

  document.getElementById("nameGate").classList.add("hidden");
  toast("Kasutaja taastatud.");
  await enterApp();
}

async function createRecoveryCode() {
  const result = await sb.rpc("create_recovery_code");

  if (result.error) {
    toast(friendlyError(result.error));
    return;
  }

  latestRecoveryCode = String(result.data || "");
  hasRecoveryCodeState = true;
  renderPlayerSummary();
  toast("Uus taastamiskood loodud.");
}

async function copyRecoveryCode() {
  if (!latestRecoveryCode) return;

  try {
    await navigator.clipboard.writeText(latestRecoveryCode);
    toast("Taastamiskood kopeeritud.");
  } catch (error) {
    window.prompt("Kopeeri taastamiskood:", latestRecoveryCode);
  }
}

async function installFutbol() {
  if (isStandaloneMode()) {
    toast("Futbol on juba avakuvale lisatud.");
    return;
  }

  if (deferredInstallPrompt) {
    deferredInstallPrompt.prompt();
    await deferredInstallPrompt.userChoice;
    deferredInstallPrompt = null;
    renderPlayerSummary();
    return;
  }

  const isIOS = /iPhone|iPad|iPod/i.test(navigator.userAgent);
  if (isIOS) {
    window.alert("iPhone/iPad: vajuta brauseris Jaga ja vali „Lisa avakuvale“.");
    return;
  }

  window.alert("Ava brauseri menüü ja vali „Lisa avakuvale“ või „Installi rakendus“.");
}

'''
text = text[:start] + new_summary + text[end:]

# Champions League share wording
text = text.replace('title: "Futbol",', 'title: "Futbol – Champions League",', 1)
text = text.replace(
    'text: "Tule ennusta meiega jalgpallimängude skoore!",',
    'text: "Tule ennusta meiega Champions League’i mängude skoore!",',
    1,
)
text = text.replace(
    'return "Tule ennusta meiega jalgpallimängude skoore!";',
    'return "Tule ennusta meiega Champions League’i mängude skoore!";',
    1,
)

# Replace leaderboard with clickable detailed player stats
start = text.find("function renderLeaderboard() {\n")
end = text.find("function showTab(name) {\n")
if start == -1 or end == -1 or end <= start:
    raise SystemExit("leaderboard boundaries not found")

new_leaderboard = r'''function renderLeaderboard() {

  const container = document.getElementById("leaderboard");

  if (!leaderboard.length) {
    container.innerHTML =
      '<div class="card"><div class="notice">Tabel on veel tühi.</div></div>';
    return;
  }

  let html =
    '<div class="card table-wrap"><table><thead><tr>' +
    '<th>Koht</th><th>Mängija</th><th class="num">Punktid</th>' +
    '<th class="num">Täpsed</th><th class="num">Enn.</th>' +
    '</tr></thead><tbody>';

  leaderboard.forEach(row => {

    const rank = Number(row.rank_no);
    const medal = rank === 1 ? "🥇" : rank === 2 ? "🥈" : rank === 3 ? "🥉" : "";
    const isSelf = currentUser && row.player_id === currentUser.id;

    html += '<tr class="' + (isSelf ? "leaderboard-self" : "") + '">' +
      '<td class="rank">' +
        (medal ? '<span class="rank-medal">' + medal + '</span>' : "") +
        row.rank_no +
      '</td>' +
      '<td class="' + (rank === 1 ? "leader" : "") + '">' +
        '<button class="player-name-btn" type="button" onclick="openPlayerStats(\'' + row.player_id + '\')">' +
          esc(row.player_name) +
        '</button>' +
        (isSelf ? '<span class="self-chip">Sina</span>' : "") +
      '</td>' +
      '<td class="num"><strong>' + row.total_points + '</strong></td>' +
      '<td class="num">' + row.exact_scores + '</td>' +
      '<td class="num">' + row.predictions_count + '</td>' +
    '</tr>';
  });

  html += '</tbody></table></div>';
  container.innerHTML = html;
}

function closePlayerStats() {
  const modal = document.getElementById("statsModal");
  if (modal) modal.classList.add("hidden");
}

function closeStatsOnBackdrop(event) {
  if (event.target && event.target.id === "statsModal") {
    closePlayerStats();
  }
}

function openPlayerStats(playerId) {

  const player = players.find(p => p.id === playerId);
  const boardRow = leaderboard.find(row => row.player_id === playerId);
  const name = player ? player.display_name : (boardRow ? boardRow.player_name : "Mängija");

  const rows = predictions
    .filter(pred => pred.user_id === playerId)
    .map(pred => ({
      prediction: pred,
      match: matches.find(match => match.id === pred.match_id)
    }))
    .filter(item => item.match && isFinished(item.match))
    .sort((a, b) => new Date(b.match.kickoff_at) - new Date(a.match.kickoff_at));

  let total = 0;
  let exact = 0;
  let correctOutcome = 0;
  let wrong = 0;

  rows.forEach(item => {
    const pts = calculatePoints(item.prediction, item.match) || 0;
    total += pts;
    if (pts === 3) exact += 1;
    else if (pts === 1) correctOutcome += 1;
    else wrong += 1;
  });

  const average = rows.length ? (total / rows.length).toFixed(2).replace(".", ",") : "0,00";

  let recentHtml = "";
  rows.slice(0, 5).forEach(item => {
    const pts = calculatePoints(item.prediction, item.match) || 0;
    recentHtml +=
      '<div class="recent-stat-row">' +
        '<div>' +
          '<strong>' + esc(item.match.home_team) + ' – ' + esc(item.match.away_team) + '</strong>' +
          '<div class="match-date">' + formatDate(item.match.kickoff_at) + '</div>' +
        '</div>' +
        '<div class="recent-stat-score">' +
          item.prediction.home_score + ' : ' + item.prediction.away_score +
          ' · +' + pts + ' p' +
        '</div>' +
      '</div>';
  });

  const content = document.getElementById("statsContent");
  content.innerHTML =
    '<h2 style="padding-right:42px">' + esc(name) + '</h2>' +
    '<div class="stats-grid">' +
      '<div class="stats-box"><span class="stats-value">' + total + '</span><span class="stats-label">Punktid</span></div>' +
      '<div class="stats-box"><span class="stats-value">' + rows.length + '</span><span class="stats-label">Lõppenud ennustused</span></div>' +
      '<div class="stats-box"><span class="stats-value">' + exact + '</span><span class="stats-label">Täpsed skoorid</span></div>' +
      '<div class="stats-box"><span class="stats-value">' + correctOutcome + '</span><span class="stats-label">Õige tulemus</span></div>' +
      '<div class="stats-box"><span class="stats-value">' + wrong + '</span><span class="stats-label">Valed ennustused</span></div>' +
      '<div class="stats-box"><span class="stats-value">' + average + '</span><span class="stats-label">Punkti / mäng</span></div>' +
    '</div>' +
    (recentHtml
      ? '<h3>Viimased mängud</h3>' + recentHtml
      : '<div class="notice">Lõppenud mängude statistikat veel pole.</div>');

  document.getElementById("statsModal").classList.remove("hidden");
}

'''
text = text[:start] + new_leaderboard + text[end:]

# Admin: count plus missing player names
old_count = '''    const countRow = adminPredictionCounts.find(row => row.match_id === match.id);\n\n    if (countRow) {\n      html +=\n        '<div class="admin-prediction-count">Ennustanud ' +\n        Number(countRow.predictions_count || 0) +\n        ' / ' +\n        Number(countRow.players_count || 0) +\n        '</div>';\n    }'''
new_count = '''    const countRow = adminPredictionCounts.find(row => row.match_id === match.id);\n\n    if (countRow) {\n      const missingNames = Array.isArray(countRow.missing_names)\n        ? countRow.missing_names\n        : [];\n\n      html +=\n        '<div class="admin-count-wrap">' +\n          '<div class="admin-prediction-count">Ennustanud ' +\n            Number(countRow.predictions_count || 0) +\n            ' / ' +\n            Number(countRow.players_count || 0) +\n          '</div>';\n\n      if (!started && missingNames.length) {\n        html +=\n          '<details class="missing-predictions">' +\n            '<summary>Ennustamata (' + missingNames.length + ')</summary>' +\n            '<div class="missing-names">' + missingNames.map(esc).join(', ') + '</div>' +\n          '</details>';\n      } else if (!started && !missingNames.length && Number(countRow.players_count || 0) > 0) {\n        html += '<div class="hint" style="text-align:left;color:var(--green)">Kõik kasutajad on ennustanud ✓</div>';\n      }\n\n      html += '</div>';\n    }'''
if old_count in text:
    text = text.replace(old_count, new_count, 1)
elif "missingNames = Array.isArray(countRow.missing_names)" not in text:
    raise SystemExit("admin count anchor not found")

# PWA events and service worker registration
if 'beforeinstallprompt' not in text:
    anchor = "init();\n\nsetInterval(() => {"
    pwa = '''window.addEventListener("beforeinstallprompt", event => {\n  event.preventDefault();\n  deferredInstallPrompt = event;\n  if (currentUser && currentPlayer) renderPlayerSummary();\n});\n\nwindow.addEventListener("appinstalled", () => {\n  deferredInstallPrompt = null;\n  if (currentUser && currentPlayer) renderPlayerSummary();\n});\n\nif ("serviceWorker" in navigator) {\n  window.addEventListener("load", () => {\n    navigator.serviceWorker.register("./sw.js").catch(() => {});\n  });\n}\n\ninit();\n\nsetInterval(() => {'''
    replace_once(anchor, pwa, "PWA init")

path.write_text(text, encoding="utf-8")
