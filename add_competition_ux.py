from pathlib import Path

path = Path("index.html")
text = path.read_text(encoding="utf-8")

# --- CSS ---
css_anchor = "    .match-header {\n"
css_code = '''    .prediction-reminder {
      margin: 12px 0;
      padding: 12px 14px;
      border: 1px solid #d8e8df;
      border-radius: 14px;
      background: #f1f8f4;
      color: var(--green);
      font-size: 14px;
      font-weight: 800;
      line-height: 1.4;
    }

    .prediction-reminder.done {
      background: #edf7f1;
    }

    .game-filters {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 7px;
      margin: 14px 0 4px;
    }

    .filter-btn {
      min-height: 40px;
      padding: 8px 7px;
      border: 1px solid var(--border);
      border-radius: 11px;
      background: white;
      color: var(--muted);
      font-size: 12px;
      font-weight: 850;
      cursor: pointer;
    }

    .filter-btn.active {
      border-color: var(--green);
      background: var(--green-soft);
      color: var(--green);
    }

    .leaderboard-self td {
      background: #eef8f2;
      font-weight: 800;
    }

    .self-chip {
      display: inline-block;
      margin-left: 6px;
      padding: 2px 6px;
      border-radius: 999px;
      background: var(--green-soft);
      color: var(--green);
      font-size: 10px;
      font-weight: 900;
      vertical-align: middle;
    }

    .rank-medal {
      display: inline-block;
      min-width: 22px;
      margin-right: 3px;
      font-size: 18px;
      vertical-align: -1px;
    }

    .admin-prediction-count {
      margin-top: 8px;
      display: inline-block;
      padding: 6px 9px;
      border-radius: 999px;
      background: var(--green-soft);
      color: var(--green);
      font-size: 12px;
      font-weight: 900;
    }

'''
if ".prediction-reminder {" not in text:
    if css_anchor not in text:
        raise SystemExit("CSS anchor not found")
    text = text.replace(css_anchor, css_code + css_anchor, 1)

# --- Globals ---
global_anchor = 'let leaderboard = [];\n\nlet adminPin = "";'
if 'let gamesFilter = "all";' not in text:
    if global_anchor not in text:
        raise SystemExit("Global anchor not found")
    text = text.replace(
        global_anchor,
        'let leaderboard = [];\nlet gamesFilter = "all";\nlet adminPredictionCounts = [];\n\nlet adminPin = "";',
        1,
    )

# --- Player summary with missing-prediction reminder ---
summary_start = text.find("function renderPlayerSummary() {\n")
summary_end = text.find("async function shareFutbol() {\n")
if summary_start == -1 or summary_end == -1 or summary_end <= summary_start:
    raise SystemExit("Player summary boundaries not found")

if "prediction-reminder" not in text[summary_start:summary_end]:
    new_summary = r'''function renderPlayerSummary() {

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
          '<div class="share-card-title">Kutsu sõbrad ennustama</div>' +
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
    '</div>';
}

'''
    text = text[:summary_start] + new_summary + text[summary_end:]

# --- Match filter helper ---
filter_anchor = "function renderGames() {\n"
filter_code = r'''function setGamesFilter(filter) {

  if (!["all", "predicted", "unpredicted"].includes(filter)) {
    return;
  }

  gamesFilter = filter;
  renderGames();
}

function hasOwnPrediction(matchId) {
  return predictions.some(
    p => p.match_id === matchId && p.user_id === currentUser.id
  );
}

'''
if "function setGamesFilter(" not in text:
    if filter_anchor not in text:
        raise SystemExit("Filter helper anchor not found")
    text = text.replace(filter_anchor, filter_code + filter_anchor, 1)

# --- Replace renderGames with filtered grouped version ---
games_start = text.find("function renderGames() {\n")
games_end = text.find("async function savePrediction(matchId) {\n")
if games_start == -1 or games_end == -1 or games_end <= games_start:
    raise SystemExit("renderGames boundaries not found")

