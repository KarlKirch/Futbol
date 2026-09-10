// FUTBOL PROFESSIONAL UI POLISH V1
(function () {
  'use strict';

  var NAV_ICONS = {
    games: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8.5"></circle><path d="m12 8 2.6 1.9-1 3.1h-3.2l-1-3.1L12 8Z"></path><path d="m7.2 8.5 2.2 1.4M16.8 8.5l-2.2 1.4M8.3 16.2l2.1-3.2M15.7 16.2 13.6 13"></path></svg>',
    table: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 20V10h4v10M10 20V4h4v16M15 20v-7h4v7"></path></svg>',
    chat: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 6.5h14v9H10l-5 3v-12Z"></path><path d="M8 10h8M8 13h5"></path></svg>',
    rules: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 3.5h8l3 3V20H7Z"></path><path d="M15 3.5V7h3M10 11h5M10 14h5M10 17h3"></path></svg>'
  };

  var NAV_LABELS = {
    games: 'Mängud',
    table: 'Tabel',
    chat: 'Chat',
    rules: 'Reeglid'
  };

  function decorateNavButton(name) {
    var button = document.getElementById('nav-' + name);
    if (!button || button.dataset.proUi === '1') return;
    var unread = name === 'chat' ? button.querySelector('#chatUnread') : null;
    if (unread) unread.remove();
    button.innerHTML = '<span class="nav-icon">' + NAV_ICONS[name] + '</span>' +
      '<span class="nav-label">' + NAV_LABELS[name] + '</span>';
    if (unread) button.appendChild(unread);
    button.dataset.proUi = '1';
  }

  function decorateNavigation() {
    ['games', 'table', 'chat', 'rules'].forEach(decorateNavButton);
  }

  function buildRuleAccordions() {
    var rules = document.getElementById('tab-rules');
    if (!rules || rules.dataset.proAccordions === '1') return;

    var cards = Array.prototype.slice.call(rules.children).filter(function (node) {
      return node.classList && node.classList.contains('card') && node.querySelector(':scope > h3');
    });

    cards.forEach(function (card, index) {
      var heading = card.querySelector(':scope > h3');
      if (!heading) return;

      var details = document.createElement('details');
      details.className = 'rules-accordion';
      if (index === 0) details.open = true;

      var summary = document.createElement('summary');
      summary.textContent = heading.textContent.trim();

      var body = document.createElement('div');
      body.className = 'rules-accordion-body';

      Array.prototype.slice.call(card.childNodes).forEach(function (child) {
        if (child !== heading) body.appendChild(child);
      });

      details.appendChild(summary);
      details.appendChild(body);
      card.replaceWith(details);
    });

    rules.dataset.proAccordions = '1';
  }

  function polishDynamicContent() {
    decorateNavigation();
    buildRuleAccordions();
  }

  function start() {
    polishDynamicContent();
    var nav = document.querySelector('.bottom-nav-inner');
    if (nav && typeof MutationObserver !== 'undefined') {
      new MutationObserver(function () { decorateNavigation(); })
        .observe(nav, { childList: true, subtree: true });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start, { once: true });
  } else {
    start();
  }
})();
