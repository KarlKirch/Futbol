from pathlib import Path
import re

path = Path('index.html')
text = path.read_text(encoding='utf-8')

marker = '/* FUTBOL CHAT TAB EXCLUSIVITY FIX */'
if marker not in text:
    old = '''function showTab(name) {\n\n  [\n    "games",\n    "table",\n    "rules",\n    "admin"\n  ].forEach(tab => {'''
    new = '''function showTab(name) {\n\n  /* FUTBOL CHAT TAB EXCLUSIVITY FIX */\n  const chatTab = document.getElementById("tab-chat");\n  const chatNav = document.getElementById("nav-chat");\n  if (chatTab) chatTab.classList.add("hidden");\n  if (chatNav) chatNav.classList.remove("active");\n\n  [\n    "games",\n    "table",\n    "rules",\n    "admin"\n  ].forEach(tab => {'''
    if old not in text:
        raise SystemExit('showTab anchor not found')
    text = text.replace(old, new, 1)

# Remove every duplicated external chat loader and add exactly one back.
chat_tag_re = re.compile(r'\s*<script\s+src=["\']\.\/chat\.js\?v=8["\']></script>\s*', re.I)
count = len(chat_tag_re.findall(text))
if count < 1:
    raise SystemExit('chat.js loader not found')
text = chat_tag_re.sub('\n', text)
body_close = '</body>'
if body_close not in text:
    raise SystemExit('body closing tag not found')
text = text.replace(body_close, '<script src="./chat.js?v=8"></script>\n\n' + body_close, 1)

# Verification guards.
if text.count('<script src="./chat.js?v=8"></script>') != 1:
    raise SystemExit('chat.js must be loaded exactly once')
if marker not in text:
    raise SystemExit('chat exclusivity fix missing')

path.write_text(text, encoding='utf-8')
print(f'Fixed mobile chat navigation; removed {max(0, count-1)} duplicate chat loader(s).')
