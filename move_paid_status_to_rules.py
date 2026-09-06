from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

MARKER = '// FUTBOL PAID STATUS IN RULES'

# Dedicated mount in Rules for confirmed payment status.
if 'id="paidRulesStatus"' not in text:
    text = text.replace(
        '      <div id="recoverySettings"></div>',
        '      <div id="paidRulesStatus"></div>\n\n      <div id="recoverySettings"></div>',
        1
    )

# Keep Rules copy aligned with the new placement.
text = text.replace(
    'Makse staatust näed Mängud lehel: „Makse kinnitamata“, „Tähtaeg möödas“ või „✓ Makstud“.',
    'Kuni makse kinnitamiseni näed makseinfot Mängud lehel. Pärast admini kinnitust kaob maksekaart Mängud lehelt ja kinnitatud makse staatus liigub Reeglite alla.'
)

if MARKER not in text:
    js = r'''

// FUTBOL PAID STATUS IN RULES
const __paidRulesBasePaymentCardHtml = paymentCardHtml;
paymentCardHtml = function() {
  if (paymentInfo && paymentInfo.is_paid) return '';
  return __paidRulesBasePaymentCardHtml();
};

function paidRulesStatusHtml() {
  if (!paymentInfo || !paymentInfo.is_paid) return '';
  const amount = paymentAmountText(paymentInfo.amount);
  const paidDate = paymentInfo.paid_at
    ? formatDate(paymentInfo.paid_at) + ' kell ' + formatTime(paymentInfo.paid_at)
    : '';

  return '<div class="card payment-card paid">' +
    '<div class="payment-status-line">' +
      '<div><div class="payment-status-title">Osalustasu ' + esc(amount) + '</div>' +
      '<div class="hint" style="text-align:left;margin-top:2px">Sinu osalemine on kinnitatud ja punktid lähevad ametlikku tabelisse.</div></div>' +
      '<span class="payment-status-badge">✓ Makstud</span>' +
    '</div>' +
    (paidDate ? '<div class="payment-deadline">Admin kinnitas makse: ' + esc(paidDate) + '.</div>' : '') +
  '</div>';
}

function renderPaidRulesStatus() {
  const mount = document.getElementById('paidRulesStatus');
  if (!mount) return;
  mount.innerHTML = paidRulesStatusHtml();
}

const __paidRulesBaseLoadAll = loadAll;
loadAll = async function() {
  await __paidRulesBaseLoadAll();
  renderPaidRulesStatus();
};

const __paidRulesBaseRenderRecoverySettings = renderRecoverySettings;
renderRecoverySettings = function() {
  __paidRulesBaseRenderRecoverySettings();
  renderPaidRulesStatus();
};
'''
    text = text.replace('\n\ninit();', js + '\n\ninit();', 1)

path.write_text(text, encoding='utf-8')
