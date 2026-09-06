from pathlib import Path

path = Path("index.html")
text = path.read_text(encoding="utf-8")

# Add helpers for explicitly European date format and 24-hour time.
helper_anchor = "function isStarted(match) {\n"
helper_code = r'''function formatEuropeanDateInput(input) {

  const digits = input.value.replace(/\D/g, "").slice(0, 8);

  if (digits.length <= 2) {
    input.value = digits;
  } else if (digits.length <= 4) {
    input.value = digits.slice(0, 2) + "." + digits.slice(2);
  } else {
    input.value =
      digits.slice(0, 2) + "." +
      digits.slice(2, 4) + "." +
      digits.slice(4);
  }
}

function formatEuropeanTimeInput(input) {

  const digits = input.value.replace(/\D/g, "").slice(0, 4);

  if (digits.length <= 2) {
    input.value = digits;
  } else {
    input.value = digits.slice(0, 2) + ":" + digits.slice(2);
  }
}

function europeanKickoffToIso(dateValue, timeValue) {

  const dateMatch = String(dateValue || "").trim()
    .match(/^(\d{2})\.(\d{2})\.(\d{4})$/);

  const timeMatch = String(timeValue || "").trim()
    .match(/^(\d{2}):(\d{2})$/);

  if (!dateMatch || !timeMatch) {
    return null;
  }

  const day = Number(dateMatch[1]);
  const month = Number(dateMatch[2]);
  const year = Number(dateMatch[3]);
  const hour = Number(timeMatch[1]);
  const minute = Number(timeMatch[2]);

  if (
    year < 2000 ||
    month < 1 || month > 12 ||
    day < 1 || day > 31 ||
    hour < 0 || hour > 23 ||
    minute < 0 || minute > 59
  ) {
    return null;
  }

  const testDate = new Date(Date.UTC(year, month - 1, day));

  if (
    testDate.getUTCFullYear() !== year ||
    testDate.getUTCMonth() !== month - 1 ||
    testDate.getUTCDate() !== day
  ) {
    return null;
  }

  const local =
    String(year).padStart(4, "0") + "-" +
    String(month).padStart(2, "0") + "-" +
    String(day).padStart(2, "0") + "T" +
    String(hour).padStart(2, "0") + ":" +
    String(minute).padStart(2, "0");

  return tallinnLocalToIso(local);
}

'''

if "function europeanKickoffToIso(" not in text:
    if helper_anchor not in text:
        raise SystemExit("Time helper anchor not found")
    text = text.replace(helper_anchor, helper_code + helper_anchor, 1)

# Replace the add-match datetime-local input with explicit DD.MM.YYYY + 24h HH:MM inputs.
old_add = '''        "<div>" +
          "<label>Mängu algus – Eesti aeg</label>" +
          '<input ' +
            'id="newKickoff" ' +
            'class="input" ' +
            'type="datetime-local">' +
        "</div>" +'''

new_add = '''        "<div>" +
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

        "<div>" +
          "<label>Kellaaeg (24 h)</label>" +
          '<input ' +
            'id="newKickoffTime" ' +
            'class="input" ' +
            'type="text" ' +
            'inputmode="numeric" ' +
            'maxlength="5" ' +
            'autocomplete="off" ' +
            'placeholder="19:30" ' +
            'oninput="formatEuropeanTimeInput(this)">' +
        "</div>" +'''

if 'id="newKickoff" ' in text:
    if old_add not in text:
        raise SystemExit("Add-match datetime block not found")
    text = text.replace(old_add, new_add, 1)

# Replace edit-match datetime-local input similarly.
old_edit = '''            "<div>" +
              "<label>Mängu algus – Eesti aeg</label>" +
              '<input ' +
                'id="ek-' +
                match.id +
                '" ' +
                'class="input" ' +
                'type="datetime-local" ' +
                'value="' +
                isoToTallinnInput(
                  match.kickoff_at
                ) +
                '">' +
            "</div>" +'''

new_edit = '''            "<div>" +
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

            "<div>" +
              "<label>Kellaaeg (24 h)</label>" +
              '<input ' +
                'id="ekt-' +
                match.id +
                '" ' +
                'class="input" ' +
                'type="text" ' +
                'inputmode="numeric" ' +
                'maxlength="5" ' +
                'autocomplete="off" ' +
                'oninput="formatEuropeanTimeInput(this)" ' +
                'value="' +
                formatTime(
                  match.kickoff_at
                ) +
                '">' +
            "</div>" +'''

if 'id="ek-' in text:
    if old_edit not in text:
        raise SystemExit("Edit-match datetime block not found")
    text = text.replace(old_edit, new_edit, 1)

# Update add-match handler.
old_create_logic = '''  const local =
    document
      .getElementById("newKickoff")
      .value;

  if (!home || !away || !local) {

    toast(
      "Täida kõik mängu väljad."
    );

    return;
  }

  const kickoff =
    tallinnLocalToIso(local);'''

new_create_logic = '''  const dateValue =
    document
      .getElementById("newKickoffDate")
      .value;

  const timeValue =
    document
      .getElementById("newKickoffTime")
      .value;

  if (!home || !away || !dateValue || !timeValue) {

    toast(
      "Täida kõik mängu väljad."
    );

    return;
  }

  const kickoff =
    europeanKickoffToIso(dateValue, timeValue);

  if (!kickoff) {

    toast(
      "Sisesta kuupäev kujul PP.KK.AAAA ja kellaaeg 24 tunni kujul HH:MM."
    );

    return;
  }'''

if 'getElementById("newKickoff")' in text:
    if old_create_logic not in text:
        raise SystemExit("Create handler datetime logic not found")
    text = text.replace(old_create_logic, new_create_logic, 1)

# Update edit-match handler.
old_update_logic = '''  const local =
    document
      .getElementById(
        "ek-" + matchId
      )
      .value;

  const kickoff =
    tallinnLocalToIso(local);'''

new_update_logic = '''  const dateValue =
    document
      .getElementById(
        "ekd-" + matchId
      )
      .value;

  const timeValue =
    document
      .getElementById(
        "ekt-" + matchId
      )
      .value;

  const kickoff =
    europeanKickoffToIso(dateValue, timeValue);

  if (!kickoff) {

    toast(
      "Sisesta kuupäev kujul PP.KK.AAAA ja kellaaeg 24 tunni kujul HH:MM."
    );

    return;
  }'''

if '"ek-" + matchId' in text:
    if old_update_logic not in text:
        raise SystemExit("Update handler datetime logic not found")
    text = text.replace(old_update_logic, new_update_logic, 1)

path.write_text(text, encoding="utf-8")
