from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

CSS_MARKER = '/* FUTBOL BONUS VISIBILITY */'
JS_MARKER = '// FUTBOL BONUS VISIBILITY'

if CSS_MARKER not in text:
    css = r'''

    /* FUTBOL BONUS VISIBILITY */
    .bonus-reveal-card { border-color:#cbd5f4; background:linear-gradient(145deg,#f7f9ff,#fff); }
    .bonus-reveal-intro { margin:-3px 0 10px; color:#707992; font-size:11px; line-height:1.45; }
    .bonus-reveal-question { margin-top:12px; padding-top:10px; border-top:1px solid #e4e8f4; }
    .bonus-reveal-question:first-of-type { margin-top:6px; padding-top:0; border-top:0; }
    .bonus-reveal-title { color:#1d2f71; font-size:13px; font-weight:950; }
    .bonus-reveal-row { display:grid; grid-template-columns:minmax(0,1fr) minmax(110px,42%); gap:10px; padding:7px 0; border-top:1px solid #f0f2f7; font-size:12px; }
    .bonus-reveal-row:first-of-type { border-top:0; }
    .bonus-reveal-name { font-weight:850; }
    .bonus-reveal-answer { text-align:right; color:#334a9a; font-weight:850; overflow-wrap:anywhere; }
    .bonus-reveal-answer.missing { color:#9a6a18; font-weight:800; }
    .admin-bonus-missing-card { border-color:#eadbb7; background:#fffdf7; }
    .admin-bonus-missing-block { margin-top:10px; padding-top:9px; border-top:1px solid #eee4cc; }
    .admin-bonus-missing-block:first-of-type { border-top:0; padding-top:0; }
    .admin-bonus-missing-names { margin-top:4px; color:#5f5540; font-size:11px; line-height:1.5; }
'''
    text = text.replace('  </style>', css + '\n  </style>', 1)

rule_line = '          <li>Vastuseid saab muuta kuni 1. vooru esimese valitud mängu alguseni. Seejärel lukustuvad mõlemad vastused automaatselt.</li>'
rule_extra = '          <li>Pärast lukustumist muutuvad kõigi osalejate boonusvastused kõigile nähtavaks.</li>'
if rule_extra not in text and rule_line in text:
    text = text.replace(rule_line, rule_line + '\n' + rule_extra, 1)

if JS_MARKER not in text:
    js = r'''

// FUTBOL BONUS VISIBILITY
let lockedBonusAnswersState = [];
let adminBonusMissingState = [];

const __bonusVisibilityBaseLoadDeep = loadDeepCompetitionData;
loadDeepCompetitionData = async function() {
  await __bonusVisibilityBaseLoadDeep();
  if (!currentUser || !currentPlayer || !bonusDeadlinePassedFix()) {
    lockedBonusAnswersState = [];
    return;
  }
  const result = await sb.rpc('get_locked_bonus_answers');
  if (result.error) {
    console.error('Locked bonus answers error', result.error);
    lockedBonusAnswersState = [];
    return;
  }
  lockedBonusAnswersState = result.data || [];
};

const __bonusVisibilityBaseLoadAdmin = loadAdminDeepData;
loadAdminDeepData = async function() {
  await __bonusVisibilityBaseLoadAdmin();
  if (!adminVerified || !adminPin) {
    adminBonusMissingState = [];
    return;
  }
  const result = await sb.rpc('admin_get_bonus_missing', { p_pin: adminPin });
  if (result.error) {
    console.error('Admin bonus missing error', result.error);
    adminBonusMissingState = [];
    return;
  }
  adminBonusMissingState = result.data || [];
};

function lockedBonusAnswersHtml() {
  if (!bonusDeadlinePassedFix() || !Array.isArray(lockedBonusAnswersState) || !lockedBonusAnswersState.length) return '';

  const grouped = new Map();
  lockedBonusAnswersState.forEach(row => {
    const key = String(row.question_key || '');
    if (!grouped.has(key)) grouped.set(key, []);
    grouped.get(key).push(row);
  });

  let questions = '';
  grouped.forEach(rows => {
    const title = rows[0]?.title || '';
    const list = rows.map(row => {
      const hasAnswer = String(row.answer_text || '').trim().length > 0;
      return '<div class="bonus-reveal-row">' +
        '<div class="bonus-reveal-name">' + esc(row.player_name || '–') + '</div>' +
        '<div class="bonus-reveal-answer ' + (hasAnswer ? '' : 'missing') + '">' + esc(hasAnswer ? row.answer_text : 'Vastamata') + '</div>' +
      '</div>';
    }).join('');
    questions += '<div class="bonus-reveal-question"><div class="bonus-reveal-title">' + esc(title) + '</div>' + list + '</div>';
  });

  return '<div class="recovery-card bonus-reveal-card">' +
    '<div class="recovery-card-title">Kõigi boonusvastused</div>' +
    '<div class="bonus-reveal-intro">Vastused on lukus ja nüüd kõigile osalejatele nähtavad.</div>' +
    questions +
  '</div>';
}

function adminBonusMissingHtml() {
  if (!adminVerified || !Array.isArray(adminBonusMissingState) || !adminBonusMissingState.length) return '';

  const blocks = adminBonusMissingState.map(row => {
    const names = Array.isArray(row.missing_names) ? row.missing_names : [];
    const count = Number(row.missing_count || 0);
    return '<div class="admin-bonus-missing-block">' +
      '<strong>' + esc(row.title || row.question_key || '') + '</strong>' +
      '<div class="hint" style="text-align:left;margin-top:2px">Vastamata: ' + count + '</div>' +
      '<div class="admin-bonus-missing-names">' + (count ? esc(names.join(', ')) : 'Kõik on vastanud.') + '</div>' +
    '</div>';
  }).join('');

  return '<div class="card admin-bonus-missing-card">' +
    '<h3>Vastamata boonusennustused</h3>' +
    '<div class="hint" style="text-align:left">Siin näed enne lukustumist kohe, kellel on mõni boonusvastus puudu.</div>' +
    blocks +
  '</div>';
}

const __bonusVisibilityBaseRulesStatus = bonusRulesStatusHtmlDeep;
bonusRulesStatusHtmlDeep = function() {
  const own = __bonusVisibilityBaseRulesStatus();
  if (!bonusDeadlinePassedFix()) return own;
  return own + lockedBonusAnswersHtml();
};

const __bonusVisibilityBaseAdminCard = adminBonusCardHtmlDeep;
adminBonusCardHtmlDeep = function() {
  return __bonusVisibilityBaseAdminCard() + adminBonusMissingHtml();
};
'''
    text = text.replace('\ninit();', js + '\n\ninit();', 1)

path.write_text(text, encoding='utf-8')
