from pathlib import Path

path = Path("index.html")
text = path.read_text(encoding="utf-8")

CSS_MARKER = "/* UCL DAY GROUPING UX */"
JS_MARKER = "// UCL DAY GROUPING UX"

if CSS_MARKER not in text:
    css = r'''

    /* UCL DAY GROUPING UX */
    .match-day-title,
    .fixture-day-title {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      margin: 13px 2px 9px;
      padding: 10px 12px;
      border: 1px solid #d4dcf5;
      border-radius: 12px;
      background: linear-gradient(90deg, #eef2ff 0%, #f8f9ff 100%);
      color: #12265d;
      box-shadow: 0 2px 9px rgba(24, 48, 112, .05);
    }

    .match-day-weekday,
    .fixture-day-weekday {
      color: #3154e8;
      font-size: 12px;
      font-weight: 950;
      letter-spacing: .7px;
      text-transform: uppercase;
    }

    .match-day-date,
    .fixture-day-date {
      color: #59657f;
      font-size: 12px;
      font-weight: 800;
      text-align: right;
    }

    .fixture-check-list .fixture-day-title {
      margin: 12px 0 0;
      border-radius: 10px;
    }

    .fixture-day-title + .fixture-check-row {
      border-top: 0;
    }

    @media (max-width: 480px) {
      .match-day-title,
      .fixture-day-title {
        align-items: flex-start;
        flex-direction: column;
        gap: 2px;
      }

      .match-day-date,
      .fixture-day-date {
        text-align: left;
      }
    }
'''
    text = text.replace("  </style>", css + "\n  </style>", 1)

if JS_MARKER not in text:
    js = r'''

// UCL DAY GROUPING UX
function dayPartsFromEuropeanDate(value) {
  const match = String(value || '').match(/(\d{2})\.(\d{2})\.(\d{4})/);
  if (!match) return null;
  const day = Number(match[1]);
  const month = Number(match[2]);
  const year = Number(match[3]);
  const date = new Date(Date.UTC(year, month - 1, day));
  if (Number.isNaN(date.getTime())) return null;

  const weekday = new Intl.DateTimeFormat('et-EE', {
    weekday: 'long',
    timeZone: 'UTC'
  }).format(date);

  const longDate = new Intl.DateTimeFormat('et-EE', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    timeZone: 'UTC'
  }).format(date);

  return {
    key: year + '-' + String(month).padStart(2, '0') + '-' + String(day).padStart(2, '0'),
    weekday: weekday,
    longDate: longDate
  };
}

function dayHeaderHtml(parts, prefix) {
  if (!parts) return '';
  return '<div class="' + prefix + '-day-title">' +
    '<span class="' + prefix + '-day-weekday">' + esc(parts.weekday) + '</span>' +
    '<span class="' + prefix + '-day-date">' + esc(parts.longDate) + '</span>' +
  '</div>';
}

function decoratePublishedGamesByDay() {
  const container = document.getElementById('games');
  if (!container) return;

  container.querySelectorAll('.match-day-title').forEach(el => el.remove());
  let lastDateKey = null;

  Array.from(container.children).forEach(child => {
    if (child.classList.contains('match-group-title') || child.classList.contains('round-section-title')) {
      lastDateKey = null;
      return;
    }

    if (!(child.tagName === 'ARTICLE' && child.classList.contains('card'))) return;
    const dateEl = child.querySelector('.match-date');
    const parts = dayPartsFromEuropeanDate(dateEl ? dateEl.textContent : '');
    if (!parts || parts.key === lastDateKey) return;

    child.insertAdjacentHTML('beforebegin', dayHeaderHtml(parts, 'match'));
    lastDateKey = parts.key;
  });
}

function decorateFixturePickerByDay() {
  const list = document.querySelector('#uclFixturePickerMount .fixture-check-list');
  if (!list) return;

  list.querySelectorAll('.fixture-day-title').forEach(el => el.remove());
  let lastDateKey = null;

  Array.from(list.querySelectorAll('.fixture-check-row')).forEach(row => {
    const meta = row.querySelector('.fixture-check-meta');
    const parts = dayPartsFromEuropeanDate(meta ? meta.textContent : '');
    if (!parts || parts.key === lastDateKey) return;

    row.insertAdjacentHTML('beforebegin', dayHeaderHtml(parts, 'fixture'));
    lastDateKey = parts.key;
  });
}

function removeObsoleteManualMatchAdders() {
  const area = document.getElementById('adminArea');
  if (!area) return;

  Array.from(area.querySelectorAll('.card')).forEach(card => {
    const heading = card.querySelector('h3');
    if (!heading) return;
    const title = heading.textContent.trim();
    if (title === 'Lisa mäng' || title === 'Lisa mitu mängu korraga') {
      card.remove();
    }
  });
}

const __dayGroupBaseRenderGames = renderGames;
renderGames = function() {
  __dayGroupBaseRenderGames();
  decoratePublishedGamesByDay();
};

const __dayGroupBaseRenderAdmin = renderAdmin;
renderAdmin = function() {
  __dayGroupBaseRenderAdmin();
  removeObsoleteManualMatchAdders();
  decorateFixturePickerByDay();
};
'''
    anchor = "\ninit();"
    pos = text.rfind(anchor)
    if pos == -1:
        raise SystemExit("init anchor not found")
    text = text[:pos] + js + text[pos:]

path.write_text(text, encoding="utf-8")
print("Grouped Champions League matches by day and removed manual add forms")
