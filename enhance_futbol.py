from pathlib import Path

path = Path("index.html")
text = path.read_text(encoding="utf-8")

css_anchor = "    .match-header {\n"
css_insert = """    .player-summary {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;
      margin-bottom: 14px;
    }

    .summary-stat {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 12px 8px;
      text-align: center;
      box-shadow: var(--shadow);
    }

    .summary-value {
      display: block;
      font-size: 22px;
      line-height: 1.1;
      font-weight: 950;
      color: var(--green);
    }

    .summary-label {
      display: block;
      margin-top: 4px;
      font-size: 11px;
      color: var(--muted);
      font-weight: 700;
    }

    .share-card {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 12px 14px;
      margin-bottom: 14px;
      background: var(--dark);
      color: white;
      border-radius: 16px;
      box-shadow: var(--shadow);
    }

    .share-card-text {
      min-width: 0;
    }

    .share-card-title {
      font-weight: 900;
      font-size: 14px;
    }

    .share-card-subtitle {
      margin-top: 2px;
      color: #cddbd2;
      font-size: 11px;
    }

    .share-btn {
      flex: 0 0 auto;
      min-height: 42px;
      padding: 0 14px;
      border: 1px solid rgba(255,255,255,.2);
      border-radius: 11px;
      background: white;
      color: var(--dark);
      font-weight: 900;
    }

"""
if ".player-summary {" not in text:
    if css_anchor not in text:
        raise SystemExit("CSS anchor not found")
    text = text.replace(css_anchor, css_insert + css_anchor, 1)

html_anchor = """    <section id="tab-games">
      <h2>Mängud</h2>
      <div id="games"></div>
    </section>"""
html_replacement = """    <section id="tab-games">
      <h2>Mängud</h2>
      <div id="playerSummary"></div>
      <div id="games"></div>
    </section>"""
if 'id="playerSummary"' not in text:
    if html_anchor not in text:
        raise SystemExit("Games section anchor not found")
    text = text.replace(html_anchor, html_replacement, 1)

load_anchor = """  renderGames();
  renderLeaderboard();

  if (adminVerified) {"""
load_replacement = """  renderPlayerSummary();
  renderGames();
  renderLeaderboard();

  if (adminVerified) {"""
if "renderPlayerSummary();" not in text:
    if load_anchor not in text:
        raise SystemExit("loadAll anchor not found")
    text = text.replace(load_anchor, load_replacement, 1)

js_anchor = "function renderGames() {\n"
js_insert = r'''function renderPlayerSummary() {

  const container = document.getElementById("playerSummary");

  if (!container || !currentUser) {
    return;
  }

  const row = leaderboard.find(item => item.player_id === currentUser.id);
  const points = row ? Number(row.total_points || 0) : 0;
  const rank = row ? row.rank_no : "–";
  const exact = row ? Number(row.exact_scores || 0) : 0;

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
    '<div class="share-card">' +
      '<div class="share-card-text">' +
        '<div class="share-card-title">Kutsu sõbrad ennustama</div>' +
        '<div class="share-card-subtitle">Jaga Futboli linki otse telefonist</div>' +
      '</div>' +
      '<button class="share-btn" onclick="shareFutbol()">Jaga</button>' +
    '</div>';
}

async function shareFutbol() {

  const shareData = {
    title: "Futbol",
    text: "Tule ennusta meiega jalgpallimängude skoore!",
    url: window.location.href
  };

  try {
    if (navigator.share) {
      await navigator.share(shareData);
      return;
    }

    if (navigator.clipboard) {
      await navigator.clipboard.writeText(window.location.href);
      toast("Futboli link kopeeritud.");
      return;
    }

    window.prompt("Kopeeri Futboli link:", window.location.href);
  } catch (error) {
    if (error && error.name === "AbortError") {
      return;
    }

    toast("Lingi jagamine ebaõnnestus.");
  }
}

'''
if "function renderPlayerSummary()" not in text:
    if js_anchor not in text:
        raise SystemExit("renderGames anchor not found")
    text = text.replace(js_anchor, js_insert + js_anchor, 1)

path.write_text(text, encoding="utf-8")
