from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

CSS_MARKER = '/* FUTBOL STATS BUTTON AND BONUS MOVE FIX */'
JS_MARKER = '// FUTBOL STATS BUTTON AND BONUS MOVE FIX'

if CSS_MARKER not in text:
    css = r'''

    /* FUTBOL STATS BUTTON AND BONUS MOVE FIX */
    .match-insight-shell.stats-visible-fix {
      margin: 12px 0;
    }
    .match-insight-btn.stats-visible-fix-btn {
      width: 100%;
      min-height: 44px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 7px;
      border: 1px solid #bfcbee;
      border-radius: 12px;
      background: #f1f4ff;
      color: #213b86;
      font-size: 13px;
      font-weight: 950;
    }
    .match-insight-btn.stats-visible-fix-btn:hover,
    .match-insight-btn.stats-visible-fix-btn:focus-visible {
      background: #e8edff;
      border-color: #9daedf;
      outline: none;
    }
'''
    text = text.replace('  </style>', css + '\n  </style>', 1)

if JS_MARKER not in text:
    js = r'''

// FUTBOL STATS BUTTON AND BONUS MOVE FIX
function bonusDeadlinePassedFix() {
  if (!Array.isArray(bonusQuestionsState) || !bonusQuestionsState.length) return false;
  if (bonusQuestionsState.some(q => !!q.is_locked)) return true;
  const deadline = bonusQuestionsState.find(q => q.deadline)?.deadline;
  if (!deadline) return false;
  const ts = new Date(deadline).getTime();
  return Number.isFinite(ts) && Date.now() >= ts;
}

const __bonusMoveBaseHomeCard = bonusHomeCardHtmlDeep;
bonusHomeCardHtmlDeep = function() {
  if (bonusDeadlinePassedFix()) return '';
  return __bonusMoveBaseHomeCard();
};

const __bonusMoveBaseRulesStatus = bonusRulesStatusHtmlDeep;
bonusRulesStatusHtmlDeep = function() {
  if (!bonusDeadlinePassedFix()) return '';
  return __bonusMoveBaseRulesStatus();
};

function matchIdFromCardFix(card) {
  if (!card) return '';
  if (card.dataset && card.dataset.matchId) return card.dataset.matchId;
  const scoreInput = card.querySelector('[id^="ph-"]');
  if (scoreInput && scoreInput.id) return scoreInput.id.slice(3);
  const title = String(card.querySelector('.match-title')?.textContent || '').trim();
  if (title && Array.isArray(matches)) {
    const match = matches.find(m => (String(m.home_team || '') + ' – ' + String(m.away_team || '')).trim() === title);
    if (match) return match.id;
  }
  return '';
}

function ensureVisibleMatchStatsButtonsFix() {
  const container = document.getElementById('games');
  if (!container) return;

  container.querySelectorAll('article.card').forEach(card => {
    const matchId = matchIdFromCardFix(card);
    if (!matchId) return;
    card.dataset.matchId = matchId;

    card.querySelectorAll('.match-insight-shell').forEach(el => el.remove());

    const shell = document.createElement('div');
    shell.className = 'match-insight-shell stats-visible-fix';
    shell.innerHTML =
      '<button class="match-insight-btn stats-visible-fix-btn" type="button" onclick="toggleMatchInsightsDeep(\'' + matchId + '\')">' +
        '<span aria-hidden="true">📊</span><span>Mängu statistika</span>' +
      '</button>' +
      '<div id="insight-' + matchId + '" class="match-insight-panel hidden"></div>';

    const scoreEntry = card.querySelector('.score-entry');
    if (scoreEntry) {
      scoreEntry.insertAdjacentElement('beforebegin', shell);
      return;
    }

    const teams = card.querySelector('.teams');
    if (teams) {
      teams.insertAdjacentElement('afterend', shell);
      return;
    }

    card.appendChild(shell);
  });
}

const __statsVisibleBaseRenderGames = renderGames;
renderGames = function() {
  __statsVisibleBaseRenderGames();
  ensureVisibleMatchStatsButtonsFix();
};

let __bonusMovedAfterDeadline = false;
window.setInterval(function() {
  if (!currentUser || !currentPlayer || !Array.isArray(bonusQuestionsState) || !bonusQuestionsState.length) return;
  const passed = bonusDeadlinePassedFix();
  if (passed && !__bonusMovedAfterDeadline) {
    __bonusMovedAfterDeadline = true;
    renderPlayerSummary();
    renderRecoverySettings();
  } else if (!passed) {
    __bonusMovedAfterDeadline = false;
  }
}, 10000);
'''
    text = text.replace('\n\ninit();', js + '\n\ninit();', 1)

path.write_text(text, encoding='utf-8')
