from pathlib import Path

path = Path("index.html")
text = path.read_text(encoding="utf-8")

old = """function ensureChatUI() {\n  const main = document.querySelector('main');\n  const rules = document.getElementById('tab-rules');"""
new = """function ensureChatUI() {\n  const rules = document.getElementById('tab-rules');\n  const main = rules ? rules.parentElement : document.querySelector('main');"""

if old in text:
    text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8")
