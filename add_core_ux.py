from pathlib import Path

path = Path("index.html")
text = path.read_text(encoding="utf-8")

# --- CSS ---
css_anchor = "    .match-header {\n"
css_code = '''    .match-group-title {
      margin: 22px 2px 10px;
      color: var(--dark);
      font-size: 16px;
      font-weight: 950;
    }

    .match-group-title:first-child {
      margin-top: 4px;
    }

    .match-badges {
      display: flex;
      flex-direction: column;
      align-items: flex-end;
      gap: 6px;
    }

    .own-prediction-badge {
      display: inline-block;
      padding: 5px 9px;
      border-radius: 999px;
      background: var(--green-soft);
      color: var(--green);
      font-size: 12px;
      font-weight: 900;
      white-space: nowrap;
    }

    .countdown {
      margin: -2px 0 12px;
      padding: 9px 11px;
      border-radius: 11px;
      background: #f1f8f4;
      color: var(--green);
      font-size: 12px;
      font-weight: 850;
      text-align: center;
    }

    .rules-points {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 9px;
      margin-bottom: 14px;
    }

    .rule-point {
      padding: 13px 10px;
      border: 1px solid var(--border);
      border-radius: 14px;
      background: white;
      text-align: center;
    }

    .rule-points-value {
      display: block;
      color: var(--green);
      font-size: 23px;
      font-weight: 950;
    }

    .rule-points-label {
      display: block;
      margin-top: 4px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.35;
      font-weight: 700;
    }

    .rules-list {
      margin: 0;
      padding-left: 20px;
      color: var(--text);
      font-size: 14px;
      line-height: 1.55;
    }

    .rules-list li + li {
      margin-top: 8px;
    }

'''
if ".match-group-title {" not in text:
    if css_anchor not in text:
        raise SystemExit("CSS anchor not found")
    text = text.replace(css_anchor, css_code + css_anchor, 1)

text = text.replace(
    "      grid-template-columns: repeat(3, 1fr);\n    }\n\n    .nav-btn {",
    "      grid-template-columns: repeat(4, 1fr);\n    }\n\n    .nav-btn {",
    1,
)

# --- Rules tab HTML ---
rules_anchor = '''    <section id="tab-admin" class="hidden">
      <h2>Admin</h2>
      <div id="adminArea"></div>
    </section>'''
rules_html = '''    <section id="tab-rules" class="hidden">
      <h2>Reeglid</h2>

      <div class="card">
        <h3>Punktide jagamine</h3>
        <div class="rules-points">
          <div class="rule-point">
            <span class="rule-points-value">3 p</span>
            <span class="rule-points-label">Täpne lõppskoor</span>
          </div>
          <div class="rule-point">
            <span class="rule-points-value">1 p</span>
            <span class="rule-points-label">Õige võitja, vale skoor</span>
          </div>
          <div class="rule-point">
            <span class="rule-points-value">1 p</span>
            <span class="rule-points-label">Õige viik, vale viigiskoor</span>
          </div>
          <div class="rule-point">
            <span class="rule-points-value">0 p</span>
            <span class="rule-points-label">Vale mängutulemus</span>
          </div>
        </div>
      </div>

      <div class="card">
        <h3>Oluline teada</h3>
        <ul class="rules-list">
          <li>Ennustust saab sisestada ja muuta kuni mängu ametliku algusajani.</li>
          <li>Teiste mängijate ennustused on peidetud kuni mängu alguseni.</li>
          <li>Pärast mängu algust lukustub ennustus automaatselt.</li>
          <li>Kui mäng läheb lisaajale, arvestatakse tulemust pärast lisaaega.</li>
          <li>Penaltiseeria väravaid lõppskoori hulka ei arvestata.</li>
          <li>Üldtabelis järjestatakse mängijad punktide järgi; võrdsete punktide korral annab eelise suurem täpsete skooride arv.</li>
        </ul>
      </div>
    </section>

    <section id="tab-admin" class="hidden">
      <h2>Admin</h2>
      <div id="adminArea"></div>
    </section>'''
if 'id="tab-rules"' not in text:
    if rules_anchor not in text:
        raise SystemExit("Rules HTML anchor not found")
    text = text.replace(rules_anchor, rules_html, 1)

# --- Rules nav button ---
nav_anchor = '''      <button
        id="nav-admin"
        class="nav-btn"
        onclick="showTab('admin')"
      >
        Admin
      </button>'''
nav_html = '''      <button
        id="nav-rules"
        class="nav-btn"
        onclick="showTab('rules')"
      >
        Reeglid
      </button>

      <button
        id="nav-admin"
        class="nav-btn"
        onclick="showTab('admin')"
      >
        Admin
      </button>'''
if 'id="nav-rules"' not in text:
    if nav_anchor not in text:
        raise SystemExit("Rules nav anchor not found")
    text = text.replace(nav_anchor, nav_html, 1)

# --- Countdown helpers ---
helper_anchor = "function renderGames() {\n"
helper_code = r'''function countdownText(kickoffAt) {

  const diff = new Date(kickoffAt).getTime() - Date.now();

  if (diff <= 0) {
    return "Ennustamine on lõppenud";
  }

  const totalMinutes = Math.max(1, Math.ceil(diff / 60000));
  const days = Math.floor(totalMinutes / 1440);
  const hours = Math.floor((totalMinutes % 1440) / 60);
  const minutes = totalMinutes % 60;

  if (days > 0) {
    return "Ennustamine sulgub " + days + " p " + hours + " h pärast";
  }

  if (hours > 0) {
    return "Ennustamine sulgub " + hours + " h " + minutes + " min pärast";
  }

  return "Ennustamine sulgub " + minutes + " min pärast";
}

function refreshCountdowns() {

  document.querySelectorAll("[data-kickoff-countdown]")
    .forEach(el => {
      el.textContent = countdownText(el.dataset.kickoffCountdown);
    });
}

'''
if "function countdownText(" not in text:
    if helper_anchor not in text:
        raise SystemExit("Countdown helper anchor not found")
    text = text.replace(helper_anchor, helper_code + helper_anchor, 1)

