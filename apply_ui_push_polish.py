from pathlib import Path
import re

index_path = Path('index.html')
chat_path = Path('chat.js')
sw_path = Path('sw.js')

index = index_path.read_text(encoding='utf-8')

# Load the professional UI overrides after the existing inline stylesheet.
if './ui-polish.css?v=1' not in index:
    index = index.replace('</head>', '  <link rel="stylesheet" href="./ui-polish.css?v=1">\n</head>', 1)

# Keep exactly one chat script and bump it so installed PWAs fetch the retry logic.
index = re.sub(r'\s*<script src="\./chat\.js\?v=\d+"></script>\s*', '\n<script src="./chat.js?v=9"></script>\n', index)
# The regex above can leave repeated normalized tags if the source ever regresses.
first = index.find('<script src="./chat.js?v=9"></script>')
if first >= 0:
    before = index[:first]
    after = index[first:]
    after = '<script src="./chat.js?v=9"></script>' + after[len('<script src="./chat.js?v=9"></script>'):].replace('<script src="./chat.js?v=9"></script>', '')
    index = before + after

if './ui-polish.js?v=1' not in index:
    marker = '<script src="./chat.js?v=9"></script>'
    if marker not in index:
        raise SystemExit('chat.js include not found')
    index = index.replace(marker, marker + '\n<script src="./ui-polish.js?v=1"></script>', 1)

index_path.write_text(index, encoding='utf-8')

chat = chat_path.read_text(encoding='utf-8')
old_notify = """  function notifyChatRecipients(messageId) {\n    if (!messageId || typeof sb === 'undefined' || !sb.functions) return;\n    Promise.resolve(sb.functions.invoke('send-chat-notification', { body: { message_id: messageId } }))\n      .then(function (result) {\n        if (result && result.error) console.error('Chat push invoke error', result.error);\n      })\n      .catch(function (error) { console.error('Chat push invoke error', error); });\n  }\n"""
new_notify = """  function notifyChatRecipients(messageId) {\n    if (!messageId || typeof sb === 'undefined' || !sb.functions) return;\n\n    var attempts = 0;\n    function sendAttempt() {\n      attempts += 1;\n      Promise.resolve(sb.functions.invoke('send-chat-notification', { body: { message_id: messageId } }))\n        .then(function (result) {\n          var failed = result && (result.error || (result.data && result.data.ok === false));\n          if (failed && attempts < 2) {\n            window.setTimeout(sendAttempt, 1800);\n            return;\n          }\n          if (failed) console.error('Chat push invoke error', result.error || result.data);\n        })\n        .catch(function (error) {\n          if (attempts < 2) {\n            window.setTimeout(sendAttempt, 1800);\n            return;\n          }\n          console.error('Chat push invoke error', error);\n        });\n    }\n\n    sendAttempt();\n  }\n"""
if old_notify in chat:
    chat = chat.replace(old_notify, new_notify, 1)
elif 'var attempts = 0;' not in chat:
    raise SystemExit('notifyChatRecipients block not found')
chat_path.write_text(chat, encoding='utf-8')

sw = sw_path.read_text(encoding='utf-8')
sw = re.sub(r'const CACHE_NAME = "futbol-champions-v\d+";', 'const CACHE_NAME = "futbol-champions-v12";', sw, count=1)
sw = re.sub(r'"\.\/chat\.js\?v=\d+"', '"./chat.js?v=9"', sw)
if '"./ui-polish.css?v=1"' not in sw:
    sw = sw.replace('"./chat.js?v=9",', '"./chat.js?v=9",\n  "./ui-polish.css?v=1",\n  "./ui-polish.js?v=1",', 1)
sw_path.write_text(sw, encoding='utf-8')

# Safety checks.
final_index = index_path.read_text(encoding='utf-8')
assert final_index.count('<script src="./chat.js?v=9"></script>') == 1
assert final_index.count('./ui-polish.css?v=1') == 1
assert final_index.count('./ui-polish.js?v=1') == 1
assert 'var attempts = 0;' in chat_path.read_text(encoding='utf-8')
assert 'futbol-champions-v12' in sw_path.read_text(encoding='utf-8')
print('UI polish and chat push client retry applied')
