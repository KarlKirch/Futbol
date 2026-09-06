from pathlib import Path

path = Path("index.html")
text = path.read_text(encoding="utf-8")

CSS_MARKER = "/* FUTBOL PAID ENTRY */"
JS_MARKER = "// FUTBOL PAID ENTRY"

if CSS_MARKER not in text:
    css = r'''

    /* FUTBOL PAID ENTRY */
    .payment-card {
      border: 1px solid #d9e0ef;
      background: #fff;
    }
    .payment-card.paid {
      border-color: #b8d9c5;
      background: #f4fbf6;
    }
    .payment-card.overdue {
      border-color: #e5c2c2;
      background: #fff8f8;
    }
    .payment-status-line {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 10px;
    }
    .payment-status-title {
      font-size: 15px;
      font-weight: 950;
    }
    .payment-status-badge {
      display: inline-flex;
      align-items: center;
      min-height: 28px;
      padding: 4px 9px;
      border-radius: 999px;
      background: #fff0cf;
      color: #7b5710;
      font-size: 11px;
      font-weight: 900;
      white-space: nowrap;
    }
    .payment-card.paid .payment-status-badge {
      background: #dff3e6;
      color: #176b43;
    }
    .payment-card.overdue .payment-status-badge {
      background: #fde4e4;
      color: #9c2d2d;
    }
    .payment-grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: 8px;
      margin: 10px 0;
    }
    .payment-field {
      padding: 10px 11px;
      border: 1px solid #e2e6ef;
      border-radius: 12px;
      background: rgba(255,255,255,.8);
    }
    .payment-field-label {
      display: block;
      margin-bottom: 3px;
      color: var(--muted);
      font-size: 10px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: .5px;
    }
    .payment-field-value {
      display: block;
      color: var(--text);
      font-size: 13px;
      font-weight: 900;
      overflow-wrap: anywhere;
    }
    .payment-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 10px;
    }
    .payment-deadline {
      margin-top: 9px;
      color: var(--muted);
      font-size: 11px;
      line-height: 1.45;
    }
    .payment-deadline.warning {
      color: #9c2d2d;
      font-weight: 800;
    }
    .payment-qr {
      display: flex;
      justify-content: center;
      margin-top: 12px;
      padding: 12px;
      border: 1px dashed #ccd4e3;
      border-radius: 14px;
      background: white;
    }
    .payment-qr > div,
    .payment-qr img,
    .payment-qr canvas {
      max-width: 180px !important;
      height: auto !important;
    }
    .payment-qr-note {
      margin-top: 7px;
      color: var(--muted);
      font-size: 10px;
      text-align: center;
    }
    .admin-payment-summary {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 8px;
      margin: 12px 0;
    }
    .admin-payment-stat {
      padding: 10px 8px;
      border: 1px solid var(--border);
      border-radius: 12px;
      text-align: center;
      background: #fafbfe;
    }
    .admin-payment-stat strong {
      display: block;
      font-size: 18px;
      color: #263d83;
    }
    .admin-payment-stat span {
      display: block;
      margin-top: 2px;
      color: var(--muted);
      font-size: 10px;
      font-weight: 750;
    }
    .admin-payment-row {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 10px;
      align-items: center;
      padding: 10px 0;
      border-top: 1px solid #edf0f5;
    }
    .admin-payment-row:first-of-type { border-top: 0; }
    .admin-payment-name { font-size: 13px; font-weight: 900; }
    .admin-payment-meta { margin-top: 3px; color: var(--muted); font-size: 10px; line-height: 1.4; }
    .admin-payment-paid { color: #176b43; font-weight: 900; }
    .admin-payment-unpaid { color: #9b6710; font-weight: 900; }
    .official-table-note {
      margin: 0 0 10px;
      padding: 9px 11px;
      border-radius: 11px;
      background: #f0f3ff;
      color: #34446f;
      font-size: 11px;
      line-height: 1.4;
      font-weight: 750;
    }
'''
    text = text.replace("  </style>", css + "\n  </style>", 1)

