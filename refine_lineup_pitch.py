from pathlib import Path

INDEX = Path('index.html')
EDGE = Path('supabase/functions/ucl-lineups/index.ts')


def replace_between(text: str, start: str, end: str, replacement: str) -> str:
    a = text.find(start)
    if a == -1:
        raise SystemExit(f'start marker missing: {start}')
    b = text.find(end, a)
    if b == -1:
        raise SystemExit(f'end marker missing: {end}')
    return text[:a] + replacement.rstrip() + '\n\n' + text[b:]

# 1) Preserve FotMob's actual vertical pitch coordinates in the Edge Function response.
edge = EDGE.read_text(encoding='utf-8')
new_player_row = r'''function playerRow(player:any) {
  if (!player || typeof player !== "object") return null;
  const name = String(player?.name || player?.fullName || player?.playerName || "").trim();
  if (!name) return null;
  const rawNumber = player?.shirtNumber ?? player?.shirt ?? player?.shirtNo ?? null;
  const vertical = player?.verticalLayout || player?.vertical_layout || null;
  const layoutX = Number(vertical?.x);
  const layoutY = Number(vertical?.y);
  return {
    id: player?.id ?? player?.playerId ?? null,
    name,
    shirt_number: rawNumber == null ? null : String(rawNumber),
    position: String(player?.position || player?.role || "").trim() || null,
    position_id: player?.positionId ?? player?.position_id ?? null,
    layout_x: Number.isFinite(layoutX) ? layoutX : null,
    layout_y: Number.isFinite(layoutY) ? layoutY : null,
  };
}'''
edge = replace_between(edge, 'function playerRow(player:any) {', 'function uniquePlayers(rows:any[]) {', new_player_row)
EDGE.write_text(edge, encoding='utf-8')

# 2) Render starters on a football pitch. Exact FotMob coordinates are preferred;
#    formation-based positions are used only as a fallback.
text = INDEX.read_text(encoding='utf-8')
CSS_MARKER = '/* FUTBOL LINEUP PITCH UX V3 */'
if CSS_MARKER not in text:
    css = r'''

    /* FUTBOL LINEUP PITCH UX V3 */
    .match-lineups-grid { align-items:start; }
    .lineup-team-card { padding:10px; }
    .lineup-pitch {
      position:relative;
      width:100%;
      aspect-ratio:0.72;
      min-height:300px;
      margin-top:9px;
      overflow:hidden;
      border:2px solid rgba(255,255,255,.82);
      border-radius:12px;
      background:linear-gradient(180deg,#3d985d 0%,#2f854f 100%);
      box-shadow:inset 0 0 0 1px rgba(0,0,0,.06);
    }
    .lineup-pitch::before {
      content:'';
      position:absolute;
      left:0; right:0; top:50%;
      border-top:1px solid rgba(255,255,255,.72);
    }
    .lineup-pitch-center {
      position:absolute;
      left:50%; top:50%;
      width:25%; aspect-ratio:1;
      border:1px solid rgba(255,255,255,.72);
      border-radius:50%;
      transform:translate(-50%,-50%);
    }
    .lineup-pitch-center::after {
      content:'';
      position:absolute;
      left:50%; top:50%;
      width:4px; height:4px;
      border-radius:50%;
      background:rgba(255,255,255,.8);
      transform:translate(-50%,-50%);
    }
    .lineup-box {
      position:absolute;
      left:20%;
      width:60%;
      height:15%;
      border:1px solid rgba(255,255,255,.72);
    }
    .lineup-box.top { top:-1px; border-top:0; }
    .lineup-box.bottom { bottom:-1px; border-bottom:0; }
    .lineup-six {
      position:absolute;
      left:35%;
      width:30%;
      height:6%;
      border:1px solid rgba(255,255,255,.72);
    }
    .lineup-six.top { top:-1px; border-top:0; }
    .lineup-six.bottom { bottom:-1px; border-bottom:0; }
    .lineup-player-dot {
      position:absolute;
      z-index:3;
      width:58px;
      text-align:center;
      transform:translate(-50%,-50%);
    }
    .lineup-player-shirt {
      display:flex;
      align-items:center;
      justify-content:center;
      width:27px;
      height:27px;
      margin:0 auto 3px;
      border:2px solid rgba(255,255,255,.96);
      border-radius:50%;
      background:#173f2a;
      color:#fff;
      box-shadow:0 2px 5px rgba(0,0,0,.25);
      font-size:9px;
      font-weight:950;
    }
    .lineup-player-label {
      display:block;
      overflow:hidden;
      padding:2px 3px;
      border-radius:5px;
      background:rgba(19,47,32,.78);
      color:#fff;
      font-size:8px;
      font-weight:900;
      line-height:1.12;
      text-overflow:ellipsis;
      white-space:nowrap;
      text-shadow:0 1px 1px rgba(0,0,0,.28);
    }
    .lineup-bench-wrap { margin-top:9px; padding-top:8px; border-top:1px solid #edf2ef; }
    .lineup-layout-note { margin-top:6px; color:#87918b; font-size:8px; text-align:center; }
    @media (max-width:620px) {
      .match-lineups-grid { grid-template-columns:1fr; gap:10px; }
      .lineup-pitch { min-height:360px; aspect-ratio:.78; }
      .lineup-player-dot { width:66px; }
      .lineup-player-shirt { width:29px; height:29px; font-size:9.5px; }
      .lineup-player-label { font-size:8.5px; }
    }
'''
    text = text.replace('  </style>', css + '\n  </style>', 1)