# --- Replace renderGames with grouped version ---
start = text.find("function renderGames() {\n")
end = text.find("async function savePrediction(matchId) {\n")
if start == -1 or end == -1 or end <= start:
    raise SystemExit("renderGames boundaries not found")

current_render = text[start:end]
if "match-group-title" not in current_render:
    new_render = r'''function renderGames() {

  const container =
    document.getElementById("games");

  if (!matches.length) {

    container.innerHTML =
      '<div class="card">' +
      '<div class="notice">' +
      "Ühtegi mängu pole veel lisatud." +
      "</div></div>";

    return;
  }

  const upcoming = matches.filter(match => !isStarted(match));
  const waitingResult = matches.filter(match => isStarted(match) && !isFinished(match));
  const finishedMatches = matches.filter(match => isFinished(match));

  let html = "";

  const renderGroup = (title, groupMatches) => {

    if (!groupMatches.length) {
      return;
    }

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
            '<div class="match-title">' +
              esc(match.home_team) +
              " – " +
              esc(match.away_team) +
            "</div>" +
            '<div class="match-date">' +
              formatDate(match.kickoff_at) +
              " · " +
              formatTime(match.kickoff_at) +
            "</div>" +
          "</div>" +
          '<div class="match-badges">' +
            '<span class="badge ' + badgeClass + '">' + badgeText + "</span>" +
            (own && !started
              ? '<span class="own-prediction-badge">✓ Ennustatud ' +
                own.home_score + " : " + own.away_score + "</span>"
              : "") +
          "</div>" +
        "</div>";

      if (!started) {
        html +=
          '<div class="countdown" data-kickoff-countdown="' +
          esc(match.kickoff_at) +
          '">' +
          esc(countdownText(match.kickoff_at)) +
          "</div>";
      }

      html +=
        '<div class="teams">' +
          '<div class="team">' + esc(match.home_team) + "</div>" +
          '<div class="vs">VS</div>' +
          '<div class="team">' + esc(match.away_team) + "</div>" +
        "</div>";

      if (finished) {

        html +=
          '<div class="result">' +
            match.home_score + " : " + match.away_score +
          "</div>";

        if (match.went_to_extra_time) {
          html +=
            '<div class="hint">' +
            "Tulemus sisaldab lisaaega. Penaltiseeria ei lähe skoori." +
            "</div>";
        }
      }

      if (!started) {

        html +=
          '<div class="score-entry">' +
            '<div class="score-label-left">' + esc(match.home_team) + "</div>" +
            '<input id="ph-' + match.id + '" class="score-input" type="number" min="0" max="30" inputmode="numeric" value="' +
              (own ? own.home_score : "") + '">' +
            '<div class="colon">:</div>' +
            '<input id="pa-' + match.id + '" class="score-input" type="number" min="0" max="30" inputmode="numeric" value="' +
              (own ? own.away_score : "") + '">' +
            '<div class="score-label-right">' + esc(match.away_team) + "</div>" +
          "</div>";

        html +=
          '<button class="btn btn-block" onclick="savePrediction(\'' +
          match.id +
          '\')">' +
          (own ? "Muuda ennustust" : "Salvesta ennustus") +
          "</button>";

        html +=
          '<div class="hint">' +
          "Ennustamine lõpeb mängu alguses. Teiste ennustused on seni peidetud." +
          "</div>";

      } else {

        html +=
          '<div class="notice">Ennustamine on lõppenud.</div>';

        if (own) {

          html +=
            '<div class="my-prediction">' +
            "Sinu ennustus: <strong>" + own.home_score + " : " + own.away_score + "</strong>";

          if (finished) {
            html += " · <strong>" + calculatePoints(own, match) + " p</strong>";
          }

          html += "</div>";
        }

        html += '<div class="prediction-list">';

        if (!visiblePredictions.length) {
          html +=
            '<div class="hint">Sellele mängule ennustusi ei tehtud.</div>';
        } else {

          visiblePredictions.forEach(pred => {

            html +=
              '<div class="prediction-row">' +
                "<div>" + esc(playerName(pred.user_id)) + "</div>" +
                '<div class="prediction-score">' + pred.home_score + " : " + pred.away_score + "</div>" +
                '<div class="points">';

            if (finished) {
              html += calculatePoints(pred, match) + " p";
            }

            html += "</div></div>";
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
    text = text[:start] + new_render + text[end:]

# --- showTab supports rules ---
text = text.replace(
    '''  [
    "games",
    "table",
    "admin"
  ].forEach(tab => {''',
    '''  [
    "games",
    "table",
    "rules",
    "admin"
  ].forEach(tab => {''',
    1,
)

# Refresh only countdown text between full data refreshes.
interval_anchor = '''setInterval(() => {
  if (
    currentUser &&
    currentPlayer
  ) {
    loadAll();
  }
}, 60000);'''
interval_replacement = '''setInterval(() => {
  if (
    currentUser &&
    currentPlayer
  ) {
    loadAll();
  }
}, 60000);

setInterval(() => {
  if (currentUser && currentPlayer) {
    refreshCountdowns();
  }
}, 30000);'''
if "refreshCountdowns();\n  }\n}, 30000);" not in text:
    if interval_anchor not in text:
        raise SystemExit("Interval anchor not found")
    text = text.replace(interval_anchor, interval_replacement, 1)

path.write_text(text, encoding="utf-8")
