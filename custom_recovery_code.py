from pathlib import Path
import re

path = Path("index.html")
text = path.read_text(encoding="utf-8")

# Make the recovery input simple and memorable instead of forcing generated groups.
text = text.replace(
    'id="recoveryInput" class="input" maxlength="14" autocomplete="off" placeholder="XXXX-XXXX-XXXX" oninput="formatRecoveryInput(this)"',
    'id="recoveryInput" class="input" maxlength="20" autocomplete="off" placeholder="Näiteks KARL2026" oninput="formatRecoveryInput(this)"',
)

# Recovery input formatter: uppercase letters/numbers only, max 20 chars.
text = re.sub(
    r'function formatRecoveryInput\(input\) \{.*?\n\}',
    '''function formatRecoveryInput(input) {
  input.value = String(input.value || "")
    .toUpperCase()
    .replace(/[^A-Z0-9]/g, "")
    .slice(0, 20);
}''',
    text,
    count=1,
    flags=re.S,
)

# Replace the recovery card with a user-chosen code field.
recovery_block = r'''  let recoveryCard =
    '<div class="recovery-card">' +
      '<div class="recovery-card-title">Kasutaja taastamine</div>' +
      '<div class="recovery-card-text">Vali endale lihtne, kuid teistele raskesti äraarvatav taastekood. Kasuta 8–20 tähte või numbrit, näiteks KARL2026.</div>';

  if (latestRecoveryCode) {
    recoveryCard +=
      '<div class="recovery-code-box">' + esc(latestRecoveryCode) + '</div>' +
      '<div class="recovery-actions">' +
        '<button class="btn btn-secondary btn-small" type="button" onclick="copyRecoveryCode()">Kopeeri kood</button>' +
      '</div>';
  } else if (hasRecoveryCodeState) {
    recoveryCard +=
      '<div class="recovery-card-text"><strong>Taastekood on olemas.</strong> Soovi korral saad selle siin uue enda valitud koodiga asendada.</div>';
  }

  recoveryCard +=
    '<input id="customRecoveryCode" class="input" maxlength="20" autocomplete="off" placeholder="Näiteks KARL2026" oninput="formatRecoveryInput(this)" style="margin-top:10px">' +
    '<button class="btn btn-block" type="button" onclick="saveRecoveryCode()">Salvesta taastekood</button>' +
    '</div>';'''

text, n = re.subn(
    r"  let recoveryCard =.*?  recoveryCard \+= '</div>';",
    recovery_block,
    text,
    count=1,
    flags=re.S,
)
if n != 1:
    raise SystemExit("recovery card block not found")

# Replace generated-code action with save-your-own-code action.
new_save = r'''async function saveRecoveryCode() {
  const input = document.getElementById("customRecoveryCode");
  if (!input) return;

  const code = String(input.value || "")
    .toUpperCase()
    .replace(/[^A-Z0-9]/g, "");

  if (code.length < 8 || code.length > 20) {
    toast("Taastekood peab olema 8–20 tähte või numbrit.");
    return;
  }

  const result = await sb.rpc("set_recovery_code", { p_code: code });

  if (result.error) {
    toast(friendlyError(result.error));
    return;
  }

  latestRecoveryCode = result.data || code;
  hasRecoveryCodeState = true;
  renderPlayerSummary();
  toast("Taastekood salvestatud.");
}'''

text, n = re.subn(
    r'async function createRecoveryCode\(\) \{.*?\n\}\n\n(?=async function copyRecoveryCode)',
    new_save + "\n\n",
    text,
    count=1,
    flags=re.S,
)
if n != 1:
    raise SystemExit("createRecoveryCode function not found")

# Friendly backend errors for custom codes.
if 'msg.includes("Taastamiskood peab olema 8 kuni 20 märki")' not in text:
    anchor = '  if (msg.includes("Taastamiskood ei kehti")) {'
    block = '''  if (msg.includes("Taastamiskood peab olema 8 kuni 20 märki")) {
    return "Taastekood peab olema 8–20 tähte või numbrit.";
  }

  if (msg.includes("See taastamiskood on juba kasutusel")) {
    return "See taastekood on juba kasutusel. Vali teine kood.";
  }

'''
    if anchor not in text:
        raise SystemExit("friendly error anchor not found")
    text = text.replace(anchor, block + anchor, 1)

path.write_text(text, encoding="utf-8")
print("Custom recovery code UI applied")
