from pathlib import Path

path = Path("index.html")
text = path.read_text(encoding="utf-8")

CSS_MARKER = "/* FUTBOL DYNAMIC ROUND LEADERBOARD */"
JS_MARKER = "// FUTBOL DYNAMIC ROUND LEADERBOARD"

if CSS_MARKER not in text:
    css = r'''

    /* FUTBOL DYNAMIC ROUND LEADERBOARD */
    .leaderboard-dynamic {
      min-width: 560px;
    }
    .leaderboard-dynamic th,
    .leaderboard-dynamic td {
      white-space: nowrap;
    }
    .leaderboard-dynamic .round-history-cell {
      min-width: 64px;
      text-align: center;
      font-weight: 900;
      color: #334a9a;
    }
    .leaderboard-dynamic .round-history-cell.latest {
      background: #f1f4ff;
      color: #1d378f;
    }
    .leaderboard-dynamic th.round-history-head.latest {
      background: #e8edff;
      color: #1d378f;
    }
    .leaderboard-table-note {
      margin-top: 3px;
      color: var(--muted);
      font-size: 11px;
      line-height: 1.4;
    }
    @media (max-width: 520px) {
      .leaderboard-dynamic {
        min-width: 620px;
      }
    }
'''
    text = text.replace("  </style>", css + "\n  </style>", 1)

if JS_MARKER not in text:
    js = r'''

// FUTBOL DYNAMIC ROUND LEADERBOARD
function leaderboardVisibleRounds() {
  // A round appears only after at least one selected match in that round
  // has a recorded result. The points in that column then grow as more
  // results from the same round arrive.
  return scoredRounds();
}

renderLeaderboard = function() {
  const container = document.getElementById('leaderboard');
  if (!container) return;
  if (!leaderboard.length) {
    container.innerHTML = '<div class="card"><div class="notice">Tabel on veel tühi.</div></div>';
    return;
  }

  const rounds = leaderboardVisibleRounds();
  const latestRound = rounds.length ? rounds[rounds.length - 1] : null;
  const roundMaps = new Map(rounds.map(n => [n, roundStatMap(n)]));
  const leaderPoints = leaderboard.length
    ? Math.max(...leaderboard.map(item => Number(item.total_points || 0)))
    : 0;

  let html = (latestRound ? roundSummaryHtml(latestRound) : '') +
    '<div class="leaderboard-toolbar">' +
      '<div><div class="leaderboard-toolbar-title">Üldtabel</div>' +
      '<div class="leaderboard-table-note">Voor lisandub tabelisse pärast selle vooru esimese lõppenud mängu tulemuse sisestamist. Vooru punktid täienevad jooksvalt kuni vooru lõpuni.</div></div>' +
    '</div>' +
    '<div class="card table-wrap"><table class="leaderboard-plus leaderboard-dynamic"><thead><tr>' +
      '<th>Koht</th><th>Mängija</th>';

  rounds.forEach(n => {
    html += '<th class="num round-history-head ' + (n === latestRound ? 'latest' : '') + '">' + esc(competitionRoundShort(n)) + '</th>';
  });

  html += '<th class="num">Kokku</th><th class="num">Liidrist</th><th class="num">±</th>' +
    '</tr></thead><tbody>';

  leaderboard.forEach(row => {
    const rank = Number(row.rank_no);
    const medal = rank === 1 ? '🥇' : rank === 2 ? '🥈' : rank === 3 ? '🥉' : '';
    const isSelf = currentUser && row.player_id === currentUser.id;
    const total = Number(row.total_points || 0);
    const gapToLeader = Math.max(0, leaderPoints - total);

    html += '<tr class="' + (isSelf ? 'leaderboard-self' : '') + '">' +
      '<td class="rank">' + (medal ? '<span class="rank-medal">' + medal + '</span>' : '') + row.rank_no + '</td>' +
      '<td><button class="player-name-btn" onclick="openPlayerStats(\'' + row.player_id + '\')">' + esc(row.player_name) + '</button>' +
        '<div class="leader-player-meta">' + Number(row.exact_scores || 0) + ' täpset · ' + Number(row.predictions_count || 0) + ' ennustust</div></td>';

    rounds.forEach(n => {
      const stat = roundMaps.get(n)?.get(row.player_id) || { points: 0 };
      html += '<td class="num round-history-cell ' + (n === latestRound ? 'latest' : '') + '">' + Number(stat.points || 0) + '</td>';
    });

    html += '<td class="num leader-total-cell">' + total + '</td>' +
      '<td class="num leader-gap-cell">' + (gapToLeader === 0 ? '–' : '−' + gapToLeader) + '</td>' +
      '<td class="num">' + (latestRound ? rankMoveHtml(row.player_id, latestRound) : '<span class="rank-move same">–</span>') + '</td>' +
    '</tr>';
  });

  container.innerHTML = html + '</tbody></table></div>';
};
'''
    text = text.replace("\ninit();", js + "\n\ninit();", 1)

path.write_text(text, encoding="utf-8")
