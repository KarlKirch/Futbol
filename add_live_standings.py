from pathlib import Path

index = Path('index.html')
sw = Path('sw.js')

text = index.read_text(encoding='utf-8')

css_line = '  <link rel="stylesheet" href="./live-standings.css?v=1">\n'
css_anchor = '  <link rel="stylesheet" href="./ui-polish.css?v=1">\n'
if css_line not in text:
    if css_anchor not in text:
        raise SystemExit('ui-polish css anchor not found')
    text = text.replace(css_anchor, css_anchor + css_line, 1)

js_line = '<script src="./live-standings.js?v=1"></script>\n'
js_anchor = '<script src="./ui-polish.js?v=1"></script>\n'
if js_line not in text:
    if js_anchor not in text:
        raise SystemExit('ui-polish js anchor not found')
    text = text.replace(js_anchor, js_anchor + js_line, 1)

index.write_text(text, encoding='utf-8')

sw_text = sw.read_text(encoding='utf-8')
sw_text = sw_text.replace('const CACHE_NAME = "futbol-champions-v11";', 'const CACHE_NAME = "futbol-champions-v12";', 1)

chat_asset = '  "./chat.js?v=9",\n'
assets = '  "./chat.js?v=9",\n  "./ui-polish.css?v=1",\n  "./ui-polish.js?v=1",\n  "./live-standings.css?v=1",\n  "./live-standings.js?v=1",\n'
if '"./live-standings.js?v=1"' not in sw_text:
    if chat_asset not in sw_text:
        raise SystemExit('service worker asset anchor not found')
    sw_text = sw_text.replace(chat_asset, assets, 1)

sw.write_text(sw_text, encoding='utf-8')

print('Live standings assets wired successfully')
