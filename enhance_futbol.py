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

# Admin user management UI.
css_anchor = "    .admin-actions {\n"
css_code = '''    .user-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 10px 0;
      border-bottom: 1px solid #edf1ee;
    }

    .user-row:last-child {
      border-bottom: 0;
    }

    .user-self {
      color: var(--muted);
      font-size: 12px;
      font-weight: 800;
    }

'''
if ".user-row {" not in text:
    if css_anchor not in text:
        raise SystemExit("User CSS anchor not found")
    text = text.replace(css_anchor, css_code + css_anchor, 1)

admin_users_anchor = '''  html +=
    '<div class="card">' +

      "<h3>Lisa mäng</h3>" +'''
admin_users_code = '''  html +=
    '<div class="card">' +
      "<h3>Kasutajad</h3>" +
      '<div class="hint" style="text-align:left;margin-bottom:8px">' +
        "Kasutaja kustutamisel kustutatakse ka tema kõik ennustused." +
      "</div>";

  [...players]
    .sort((a, b) =>
      a.display_name.localeCompare(b.display_name, "et")
    )
    .forEach(player => {

      html +=
        '<div class="user-row">' +
          "<strong>" + esc(player.display_name) + "</strong>";

      if (player.id === currentUser.id) {
        html += '<span class="user-self">Sina</span>';
      } else {
        html +=
          '<button ' +
            'class="btn btn-danger btn-small" ' +
            'onclick="adminDeletePlayer(\\'' +
            player.id +
            '\\')">' +
            "Kustuta" +
          "</button>";
      }

      html += "</div>";
    });

  html += "</div>";

'''
if "<h3>Kasutajad</h3>" not in text:
    if admin_users_anchor not in text:
        raise SystemExit("Admin users insertion anchor not found")
    text = text.replace(admin_users_anchor, admin_users_code + admin_users_anchor, 1)

function_anchor = "async function adminCreateMatch() {\n"
function_code = r'''async function adminDeletePlayer(playerId) {

  if (playerId === currentUser.id) {
    toast("Enda kasutajat ei saa kustutada.");
    return;
  }

  const player = players.find(p => p.id === playerId);

  if (!player) {
    toast("Kasutajat ei leitud.");
    return;
  }

  const confirmed = window.confirm(
    "Kas kustutada kasutaja " + player.display_name +
    "? Kõik tema ennustused kustutatakse samuti."
  );

  if (!confirmed) {
    return;
  }

  const result = await sb.rpc(
    "admin_delete_player",
    {
      p_pin: adminPin,
      p_player_id: playerId
    }
  );

  if (result.error) {
    toast(friendlyError(result.error));
    return;
  }

  toast("Kasutaja " + player.display_name + " kustutatud.");
  await loadAll();
}

'''
if "async function adminDeletePlayer(" not in text:
    if function_anchor not in text:
        raise SystemExit("Delete-player function anchor not found")
    text = text.replace(function_anchor, function_code + function_anchor, 1)

path.write_text(text, encoding="utf-8")
