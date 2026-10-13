from pathlib import Path
import re

index = Path('index.html')
text = index.read_text(encoding='utf-8')
script = '<script src="./account-admin-tools.js?v=1"></script>'
if script not in text:
    marker = '<script src="./admin-session.js?v=1"></script>'
    if marker not in text:
        raise SystemExit('admin session marker missing')
    text = text.replace(marker, marker + '\n' + script, 1)
    index.write_text(text, encoding='utf-8')

sw = Path('sw.js')
sw_text = sw.read_text(encoding='utf-8')
sw_text = re.sub(r'const CACHE_NAME = "futbol-champions-v\d+";', 'const CACHE_NAME = "futbol-champions-v15";', sw_text, count=1)
asset = '  "./account-admin-tools.js?v=1",\n'
if './account-admin-tools.js?v=1' not in sw_text:
    marker = '  "./admin-session.js?v=1",\n'
    if marker not in sw_text:
        raise SystemExit('service worker admin session marker missing')
    sw_text = sw_text.replace(marker, marker + asset, 1)
sw.write_text(sw_text, encoding='utf-8')
