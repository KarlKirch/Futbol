from pathlib import Path

path = Path("index.html")
text = path.read_text(encoding="utf-8")

CSS_MARKER = "/* UCL ADVANCED UX */"
JS_MARKER = "// UCL ADVANCED UX"

if CSS_MARKER not in text:
    css = r'''

    /* UCL ADVANCED UX */
    :root {
      --bg: #f3f5fb;
      --dark: #071633;
      --green: #3154e8;
      --green2: #6657e8;
      --green-soft: #edf0ff;
      --border: #dce2f1;
      --warning: #8a6714;
    }

    body {
      background:
        radial-gradient(circle at 10% 0%, rgba(66, 93, 220, .09), transparent 32%),
        radial-gradient(circle at 90% 8%, rgba(113, 82, 211, .08), transparent 30%),
        var(--bg);
    }

    .topbar {
      background:
        radial-gradient(circle at 18% 15%, rgba(109, 117, 255, .30), transparent 26%),
        radial-gradient(circle at 78% 0%, rgba(105, 67, 189, .32), transparent 32%),
        linear-gradient(135deg, #06132f 0%, #0b1f4d 55%, #180b3f 100%);
      box-shadow: 0 8px 28px rgba(5, 17, 50, .18);
    }

    .brand-subtitle,
    .player-label {
      color: #cbd6ff;
    }

    .card {
      box-shadow: 0 6px 22px rgba(18, 34, 76, .07);
    }

    .round-filter-bar {
      display: flex;
      gap: 7px;
      overflow-x: auto;
      padding: 3px 1px 10px;
      scrollbar-width: none;
    }

    .round-filter-bar::-webkit-scrollbar {
      display: none;
    }

    .round-filter-btn {
      flex: 0 0 auto;
      min-height: 38px;
      padding: 0 12px;
      border: 1px solid var(--border);
      border-radius: 999px;
      background: white;
      color: var(--muted);
      font-size: 12px;
      font-weight: 850;
    }

    .round-filter-btn.active {
      border-color: var(--green);
      background: var(--green-soft);
      color: var(--green);
    }

    .round-section-title {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      margin: 15px 2px 9px;
      padding: 9px 11px;
      border-radius: 12px;
      background: linear-gradient(90deg, #0c234f, #251455);
      color: white;
      font-size: 13px;
      font-weight: 900;
    }

    .round-section-count {
      color: #cad4ff;
      font-size: 11px;
      font-weight: 800;
    }

    .round-chip {
      display: inline-flex;
      align-items: center;
      margin-top: 5px;
      padding: 4px 8px;
      border-radius: 999px;
      background: #eef1ff;
      color: #304bad;
      font-size: 11px;
      font-weight: 850;
    }

    .teams-logo-grid {
      display: grid;
      grid-template-columns: minmax(0, 1fr) 42px minmax(0, 1fr);
      gap: 10px;
      align-items: center;
      margin: 16px 0;
    }

    .team-logo-side {
      display: flex;
      align-items: center;
      gap: 9px;
      min-width: 0;
      font-weight: 850;
    }

    .team-logo-side.away {
      justify-content: flex-end;
      text-align: right;
    }

    .team-logo {
      width: 38px;
      height: 38px;
      object-fit: contain;
      flex: 0 0 38px;
    }

    .team-logo-fallback {
      width: 38px;
      height: 38px;
      flex: 0 0 38px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border-radius: 50%;
      background: linear-gradient(145deg, #e9edff, #f7f5ff);
      color: #243d9c;
      border: 1px solid #d8dff7;
      font-size: 11px;
      font-weight: 950;
    }

    .team-logo-name {
      min-width: 0;
      overflow-wrap: anywhere;
    }

    .round-winner-card {
      position: relative;
      overflow: hidden;
      border: 1px solid #cfd8ff;
      background:
        radial-gradient(circle at 95% 5%, rgba(113, 85, 232, .16), transparent 35%),
        linear-gradient(135deg, #f8f9ff, #eef2ff);
    }

    .round-winner-eyebrow {
      color: #5367bd;
      font-size: 11px;
      font-weight: 900;
      text-transform: uppercase;
      letter-spacing: 1.2px;
    }

    .round-winner-name {
      margin-top: 5px;
      color: var(--dark);
      font-size: 21px;
      font-weight: 950;
    }

    .round-winner-meta {
      margin-top: 3px;
      color: var(--muted);
      font-size: 12px;
    }

    .admin-tools-card textarea {
      width: 100%;
      min-height: 126px;
      resize: vertical;
      padding: 12px 13px;
      border: 1px solid #cbd6cf;
      border-radius: 12px;
      background: white;
      font: inherit;
      line-height: 1.45;
      outline: none;
    }

    .admin-tools-card textarea:focus {
      border-color: var(--green2);
      box-shadow: 0 0 0 3px rgba(49, 84, 232, .12);
    }

    .sync-note {
      margin-top: 8px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.45;
    }

    .source-chip {
      display: inline-flex;
      margin-left: 6px;
      padding: 3px 7px;
      border-radius: 999px;
      background: #edf0ff;
      color: #4458b3;
      font-size: 10px;
      font-weight: 850;
      vertical-align: 1px;
    }
'''
    text = text.replace("  </style>", css + "\n  </style>", 1)

