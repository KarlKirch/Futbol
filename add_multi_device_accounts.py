from pathlib import Path
import re

index_path = Path('index.html')
text = index_path.read_text(encoding='utf-8')

MARKER = '// FUTBOL MULTI DEVICE ACCOUNTS'

# Canonical player helper: auth user identifies a device; currentPlayer identifies the shared Futbol player.
if 'function ownPlayerId()' not in text:
    anchor = 'let currentPlayer = null;\n'
    text = text.replace(anchor, anchor + "\nfunction ownPlayerId() {\n  return currentPlayer?.id || currentUser?.id || null;\n}\n", 1)

# On startup resolve the shared player through the device mapping instead of assuming player id = auth uid.
old = '''    const playerResult =\n      await sb\n        .from("players")\n        .select("*")\n        .eq("id", currentUser.id)\n        .maybeSingle();'''
new = '''    const playerResult =\n      await sb.rpc("get_current_player");'''
if old in text:
    text = text.replace(old, new, 1)

old_assign = '''    currentPlayer =\n      playerResult.data;'''
new_assign = '''    currentPlayer = Array.isArray(playerResult.data)\n      ? (playerResult.data[0] || null)\n      : (playerResult.data || null);'''
if old_assign in text:
    text = text.replace(old_assign, new_assign, 1)

# All player ownership in the app uses the canonical shared player id.
text = text.replace('currentUser.id', 'ownPlayerId()')

# Push subscriptions belong to the individual browser auth session, not the shared player.
text = text.replace("user_id: ownPlayerId(),\n    endpoint: subscription.endpoint", "user_id: currentUser.id,\n    endpoint: subscription.endpoint")
text = text.replace("pushSubscriptionCheckedUser === ownPlayerId()", "pushSubscriptionCheckedUser === currentUser.id")
text = text.replace("pushSubscriptionCheckedUser = ownPlayerId()", "pushSubscriptionCheckedUser = currentUser.id")

# Fresh player creation still uses the device auth id; ownPlayerId() already resolves to it while currentPlayer is null.

# Restore/link now keeps other devices signed in. Resolve canonical profile after the RPC.
pattern = re.compile(r'''  currentPlayer = \{\n    id: ownPlayerId\(\),\n    display_name: result\.data\n  \};\n\n  hasRecoveryCodeState = true;''')
replacement = '''  const linkedPlayerResult = await sb.rpc("get_current_player");\n  if (linkedPlayerResult.error) {\n    errorBox.textContent = friendlyError(linkedPlayerResult.error);\n    return;\n  }\n  currentPlayer = Array.isArray(linkedPlayerResult.data)\n    ? (linkedPlayerResult.data[0] || null)\n    : (linkedPlayerResult.data || null);\n\n  hasRecoveryCodeState = true;'''
text = pattern.sub(replacement, text, count=1)

# Clarify name-gate recovery copy for multi-device use.
text = text.replace('Kasutasid Futboli varem teises telefonis või brauseris?', 'Kas sul on Futbol juba teises telefonis või arvutis?')
text = text.replace('Taasta varasem kasutaja', 'Kasuta olemasolevat kasutajat')

# Add participation/payment rules to Rules section.
if 'Osalustasu ja osalemine' not in text:
    payment_rules = '''\n      <div class="card">\n        <h3>Osalustasu ja osalemine</h3>\n        <ul class="rules-list">\n          <li>Futboli osalustasu on <strong>10 € inimese kohta</strong>.</li>\n          <li>Makse tehakse pangakontole: <strong>Oliver Ossipov</strong>, IBAN <strong>EE597700771005156592</strong>.</li>\n          <li>Iga mängija näeb Mängud lehel enda personaalset makseselgitust. Kasuta ülekandel täpselt seda selgitust, sest see sisaldab sinu nime ja unikaalset maksekoodi.</li>\n          <li>Ennustada saab ka enne makse kinnitamist, kuid ametlikku üldtabelisse ja voorude punktiarvestusse jõuab mängija alles pärast seda, kui admin on makse kinnitanud.</li>\n          <li>Osalustasu tavapärane tähtaeg on esimese avaldatud ennustusmängu algusaeg. Pärast tähtaega saab admin vajadusel osalemise erandina siiski kinnitada.</li>\n          <li>Makse staatust näed Mängud lehel: „Makse kinnitamata“, „Tähtaeg möödas“ või „✓ Makstud“.</li>\n        </ul>\n      </div>\n'''
    text = text.replace('      <div id="recoverySettings"></div>', payment_rules + '\n      <div id="recoverySettings"></div>', 1)

