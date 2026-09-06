from pathlib import Path

path = Path("index.html")
text = path.read_text(encoding="utf-8")

CSS_MARKER = "/* UCL CURATED SELECTION UX */"
JS_MARKER = "// UCL CURATED SELECTION UX"

if CSS_MARKER not in text:
    css = r'''

    /* UCL CURATED SELECTION UX */
    .fixture-picker-card {
      border: 1px solid #ccd6f6;
      background: linear-gradient(145deg, #fbfcff, #f3f5ff);
    }

    .fixture-picker-head {
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 10px;
    }

    .fixture-picker-head > div:first-child {
      flex: 1;
    }

    .fixture-check-list {
      margin-top: 12px;
      border-top: 1px solid var(--border);
    }

    .fixture-check-row {
      display: grid;
      grid-template-columns: 24px minmax(0, 1fr);
      align-items: center;
      gap: 10px;
      margin: 0;
      padding: 11px 2px;
      border-bottom: 1px solid #e8ecf6;
      color: var(--text);
      font-size: 14px;
      cursor: pointer;
    }

    .fixture-check-row input {
      width: 19px;
      height: 19px;
      margin: 0;
      accent-color: var(--green);
    }

    .fixture-check-title {
      font-weight: 850;
    }

    .fixture-check-meta {
      margin-top: 3px;
      color: var(--muted);
      font-size: 11px;
      font-weight: 650;
    }

    .history-hint {
      margin: 8px 0 2px;
      padding: 9px 11px;
      border-radius: 10px;
      background: #eef1ff;
      color: #4053a3;
      font-size: 12px;
      line-height: 1.4;
    }
'''
    text = text.replace("  </style>", css + "\n  </style>", 1)

