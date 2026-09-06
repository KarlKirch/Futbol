from pathlib import Path

path = Path("index.html")
text = path.read_text(encoding="utf-8")

CSS_MARKER = "/* FUTBOL LEADER GAP UX */"

if CSS_MARKER not in text:
    css = r'''

    /* FUTBOL LEADER GAP UX */
    .leader-gap-cell {
      color: #687188;
      font-size: 12px;
      font-weight: 900;
      white-space: nowrap;
    }
    .leaderboard-self .leader-gap-cell {
      color: #176b43;
    }
'''
    text = text.replace("  </style>", css + "\n  </style>", 1)

old_header = "<th>Koht</th><th>Mängija</th><th class=\"num\">Voor</th><th class=\"num\">Kokku</th><th class=\"num\">±</th>"
new_header = "<th>Koht</th><th>Mängija</th><th class=\"num\">Voor</th><th class=\"num\">Kokku</th><th class=\"num\">Liidrist</th><th class=\"num\">±</th>"
text = text.replace(old_header, new_header)

old_round_stats = "  const roundStats = roundStatMap(round);\n"
new_round_stats = "  const roundStats = roundStatMap(round);\n  const leaderPoints = leaderboard.length ? Math.max(...leaderboard.map(item => Number(item.total_points || 0))) : 0;\n"
if "const leaderPoints = leaderboard.length" not in text:
    text = text.replace(old_round_stats, new_round_stats, 1)

old_rs = "    const rs = roundStats.get(row.player_id) || { points: 0, exact: 0, predicted: 0 };\n"
new_rs = "    const rs = roundStats.get(row.player_id) || { points: 0, exact: 0, predicted: 0 };\n    const gapToLeader = Math.max(0, leaderPoints - Number(row.total_points || 0));\n"
if "const gapToLeader =" not in text:
    text = text.replace(old_rs, new_rs, 1)

old_cells = "      '<td class=\"num leader-total-cell\">' + Number(row.total_points || 0) + '</td>' +\n      '<td class=\"num\">' + rankMoveHtml(row.player_id, round) + '</td>' +"
new_cells = "      '<td class=\"num leader-total-cell\">' + Number(row.total_points || 0) + '</td>' +\n      '<td class=\"num leader-gap-cell\">' + (gapToLeader === 0 ? '–' : '−' + gapToLeader) + '</td>' +\n      '<td class=\"num\">' + rankMoveHtml(row.player_id, round) + '</td>' +"
text = text.replace(old_cells, new_cells)

path.write_text(text, encoding="utf-8")