# Add multi-device controls to recovery settings.
if 'id="deviceLinkCode"' not in text:
    needle = "  container.innerHTML = html;\n}\n\nfunction toggleRecoveryPanel()"
    replacement = '''  html +=\n    '<div class="recovery-card" style="margin-top:12px">' +\n      '<div class="recovery-card-title">Sama kasutaja mitmes seadmes</div>' +\n      '<div class="recovery-card-text">Võid olla sama Futboli kasutajaga korraga sisse logitud telefonis ja arvutis. Teises seadmes sisesta selle kasutaja taastekood. Ühe seadme ühendamine ei logi teisi seadmeid välja.</div>' +\n      '<input id="deviceLinkCode" class="input" maxlength="20" autocomplete="off" placeholder="Sisesta olemasoleva kasutaja taastekood" oninput="formatRecoveryInput(this)" style="margin-top:10px">' +\n      '<button class="btn btn-secondary btn-block" type="button" onclick="linkThisDevice()">Seo see seade kasutajaga</button>' +\n    '</div>';\n\n  container.innerHTML = html;\n}\n\nasync function linkThisDevice() {\n  const input = document.getElementById('deviceLinkCode');\n  const code = String(input?.value || '').trim();\n  if (!code) {\n    toast('Sisesta taastekood.');\n    return;\n  }\n  const result = await sb.rpc('link_player_device', { p_code: code });\n  if (result.error) {\n    toast(friendlyError(result.error));\n    return;\n  }\n  const playerResult = await sb.rpc('get_current_player');\n  if (playerResult.error) {\n    toast(friendlyError(playerResult.error));\n    return;\n  }\n  currentPlayer = Array.isArray(playerResult.data) ? (playerResult.data[0] || null) : (playerResult.data || null);\n  if (!currentPlayer) {\n    toast('Kasutaja ühendamine ebaõnnestus.');\n    return;\n  }\n  document.getElementById('currentPlayer').textContent = currentPlayer.display_name;\n  latestRecoveryCode = '';\n  hasRecoveryCodeState = true;\n  toast('Seade on kasutajaga seotud. Teised seadmed jäid sisse logituks.');\n  await loadAll();\n}\n\nfunction toggleRecoveryPanel()'''
    if needle in text:
        text = text.replace(needle, replacement, 1)

# Improve recovery explanation.
text = text.replace(
    'Taastekoodi on vaja selleks, et saaksid telefoni või brauseri vahetamisel oma Futboli kasutaja, punktid ja ennustused taastada.',
    'Taastekoodiga saad sama Futboli kasutaja avada ka teises telefonis või arvutis. Senine seade jääb samal ajal sisse logituks.'
)

if MARKER not in text:
    text = text.replace('\n\ninit();', '\n\n' + MARKER + '\n\ninit();', 1)

index_path.write_text(text, encoding='utf-8')

# Chat must also write/read ownership using the shared canonical player id.
chat_path = Path('chat.js')
if chat_path.exists():
    chat = chat_path.read_text(encoding='utf-8')
    chat = chat.replace("item.user_id === currentUser.id", "item.user_id === (currentPlayer?.id || currentUser.id)")
    chat = chat.replace("message.user_id === currentUser.id", "message.user_id === (currentPlayer?.id || currentUser.id)")
    chat = chat.replace(".insert({ user_id: currentUser.id, message: message })", ".insert({ user_id: (currentPlayer?.id || currentUser.id), message: message })")
    chat_path.write_text(chat, encoding='utf-8')
