from pathlib import Path

path = Path("index.html")
text = path.read_text(encoding="utf-8")

# Calendar picker styles.
css_anchor = "    .user-row {\n"
css_code = '''    .date-picker-row {
      position: relative;
      display: grid;
      grid-template-columns: minmax(0, 1fr) 48px;
      gap: 8px;
      align-items: end;
    }

    .calendar-trigger {
      height: 48px;
      border: 1px solid var(--border);
      border-radius: 12px;
      background: white;
      color: var(--dark);
      font-size: 21px;
      cursor: pointer;
      box-shadow: var(--shadow);
    }

    .calendar-trigger:active {
      transform: translateY(1px);
    }

    .calendar-native {
      position: absolute;
      right: 0;
      bottom: 0;
      width: 48px;
      height: 48px;
      opacity: 0;
      pointer-events: none;
    }

'''

if ".date-picker-row {" not in text:
    if css_anchor not in text:
        raise SystemExit("Calendar CSS anchor not found")
    text = text.replace(css_anchor, css_code + css_anchor, 1)

# Calendar helper functions. The visible field remains DD.MM.YYYY; the native
# date input exists only to provide the browser's calendar UI.
helper_anchor = "function isStarted(match) {\n"
helper_code = r'''function europeanDateToNative(value) {

  const match = String(value || "").trim()
    .match(/^(\d{2})\.(\d{2})\.(\d{4})$/);

  if (!match) {
    return "";
  }

  return match[3] + "-" + match[2] + "-" + match[1];
}

function nativeDateToEuropean(value) {

  const match = String(value || "").trim()
    .match(/^(\d{4})-(\d{2})-(\d{2})$/);

  if (!match) {
    return "";
  }

  return match[3] + "." + match[2] + "." + match[1];
}

function openDatePicker(nativeId, textId) {

  const nativeInput = document.getElementById(nativeId);
  const textInput = document.getElementById(textId);

  if (!nativeInput || !textInput) {
    return;
  }

  const nativeValue = europeanDateToNative(textInput.value);
  if (nativeValue) {
    nativeInput.value = nativeValue;
  }

  try {
    if (typeof nativeInput.showPicker === "function") {
      nativeInput.showPicker();
    } else {
      nativeInput.focus();
      nativeInput.click();
    }
  } catch (error) {
    nativeInput.focus();
    nativeInput.click();
  }
}

function syncDateFromPicker(nativeId, textId) {

  const nativeInput = document.getElementById(nativeId);
  const textInput = document.getElementById(textId);

  if (!nativeInput || !textInput || !nativeInput.value) {
    return;
  }

  textInput.value = nativeDateToEuropean(nativeInput.value);
}

'''

if "function openDatePicker(" not in text:
    if helper_anchor not in text:
        raise SystemExit("Calendar helper anchor not found")
    text = text.replace(helper_anchor, helper_code + helper_anchor, 1)

# Add-match date field: keep European text input and add a calendar button.
old_add = '''        "<div>" +
          "<label>Kuupäev (PP.KK.AAAA)</label>" +
          '<input ' +
            'id="newKickoffDate" ' +
            'class="input" ' +
            'type="text" ' +
            'inputmode="numeric" ' +
            'maxlength="10" ' +
            'autocomplete="off" ' +
            'placeholder="06.09.2026" ' +
            'oninput="formatEuropeanDateInput(this)">' +
        "</div>" +'''

new_add = '''        '<div class="date-picker-row">' +
          "<div>" +
            "<label>Kuupäev (PP.KK.AAAA)</label>" +
            '<input ' +
              'id="newKickoffDate" ' +
              'class="input" ' +
              'type="text" ' +
              'inputmode="numeric" ' +
              'maxlength="10" ' +
              'autocomplete="off" ' +
              'placeholder="06.09.2026" ' +
              'oninput="formatEuropeanDateInput(this)">' +
          "</div>" +
          '<button ' +
            'type="button" ' +
            'class="calendar-trigger" ' +
            'aria-label="Vali kuupäev kalendrist" ' +
            'title="Vali kuupäev kalendrist" ' +
            'onclick="openDatePicker(\\'newKickoffCalendar\\', \\'newKickoffDate\\')">📅</button>' +
          '<input ' +
            'id="newKickoffCalendar" ' +
            'class="calendar-native" ' +
            'type="date" ' +
            'tabindex="-1" ' +
            'aria-hidden="true" ' +
            'onchange="syncDateFromPicker(\\'newKickoffCalendar\\', \\'newKickoffDate\\')">' +
        "</div>" +'''

if 'id="newKickoffCalendar"' not in text:
    if old_add not in text:
        raise SystemExit("Current add-date block not found")
    text = text.replace(old_add, new_add, 1)

# Edit-match date field gets the same calendar button.
old_edit = '''            "<div>" +
              "<label>Kuupäev (PP.KK.AAAA)</label>" +
              '<input ' +
                'id="ekd-' +
                match.id +
                '" ' +
                'class="input" ' +
                'type="text" ' +
                'inputmode="numeric" ' +
                'maxlength="10" ' +
                'autocomplete="off" ' +
                'oninput="formatEuropeanDateInput(this)" ' +
                'value="' +
                formatDate(
                  match.kickoff_at
                ) +
                '">' +
            "</div>" +'''

new_edit = '''            '<div class="date-picker-row">' +
              "<div>" +
                "<label>Kuupäev (PP.KK.AAAA)</label>" +
                '<input ' +
                  'id="ekd-' +
                  match.id +
                  '" ' +
                  'class="input" ' +
                  'type="text" ' +
                  'inputmode="numeric" ' +
                  'maxlength="10" ' +
                  'autocomplete="off" ' +
                  'oninput="formatEuropeanDateInput(this)" ' +
                  'value="' +
                  formatDate(
                    match.kickoff_at
                  ) +
                  '">' +
              "</div>" +
              '<button ' +
                'type="button" ' +
                'class="calendar-trigger" ' +
                'aria-label="Vali kuupäev kalendrist" ' +
                'title="Vali kuupäev kalendrist" ' +
                'onclick="openDatePicker(\\'ekc-' +
                match.id +
                '\\', \\'ekd-' +
                match.id +
                '\\')">📅</button>' +
              '<input ' +
                'id="ekc-' +
                match.id +
                '" ' +
                'class="calendar-native" ' +
                'type="date" ' +
                'tabindex="-1" ' +
                'aria-hidden="true" ' +
                'onchange="syncDateFromPicker(\\'ekc-' +
                match.id +
                '\\', \\'ekd-' +
                match.id +
                '\\')">' +
            "</div>" +'''

if 'id="ekc-' not in text:
    if old_edit not in text:
        raise SystemExit("Current edit-date block not found")
    text = text.replace(old_edit, new_edit, 1)

path.write_text(text, encoding="utf-8")