current_games = text[games_start:games_end]
if "game-filters" not in current_games:
    new_games = r'''function renderGames() {

  const container = document.getElementById("games");

  if (!matches.length) {
    container.innerHTML =
      '<div class="card"><div class="notice">Ühtegi mängu pole veel lisatud.</div></div>';
    return;
  }

  const predictedCount = matches.filter(match => hasOwnPrediction(match.id)).length;
  const unpredictedCount = matches.length - predictedCount;

  let html =
    '<div class="game-filters">' +
      '<button class="filter-btn ' + (gamesFilter === "all" ? "active" : "") +
        '" onclick="setGamesFilter(\'all\')">Kõik (' + matches.length + ')</button>' +
      '<button class="filter-btn ' + (gamesFilter === "predicted" ? "active" : "") +
        '" onclick="setGamesFilter(\'predicted\')">Ennustatud (' + predictedCount + ')</button>' +
      '<button class="filter-btn ' + (gamesFilter === "unpredicted" ? "active" : "") +
        '" onclick="setGamesFilter(\'unpredicted\')">Ennustamata (' + unpredictedCount + ')</button>' +
    '</div>';

  const visibleMatches = matches.filter(match => {
    const own = hasOwnPrediction(match.id);
    if (gamesFilter === "predicted") return own;
    if (gamesFilter === "unpredicted") return !own;
    return true;
  });

  if (!visibleMatches.length) {
    html += '<div class="card"><div class="notice">Selle filtri all mänge ei ole.</div></div>';
    container.innerHTML = html;
    return;
  }

  const upcoming = visibleMatches.filter(match => !isStarted(match));
  const waitingResult = visibleMatches.filter(match => isStarted(match) && !isFinished(match));
  const finishedMatches = visibleMatches.filter(match => isFinished(match));

  const renderGroup = (title, groupMatches) => {

    if (!groupMatches.length) return;

    html += '<div class="match-group-title">' + esc(title) + '</div>';

    groupMatches.forEach(match => {

      const started = isStarted(match);
      const finished = isFinished(match);

      let badgeClass = "badge-open";
      let badgeText = "Avatud";

      if (started) {
        badgeClass = "badge-locked";
        badgeText = "Lukus";
      }

      if (finished) {
        badgeClass = "badge-finished";
        badgeText = "Lõppenud";
      }

      const own = predictions.find(
        p => p.match_id === match.id && p.user_id === currentUser.id
      );

      const visiblePredictions = predictions
        .filter(p => p.match_id === match.id)
        .sort((a, b) =>
          playerName(a.user_id).localeCompare(playerName(b.user_id), "et")
        );

      html += '<article class="card">';

      html +=
        '<div class="match-header">' +
          "<div>" +
            '<div class="match-title">' + esc(match.home_team) + " – " + esc(match.away_team) + "</div>" +
            '<div class="match-date">' + formatDate(match.kickoff_at) + " · " + formatTime(match.kickoff_at) + "</div>" +
          "</div>" +
          '<div class="match-badges">' +
            '<span class="badge ' + badgeClass + '">' + badgeText + "</span>" +
            (own && !started
              ? '<span class="own-prediction-badge">✓ Ennustatud ' + own.home_score + " : " + own.away_score + "</span>"
              : "") +
          "</div>" +
        "</div>";

      if (!started) {
        html +=
          '<div class="countdown" data-kickoff-countdown="' + esc(match.kickoff_at) + '">' +
          esc(countdownText(match.kickoff_at)) + "</div>";
      }

      html +=
        '<div class="teams">' +
          '<div class="team">' + esc(match.home_team) + "</div>" +
          '<div class="vs">VS</div>' +
          '<div class="team">' + esc(match.away_team) + "</div>" +
        "</div>";

      if (finished) {
        html += '<div class="result">' + match.home_score + " : " + match.away_score + "</div>";

        if (match.went_to_extra_time) {
          html += '<div class="hint">Tulemus sisaldab lisaaega. Penaltiseeria ei lähe skoori.</div>';
        }
      }

      if (!started) {
        html +=
          '<div class="score-entry">' +
            '<div class="score-label-left">' + esc(match.home_team) + "</div>" +
            '<input id="ph-' + match.id + '" class="score-input" type="number" min="0" max="30" inputmode="numeric" value="' + (own ? own.home_score : "") + '">' +
            '<div class="colon">:</div>' +
            '<input id="pa-' + match.id + '" class="score-input" type="number" min="0" max="30" inputmode="numeric" value="' + (own ? own.away_score : "") + '">' +
            '<div class="score-label-right">' + esc(match.away_team) + "</div>" +
          "</div>";

        html +=
          '<button class="btn btn-block" onclick="savePrediction(\'' + match.id + '\')">' +
          (own ? "Muuda ennustust" : "Salvesta ennustus") + "</button>";

        html += '<div class="hint">Ennustamine lõpeb mängu alguses. Teiste ennustused on seni peidetud.</div>';

      } else {
        html += '<div class="notice">Ennustamine on lõppenud.</div>';

        if (own) {
          html += '<div class="my-prediction">Sinu ennustus: <strong>' + own.home_score + " : " + own.away_score + "</strong>";
          if (finished) html += " · <strong>" + calculatePoints(own, match) + " p</strong>";
          html += "</div>";
        }

        html += '<div class="prediction-list">';

        if (!visiblePredictions.length) {
          html += '<div class="hint">Sellele mängule ennustusi ei tehtud.</div>';
        } else {
          visiblePredictions.forEach(pred => {
            html +=
              '<div class="prediction-row">' +
                "<div>" + esc(playerName(pred.user_id)) + "</div>" +
                '<div class="prediction-score">' + pred.home_score + " : " + pred.away_score + "</div>" +
                '<div class="points">' + (finished ? calculatePoints(pred, match) + " p" : "") + "</div>" +
              "</div>";
          });
        }

        html += "</div>";
      }

      html += "</article>";
    });
  };

  renderGroup("Tulevased mängud", upcoming);
  renderGroup("Alanud – ootab tulemust", waitingResult);
  renderGroup("Lõppenud mängud", finishedMatches);

  container.innerHTML = html;
  refreshCountdowns();
}

'''
    text = text[:games_start] + new_games + text[games_end:]

