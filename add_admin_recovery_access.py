from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

CSS_MARKER = '/* FUTBOL ADMIN RECOVERY ACCESS */'
JS_MARKER = '// FUTBOL ADMIN RECOVERY ACCESS'

if CSS_MARKER not in text:
    css = r'''

    /* FUTBOL ADMIN RECOVERY ACCESS */
    .admin-access-recovery-card { border-color:#cfded5; background:linear-gradient(145deg,#fbfdfc,#fff); }
    .admin-access-recovery-row { display:grid; grid-template-columns:minmax(0,1fr) auto; gap:9px; align-items:center; margin-top:10px; }
    .admin-access-recovery-select { width:100%; min-height:44px; padding:0 11px; border:1px solid #cbd6cf; border-radius:11px; background:#fff; color:var(--text); font:inherit; }
    .admin-access-recovery-result { margin-top:10px; padding:11px 12px; border:1px dashed #9fbbaa; border-radius:12px; background:var(--green-soft); }
    .admin-access-recovery-code { display:block; margin-top:4px; color:var(--dark); font-size:20px; font-weight:950; letter-spacing:1.6px; word-break:break-all; }
    @media (max-width:520px) { .admin-access-recovery-row { grid-template-columns:1fr; } }
'''
    text = text.replace('  </style>', css + '\n  </style>', 1)

if JS_MARKER not in text:
    js = r'''

// FUTBOL ADMIN RECOVERY ACCESS
let adminIssuedRecoveryCode = '';

function adminRecoveryPlayerOptions() {
  const list = Array.isArray(players) ? players.slice() : [];
  list.sort((a,b) => String(a.display_name || '').localeCompare(String(b.display_name || ''), 'et'));
  return list.map(player => '<option value="' + esc(player.id) + '">' + esc(player.display_name || 'Nimetu') + '</option>').join('');
}

function adminAccessRecoveryCardHtml() {
  if (!adminVerified) return '';
  const options = adminRecoveryPlayerOptions();
  return '<div class="card admin-access-recovery-card">' +
    '<h3>Kasutaja ligipääsu taastamine</h3>' +
    '<div class="hint" style="text-align:left">Kui kasutaja nimi on juba olemas, kuid ta avab Futboli uues telefonis või brauseris, loo talle uus taastamiskood. Ennustused, makseinfo ja chati ajalugu jäävad alles.</div>' +
    '<div class="admin-access-recovery-row">' +
      '<select id="adminRecoveryPlayerSelect" class="admin-access-recovery-select">' + options + '</select>' +
      '<button class="btn btn-secondary btn-small" type="button" onclick="adminIssueRecoveryCodeUi()">Loo taastamiskood</button>' +
    '</div>' +
    '<div id="adminRecoveryCodeResult" class="admin-access-recovery-result hidden">' +
      '<div class="hint" style="text-align:left">Saada see kood ainult sellele kasutajale. Ta sisestab selle avakuval taastamiskoodi väljale.</div>' +
      '<span id="adminRecoveryCodeValue" class="admin-access-recovery-code"></span>' +
      '<button class="btn btn-secondary btn-small" style="margin-top:8px" type="button" onclick="copyAdminRecoveryCode()">Kopeeri kood</button>' +
    '</div>' +
  '</div>';
}

function mountAdminAccessRecoveryCard() {
  if (!adminVerified) return;
  const area = document.getElementById('adminArea');
  if (!area) return;
  area.querySelectorAll('.admin-access-recovery-card').forEach(el => el.remove());
  area.insertAdjacentHTML('afterbegin', adminAccessRecoveryCardHtml());
}

async function adminIssueRecoveryCodeUi() {
  if (!adminVerified || !adminPin) return;
  const select = document.getElementById('adminRecoveryPlayerSelect');
  const playerId = String(select?.value || '');
  if (!playerId) { toast('Vali kasutaja.'); return; }
  const player = (Array.isArray(players) ? players : []).find(p => String(p.id) === playerId);
  const name = player?.display_name || 'kasutaja';
  if (!window.confirm('Loon kasutajale ' + name + ' uue taastamiskoodi. Olemasolev kood muutub kehtetuks. Ennustused ja chat ei muutu.')) return;

  const result = await sb.rpc('admin_issue_player_recovery_code', {
    p_pin: adminPin,
    p_player_id: playerId
  });
  if (result.error) { toast(friendlyError(result.error)); return; }

  adminIssuedRecoveryCode = String(result.data || '').trim();
  const box = document.getElementById('adminRecoveryCodeResult');
  const value = document.getElementById('adminRecoveryCodeValue');
  if (value) value.textContent = adminIssuedRecoveryCode;
  if (box) box.classList.remove('hidden');
  toast('Taastamiskood loodud.');
}

async function copyAdminRecoveryCode() {
  if (!adminIssuedRecoveryCode) return;
  try {
    await navigator.clipboard.writeText(adminIssuedRecoveryCode);
    toast('Taastamiskood kopeeritud.');
  } catch (_) {
    toast('Koodi kopeerimine ebaõnnestus.');
  }
}

const __adminRecoveryBaseRenderAdmin = renderAdmin;
renderAdmin = function() {
  __adminRecoveryBaseRenderAdmin();
  mountAdminAccessRecoveryCard();
};
'''
    text = text.replace('\ninit();', js + '\n\ninit();', 1)

path.write_text(text, encoding='utf-8')
