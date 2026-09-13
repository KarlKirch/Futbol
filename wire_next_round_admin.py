from pathlib import Path

index = Path('index.html')
text = index.read_text(encoding='utf-8')
script = '<script src="./next-round-admin.js?v=1"></script>'
if script not in text:
    marker = '<script src="./live-standings.js?v=1"></script>'
    if marker not in text:
        raise SystemExit('live standings marker missing')
    text = text.replace(marker, marker + '\n' + script, 1)
    index.write_text(text, encoding='utf-8')

sw = Path('sw.js')
sw_text = sw.read_text(encoding='utf-8')
sw_text = sw_text.replace('const CACHE_NAME = "futbol-champions-v12";', 'const CACHE_NAME = "futbol-champions-v13";')
asset = '  "./next-round-admin.js?v=1",\n'
if './next-round-admin.js?v=1' not in sw_text:
    marker = '  "./live-standings.js?v=1",\n'
    if marker not in sw_text:
        raise SystemExit('service worker marker missing')
    sw_text = sw_text.replace(marker, marker + asset, 1)
    sw.write_text(sw_text, encoding='utf-8')
