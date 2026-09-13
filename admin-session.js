/* FUTBOL ADMIN SESSION UX */
(function () {
  const SESSION_KEY = 'futbol-admin-session-v1';
  const SESSION_TTL_MS = 8 * 60 * 60 * 1000;

  function readSessionRaw() {
    try {
      const raw = sessionStorage.getItem(SESSION_KEY);
      if (!raw) return null;
      const parsed = JSON.parse(raw);
      if (!parsed || typeof parsed.pin !== 'string' || !Number.isFinite(Number(parsed.expiresAt))) return null;
      return { pin: parsed.pin, expiresAt: Number(parsed.expiresAt) };
    } catch (_) {
      return null;
    }
  }

  function clearSession() {
    try { sessionStorage.removeItem(SESSION_KEY); } catch (_) {}
  }

  function saveSession(pin, expiresAt) {
    if (!pin) return;
    const expiry = Number(expiresAt) || (Date.now() + SESSION_TTL_MS);
    try {
      sessionStorage.setItem(SESSION_KEY, JSON.stringify({ pin, expiresAt: expiry }));
    } catch (_) {}
  }

  function activeSession() {
    const session = readSessionRaw();
    if (!session || session.expiresAt <= Date.now()) {
      clearSession();
      return null;
    }
    return session;
  }

  function styleAdminButton() {
    const button = document.getElementById('adminAccessButton');
    if (!button) return;

    const active = !!adminVerified;
    button.classList.toggle('verified', active);
    button.textContent = active ? 'ADMIN' : '⚙';
    button.title = active ? 'Admin – sessioon aktiivne' : 'Admin';
    button.setAttribute('aria-label', button.title);

    if (active) {
      button.style.width = 'auto';
      button.style.minWidth = '62px';
      button.style.padding = '0 10px';
      button.style.fontSize = '11px';
      button.style.letterSpacing = '.7px';
      button.style.background = 'rgba(44, 151, 91, .34)';
      button.style.borderColor = 'rgba(255,255,255,.48)';
    } else {
      button.style.width = '';
      button.style.minWidth = '';
      button.style.padding = '';
      button.style.fontSize = '';
      button.style.letterSpacing = '';
      button.style.background = '';
      button.style.borderColor = '';
    }
  }

  if (typeof ensureAdminAccessUI === 'function') {
    const baseEnsureAdminAccessUI = ensureAdminAccessUI;
    ensureAdminAccessUI = function () {
      const result = baseEnsureAdminAccessUI.apply(this, arguments);
      styleAdminButton();
      return result;
    };
  }

  if (typeof adminLogin === 'function') {
    const baseAdminLogin = adminLogin;
    adminLogin = async function () {
      const result = await baseAdminLogin.apply(this, arguments);
      if (adminVerified && adminPin) {
        saveSession(adminPin, Date.now() + SESSION_TTL_MS);
      }
      if (typeof ensureAdminAccessUI === 'function') ensureAdminAccessUI();
      else styleAdminButton();
      return result;
    };
  }

  if (typeof adminLogout === 'function') {
    const baseAdminLogout = adminLogout;
    adminLogout = function () {
      clearSession();
      const result = baseAdminLogout.apply(this, arguments);
      if (typeof ensureAdminAccessUI === 'function') ensureAdminAccessUI();
      else styleAdminButton();
      return result;
    };
  }

  if (typeof showTab === 'function') {
    const baseShowTab = showTab;
    showTab = function () {
      const result = baseShowTab.apply(this, arguments);
      styleAdminButton();
      return result;
    };
  }

  async function restoreAdminSession() {
    const session = activeSession();
    if (!session) {
      if (typeof ensureAdminAccessUI === 'function') ensureAdminAccessUI();
      else styleAdminButton();
      return;
    }

    try {
      const result = await sb.rpc('admin_check_pin', { p_pin: session.pin });
      if (result.error || !result.data) throw result.error || new Error('Admini sessioon ei kehti enam');

      adminPin = session.pin;
      adminVerified = true;

      if (typeof loadAdminPredictionCounts === 'function') {
        await loadAdminPredictionCounts();
      }

      if (typeof loadAdminFixtureCatalog === 'function') {
        try {
          adminFixtureCatalogLoaded = false;
          await loadAdminFixtureCatalog(true);
        } catch (_) {}
      }

      if (typeof ensureAdminAccessUI === 'function') ensureAdminAccessUI();
      else styleAdminButton();

      const adminTab = document.getElementById('tab-admin');
      if (adminTab && !adminTab.classList.contains('hidden') && typeof renderAdmin === 'function') {
        renderAdmin();
      }
    } catch (_) {
      clearSession();
      adminPin = '';
      adminVerified = false;
      if (typeof ensureAdminAccessUI === 'function') ensureAdminAccessUI();
      else styleAdminButton();
    }
  }

  setInterval(function () {
    if (!adminVerified) return;
    const session = activeSession();
    if (session) return;

    if (typeof adminLogout === 'function') adminLogout();
    else {
      adminPin = '';
      adminVerified = false;
      styleAdminButton();
      if (typeof renderAdmin === 'function') renderAdmin();
    }

    if (typeof toast === 'function') toast('Admini sessioon aegus. Logi vajadusel uuesti sisse.');
  }, 60000);

  restoreAdminSession();
})();