if JS_MARKER not in text:
    js = r'''

// UCL CURATED SELECTION UX
let adminFixtureCatalog = [];
let adminFixtureCatalogLoaded = false;
let adminFixtureCatalogLoading = false;
let adminCatalogRound = null;

function uclRoundName(number) {
  const n = Number(number);
  return Number.isInteger(n) && n > 0 ? 'Liigafaas · ' + n + '. voor' : '';
}

function roundSelectOptions(selected, includeBlank = false, rounds = null) {
  const available = Array.isArray(rounds) && rounds.length
    ? rounds
    : [1,2,3,4,5,6,7,8];
  let html = includeBlank ? '<option value="">Vali voor</option>' : '';
  available.forEach(n => {
    html += '<option value="' + n + '" ' + (Number(selected) === Number(n) ? 'selected' : '') + '>' + n + '. voor</option>';
  });
  return html;
}

function isArchivedMatch(match) {
  if (!isFinished(match)) return false;
  const twoHours = 2 * 60 * 60 * 1000;
  if (match.finished_at) {
    const finished = new Date(match.finished_at).getTime();
    return Number.isFinite(finished) && Date.now() >= finished + twoHours;
  }
  const kickoff = new Date(match.kickoff_at).getTime();
  return Number.isFinite(kickoff) && Date.now() >= kickoff + (4 * 60 * 60 * 1000);
}

focusRoundNumber = function() {
  const rounds = availableRoundNumbers();
  for (const n of rounds) {
    const rows = matches.filter(m => Number(m.round_number) === n);
    if (rows.some(m => !isFinished(m))) return n;
    if (rows.some(m => isFinished(m) && !isArchivedMatch(m))) return n;
  }
  return rounds.length ? rounds[rounds.length - 1] : null;
};

const __curatedMatchesForRoundFilter = matchesForRoundFilter;
matchesForRoundFilter = function(list, filter) {
  if (filter === 'next') {
    const n = focusRoundNumber();
    const scoped = n ? list.filter(m => Number(m.round_number) === n) : list;
    return scoped.filter(m => !isArchivedMatch(m));
  }
  return __curatedMatchesForRoundFilter(list, filter);
};

async function loadAdminFixtureCatalog(force = false) {
  if (!adminVerified || !adminPin) return;
  if (adminFixtureCatalogLoading) return;
  if (adminFixtureCatalogLoaded && !force) return;

  adminFixtureCatalogLoading = true;
  try {
    const result = await sb.rpc('admin_get_ucl_fixtures', {
      p_pin: adminPin,
      p_round_number: null
    });
    if (result.error) throw result.error;
    adminFixtureCatalog = result.data || [];
    adminFixtureCatalogLoaded = true;

    const rounds = [...new Set(adminFixtureCatalog.map(x => Number(x.round_number)).filter(n => Number.isInteger(n) && n > 0))].sort((a,b) => a-b);
    if (!adminCatalogRound || !rounds.includes(Number(adminCatalogRound))) {
      const focus = focusRoundNumber();
      adminCatalogRound = rounds.includes(Number(focus)) ? Number(focus) : (rounds[0] || 1);
    }
  } catch (error) {
    toast('Mängude valiku laadimine ebaõnnestus: ' + friendlyError(error));
  } finally {
    adminFixtureCatalogLoading = false;
  }
}

function setAdminCatalogRound(value) {
  adminCatalogRound = Number(value) || 1;
  renderAdmin();
}

function catalogRoundNumbers() {
  const rounds = [...new Set(adminFixtureCatalog.map(x => Number(x.round_number)).filter(n => Number.isInteger(n) && n > 0))].sort((a,b) => a-b);
  return rounds.length ? rounds : [1,2,3,4,5,6,7,8];
}

function adminFixturePickerHtml() {
  if (!adminFixtureCatalogLoaded) {
    return '<div class="card fixture-picker-card"><h3>Vali ennustatavad mängud</h3><div class="hint" style="text-align:left">Laen Champions League’i mängukava…</div></div>';
  }

  const rounds = catalogRoundNumbers();
  const round = Number(adminCatalogRound) || rounds[0] || 1;
  const rows = adminFixtureCatalog.filter(x => Number(x.round_number) === round);

  let html = '<div class="card fixture-picker-card">' +
    '<div class="fixture-picker-head"><div><h3 style="margin:0">Vali ennustatavad mängud</h3>' +
    '<div class="hint" style="text-align:left;margin-top:5px">Automaatselt leitud mängud ei lähe enam ise avalehele. Märgi ainult need mängud, mida soovid ennustada, ja vajuta Kinnita valik.</div></div>' +
    '<div style="min-width:118px"><label>Voor</label><select id="catalogRoundSelect" class="input" onchange="setAdminCatalogRound(this.value)">' + roundSelectOptions(round, false, rounds) + '</select></div></div>';

  if (!rows.length) {
    html += '<div class="notice">Selle vooru mängukava pole veel saadaval.</div>';
  } else {
    html += '<div class="fixture-check-list">';
    rows.forEach(item => {
      html += '<label class="fixture-check-row">' +
        '<input class="ucl-fixture-check" type="checkbox" value="' + esc(item.external_match_id) + '" ' + (item.is_selected ? 'checked' : '') + '>' +
        '<span><span class="fixture-check-title">' + esc(item.home_team) + ' – ' + esc(item.away_team) + '</span>' +
        '<span class="fixture-check-meta">' + formatDate(item.kickoff_at) + ' · ' + formatTime(item.kickoff_at) + '</span></span>' +
      '</label>';
    });
    html += '</div>' +
      '<button class="btn btn-block" type="button" onclick="adminConfirmRoundSelection()">Kinnita valik</button>';
  }

  html += '</div>';
  return html;
}

async function adminConfirmRoundSelection() {
  const round = Number(adminCatalogRound);
  const ids = [...document.querySelectorAll('.ucl-fixture-check:checked')].map(el => el.value);
  const result = await sb.rpc('admin_set_round_selection', {
    p_pin: adminPin,
    p_round_number: round,
    p_external_ids: ids
  });
  if (result.error) {
    toast(friendlyError(result.error));
    return;
  }

  adminFixtureCatalogLoaded = false;
  await loadAdminFixtureCatalog(true);
  const info = result.data || {};
  if (Number(info.protected || 0) > 0) {
    toast('Valik salvestatud. ' + info.protected + ' alanud või ennustustega mäng jäi ajaloo kaitseks alles.');
  } else {
    toast('Valik salvestatud. Avalehel on nüüd ainult valitud mängud.');
  }
  await loadAll();
}

function replaceRoundInputWithSelect(id, selected) {
  const old = document.getElementById(id);
  if (!old || old.tagName === 'SELECT') return;
  const select = document.createElement('select');
  select.id = id;
  select.className = 'input';
  select.innerHTML = roundSelectOptions(selected || old.value || 1);
  old.replaceWith(select);
}

const __curatedBaseRenderAdmin = renderAdmin;
renderAdmin = function() {
  __curatedBaseRenderAdmin();
  if (!adminVerified) return;

  replaceRoundInputWithSelect('newRoundNumber', focusRoundNumber() || 1);
  const newRoundName = document.getElementById('newRoundName');
  if (newRoundName) newRoundName.closest('div')?.remove();

  replaceRoundInputWithSelect('bulkRoundNumber', focusRoundNumber() || 1);

  matches.forEach(match => {
    replaceRoundInputWithSelect('ern-' + match.id, match.round_number || 1);
    const nameEl = document.getElementById('ername-' + match.id);
    if (nameEl) nameEl.closest('div')?.remove();
  });

  const area = document.getElementById('adminArea');
  const tools = document.getElementById('uclAdminTools');
  if (area && tools && !document.getElementById('uclFixturePickerMount')) {
    const mount = document.createElement('div');
    mount.id = 'uclFixturePickerMount';
    mount.innerHTML = adminFixturePickerHtml();
    tools.insertAdjacentElement('beforebegin', mount);
  } else if (document.getElementById('uclFixturePickerMount')) {
    document.getElementById('uclFixturePickerMount').innerHTML = adminFixturePickerHtml();
  }

  if (!adminFixtureCatalogLoaded && !adminFixtureCatalogLoading) {
    loadAdminFixtureCatalog().then(() => {
      if (adminVerified) renderAdmin();
    });
  }
};

adminCreateMatch = async function() {
  const home = document.getElementById('newHome')?.value.trim() || '';
  const away = document.getElementById('newAway')?.value.trim() || '';
  const dateValue = document.getElementById('newKickoffDate')?.value || '';
  const timeValue = document.getElementById('newKickoffTime')?.value || '';
  const roundNumber = Number(document.getElementById('newRoundNumber')?.value || 0) || null;
  if (!home || !away || !dateValue || !timeValue || !roundNumber) { toast('Täida kõik mängu väljad ja vali voor.'); return; }
  const kickoff = europeanKickoffToIso(dateValue, timeValue);
  if (!kickoff) { toast('Sisesta korrektne kuupäev ja kellaaeg.'); return; }
  const result = await sb.rpc('admin_create_match_v2', {
    p_pin: adminPin,
    p_home_team: home,
    p_away_team: away,
    p_kickoff_at: kickoff,
    p_round_number: roundNumber,
    p_round_name: uclRoundName(roundNumber)
  });
  if (result.error) { toast(friendlyError(result.error)); return; }
  toast('Mäng lisatud.');
  await loadAll();
};

adminUpdateMatch = async function(matchId) {
  const home = document.getElementById('eh-' + matchId)?.value.trim() || '';
  const away = document.getElementById('ea-' + matchId)?.value.trim() || '';
  const dateValue = document.getElementById('ekd-' + matchId)?.value || '';
  const timeValue = document.getElementById('ekt-' + matchId)?.value || '';
  const roundNumber = Number(document.getElementById('ern-' + matchId)?.value || 0) || null;
  const kickoff = europeanKickoffToIso(dateValue, timeValue);
  if (!home || !away || !kickoff || !roundNumber) { toast('Kontrolli mängu andmeid ja vali voor.'); return; }
  const result = await sb.rpc('admin_update_match_v2', {
    p_pin: adminPin,
    p_match_id: matchId,
    p_home_team: home,
    p_away_team: away,
    p_kickoff_at: kickoff,
    p_round_number: roundNumber,
    p_round_name: uclRoundName(roundNumber)
  });
  if (result.error) { toast(friendlyError(result.error)); return; }
  toast('Mäng muudetud.');
  await loadAll();
};

adminBulkCreateMatches = async function() {
  const dateValue = document.getElementById('bulkDate')?.value || '';
  const defaultTime = document.getElementById('bulkTime')?.value || '';
  const roundNumber = Number(document.getElementById('bulkRoundNumber')?.value || 0) || null;
  const raw = document.getElementById('bulkMatches')?.value || '';
  const lines = raw.split(/\r?\n/).map(x => x.trim()).filter(Boolean);
  if (!dateValue || !defaultTime || !roundNumber || !lines.length) { toast('Vali voor ning sisesta kuupäev, kellaaeg ja vähemalt üks mäng.'); return; }

  const rows = [];
  for (let i = 0; i < lines.length; i++) {
    const parts = lines[i].split('|').map(x => x.trim());
    if (parts.length < 2 || !parts[0] || !parts[1]) { toast('Viga real ' + (i + 1) + '. Kasuta kuju: Kodumeeskond | Võõrsilmeeskond | kellaaeg'); return; }
    const kickoff = europeanKickoffToIso(dateValue, parts[2] || defaultTime);
    if (!kickoff) { toast('Vigane kuupäev või kellaaeg real ' + (i + 1) + '.'); return; }
    rows.push({ home_team: parts[0], away_team: parts[1], kickoff_at: kickoff, round_number: roundNumber, round_name: uclRoundName(roundNumber) });
  }

  const result = await sb.rpc('admin_bulk_create_matches', { p_pin: adminPin, p_matches: rows });
  if (result.error) { toast(friendlyError(result.error)); return; }
  toast(Number(result.data || rows.length) + ' mängu lisatud.');
  await loadAll();
};

syncChampionsLeague = async function(showMessage = false) {
  if (uclSyncRunning || !currentUser) return false;
  uclSyncRunning = true;
  try {
    const result = await sb.functions.invoke('sync-champions-league', { body: {} });
    if (result.error) throw result.error;
    const data = result.data || {};
    if (data.ok === false) throw new Error(data.error || 'Tundmatu sünkroonimisviga');
    const changed = Number(data.published_updated || 0) > 0 || Number(data.logos_synced || 0) > 0;
    if (adminVerified) {
      adminFixtureCatalogLoaded = false;
      await loadAdminFixtureCatalog(true);
    }
    if (showMessage) toast('Champions League’i mängukava kontrollitud ja uuendatud.');
    return changed;
  } catch (error) {
    if (showMessage) toast('Automaatne uuendamine ebaõnnestus: ' + friendlyError(error));
    return false;
  } finally {
    uclSyncRunning = false;
  }
};

adminSyncChampionsLeague = async function() {
  await syncChampionsLeague(true);
  adminFixtureCatalogLoaded = false;
  await loadAdminFixtureCatalog(true);
  await loadAll();
};

const __curatedShowTab = showTab;
showTab = function(name) {
  __curatedShowTab(name);
  if (name === 'games' && roundFilter !== 'next') {
    const container = document.getElementById('games');
    if (container && !container.querySelector('.history-hint')) {
      container.insertAdjacentHTML('afterbegin', '<div class="history-hint">Vooru valides näed ka selle vooru lõppenud mänge ja oma varasemaid ennustusi.</div>');
    }
  }
};
'''
    anchor = "\ninit();"
    pos = text.rfind(anchor)
    if pos == -1:
        raise SystemExit("init anchor not found")
    text = text[:pos] + js + text[pos:]

path.write_text(text, encoding="utf-8")
print("Added curated UCL round selection and history UX")
