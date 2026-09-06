from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

# Remove the inline chat JavaScript block if present. Chat is loaded from chat.js
# so any chat-specific problem can no longer stop the core app from starting.
marker = '\n// FUTBOL USER CHAT\n'
start = text.rfind(marker)
if start != -1:
    end = text.find('\n\ninit();', start)
    if end != -1:
        text = text[:start] + '\n' + text[end:]

# Add a small startup guard before the main app script. If a future JavaScript
# error happens before init completes, mobile users see the real reason instead
# of an endless "Futbol käivitub..." screen.
guard_marker = 'data-futbol-startup-guard'
if guard_marker not in text:
    guard = r'''<script data-futbol-startup-guard>
(function () {
  function showStartupError(message) {
    var loading = document.getElementById('loadingScreen');
    var app = document.getElementById('app');
    var gate = document.getElementById('nameGate');
    if (!loading || loading.classList.contains('hidden')) return;
    if (app && !app.classList.contains('hidden')) return;
    if (gate && !gate.classList.contains('hidden')) return;
    loading.innerHTML = '<main><div class="card"><h2>Futboli käivitamine ebaõnnestus</h2>' +
      '<div class="error">' + String(message || 'Tundmatu käivitusviga').replace(/[&<>"']/g, function (ch) {
        return ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'})[ch];
      }) + '</div>' +
      '<button class="btn btn-block" type="button" onclick="location.reload()">Proovi uuesti</button></div></main>';
  }
  window.addEventListener('error', function (event) {
    showStartupError(event && event.message ? event.message : 'JavaScripti viga');
  });
  window.addEventListener('unhandledrejection', function (event) {
    var reason = event && event.reason;
    showStartupError(reason && reason.message ? reason.message : String(reason || 'Käivitusviga'));
  });
  window.setTimeout(function () {
    var loading = document.getElementById('loadingScreen');
    if (loading && !loading.classList.contains('hidden')) {
      showStartupError('Käivitamine võtab liiga kaua. Kontrolli internetiühendust ja proovi uuesti.');
    }
  }, 15000);
})();
</script>

'''
    text = text.replace('<script>\n\n\nconst SUPABASE_URL', guard + '<script>\n\n\nconst SUPABASE_URL', 1)

# Load chat only after the core inline application script has been parsed and
# init() has already been started.
chat_script = '<script src="./chat.js?v=4"></script>'
if chat_script not in text:
    text = text.replace('\n</body>', '\n' + chat_script + '\n\n</body>', 1)

path.write_text(text, encoding='utf-8')
