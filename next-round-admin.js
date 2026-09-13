/* FUTBOL ADMIN NEXT ROUND READY */
(function () {
  if (typeof renderAdmin !== 'function' || typeof setAdminCatalogRound !== 'function') return;

  let manualRoundChosen = false;

  function catalogRounds() {
    return [...new Set((adminFixtureCatalog || [])
      .map(row => Number(row.round_number))
      .filter(n => Number.isInteger(n) && n > 0))]
      .sort((a, b) => a - b);
  }

  function publishedRounds() {
    return [...new Set((matches || [])
      .map(row => Number(row.round_number))
      .filter(n => Number.isInteger(n) && n > 0))]
      .sort((a, b) => a - b);
  }

  function roundRows(round) {
    return (matches || []).filter(match => Number(match.round_number) === Number(round));
  }

  function preferredAdminRound() {
    const catalog = catalogRounds();
    if (!catalog.length) return null;

    const published = publishedRounds();
    if (!published.length) return catalog[0];

    // If a published round is still unfinished, keep that round in focus.
    for (const round of published) {
      const rows = roundRows(round);
      if (rows.length && rows.some(match => !isFinished(match))) return round;
    }

    // All published rounds are finished: offer the next catalog round immediately.
    const lastPublished = published[published.length - 1];
    return catalog.find(round => round > lastPublished) || lastPublished;
  }

  function nextRoundContext() {
    const catalog = catalogRounds();
    const published = publishedRounds();
    if (!catalog.length || !published.length) return null;

    const lastPublished = published[published.length - 1];
    const rows = roundRows(lastPublished);
    if (!rows.length || rows.some(match => !isFinished(match))) return null;

    const next = catalog.find(round => round > lastPublished);
    return next ? { previous: lastPublished, next } : null;
  }

  function applyAutomaticRound() {
    if (manualRoundChosen || !adminFixtureCatalogLoaded) return;
    const preferred = preferredAdminRound();
    if (preferred && Number(adminCatalogRound) !== Number(preferred)) {
      adminCatalogRound = preferred;
    }
  }

  function decorateReadyNotice() {
    const context = nextRoundContext();
    const card = document.querySelector('#adminArea .fixture-picker-card');
    if (!card) return;
    card.querySelectorAll('.next-round-ready-note').forEach(node => node.remove());
    if (!context || Number(adminCatalogRound) !== Number(context.next)) return;

    const head = card.querySelector('.fixture-picker-head') || card;
    head.insertAdjacentHTML('afterend',
      '<div class="next-round-ready-note" style="margin:12px 0;padding:11px 12px;border:1px solid #b9ddc8;border-radius:12px;background:#eef8f2;color:#174b31;font-size:13px;line-height:1.4">' +
      '<strong>' + context.previous + '. voor on lõppenud.</strong> ' +
      context.next + '. vooru mängud on valmis valimiseks. Märgi soovitud mängud ja vajuta <strong>Kinnita valik</strong>.' +
      '</div>'
    );
  }

  const baseLoadCatalog = loadAdminFixtureCatalog;
  loadAdminFixtureCatalog = async function(force = false) {
    await baseLoadCatalog(force);
    applyAutomaticRound();
  };

  const baseSetRound = setAdminCatalogRound;
  setAdminCatalogRound = function(value) {
    manualRoundChosen = true;
    return baseSetRound(value);
  };

  const baseRenderAdmin = renderAdmin;
  renderAdmin = function() {
    applyAutomaticRound();
    const result = baseRenderAdmin();
    decorateReadyNotice();
    return result;
  };

  if (typeof adminLogin === 'function') {
    const baseAdminLogin = adminLogin;
    adminLogin = async function() {
      manualRoundChosen = false;
      return baseAdminLogin.apply(this, arguments);
    };
  }
})();