if JS_MARKER not in text:
    js = r'''

// FUTBOL PAID ENTRY
let paymentInfo = null;
let adminPaymentRows = [];
let paymentQrLoading = null;

function paidPlayerIdSet() {
  return new Set((leaderboard || []).map(row => row.player_id));
}

function eligiblePlayers() {
  const ids = paidPlayerIdSet();
  return (players || []).filter(player => ids.has(player.id));
}

async function loadPaymentInfo() {
  if (!currentUser || !currentPlayer) {
    paymentInfo = null;
    return;
  }
  const result = await sb.rpc('get_my_payment_info');
  if (result.error) {
    paymentInfo = null;
    return;
  }
  paymentInfo = Array.isArray(result.data) ? (result.data[0] || null) : (result.data || null);
}

async function loadAdminPayments() {
  if (!adminVerified || !adminPin) {
    adminPaymentRows = [];
    return;
  }
  const result = await sb.rpc('admin_get_payments', { p_pin: adminPin });
  adminPaymentRows = result.error ? [] : (result.data || []);
}

function paymentAmountText(value) {
  const n = Number(value || 10);
  return Number.isInteger(n) ? n + ' €' : n.toFixed(2).replace('.', ',') + ' €';
}

function paymentDeadlineText(info) {
  if (!info) return '';
  if (!info.entry_deadline) {
    return 'Osalustasu tähtaeg määratakse automaatselt esimese valitud ennustusmängu algusajaks.';
  }
  const text = 'Osalustasu tähtaeg: ' + formatDate(info.entry_deadline) + ' kell ' + formatTime(info.entry_deadline) + '.';
  if (!info.is_paid && info.deadline_passed) {
    return text + ' Tähtaeg on möödas. Sinu ennustused ei kuulu ametlikku tabelisse enne, kui admin osalemise erandina kinnitab.';
  }
  return text;
}

function paymentCardHtml() {
  if (!paymentInfo) return '';
  const paid = !!paymentInfo.is_paid;
  const overdue = !paid && !!paymentInfo.deadline_passed;
  const cls = 'card payment-card' + (paid ? ' paid' : '') + (overdue ? ' overdue' : '');
  const amount = paymentAmountText(paymentInfo.amount);
  let html = '<div class="' + cls + '">' +
    '<div class="payment-status-line">' +
      '<div><div class="payment-status-title">Osalustasu ' + esc(amount) + '</div>' +
      '<div class="hint" style="text-align:left;margin-top:2px">' + (paid ? 'Osalemine on kinnitatud.' : 'Ennustada saad kohe; ametlikku tabelisse jõuad pärast makse kinnitamist.') + '</div></div>' +
      '<span class="payment-status-badge">' + (paid ? '✓ Makstud' : (overdue ? 'Tähtaeg möödas' : 'Makse kinnitamata')) + '</span>' +
    '</div>';

  if (!paid) {
    html += '<div class="payment-grid">' +
      '<div class="payment-field"><span class="payment-field-label">Saaja</span><span class="payment-field-value">' + esc(paymentInfo.payee) + '</span></div>' +
      '<div class="payment-field"><span class="payment-field-label">IBAN</span><span class="payment-field-value">' + esc(paymentInfo.iban) + '</span></div>' +
      '<div class="payment-field"><span class="payment-field-label">Selgitus</span><span class="payment-field-value">' + esc(paymentInfo.payment_description) + '</span></div>' +
    '</div>' +
    '<div class="payment-actions">' +
      '<button class="btn btn-secondary btn-small" type="button" onclick="copyPaymentValue(\'iban\')">Kopeeri IBAN</button>' +
      '<button class="btn btn-secondary btn-small" type="button" onclick="copyPaymentValue(\'description\')">Kopeeri selgitus</button>' +
      '<button class="btn btn-secondary btn-small" type="button" onclick="copyPaymentValue(\'all\')">Kopeeri kõik</button>' +
      '<button class="btn btn-secondary btn-small" type="button" onclick="togglePaymentQr()">Makse QR</button>' +
    '</div>' +
    '<div id="paymentQrWrap" class="hidden"><div id="paymentQr" class="payment-qr"></div><div class="payment-qr-note">QR sisaldab SEPA makse andmeid. Kui pangarakendus seda ei loe, kasuta ülal olevaid kopeerimisnuppe.</div></div>';
  }

  const deadline = paymentDeadlineText(paymentInfo);
  if (deadline) html += '<div class="payment-deadline ' + (overdue ? 'warning' : '') + '">' + esc(deadline) + '</div>';
  html += '</div>';
  return html;
}

async function copyTextSafe(value, success) {
  try {
    if (navigator.clipboard) {
      await navigator.clipboard.writeText(value);
      toast(success);
      return;
    }
  } catch (_) {}
  window.prompt('Kopeeri:', value);
}

function copyPaymentValue(kind) {
  if (!paymentInfo) return;
  if (kind === 'iban') {
    copyTextSafe(String(paymentInfo.iban || ''), 'IBAN kopeeritud.');
    return;
  }
  if (kind === 'description') {
    copyTextSafe(String(paymentInfo.payment_description || ''), 'Makse selgitus kopeeritud.');
    return;
  }
  const textValue = [
    'Saaja: ' + paymentInfo.payee,
    'IBAN: ' + paymentInfo.iban,
    'Summa: ' + paymentAmountText(paymentInfo.amount),
    'Selgitus: ' + paymentInfo.payment_description
  ].join('\n');
  copyTextSafe(textValue, 'Makseandmed kopeeritud.');
}

function epcPaymentPayload(info) {
  const amount = Number(info.amount || 10).toFixed(2);
  return [
    'BCD',
    '002',
    '1',
    'SCT',
    '',
    String(info.payee || ''),
    String(info.iban || '').replace(/\s+/g, ''),
    'EUR' + amount,
    '',
    '',
    String(info.payment_description || ''),
    ''
  ].join('\n');
}

function loadPaymentQrLibrary() {
  if (window.QRCode) return Promise.resolve();
  if (paymentQrLoading) return paymentQrLoading;
  paymentQrLoading = new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/qrcodejs@1.0.0/qrcode.min.js';
    script.async = true;
    script.onload = resolve;
    script.onerror = reject;
    document.head.appendChild(script);
  });
  return paymentQrLoading;
}

async function togglePaymentQr() {
  const wrap = document.getElementById('paymentQrWrap');
  const mount = document.getElementById('paymentQr');
  if (!wrap || !mount || !paymentInfo) return;
  const opening = wrap.classList.contains('hidden');
  wrap.classList.toggle('hidden');
  if (!opening || mount.dataset.ready === '1') return;
  try {
    await loadPaymentQrLibrary();
    mount.innerHTML = '';
    new window.QRCode(mount, {
      text: epcPaymentPayload(paymentInfo),
      width: 180,
      height: 180,
      correctLevel: window.QRCode.CorrectLevel.M
    });
    mount.dataset.ready = '1';
  } catch (_) {
    wrap.classList.add('hidden');
    toast('QR-koodi loomine ebaõnnestus. Kasuta kopeerimisnuppe.');
  }
}

const __paidBaseLoadAll = loadAll;
loadAll = async function() {
  await __paidBaseLoadAll();
  await loadPaymentInfo();
  if (adminVerified) await loadAdminPayments();
  renderPlayerSummary();
  renderLeaderboard();
  if (adminVerified) renderAdmin();
};

const __paidBaseRenderPlayerSummary = renderPlayerSummary;
renderPlayerSummary = function() {
  const container = document.getElementById('playerSummary');
  if (!container || !currentUser) return;

  const row = leaderboard.find(item => item.player_id === currentUser.id);
  const points = row ? Number(row.total_points || 0) : 0;
  const rank = row ? row.rank_no : '–';
  const exact = row ? Number(row.exact_scores || 0) : 0;
  const focus = typeof focusRoundNumber === 'function' ? focusRoundNumber() : null;
  const focusMatches = focus
    ? matches.filter(m => Number(m.round_number) === focus && !isStarted(m))
    : matches.filter(m => !isStarted(m));
  const missing = focusMatches.filter(m => !hasOwnPrediction(m.id)).length;

  let reminder = '';
  if (focusMatches.length) {
    reminder = missing
      ? '<div class="prediction-reminder"><strong>' + (focus ? focus + '. voor: ' : '') + '</strong>sul on veel <strong>' + missing + '</strong> mängu ennustamata.</div>'
      : '<div class="prediction-reminder done"><strong>' + (focus ? focus + '. voor: ' : '') + '</strong>kõik mängud on ennustatud ✓</div>';
  }

  const installCard = isStandaloneMode() ? '' :
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
    '</div>' +
    paymentCardHtml() +
    reminder +
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

roundStatMap = function(roundNumber) {
  const eligible = paidPlayerIdSet();
  const matchRows = matches.filter(m => Number(m.round_number) === Number(roundNumber) && isFinished(m));
  const ids = new Set(matchRows.map(m => m.id));
  const map = new Map();
  predictions.filter(p => ids.has(p.match_id) && eligible.has(p.user_id)).forEach(pred => {
    const match = matchRows.find(m => m.id === pred.match_id);
    if (!match) return;
    const pts = Number(calculatePoints(pred, match) || 0);
    const stat = map.get(pred.user_id) || { points: 0, exact: 0, predicted: 0 };
    stat.points += pts;
    stat.exact += pts === 3 ? 1 : 0;
    stat.predicted += 1;
    map.set(pred.user_id, stat);
  });
  return map;
};

rankingThroughRound = function(roundNumber) {
  const maxRound = Number(roundNumber);
  const eligibleRows = eligiblePlayers();
  const eligible = new Set(eligibleRows.map(p => p.id));
  const usable = matches.filter(m => isFinished(m) && Number(m.round_number) <= maxRound);
  const ids = new Set(usable.map(m => m.id));
  const stats = new Map(eligibleRows.map(p => [p.id, { points: 0, exact: 0 }]));
  predictions.filter(p => ids.has(p.match_id) && eligible.has(p.user_id)).forEach(pred => {
    const match = usable.find(m => m.id === pred.match_id);
    if (!match) return;
    const pts = Number(calculatePoints(pred, match) || 0);
    const stat = stats.get(pred.user_id) || { points: 0, exact: 0 };
    stat.points += pts;
    stat.exact += pts === 3 ? 1 : 0;
    stats.set(pred.user_id, stat);
  });
  const rows = eligibleRows.map(p => ({
    id: p.id,
    name: p.display_name,
    points: (stats.get(p.id) || {}).points || 0,
    exact: (stats.get(p.id) || {}).exact || 0
  })).sort((a,b) => b.points - a.points || b.exact - a.exact || a.name.localeCompare(b.name, 'et'));
  const rank = new Map();
  rows.forEach((row, index) => rank.set(row.id, index + 1));
  return rank;
};

latestCompletedRoundWinner = function() {
  const eligible = paidPlayerIdSet();
  const rounds = availableRoundNumbers().sort((a, b) => b - a);
  for (const n of rounds) {
    const roundMatches = matches.filter(m => Number(m.round_number) === n);
    if (!roundMatches.length || roundMatches.some(m => !isFinished(m))) continue;
    const ids = new Set(roundMatches.map(m => m.id));
    const scoreMap = new Map();
    predictions.filter(p => ids.has(p.match_id) && eligible.has(p.user_id)).forEach(pred => {
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
      exact: stat.exact
    })).sort((a,b) => b.points - a.points || b.exact - a.exact || a.name.localeCompare(b.name, 'et'));
    if (!rows.length) continue;
    const best = rows[0];
    return {
      round: n,
      winners: rows.filter(r => r.points === best.points && r.exact === best.exact),
      points: best.points,
      exact: best.exact
    };
  }
  return null;
};

const __paidBaseRenderLeaderboard = renderLeaderboard;
renderLeaderboard = function() {
  const container = document.getElementById('leaderboard');
  if (!container) return;
  if (!leaderboard.length) {
    container.innerHTML = '<div class="card"><div class="notice"><strong>Ametlik tabel on veel tühi.</strong><br>Tabelisse ilmuvad ainult kasutajad, kelle 10 € osalustasu on admin kinnitanud.</div></div>';
    return;
  }
  __paidBaseRenderLeaderboard();
  if (!container.querySelector('.official-table-note')) {
    container.insertAdjacentHTML('afterbegin', '<div class="official-table-note">Ametlikus tabelis kuvatakse ainult kinnitatud osalejad. Maksmata kasutaja saab ennustada, kuid tema punktid lisanduvad tabelisse alles pärast makse kinnitamist.</div>');
  }
};

function adminPaymentsHtml() {
  const amount = paymentInfo ? Number(paymentInfo.amount || 10) : 10;
  const total = adminPaymentRows.length;
  const paid = adminPaymentRows.filter(row => row.is_paid).length;
  const unpaid = total - paid;
  const collected = paid * amount;
  const expected = total * amount;
  const deadline = adminPaymentRows.find(row => row.entry_deadline)?.entry_deadline || null;

  let html = '<div class="card" id="adminPaymentsCard">' +
    '<h3>Osalustasud</h3>' +
    '<div class="hint" style="text-align:left">Osalustasu on ' + esc(paymentAmountText(amount)) + ' inimese kohta. Makse laekumisel märgi kasutaja makstuks.</div>' +
    '<div class="admin-payment-summary">' +
      '<div class="admin-payment-stat"><strong>' + total + '</strong><span>Osalejaid</span></div>' +
      '<div class="admin-payment-stat"><strong>' + paid + '</strong><span>Tasunud</span></div>' +
      '<div class="admin-payment-stat"><strong>' + unpaid + '</strong><span>Maksmata</span></div>' +
      '<div class="admin-payment-stat"><strong>' + esc(paymentAmountText(collected)) + '</strong><span>Kogutud · oodatav ' + esc(paymentAmountText(expected)) + '</span></div>' +
    '</div>';

  html += '<div class="hint" style="text-align:left;margin-bottom:8px">' +
    (deadline ? 'Automaatne tähtaeg: ' + formatDate(deadline) + ' kell ' + formatTime(deadline) + '.' : 'Tähtaeg tekib automaatselt esimese valitud ennustusmängu algusaja järgi.') +
    ' Admin võib ka pärast tähtaega kasutaja makse kinnitada; see toimib erandina ja lisab tema punktid ametlikku tabelisse.' +
    '</div>';

  if (!adminPaymentRows.length) {
    html += '<div class="notice">Kasutajaid pole veel.</div>';
  } else {
    adminPaymentRows.forEach(row => {
      html += '<div class="admin-payment-row">' +
        '<div><div class="admin-payment-name">' + esc(row.player_name) + '</div>' +
        '<div class="admin-payment-meta">' + esc(row.payment_description) + '<br>' +
        (row.is_paid ? '<span class="admin-payment-paid">✓ Makstud</span>' : '<span class="admin-payment-unpaid">Maksmata</span>') + '</div></div>' +
        '<button class="btn ' + (row.is_paid ? 'btn-secondary' : '') + ' btn-small" type="button" onclick="adminSetPlayerPaid(\'' + row.player_id + '\',' + (row.is_paid ? 'false' : 'true') + ')">' +
          (row.is_paid ? 'Tühista kinnitus' : 'Märgi makstuks') +
        '</button>' +
      '</div>';
    });
  }
  return html + '</div>';
}

const __paidBaseRenderAdmin = renderAdmin;
renderAdmin = function() {
  __paidBaseRenderAdmin();
  if (!adminVerified) return;
  const area = document.getElementById('adminArea');
  if (!area || document.getElementById('adminPaymentsCard')) return;
  const firstCard = area.querySelector('.card');
  if (firstCard) firstCard.insertAdjacentHTML('afterend', adminPaymentsHtml());
  else area.insertAdjacentHTML('afterbegin', adminPaymentsHtml());
};

async function adminSetPlayerPaid(playerId, paid) {
  if (!adminVerified || !adminPin) return;
  const result = await sb.rpc('admin_set_player_paid', {
    p_pin: adminPin,
    p_player_id: playerId,
    p_paid: !!paid
  });
  if (result.error) {
    toast(friendlyError(result.error));
    return;
  }
  toast(paid ? 'Makse kinnitatud.' : 'Makse kinnitus tühistatud.');
  await loadAll();
}

const __paidBaseAdminLogin = adminLogin;
adminLogin = async function() {
  await __paidBaseAdminLogin();
  if (adminVerified) {
    await loadAdminPayments();
    renderAdmin();
  }
};

const __paidBaseAdminLogout = adminLogout;
adminLogout = function() {
  adminPaymentRows = [];
  __paidBaseAdminLogout();
};
'''
    text = text.replace("\ninit();", js + "\n\ninit();", 1)

path.write_text(text, encoding="utf-8")
