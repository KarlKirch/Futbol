from pathlib import Path

index_path = Path('index.html')
text = index_path.read_text(encoding='utf-8')

# Add prize-pool distribution to the participation rules.
prize_rule = '<li>Kogutud osalustasude summa jaguneb esikolmiku vahel: <strong>1. koht 50%</strong>, <strong>2. koht 30%</strong> ja <strong>3. koht 20%</strong>.</li>'
if prize_rule not in text:
    anchor = '<li>Futboli osalustasu on <strong>10 € inimese kohta</strong>.</li>'
    if anchor in text:
        text = text.replace(anchor, anchor + '\n          ' + prize_rule, 1)

# Make chat author names darker and slightly larger while leaving date/time styling unchanged.
chat_css_marker = '/* FUTBOL CHAT NAME EMPHASIS */'
if chat_css_marker not in text:
    css = '''\n\n    /* FUTBOL CHAT NAME EMPHASIS */\n    .chat-meta .chat-name {\n      color: #20283b;\n      font-size: 12px;\n      font-weight: 900;\n    }\n    .chat-meta .chat-time {\n      color: #7b8396;\n      font-size: 10px;\n      font-weight: 750;\n    }\n'''
    text = text.replace('  </style>', css + '\n  </style>', 1)

index_path.write_text(text, encoding='utf-8')

chat_path = Path('chat.js')
if chat_path.exists():
    chat = chat_path.read_text(encoding='utf-8')
    old = "'<div class=\"chat-meta\">' + esc(name) + ' · ' + esc(chatTimestamp(item.created_at)) + '</div>' +"
    new = "'<div class=\"chat-meta\"><span class=\"chat-name\">' + esc(name) + '</span><span class=\"chat-time\"> · ' + esc(chatTimestamp(item.created_at)) + '</span></div>' +"
    if old in chat:
        chat = chat.replace(old, new, 1)
    chat_path.write_text(chat, encoding='utf-8')
