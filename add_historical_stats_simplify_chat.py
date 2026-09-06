from pathlib import Path
import re

index_path = Path('index.html')
chat_path = Path('chat.js')
sw_path = Path('sw.js')

text = index_path.read_text(encoding='utf-8')
chat = chat_path.read_text(encoding='utf-8') if chat_path.exists() else ''
sw = sw_path.read_text(encoding='utf-8') if sw_path.exists() else ''

CSS_MARKER = '/* FUTBOL HISTORICAL UCL STATS + SIMPLE CHAT */'
JS_MARKER = '// FUTBOL HISTORICAL UCL STATS + SIMPLE CHAT'

if CSS_MARKER not in text:
    css = r'''

    /* FUTBOL HISTORICAL UCL STATS + SIMPLE CHAT */
    #adminChatDeep { display: none !important; }
    .chat-admin-delete, .chat-pin-label { display: none !important; }
    .historical-stats-head {
      display:flex;
      justify-content:space-between;
      align-items:flex-start;
      gap:10px;
      margin-bottom:10px;
    }
    .historical-stats-title { color:#1f3477; font-size:13px; font-weight:950; }
    .historical-stats-range { color:#778198; font-size:9px; font-weight:800; text-align:right; }
    .historical-team-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px; }
    .historical-team-card { padding:10px; border:1px solid #e1e5ef; border-radius:11px; background:white; }
    .historical-team-name { font-size:12px; font-weight:950; color:#1e2e66; }
    .historical-main-stat { margin-top:5px; font-size:10px; color:#657087; line-height:1.5; }
    .historical-main-stat strong { color:#1d316f; }
    .historical-season-list { margin-top:9px; border-top:1px solid #edf0f5; padding-top:7px; }
    .historical-season-row { display:grid; grid-template-columns:58px 1fr; gap:7px; padding:3px 0; color:#647086; font-size:9px; }
    .historical-season-row strong { color:#344777; }
    .historical-recent { display:flex; flex-wrap:wrap; gap:4px; margin-top:7px; }
    .historical-result-pill { min-width:22px; height:22px; display:inline-flex; align-items:center; justify-content:center; border-radius:50%; background:#edf0f5; color:#687080; font-size:9px; font-weight:950; }
    .historical-result-pill.w { background:#dff3e6; color:#176b43; }
    .historical-result-pill.d { background:#fff0cf; color:#7b5710; }
    .historical-result-pill.l { background:#fde4e4; color:#9c2d2d; }
    .historical-h2h { margin-top:10px; padding-top:9px; border-top:1px solid #e1e5ef; }
    .historical-h2h-title { color:#334777; font-size:10px; font-weight:950; }
    .historical-h2h-row { display:grid; grid-template-columns:62px 1fr auto; gap:7px; padding:5px 0; border-bottom:1px solid #f0f2f6; color:#5e687d; font-size:9px; }
    .historical-source { margin-top:8px; color:#8a91a0; font-size:8px; line-height:1.4; }
    @media (max-width:520px) {
      .historical-team-grid { grid-template-columns:1fr; }
    }
'''
    text = text.replace('  </style>', css + '\n  </style>', 1)

# Older generated app shells may already contain the marker from the first pass.
if '.chat-admin-delete, .chat-pin-label { display: none !important; }' not in text:
    text = text.replace(
        '#adminChatDeep { display: none !important; }',
        '#adminChatDeep { display: none !important; }\n    .chat-admin-delete, .chat-pin-label { display: none !important; }',
        1
    )