# --- Leaderboard: own row + top 3 medals ---
board_start = text.find("function renderLeaderboard() {\n")
board_end = text.find("function showTab(name) {\n")
if board_start == -1 or board_end == -1 or board_end <= board_start:
    raise SystemExit("Leaderboard boundaries not found")

if "leaderboard-self" not in text[board_start:board_end]:
    new_board = r'''function renderLeaderboard() {

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
        esc(row.player_name) +
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

'''
    text = text[:board_start] + new_board + text[board_end:]

# --- Admin prediction count loader ---
admin_loader_anchor = "function renderAdmin() {\n"
admin_loader_code = r'''async function loadAdminPredictionCounts() {

  if (!adminVerified || !adminPin) {
    adminPredictionCounts = [];
    return;
  }

  const result = await sb.rpc(
    "admin_get_prediction_counts",
    { p_pin: adminPin }
  );

  if (result.error) {
    adminPredictionCounts = [];
    return;
  }

  adminPredictionCounts = result.data || [];
}

'''
if "function loadAdminPredictionCounts(" not in text:
    if admin_loader_anchor not in text:
        raise SystemExit("Admin loader anchor not found")
    text = text.replace(admin_loader_anchor, admin_loader_code + admin_loader_anchor, 1)

# loadAll gets admin counts before rendering admin
old_load_admin = '''  if (adminVerified) {
    renderAdmin();
  }'''
new_load_admin = '''  if (adminVerified) {
    await loadAdminPredictionCounts();
    renderAdmin();
  }'''
if new_load_admin not in text:
    if old_load_admin not in text:
        raise SystemExit("loadAll admin anchor not found")
    text = text.replace(old_load_admin, new_load_admin, 1)

# adminLogin loads counts after successful PIN verification
old_login = '''  adminVerified =
    true;

  renderAdmin();'''
new_login = '''  adminVerified =
    true;

  await loadAdminPredictionCounts();
  renderAdmin();'''
if new_login not in text:
    if old_login not in text:
        raise SystemExit("adminLogin anchor not found")
    text = text.replace(old_login, new_login, 1)

# adminLogout clears counts
old_logout = '''  adminPin = "";
  adminVerified = false;

  renderAdmin();'''
new_logout = '''  adminPin = "";
  adminVerified = false;
  adminPredictionCounts = [];

  renderAdmin();'''
if new_logout not in text:
    if old_logout not in text:
        raise SystemExit("adminLogout anchor not found")
    text = text.replace(old_logout, new_logout, 1)

# Show prediction count on each admin match card
admin_date_anchor = '''      '<div class="match-date">' +
        formatDate(
          match.kickoff_at
        ) +
        " · " +
        formatTime(
          match.kickoff_at
        ) +
      "</div>";

    if (finished) {'''
admin_date_replacement = '''      '<div class="match-date">' +
        formatDate(
          match.kickoff_at
        ) +
        " · " +
        formatTime(
          match.kickoff_at
        ) +
      "</div>";

    const countRow = adminPredictionCounts.find(row => row.match_id === match.id);

    if (countRow) {
      html +=
        '<div class="admin-prediction-count">Ennustanud ' +
        Number(countRow.predictions_count || 0) +
        ' / ' +
        Number(countRow.players_count || 0) +
        '</div>';
    }

    if (finished) {'''
if "admin-prediction-count" not in text[text.find("function renderAdmin() {"):]:
    if admin_date_anchor not in text:
        raise SystemExit("Admin match date anchor not found")
    text = text.replace(admin_date_anchor, admin_date_replacement, 1)

path.write_text(text, encoding="utf-8")
