from pathlib import Path

path = Path("index.html")
text = path.read_text(encoding="utf-8")

CSS_MARKER = "/* UCL DAY AND TIME GROUPING UX */"
JS_MARKER = "// UCL DAY AND TIME GROUPING UX"

if CSS_MARKER not in text:
    css = r'''

    /* UCL DAY AND TIME GROUPING UX */
    .match-time-title,
    .fixture-time-title {
      display: flex;
      align-items: center;
      gap: 9px;
      margin: 10px 4px 7px;
      color: #243b83;
      font-size: 13px;
      font-weight: 950;
    }

    .match-time-title::before,
    .match-time-title::after,
    .fixture-time-title::before,
    .fixture-time-title::after {
      content: "";
      height: 1px;
      background: #d8dff2;
      flex: 1;
    }

    .match-time-value,
    .fixture-time-value {
      flex: 0 0 auto;
      padding: 5px 10px;
      border-radius: 999px;
      background: #f0f3ff;
      border: 1px solid #d7def6;
      letter-spacing: .2px;
    }

    .fixture-check-list .fixture-time-title {
      margin-left: 0;
      margin-right: 0;
    }
'''
    text = text.replace("  </style>", css + "\n  </style>", 1)

if JS_MARKER not in text:
    js = r'''

// UCL DAY AND TIME GROUPING UX
function dateTimePartsFromText(value) {
  const textValue = String(value || '');
  const dateMatch = textValue.match(/(\d{2})\.(\d{2})\.(\d{4})/);
  const timeMatch = textValue.match(/(?:^|[^\d])(\d{1,2}):(\d{2})(?:[^\d]|$)/);
  if (!dateMatch) return null;

  const day = Number(dateMatch[1]);
  const month = Number(dateMatch[2]);
  const year = Number(dateMatch[3]);
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

  const hour = timeMatch ? String(Number(timeMatch[1])).padStart(2, '0') : '';
  const minute = timeMatch ? timeMatch[2] : '';
  const time = hour && minute ? hour + ':' + minute : '';

  return {
    dateKey: year + '-' + String(month).padStart(2, '0') + '-' + String(day).padStart(2, '0'),
    timeKey: time,
    weekday: weekday,
    longDate: longDate,
    time: time
  };
}

function timeHeaderHtml(time, prefix) {
  if (!time) return '';
  return '<div class="' + prefix + '-time-title"><span class="' + prefix + '-time-value">' + esc(time) + '</span></div>';
}

decoratePublishedGamesByDay = function() {
  const container = document.getElementById('games');
  if (!container) return;

  container.querySelectorAll('.match-day-title, .match-time-title').forEach(el => el.remove());
  let lastDateKey = null;
  let lastTimeKey = null;

  Array.from(container.children).forEach(child => {
    if (child.classList.contains('match-group-title') || child.classList.contains('round-section-title')) {
      lastDateKey = null;
      lastTimeKey = null;
      return;
    }

    if (!(child.tagName === 'ARTICLE' && child.classList.contains('card'))) return;

    const dateEl = child.querySelector('.match-date');
    const parts = dateTimePartsFromText(dateEl ? dateEl.textContent : '');
    if (!parts) return;

    if (parts.dateKey !== lastDateKey) {
      child.insertAdjacentHTML('beforebegin', dayHeaderHtml({
        weekday: parts.weekday,
        longDate: parts.longDate
      }, 'match'));
      lastDateKey = parts.dateKey;
      lastTimeKey = null;
    }

    if (parts.timeKey && parts.timeKey !== lastTimeKey) {
      child.insertAdjacentHTML('beforebegin', timeHeaderHtml(parts.time, 'match'));
      lastTimeKey = parts.timeKey;
    }

    if (dateEl) dateEl.remove();
  });
};

decorateFixturePickerByDay = function() {
  const list = document.querySelector('#uclFixturePickerMount .fixture-check-list');
  if (!list) return;

  list.querySelectorAll('.fixture-day-title, .fixture-time-title').forEach(el => el.remove());
  let lastDateKey = null;
  let lastTimeKey = null;

  Array.from(list.querySelectorAll('.fixture-check-row')).forEach(row => {
    const meta = row.querySelector('.fixture-check-meta');
    const parts = dateTimePartsFromText(meta ? meta.textContent : '');
    if (!parts) return;

    if (parts.dateKey !== lastDateKey) {
      row.insertAdjacentHTML('beforebegin', dayHeaderHtml({
        weekday: parts.weekday,
        longDate: parts.longDate
      }, 'fixture'));
      lastDateKey = parts.dateKey;
      lastTimeKey = null;
    }

    if (parts.timeKey && parts.timeKey !== lastTimeKey) {
      row.insertAdjacentHTML('beforebegin', timeHeaderHtml(parts.time, 'fixture'));
      lastTimeKey = parts.timeKey;
    }

    if (meta) meta.remove();
  });
};
'''
    anchor = "\ninit();"
    pos = text.rfind(anchor)
    if pos == -1:
        raise SystemExit("init anchor not found")
    text = text[:pos] + js + text[pos:]

path.write_text(text, encoding="utf-8")
print("Grouped Champions League matches by day and kickoff time")
