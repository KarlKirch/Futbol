/* FUTBOL ADMIN FIXTURE SELECTION DRAFT */
(function () {
  if (typeof renderAdmin !== 'function' || typeof adminConfirmRoundSelection !== 'function') return;

  const STORAGE_KEY = 'futbol_admin_fixture_drafts_v1';

  function readDrafts() {
    try {
      const parsed = JSON.parse(sessionStorage.getItem(STORAGE_KEY) || '{}');
      return parsed && typeof parsed === 'object' ? parsed : {};
    } catch (_) {
      return {};
    }
  }

  function writeDrafts(drafts) {
    try {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(drafts || {}));
    } catch (_) {}
  }

  function roundKey(round) {
    return String(Number(round) || 0);
  }

  function selectedIdsFromDom() {
    return [...document.querySelectorAll('#uclFixturePickerMount .ucl-fixture-check:checked')]
      .map(el => String(el.value || ''))
      .filter(Boolean);
  }

  function saveCurrentDraft() {
    if (!adminVerified || !adminCatalogRound) return;
    const checks = document.querySelectorAll('#uclFixturePickerMount .ucl-fixture-check');
    if (!checks.length) return;

    const drafts = readDrafts();
    drafts[roundKey(adminCatalogRound)] = {
      ids: selectedIdsFromDom(),
      updated_at: Date.now()
    };
    writeDrafts(drafts);
  }

  function getRoundDraft(round) {
    const drafts = readDrafts();
    const draft = drafts[roundKey(round)];
    return draft && Array.isArray(draft.ids) ? draft : null;
  }

  function clearRoundDraft(round) {
    const drafts = readDrafts();
    delete drafts[roundKey(round)];
    writeDrafts(drafts);
  }

  function restoreCurrentDraft() {
    if (!adminVerified || !adminCatalogRound) return;
    const draft = getRoundDraft(adminCatalogRound);
    if (!draft) return;

    const wanted = new Set(draft.ids.map(String));
    const checks = document.querySelectorAll('#uclFixturePickerMount .ucl-fixture-check');
    checks.forEach(check => {
      check.checked = wanted.has(String(check.value));
    });

    const card = document.querySelector('#uclFixturePickerMount .fixture-picker-card');
    if (card && checks.length) {
      let note = card.querySelector('.fixture-draft-note');
      if (!note) {
        note = document.createElement('div');
        note.className = 'fixture-draft-note';
        note.style.cssText = 'margin:10px 0 0;padding:9px 11px;border:1px solid #eadbb7;border-radius:11px;background:#fffdf7;color:#72581d;font-size:11px;font-weight:800;line-height:1.4';
        const list = card.querySelector('.fixture-check-list');
        if (list) list.insertAdjacentElement('beforebegin', note);
      }
      note.textContent = 'Sul on salvestamata mänguvalik. Automaatne värskendus seda ei kustuta.';
    }
  }

  function catalogSelectionMatches(round, wantedIds) {
    const wanted = new Set((wantedIds || []).map(String));
    const actual = new Set(
      (adminFixtureCatalog || [])
        .filter(row => Number(row.round_number) === Number(round) && row.is_selected)
        .map(row => String(row.external_match_id))
    );
    if (wanted.size !== actual.size) return false;
    for (const id of wanted) {
      if (!actual.has(id)) return false;
    }
    return true;
  }

  document.addEventListener('change', event => {
    const target = event.target;
    if (!(target instanceof Element) || !target.matches('#uclFixturePickerMount .ucl-fixture-check')) return;
    saveCurrentDraft();
    restoreCurrentDraft();
  });

  const baseRenderAdmin = renderAdmin;
  renderAdmin = function() {
    // Capture any still-visible unsaved state before another wrapper rebuilds the admin DOM.
    if (adminVerified) {
      const existingDraft = getRoundDraft(adminCatalogRound);
      const checks = document.querySelectorAll('#uclFixturePickerMount .ucl-fixture-check');
      if (existingDraft && checks.length) saveCurrentDraft();
    }

    const result = baseRenderAdmin.apply(this, arguments);
    restoreCurrentDraft();
    return result;
  };

  const baseConfirm = adminConfirmRoundSelection;
  adminConfirmRoundSelection = async function() {
    const round = Number(adminCatalogRound);
    const wantedIds = selectedIdsFromDom();
    saveCurrentDraft();

    const result = await baseConfirm.apply(this, arguments);

    // The base function reloads the fixture catalog after a successful save.
    // Only clear the draft after the reloaded catalog proves the selection was persisted.
    if (catalogSelectionMatches(round, wantedIds)) {
      clearRoundDraft(round);
      const note = document.querySelector('#uclFixturePickerMount .fixture-draft-note');
      if (note) note.remove();
    } else {
      restoreCurrentDraft();
    }

    return result;
  };

  restoreCurrentDraft();
})();
