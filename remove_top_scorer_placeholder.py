from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

old = 'placeholder="Näiteks Kylian Mbappé"'
new = 'placeholder=""'

if old in text:
    text = text.replace(old, new)

path.write_text(text, encoding='utf-8')
print('Removed top scorer example placeholder')