if JS_MARKER not in text:
    js = r'''

// UCL ADVANCED UX
let roundFilter = "next";
let adminRoundFilter = "next";
let uclSyncRunning = false;

function teamInitials(name) {
  const parts = String(name || "").trim().split(/\s+/).filter(Boolean);
  if (!parts.length) return "?";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

function teamLogoSide(name, logoUrl, side) {
  const fallback = '<span class="team-logo-fallback">' + esc(teamInitials(name)) + '</span>';
  const logo = logoUrl
    ? '<img class="team-logo" src="' + esc(logoUrl) + '" alt="" loading="lazy" onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'inline-flex\'">' +
      '<span class="team-logo-fallback" style="display:none">' + esc(teamInitials(name)) + '</span>'
    : fallback;

  if (side === "away") {
    return '<div class="team-logo-side away"><span class="team-logo-name">' + esc(name) + '</span>' + logo + '</div>';
  }
  return '<div class="team-logo-side">' + logo + '<span class="team-logo-name">' + esc(name) + '</span></div>';
}

function roundLabel(match) {
  if (match.round_name) return match.round_name;
  if (match.round_number) return 'Liigafaas · ' + match.round_number + '. voor';
  return 'Voor määramata';
}

function availableRoundNumbers() {
  return [...new Set(matches.map(m => Number(m.round_number)).filter(n => Number.isInteger(n) && n > 0))]
    .sort((a, b) => a - b);
}

function focusRoundNumber() {
  const rounds = availableRoundNumbers();
  for (const n of rounds) {
    const rows = matches.filter(m => Number(m.round_number) === n);
    if (rows.some(m => !isFinished(m))) return n;
  }
  return rounds.length ? rounds[rounds.length - 1] : null;
}

function matchesForRoundFilter(list, filter) {
  if (filter === "all") return list;
  if (filter === "next") {
    const n = focusRoundNumber();
    return n ? list.filter(m => Number(m.round_number) === n) : list;
  }
  const n = Number(filter);
  return Number.isInteger(n) ? list.filter(m => Number(m.round_number) === n) : list;
}

function setRoundFilter(value) {
  roundFilter = String(value);
  renderGames();
}

function setAdminRoundFilter(value) {
  adminRoundFilter = String(value);
  renderAdmin();
}

function roundFilterHtml(active, onclickName) {
  const rounds = availableRoundNumbers();
  let html = '<div class="round-filter-bar">';
  html += '<button class="round-filter-btn ' + (active === "next" ? "active" : "") + '" onclick="' + onclickName + '(\'next\')">Järgmine voor</button>';
  rounds.forEach(n => {
    html += '<button class="round-filter-btn ' + (String(active) === String(n) ? "active" : "") + '" onclick="' + onclickName + '(\'' + n + '\')">' + n + '. voor</button>';
  });
  html += '<button class="round-filter-btn ' + (active === "all" ? "active" : "") + '" onclick="' + onclickName + '(\'all\')">Kõik voorud</button>';
  html += '</div>';
  return html;
}

function latestCompletedRoundWinner() {
  const rounds = availableRoundNumbers().sort((a, b) => b - a);
  for (const n of rounds) {
    const roundMatches = matches.filter(m => Number(m.round_number) === n);
    if (!roundMatches.length || roundMatches.some(m => !isFinished(m))) continue;

    const ids = new Set(roundMatches.map(m => m.id));
    const scoreMap = new Map();
    predictions.filter(p => ids.has(p.match_id)).forEach(pred => {
      const match = roundMatches.find(m => m.id === pred.match_id);
      if (!match) return;
      const pts = calculatePoints(pred, match) || 0;
      const current = scoreMap.get(pred.user_id) || { points: 0, exact: 0 };
      current.points += pts;
      if (pts === 3) current.exact += 1;
      scoreMap.set(pred.user_id, current);
    });

    const rows = [...scoreMap.entries()].map(([playerId, stat]) => ({
      playerId,
      name: playerName(playerId),
      points: stat.points,
      exact: stat.exact,
    })).sort((a, b) => b.points - a.points || b.exact - a.exact || a.name.localeCompare(b.name, "et"));

    if (!rows.length) continue;
    const best = rows[0];
    const winners = rows.filter(r => r.points === best.points && r.exact === best.exact);
    return { round: n, winners, points: best.points, exact: best.exact };
  }
  return null;
}

function roundWinnerCardHtml() {
  const result = latestCompletedRoundWinner();
  if (!result) return "";
  const names = result.winners.map(w => esc(w.name)).join(" & ");
  return '<div class="card round-winner-card">' +
    '<div class="round-winner-eyebrow">Vooru parim · ' + result.round + '. voor</div>' +
    '<div class="round-winner-name">' + names + '</div>' +
    '<div class="round-winner-meta">' + result.points + ' punkti · ' + result.exact + ' täpset skoori</div>' +
  '</div>';
}

async function syncChampionsLeague(showMessage = false) {
  if (uclSyncRunning || !currentUser) return false;
  uclSyncRunning = true;
  try {
    const result = await sb.functions.invoke("sync-champions-league", { body: {} });
    if (result.error) throw result.error;
    const data = result.data || {};
    const changed = Number(data.fixtures_synced || 0) > 0 || Number(data.logos_synced || 0) > 0;
    if (showMessage) {
      if (changed) toast('Champions League’i andmed uuendatud.');
      else toast('Champions League’i andmed on juba värsked.');
    }
    return changed;
  } catch (error) {
    if (showMessage) toast('Automaatne uuendamine ebaõnnestus: ' + friendlyError(error));
    return false;
  } finally {
    uclSyncRunning = false;
  }
}

const __baseRenderPlayerSummary = renderPlayerSummary;
renderPlayerSummary = function() {
  const container = document.getElementById("playerSummary");
  if (!container || !currentUser) return;

  const row = leaderboard.find(item => item.player_id === currentUser.id);
  const points = row ? Number(row.total_points || 0) : 0;
  const rank = row ? row.rank_no : "–";
  const exact = row ? Number(row.exact_scores || 0) : 0;
  const focus = focusRoundNumber();
  const focusMatches = focus ? matches.filter(m => Number(m.round_number) === focus && !isStarted(m)) : matches.filter(m => !isStarted(m));
  const missing = focusMatches.filter(m => !hasOwnPrediction(m.id)).length;

  let reminder = "";
  if (focusMatches.length) {
    reminder = missing
      ? '<div class="prediction-reminder"><strong>' + focus + '. voor:</strong> sul on veel <strong>' + missing + '</strong> mängu ennustamata.</div>'
      : '<div class="prediction-reminder done"><strong>' + focus + '. voor:</strong> kõik mängud on ennustatud ✓</div>';
  }

  const installCard = isStandaloneMode() ? "" :
    '<div class="install-card">' +
      '<div class="install-card-title">Lisa Futbol avakuvale</div>' +
      '<div class="install-card-text">Futbol avaneb telefonis nagu eraldi rakendus. Play Store’i või App Store’i pole vaja.</div>' +
      '<div class="install-actions"><button class="btn btn-secondary btn-small" type="button" onclick="installFutbol()">Lisa avakuvale</button></div>' +
    '</div>';

  container.innerHTML =
    '<div class="player-summary">' +
      '<div class="summary-stat"><span class="summary-value">' + points + '</span><span class="summary-label">Minu punktid</span></div>' +
      '<div class="summary-stat"><span class="summary-value">' + rank + '</span><span class="summary-label">Koht tabelis</span></div>' +
      '<div class="summary-stat"><span class="summary-value">' + exact + '</span><span class="summary-label">Täpsed skoorid</span></div>' +
    '</div>' + reminder +
    '<div class="share-card">' +
      '<div class="share-top"><div class="share-card-text"><div class="share-card-title">Kutsu sõbrad Champions League’i ennustama</div><div class="share-card-subtitle">Jaga Futboli linki otse telefonist</div></div><button class="share-btn" onclick="shareFutbol()">Jaga</button></div>' +
      '<div class="share-apps">' +
        '<button class="share-app-btn" onclick="shareViaApp(\'whatsapp\')">WhatsApp</button>' +
        '<button class="share-app-btn" onclick="shareViaApp(\'messenger\')">Messenger</button>' +
        '<button class="share-app-btn" onclick="shareViaApp(\'viber\')">Viber</button>' +
        '<button class="share-app-btn" onclick="shareViaApp(\'instagram\')">Instagram</button>' +
        '<button class="share-app-btn" onclick="shareViaApp(\'telegram\')">Telegram</button>' +
        '<button class="share-app-btn" onclick="shareViaApp(\'facebook\')">Facebook</button>' +
        '<button class="share-app-btn" onclick="copyFutbolLink()">Kopeeri link</button>' +
      '</div>' +
    '</div>' + installCard;
};

const __baseRenderGames = renderGames;
renderGames = function() {
  const container = document.getElementById("games");
  if (!matches.length) {
    container.innerHTML = '<div class="card"><div class="notice">Ühtegi mängu pole veel lisatud.</div></div>';
    return;
  }

  let scopeMatches = matchesForRoundFilter(matches, roundFilter);
  const predictedCount = scopeMatches.filter(m => hasOwnPrediction(m.id)).length;
  const unpredictedCount = scopeMatches.length - predictedCount;

  let html = roundFilterHtml(roundFilter, "setRoundFilter") +
    '<div class="game-filters">' +
      '<button class="filter-btn ' + (gamesFilter === "all" ? "active" : "") + '" onclick="setGamesFilter(\'all\')">Kõik (' + scopeMatches.length + ')</button>' +
      '<button class="filter-btn ' + (gamesFilter === "predicted" ? "active" : "") + '" onclick="setGamesFilter(\'predicted\')">Ennustatud (' + predictedCount + ')</button>' +
      '<button class="filter-btn ' + (gamesFilter === "unpredicted" ? "active" : "") + '" onclick="setGamesFilter(\'unpredicted\')">Ennustamata (' + unpredictedCount + ')</button>' +
    '</div>';

  scopeMatches = scopeMatches.filter(match => {
    const own = hasOwnPrediction(match.id);
    if (gamesFilter === "predicted") return own;
    if (gamesFilter === "unpredicted") return !own;
    return true;
  });

  if (!scopeMatches.length) {
    container.innerHTML = html + '<div class="card"><div class="notice">Selle filtri all mänge ei ole.</div></div>';
    return;
  }

  const upcoming = scopeMatches.filter(m => !isStarted(m));
  const waiting = scopeMatches.filter(m => isStarted(m) && !isFinished(m));
  const finished = scopeMatches.filter(m => isFinished(m));

  const renderStatus = (title, rows) => {
    if (!rows.length) return;
    html += '<div class="match-group-title">' + esc(title) + '</div>';
    const roundGroups = new Map();
    rows.forEach(m => {
      const key = Number(m.round_number) || 999;
      if (!roundGroups.has(key)) roundGroups.set(key, []);
      roundGroups.get(key).push(m);
    });

    [...roundGroups.entries()].sort((a, b) => a[0] - b[0]).forEach(([roundNo, roundRows]) => {
      roundRows.sort((a, b) => new Date(a.kickoff_at) - new Date(b.kickoff_at));
      html += '<div class="round-section-title"><span>' + esc(roundLabel(roundRows[0])) + '</span><span class="round-section-count">' + roundRows.length + ' mängu</span></div>';

      roundRows.forEach(match => {
        const started = isStarted(match);
        const done = isFinished(match);
        const own = predictions.find(p => p.match_id === match.id && p.user_id === currentUser.id);
        const visiblePredictions = predictions.filter(p => p.match_id === match.id).sort((a, b) => playerName(a.user_id).localeCompare(playerName(b.user_id), "et"));
        let badgeClass = "badge-open", badgeText = "Avatud";
        if (started) { badgeClass = "badge-locked"; badgeText = "Lukus"; }
        if (done) { badgeClass = "badge-finished"; badgeText = "Lõppenud"; }

        html += '<article class="card">' +
          '<div class="match-header"><div>' +
            '<div class="match-title">' + esc(match.home_team) + ' – ' + esc(match.away_team) + '</div>' +
            '<div class="match-date">' + formatDate(match.kickoff_at) + ' · ' + formatTime(match.kickoff_at) + '</div>' +
            '<span class="round-chip">' + esc(roundLabel(match)) + '</span>' +
          '</div><div class="match-badges"><span class="badge ' + badgeClass + '">' + badgeText + '</span>' +
            (own && !started ? '<span class="own-prediction-badge">✓ Ennustatud ' + own.home_score + ' : ' + own.away_score + '</span>' : '') +
          '</div></div>';

        if (!started) html += '<div class="countdown" data-kickoff-countdown="' + esc(match.kickoff_at) + '">' + esc(countdownText(match.kickoff_at)) + '</div>';

        html += '<div class="teams-logo-grid">' +
          teamLogoSide(match.home_team, match.home_logo_url, "home") +
          '<div class="vs">VS</div>' +
          teamLogoSide(match.away_team, match.away_logo_url, "away") +
        '</div>';

        if (done) {
          html += '<div class="result">' + match.home_score + ' : ' + match.away_score + '</div>';
          if (match.went_to_extra_time) html += '<div class="hint">Tulemus sisaldab lisaaega. Penaltiseeria ei lähe skoori.</div>';
        }

        if (!started) {
          html += '<div class="score-entry">' +
            '<div class="score-label-left">' + esc(match.home_team) + '</div>' +
            '<input id="ph-' + match.id + '" class="score-input" type="number" min="0" max="30" inputmode="numeric" value="' + (own ? own.home_score : '') + '">' +
            '<div class="colon">:</div>' +
            '<input id="pa-' + match.id + '" class="score-input" type="number" min="0" max="30" inputmode="numeric" value="' + (own ? own.away_score : '') + '">' +
            '<div class="score-label-right">' + esc(match.away_team) + '</div></div>' +
            '<button class="btn btn-block" onclick="savePrediction(\'' + match.id + '\')">' + (own ? 'Muuda ennustust' : 'Salvesta ennustus') + '</button>' +
            '<div class="hint">Ennustamine lõpeb mängu alguses. Teiste ennustused on seni peidetud.</div>';
        } else {
          html += '<div class="notice">Ennustamine on lõppenud.</div>';
          if (own) {
            html += '<div class="my-prediction">Sinu ennustus: <strong>' + own.home_score + ' : ' + own.away_score + '</strong>';
            if (done) html += ' · <strong>' + calculatePoints(own, match) + ' p</strong>';
            html += '</div>';
          }
          html += '<div class="prediction-list">';
          if (!visiblePredictions.length) html += '<div class="hint">Sellele mängule ennustusi ei tehtud.</div>';
          else visiblePredictions.forEach(pred => {
            html += '<div class="prediction-row"><div>' + esc(playerName(pred.user_id)) + '</div><div class="prediction-score">' + pred.home_score + ' : ' + pred.away_score + '</div><div class="points">' + (done ? calculatePoints(pred, match) + ' p' : '') + '</div></div>';
          });
          html += '</div>';
        }
        html += '</article>';
      });
    });
  };

  renderStatus("Tulevased mängud", upcoming);
  renderStatus("Alanud – ootab tulemust", waiting);
  renderStatus("Lõppenud mängud", finished);
  container.innerHTML = html;
  refreshCountdowns();
};

const __baseRenderLeaderboard = renderLeaderboard;
renderLeaderboard = function() {
  const container = document.getElementById("leaderboard");
  if (!leaderboard.length) {
    container.innerHTML = roundWinnerCardHtml() + '<div class="card"><div class="notice">Tabel on veel tühi.</div></div>';
    return;
  }
  let html = roundWinnerCardHtml() + '<div class="card table-wrap"><table><thead><tr><th>Koht</th><th>Mängija</th><th class="num">Punktid</th><th class="num">Täpsed</th><th class="num">Enn.</th></tr></thead><tbody>';
  leaderboard.forEach(row => {
    const rank = Number(row.rank_no);
    const medal = rank === 1 ? "🥇" : rank === 2 ? "🥈" : rank === 3 ? "🥉" : "";
    const isSelf = currentUser && row.player_id === currentUser.id;
    html += '<tr class="' + (isSelf ? 'leaderboard-self' : '') + '"><td class="rank">' +
      (medal ? '<span class="rank-medal">' + medal + '</span>' : '') + row.rank_no + '</td>' +
      '<td class="' + (rank === 1 ? 'leader' : '') + '"><button class="player-name-btn" type="button" onclick="openPlayerStats(\'' + row.player_id + '\')">' + esc(row.player_name) + '</button>' +
      (isSelf ? '<span class="self-chip">Sina</span>' : '') + '</td>' +
      '<td class="num"><strong>' + row.total_points + '</strong></td><td class="num">' + row.exact_scores + '</td><td class="num">' + row.predictions_count + '</td></tr>';
  });
  container.innerHTML = html + '</tbody></table></div>';
};

const __baseRenderAdmin = renderAdmin;
renderAdmin = function() {
  if (!adminVerified) {
    __baseRenderAdmin();
    return;
  }

  const fullMatches = matches;
  matches = matchesForRoundFilter(fullMatches, adminRoundFilter);
  try {
    __baseRenderAdmin();
  } finally {
    matches = fullMatches;
  }

  const area = document.getElementById("adminArea");
  if (!area) return;

  const addHeading = [...area.querySelectorAll("h3")].find(el => el.textContent.trim() === "Lisa mäng");
  if (addHeading) {
    const card = addHeading.closest(".card");
    const grid = card && card.querySelector(".form-grid");
    if (grid && !document.getElementById("newRoundNumber")) {
      grid.insertAdjacentHTML("afterbegin",
        '<div><label>Vooru number</label><input id="newRoundNumber" class="input" type="number" min="1" max="20" inputmode="numeric" value="' + (focusRoundNumber() || 1) + '"></div>' +
        '<div><label>Vooru nimi</label><input id="newRoundName" class="input" value="Liigafaas · ' + (focusRoundNumber() || 1) + '. voor"></div>'
      );
    }
  }

  matchesForRoundFilter(fullMatches, adminRoundFilter).forEach(match => {
    const panel = document.getElementById("edit-" + match.id);
    const grid = panel && panel.querySelector(".form-grid");
    if (grid && !document.getElementById("ern-" + match.id)) {
      grid.insertAdjacentHTML("afterbegin",
        '<div><label>Vooru number</label><input id="ern-' + match.id + '" class="input" type="number" min="1" max="20" inputmode="numeric" value="' + (match.round_number || '') + '"></div>' +
        '<div><label>Vooru nimi</label><input id="ername-' + match.id + '" class="input" value="' + esc(roundLabel(match)) + '"></div>'
      );
    }
  });

  const managedHeading = [...area.querySelectorAll("h2")].find(el => el.textContent.trim() === "Hallatavad mängud");
  if (managedHeading && !document.getElementById("uclAdminTools")) {
    managedHeading.insertAdjacentHTML("beforebegin",
      '<div id="uclAdminTools">' +
        '<div class="card admin-tools-card">' +
          '<h3>Automaatne Champions League</h3>' +
          '<div>2026/27 liigafaasi mängud ja tulemused sünkroniseeritakse automaatselt.<span class="source-chip">Fixture Download</span></div>' +
          '<div class="sync-note">Rakendus kontrollib andmeid taustal. Admin saab vajadusel kontrolli kohe käivitada.</div>' +
          '<button class="btn btn-block" type="button" onclick="adminSyncChampionsLeague()">Sünkroniseeri nüüd</button>' +
        '</div>' +
        '<div class="card admin-tools-card">' +
          '<h3>Lisa mitu mängu korraga</h3>' +
          '<div class="form-grid">' +
            '<div><label>Vooru number</label><input id="bulkRoundNumber" class="input" type="number" min="1" max="20" inputmode="numeric" value="' + (focusRoundNumber() || 1) + '"></div>' +
            '<div><label>Kuupäev (PP.KK.AAAA)</label><input id="bulkDate" class="input" type="text" inputmode="numeric" maxlength="10" oninput="formatEuropeanDateInput(this)"></div>' +
            '<div><label>Vaikimisi kellaaeg</label><input id="bulkTime" class="input" type="text" inputmode="numeric" maxlength="5" value="22:00" oninput="formatEuropeanTimeInput(this)"></div>' +
            '<div><label>Mängud — üks mäng reale, meeskonnad eralda märgiga |</label><textarea id="bulkMatches" placeholder="Real Madrid | Inter\nPorto | Manchester City | 22:00"></textarea></div>' +
          '</div>' +
          '<button class="btn btn-block" type="button" onclick="adminBulkCreateMatches()">Lisa kõik mängud</button>' +
        '</div>' +
        '<div class="card"><h3>Hallatavate mängude voor</h3>' + roundFilterHtml(adminRoundFilter, "setAdminRoundFilter") + '</div>' +
      '</div>'
    );
  }
};

adminCreateMatch = async function() {
  const home = document.getElementById("newHome")?.value.trim() || "";
  const away = document.getElementById("newAway")?.value.trim() || "";
  const dateValue = document.getElementById("newKickoffDate")?.value || "";
  const timeValue = document.getElementById("newKickoffTime")?.value || "";
  const roundNumber = Number(document.getElementById("newRoundNumber")?.value || 0) || null;
  const roundNameValue = document.getElementById("newRoundName")?.value.trim() || (roundNumber ? 'Liigafaas · ' + roundNumber + '. voor' : '');
  if (!home || !away || !dateValue || !timeValue) { toast("Täida kõik mängu väljad."); return; }
  const kickoff = europeanKickoffToIso(dateValue, timeValue);
  if (!kickoff) { toast("Sisesta korrektne kuupäev ja kellaaeg."); return; }
  const result = await sb.rpc("admin_create_match_v2", {
    p_pin: adminPin, p_home_team: home, p_away_team: away, p_kickoff_at: kickoff,
    p_round_number: roundNumber, p_round_name: roundNameValue || null
  });
  if (result.error) { toast(friendlyError(result.error)); return; }
  toast("Mäng lisatud.");
  await loadAll();
};

adminUpdateMatch = async function(matchId) {
  const home = document.getElementById("eh-" + matchId)?.value.trim() || "";
  const away = document.getElementById("ea-" + matchId)?.value.trim() || "";
  const dateValue = document.getElementById("ekd-" + matchId)?.value || "";
  const timeValue = document.getElementById("ekt-" + matchId)?.value || "";
  const roundNumber = Number(document.getElementById("ern-" + matchId)?.value || 0) || null;
  const roundNameValue = document.getElementById("ername-" + matchId)?.value.trim() || (roundNumber ? 'Liigafaas · ' + roundNumber + '. voor' : '');
  const kickoff = europeanKickoffToIso(dateValue, timeValue);
  if (!home || !away || !kickoff) { toast("Kontrolli mängu andmeid."); return; }
  const result = await sb.rpc("admin_update_match_v2", {
    p_pin: adminPin, p_match_id: matchId, p_home_team: home, p_away_team: away,
    p_kickoff_at: kickoff, p_round_number: roundNumber, p_round_name: roundNameValue || null
  });
  if (result.error) { toast(friendlyError(result.error)); return; }
  toast("Mäng muudetud.");
  await loadAll();
};

async function adminBulkCreateMatches() {
  const dateValue = document.getElementById("bulkDate")?.value || "";
  const defaultTime = document.getElementById("bulkTime")?.value || "";
  const roundNumber = Number(document.getElementById("bulkRoundNumber")?.value || 0) || null;
  const raw = document.getElementById("bulkMatches")?.value || "";
  const lines = raw.split(/\r?\n/).map(x => x.trim()).filter(Boolean);
  if (!dateValue || !defaultTime || !lines.length) { toast("Sisesta kuupäev, kellaaeg ja vähemalt üks mäng."); return; }

  const rows = [];
  for (let i = 0; i < lines.length; i++) {
    const parts = lines[i].split("|").map(x => x.trim());
    if (parts.length < 2 || !parts[0] || !parts[1]) { toast("Viga real " + (i + 1) + ". Kasuta kuju: Kodumeeskond | Võõrsilmeeskond | kellaaeg"); return; }
    const time = parts[2] || defaultTime;
    const kickoff = europeanKickoffToIso(dateValue, time);
    if (!kickoff) { toast("Vigane kuupäev või kellaaeg real " + (i + 1) + "."); return; }
    rows.push({
      home_team: parts[0], away_team: parts[1], kickoff_at: kickoff,
      round_number: roundNumber, round_name: roundNumber ? 'Liigafaas · ' + roundNumber + '. voor' : null
    });
  }

  const result = await sb.rpc("admin_bulk_create_matches", { p_pin: adminPin, p_matches: rows });
  if (result.error) { toast(friendlyError(result.error)); return; }
  toast(Number(result.data || rows.length) + " mängu lisatud.");
  await loadAll();
}

async function adminSyncChampionsLeague() {
  const changed = await syncChampionsLeague(true);
  if (changed) await loadAll();
}

setInterval(async () => {
  if (currentUser && currentPlayer) {
    const changed = await syncChampionsLeague(false);
    if (changed) await loadAll();
  }
}, 15 * 60 * 1000);
'''
    text = text.replace("\ninit();", js + "\n\ninit();", 1)

# Trigger a non-blocking sync after the first normal load.
old = '''  await loadAll();
}

async function loadAll() {'''
new = '''  await loadAll();

  syncChampionsLeague(false).then(changed => {
    if (changed && currentUser && currentPlayer) {
      loadAll();
    }
  });
}

async function loadAll() {'''
if old in text and "syncChampionsLeague(false).then" not in text:
    text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8")
print("Added UCL advanced features")
