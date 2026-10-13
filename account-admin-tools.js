/* FUTBOL ACCOUNT SWITCH + ADMIN PREDICTED NAMES */
(function () {
  if (typeof renderRecoverySettings !== 'function' || typeof renderAdmin !== 'function') return;

  function ensureLogoutCard() {
    const container = document.getElementById('recoverySettings');
    if (!container) return;

    container.querySelectorAll('.account-switch-card').forEach(node => node.remove());

    const card = document.createElement('div');
    card.className = 'recovery-card account-switch-card';
    card.style.marginTop = '12px';
    card.innerHTML =
      '<div class="recovery-card-title">Kasutaja vahetamine</div>' +
      '<div class="recovery-card-text">Logi sellest kasutajast välja, et avada samas seadmes teine Futboli konto. Tagasitulekuks kasuta oma taastekoodi.</div>' +
      '<button class="btn btn-secondary btn-block" type="button" onclick="switchFutbolAccount()">Logi välja</button>';
    container.appendChild(card);
  }

  window.switchFutbolAccount = async function() {
    const warning = hasRecoveryCodeState
      ? 'Kas soovid sellest kasutajast välja logida ja valida teise konto?'
      : 'Sul ei ole taastekoodi salvestatud. Kui logid välja, ei pruugi sa sellele kontole tagasi saada. Kas soovid siiski jätkata?';

    if (!window.confirm(warning)) return;

    try {
      if (adminVerified && typeof adminLogout === 'function') {
        adminLogout();
      }

      await createFreshAnonymousSession();

      currentPlayer = null;
      matches = [];
      predictions = [];
      players = [];
      leaderboard = [];
      adminPredictionCounts = [];
      hasRecoveryCodeState = false;
      latestRecoveryCode = '';

      const app = document.getElementById('app');
      const gate = document.getElementById('nameGate');
      const loading = document.getElementById('loadingScreen');
      const currentPlayerEl = document.getElementById('currentPlayer');
      const nameInput = document.getElementById('nameInput');
      const nameError = document.getElementById('nameError');
      const recoveryPanel = document.getElementById('recoveryPanel');
      const recoveryInput = document.getElementById('recoveryInput');
      const recoveryError = document.getElementById('recoveryError');

      if (app) app.classList.add('hidden');
      if (loading) loading.classList.add('hidden');
      if (gate) gate.classList.remove('hidden');
      if (currentPlayerEl) currentPlayerEl.textContent = '';
      if (nameInput) nameInput.value = '';
      if (nameError) nameError.textContent = '';
      if (recoveryPanel) recoveryPanel.classList.add('hidden');
      if (recoveryInput) recoveryInput.value = '';
      if (recoveryError) recoveryError.textContent = '';
    } catch (error) {
      toast('Väljalogimine ebaõnnestus: ' + friendlyError(error));
    }
  };

  const baseRenderRecoverySettings = renderRecoverySettings;
  renderRecoverySettings = function() {
    const result = baseRenderRecoverySettings.apply(this, arguments);
    ensureLogoutCard();
    return result;
  };

  function predictedNamesForCountRow(countRow) {
    const missing = new Set(
      (Array.isArray(countRow?.missing_names) ? countRow.missing_names : [])
        .map(name => String(name || '').trim().toLocaleLowerCase('et-EE'))
    );

    return (players || [])
      .map(player => String(player?.display_name || '').trim())
      .filter(Boolean)
      .filter(name => !missing.has(name.toLocaleLowerCase('et-EE')))
      .sort((a, b) => a.localeCompare(b, 'et'));
  }

  function decorateAdminPredictedNames() {
    if (!adminVerified) return;

    (matches || []).forEach(match => {
      const countRow = (adminPredictionCounts || []).find(row => String(row.match_id) === String(match.id));
      if (!countRow) return;

      const panel =
        document.getElementById('edit-' + match.id) ||
        document.getElementById('result-' + match.id);
      const card = panel?.closest('.card');
      if (!card) return;

      const countWrap = card.querySelector('.admin-count-wrap');
      if (!countWrap) return;

      countWrap.querySelectorAll('.admin-predicted-list').forEach(node => node.remove());

      const names = predictedNamesForCountRow(countRow);
      const details = document.createElement('details');
      details.className = 'missing-predictions admin-predicted-list';
      details.innerHTML =
        '<summary>Ennustanud (' + Number(countRow.predictions_count || names.length || 0) + ')</summary>' +
        '<div class="missing-names">' +
          (names.length ? names.map(esc).join(', ') : 'Keegi pole veel ennustanud.') +
        '</div>';

      countWrap.appendChild(details);
    });
  }

  const baseRenderAdmin = renderAdmin;
  renderAdmin = function() {
    const result = baseRenderAdmin.apply(this, arguments);
    decorateAdminPredictedNames();
    return result;
  };

  ensureLogoutCard();
  decorateAdminPredictedNames();
})();