new_render = r'''function lineupPlayerRowsHtml(players) {
  const rows = Array.isArray(players) ? players : [];
  return rows.map(player => {
    const number = String(player?.shirt_number ?? '').trim();
    return '<div class="lineup-player-row">' +
      '<span class="lineup-shirt">' + esc(number || '·') + '</span>' +
      '<span class="lineup-player-name">' + esc(player?.name || '') + '</span>' +
    '</div>';
  }).join('');
}

function lineupShortName(name) {
  const parts = String(name || '').trim().split(/\s+/).filter(Boolean);
  if (!parts.length) return '';
  const last = parts[parts.length - 1];
  return last.length > 12 ? last.slice(0, 11) + '…' : last;
}

function lineupFormationNumbers(formation) {
  return String(formation || '')
    .split('-')
    .map(value => Number(value))
    .filter(value => Number.isInteger(value) && value > 0 && value <= 6);
}

function lineupFallbackLayouts(players, formation) {
  const rows = lineupFormationNumbers(formation);
  const starters = Array.isArray(players) ? players : [];
  const output = new Map();
  if (!starters.length) return output;

  // FotMob starter order follows the formation: goalkeeper, defence, midfield, attack.
  // Use this only when FotMob's own verticalLayout is missing.
  let cursor = 0;
  const goalkeeper = starters[cursor++];
  if (goalkeeper) output.set(goalkeeper, { x:.5, y:.09 });

  const lineCounts = rows.reduce((sum, value) => sum + value, 0) === starters.length - 1
    ? rows
    : [Math.min(4, Math.max(1, starters.length - 1))];
  const lineTotal = lineCounts.length;
  lineCounts.forEach((count, lineIndex) => {
    const y = lineTotal === 1 ? .66 : .27 + (lineIndex * (.62 / Math.max(1, lineTotal - 1)));
    for (let i = 0; i < count && cursor < starters.length; i += 1) {
      const player = starters[cursor++];
      output.set(player, { x:(i + 1) / (count + 1), y });
    }
  });

  while (cursor < starters.length) {
    const player = starters[cursor];
    const remaining = starters.length - cursor;
    output.set(player, { x:(remaining === 1 ? .5 : (cursor % 4 + 1) / 5), y:.88 });
    cursor += 1;
  }
  return output;
}

function lineupClamp(value, min, max) {
  const number = Number(value);
  if (!Number.isFinite(number)) return null;
  return Math.min(max, Math.max(min, number));
}

function lineupPitchPlayerHtml(player, fallback) {
  const exactX = lineupClamp(player?.layout_x, .06, .94);
  const exactY = lineupClamp(player?.layout_y, .06, .94);
  const x = exactX ?? fallback?.x ?? .5;
  const y = exactY ?? fallback?.y ?? .5;
  const number = String(player?.shirt_number ?? '').trim();
  const label = lineupShortName(player?.name || '');
  return '<div class="lineup-player-dot" style="left:' + (x * 100).toFixed(2) + '%;top:' + (y * 100).toFixed(2) + '%" title="' + esc(player?.name || '') + '">' +
    '<span class="lineup-player-shirt">' + esc(number || '·') + '</span>' +
    '<span class="lineup-player-label">' + esc(label) + '</span>' +
  '</div>';
}

function lineupPitchHtml(starters, formation) {
  const players = Array.isArray(starters) ? starters : [];
  const fallback = lineupFallbackLayouts(players, formation);
  const hasExact = players.some(player => Number.isFinite(Number(player?.layout_x)) && Number.isFinite(Number(player?.layout_y)));
  return '<div class="lineup-pitch">' +
    '<div class="lineup-pitch-center"></div>' +
    '<div class="lineup-box top"></div><div class="lineup-box bottom"></div>' +
    '<div class="lineup-six top"></div><div class="lineup-six bottom"></div>' +
    players.map(player => lineupPitchPlayerHtml(player, fallback.get(player))).join('') +
  '</div>' +
  '<div class="lineup-layout-note">' + (hasExact ? 'FotMobi ametlik positsioonipaigutus' : 'Paigutus formatsiooni järgi') + '</div>';
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
    lineupPitchHtml(starters, formation) +
    (bench ? '<div class="lineup-bench-wrap"><div class="lineup-section-title">Varumängijad</div><div class="lineup-bench">' + esc(bench) + '</div></div>' : '') +
  '</div>';
}'''

text = replace_between(text, 'function lineupPlayerRowsHtml(players) {', 'function matchLineupsDetailsHtml(match, state) {', new_render)
INDEX.write_text(text, encoding='utf-8')

print('Lineup pitch UI and FotMob coordinates applied')
