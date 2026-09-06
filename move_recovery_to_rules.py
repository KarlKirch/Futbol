from pathlib import Path

path = Path("index.html")
text = path.read_text(encoding="utf-8")

# Clean up duplicate branding/helper lines that older idempotent patches may have repeated.
while '<div class="welcome-subtitle">CHAMPIONS LEAGUE</div>\n      <div class="welcome-subtitle">CHAMPIONS LEAGUE</div>' in text:
    text = text.replace(
        '<div class="welcome-subtitle">CHAMPIONS LEAGUE</div>\n      <div class="welcome-subtitle">CHAMPIONS LEAGUE</div>',
        '<div class="welcome-subtitle">CHAMPIONS LEAGUE</div>',
        1,
    )

dup_standalone = '''function isStandaloneMode() {
  return window.matchMedia("(display-mode: standalone)").matches ||
    window.navigator.standalone === true;
}

function isStandaloneMode() {
  return window.matchMedia("(display-mode: standalone)").matches ||
    window.navigator.standalone === true;
}
'''
if dup_standalone in text:
    text = text.replace(
        dup_standalone,
        '''function isStandaloneMode() {
  return window.matchMedia("(display-mode: standalone)").matches ||
    window.navigator.standalone === true;
}
''',
        1,
    )

# Remove recovery card construction from the home/player summary.
start = text.find('  let recoveryCard =\n')
end = text.find('  const installCard = isStandaloneMode()', start)
if start != -1 and end != -1:
    text = text[:start] + text[end:]

text = text.replace(
    "    '</div>' +\n    recoveryCard +\n    installCard;",
    "    '</div>' +\n    installCard;",
    1,
)

# Add a recovery settings mount under Rules.
if 'id="recoverySettings"' not in text:
    anchor = '''      <div class="card">
        <h3>Oluline teada</h3>
        <ul class="rules-list">
          <li>Ennustust saab sisestada ja muuta kuni mängu ametliku algusajani.</li>
          <li>Teiste mängijate ennustused on peidetud kuni mängu alguseni.</li>
          <li>Pärast mängu algust lukustub ennustus automaatselt.</li>
          <li>Kui mäng läheb lisaajale, arvestatakse tulemust pärast lisaaega.</li>
          <li>Penaltiseeria väravaid lõppskoori hulka ei arvestata.</li>
          <li>Üldtabelis järjestatakse mängijad punktide järgi; võrdsete punktide korral annab eelise suurem täpsete skooride arv.</li>
        </ul>
      </div>
'''
    replacement = anchor + '''
      <div id="recoverySettings"></div>
'''
    if anchor not in text:
        raise SystemExit("rules anchor not found")
    text = text.replace(anchor, replacement, 1)

# Render recovery settings after normal data refresh.
if '  renderRecoverySettings();\n' not in text:
    anchor = '''  renderPlayerSummary();
  renderGames();
  renderLeaderboard();
'''
    replacement = '''  renderPlayerSummary();
  renderGames();
  renderLeaderboard();
  renderRecoverySettings();
'''
    if anchor not in text:
        raise SystemExit("loadAll render anchor not found")
    text = text.replace(anchor, replacement, 1)

# Add renderer before the name-gate recovery functions.
if 'function renderRecoverySettings() {' not in text:
    anchor = 'function toggleRecoveryPanel() {\n'
    renderer = r'''function renderRecoverySettings() {
  const container = document.getElementById("recoverySettings");
  if (!container || !currentUser || !currentPlayer) return;

  let html =
    '<div class="recovery-card">' +
      '<div class="recovery-card-title">Kasutaja taastamine</div>' +
      '<div class="recovery-card-text">Taastekoodi on vaja selleks, et saaksid telefoni või brauseri vahetamisel oma Futboli kasutaja, punktid ja ennustused taastada.</div>';

  if (latestRecoveryCode) {
    html +=
      '<div class="recovery-code-box">' + esc(latestRecoveryCode) + '</div>' +
      '<div class="recovery-actions">' +
        '<button class="btn btn-secondary btn-small" type="button" onclick="copyRecoveryCode()">Kopeeri kood</button>' +
      '</div>';
  } else if (hasRecoveryCodeState) {
    html +=
      '<div class="recovery-card-text"><strong>Taastekood on olemas.</strong> Uue koodi salvestamisel vana kood enam ei kehti.</div>';
  }

  html +=
    '<input id="customRecoveryCode" class="input" maxlength="20" autocomplete="off" placeholder="Vali taastekood" oninput="formatRecoveryInput(this)" style="margin-top:10px">' +
    '<button class="btn btn-block" type="button" onclick="saveRecoveryCode()">Salvesta taastekood</button>' +
    '</div>';

  container.innerHTML = html;
}

'''
    if anchor not in text:
        raise SystemExit("toggle recovery anchor not found")
    text = text.replace(anchor, renderer + anchor, 1)

# Remove example placeholders from recovery controls.
text = text.replace('placeholder="Näiteks KARL2026"', 'placeholder="Sisesta taastekood"')
text = text.replace('placeholder="Näiteks KARL2026"', 'placeholder="Vali taastekood"')

# Saving a recovery code should refresh the Rules recovery card, not the home summary.
text = text.replace(
    '''  latestRecoveryCode = result.data || code;
  hasRecoveryCodeState = true;
  renderPlayerSummary();
  toast("Taastekood salvestatud.");''',
    '''  latestRecoveryCode = result.data || code;
  hasRecoveryCodeState = true;
  renderRecoverySettings();
  toast("Taastekood salvestatud.");''',
    1,
)

path.write_text(text, encoding="utf-8")
print("Moved recovery settings to Rules")