if JS_MARKER not in text:
    js = r'''

// FUTBOL HISTORICAL UCL STATS + SIMPLE CHAT
const historicalInsightsCache = new Map();

function historicalSeasonRowsHtml(team) {
  const rows = Array.isArray(team?.seasons) ? team.seasons : [];
  if (!rows.length) return '<div class="hint" style="text-align:left;margin-top:7px">Selle perioodi CL tulemusi ei leitud.</div>';
  return '<div class="historical-season-list">' + rows.map(row =>
    '<div class="historical-season-row"><strong>' + esc(row.season) + '</strong><span>' +
      Number(row.matches || 0) + ' m · ' + Number(row.wins || 0) + 'V ' + Number(row.draws || 0) + 'Vi ' + Number(row.losses || 0) + 'K · väravad ' + Number(row.gf || 0) + ':' + Number(row.ga || 0) +
    '</span></div>'
  ).join('') + '</div>';
}

function historicalRecentHtml(team) {
  const recent = Array.isArray(team?.recent) ? team.recent.slice(0, 10) : [];
  if (!recent.length) return '';
  return '<div class="historical-recent" title="Viimased CL mängud">' + recent.map(row => {
    const r = String(row.result || '').toLowerCase();
    return '<span class="historical-result-pill ' + (r === 'w' ? 'w' : r === 'd' ? 'd' : 'l') + '" title="' + esc(row.home_team + ' ' + row.home_score + ':' + row.away_score + ' ' + row.away_team + ' · ' + row.season) + '">' +
      (r === 'w' ? 'V' : r === 'd' ? 'Vi' : 'K') + '</span>';
  }).join('') + '</div>';
}

function historicalTeamHtml(team) {
  return '<div class="historical-team-card">' +
    '<div class="historical-team-name">' + esc(team?.team || '') + '</div>' +
    '<div class="historical-main-stat"><strong>' + Number(team?.matches || 0) + ' CL mängu</strong> · ' +
      Number(team?.wins || 0) + ' võitu · ' + Number(team?.draws || 0) + ' viiki · ' + Number(team?.losses || 0) + ' kaotust<br>' +
      'Väravad ' + Number(team?.goals_for || 0) + ':' + Number(team?.goals_against || 0) + ' · võiduprotsent ' + Number(team?.win_rate || 0) + '%</div>' +
    historicalRecentHtml(team) +
    historicalSeasonRowsHtml(team) +
  '</div>';
}

function historicalInsightsHtml(data) {
  const h2h = Array.isArray(data?.h2h) ? data.h2h : [];
  let h2hHtml = '<div class="historical-h2h"><div class="historical-h2h-title">Omavahelised CL mängud selles perioodis</div>';
  if (!h2h.length) {
    h2hHtml += '<div class="hint" style="text-align:left;margin-top:6px">Omavahelisi CL mänge ei leitud.</div>';
  } else {
    h2hHtml += h2h.slice(0, 10).map(row =>
      '<div class="historical-h2h-row"><span>' + esc(row.season) + '</span><span>' + esc(row.home_team) + ' – ' + esc(row.away_team) + '</span><strong>' + Number(row.home_score) + ':' + Number(row.away_score) + '</strong></div>'
    ).join('');
  }
  h2hHtml += '</div>';

  const seasons = Array.isArray(data?.seasons_loaded) ? data.seasons_loaded : [];
  return '<div class="historical-stats-head"><div><div class="historical-stats-title">Champions League’i ajalooline statistika</div>' +
    '<div class="hint" style="text-align:left;margin-top:2px">Vorm ja tulemused mitme hooaja lõikes.</div></div>' +
    '<div class="historical-stats-range">' + esc(data?.range_label || '') + '<br>' + seasons.length + ' hooaega</div></div>' +
    '<div class="historical-team-grid">' + historicalTeamHtml(data?.home) + historicalTeamHtml(data?.away) + '</div>' +
    h2hHtml +
    '<div class="historical-source">Allikas: Fixture Download. Arvesse lähevad lõpetatud UEFA Champions League’i mängud; meeskonnanimed ühtlustatakse eri hooaegade vahel.</div>';
}

const __historicalBaseToggleMatchInsights = toggleMatchInsightsDeep;
toggleMatchInsightsDeep = async function(matchId) {
  const mount = document.getElementById('insight-' + matchId);
  const match = matches.find(m => m.id === matchId);
  if (!mount || !match) return;
  const opening = mount.classList.contains('hidden');
  mount.classList.toggle('hidden');
  if (!opening) return;

  if (historicalInsightsCache.has(matchId)) {
    mount.innerHTML = historicalInsightsHtml(historicalInsightsCache.get(matchId));
    return;
  }

  mount.innerHTML = '<div class="hint">Laen viimaste hooaegade Champions League’i statistikat…</div>';
  try {
    const result = await sb.functions.invoke('ucl-historical-stats', {
      body: { home_team: match.home_team, away_team: match.away_team }
    });
    if (result.error || !result.data || result.data.ok === false) {
      throw result.error || new Error(result.data?.error || 'Statistika laadimine ebaõnnestus');
    }
    historicalInsightsCache.set(matchId, result.data);
    mount.innerHTML = historicalInsightsHtml(result.data);
  } catch (error) {
    mount.innerHTML = '<div class="hint">Ajaloolise statistika laadimine ebaõnnestus. Proovi mõne hetke pärast uuesti.</div>';
  }
};

const __historicalBaseRenderGames = renderGames;
renderGames = function() {
  __historicalBaseRenderGames();
  document.querySelectorAll('#games .match-insight-btn').forEach(btn => {
    btn.textContent = '📊 Mängu statistika · 5+ hooaega';
  });
};

const __simpleChatBaseRenderAdmin = renderAdmin;
renderAdmin = function() {
  __simpleChatBaseRenderAdmin();
  const moderation = document.getElementById('adminChatDeep');
  if (moderation) moderation.remove();
};
'''
    pos = text.rfind('\n\ninit();')
    if pos == -1:
        raise SystemExit('init anchor not found')
    text = text[:pos] + js + text[pos:]

# Chat stays a simple chronological conversation. Legacy announcement columns may remain in storage,
# but their pin and delete controls are not exposed in the user interface.
if chat:
    chat = re.sub(
        r"\s*var pinnedMessages = chatMessages\.filter\(function \(item\) \{ return !!item\.pinned; \}\);\n\s*var regularMessages = chatMessages\.filter\(function \(item\) \{ return !item\.pinned; \}\);\n\s*box\.innerHTML = pinnedMessages\.concat\(regularMessages\)\.map",
        "\n    box.innerHTML = chatMessages.map",
        chat,
        count=1
    )
    chat = chat.replace(
        "return '<div class=\"chat-message ' + (own ? 'own ' : '') + (item.is_announcement ? 'announcement' : '') + '\">' +",
        "return '<div class=\"chat-message ' + (own ? 'own' : '') + '\">' +"
    )

# Force installed/PWA clients to receive the new chat and app shell.
text = re.sub(r'chat\.js\?v=\d+', 'chat.js?v=6', text)
if sw:
    sw = re.sub(r'const CACHE_NAME = "futbol-champions-v\d+";', 'const CACHE_NAME = "futbol-champions-v6";', sw)
    sw = re.sub(r'"\./chat\.js\?v=\d+"', '"./chat.js?v=6"', sw)

index_path.write_text(text, encoding='utf-8')
if chat_path.exists(): chat_path.write_text(chat, encoding='utf-8')
if sw_path.exists(): sw_path.write_text(sw, encoding='utf-8')
print('Added historical UCL stats and simplified chat')
