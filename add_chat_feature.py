from pathlib import Path

path = Path("index.html")
text = path.read_text(encoding="utf-8")

CSS_MARKER = "/* FUTBOL USER CHAT */"
JS_MARKER = "// FUTBOL USER CHAT"

if CSS_MARKER not in text:
    css = r'''

    /* FUTBOL USER CHAT */
    .bottom-nav-inner { grid-template-columns: repeat(4, 1fr) !important; }
    .nav-btn { position: relative; }
    .chat-unread {
      position: absolute;
      top: 7px;
      left: calc(50% + 18px);
      min-width: 18px;
      height: 18px;
      padding: 0 5px;
      border-radius: 999px;
      background: #d34242;
      color: white;
      font-size: 10px;
      font-weight: 900;
      line-height: 18px;
      text-align: center;
    }
    .chat-card {
      padding: 0;
      overflow: hidden;
    }
    .chat-messages {
      min-height: 360px;
      max-height: calc(100vh - 300px);
      overflow-y: auto;
      padding: 14px;
      display: flex;
      flex-direction: column;
      gap: 9px;
      background: #f7f8fc;
      overscroll-behavior: contain;
    }
    .chat-empty {
      margin: auto;
      padding: 30px 16px;
      color: var(--muted);
      text-align: center;
      font-size: 13px;
      line-height: 1.5;
    }
    .chat-message {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      max-width: 84%;
    }
    .chat-message.own {
      align-self: flex-end;
      align-items: flex-end;
    }
    .chat-meta {
      margin: 0 4px 3px;
      color: #7b8396;
      font-size: 10px;
      font-weight: 750;
    }
    .chat-bubble {
      padding: 9px 11px;
      border: 1px solid #e0e4ee;
      border-radius: 14px 14px 14px 4px;
      background: white;
      color: #20283b;
      font-size: 13px;
      line-height: 1.42;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      box-shadow: 0 2px 8px rgba(25,40,70,.04);
    }
    .chat-message.own .chat-bubble {
      border-color: #2b428d;
      border-radius: 14px 14px 4px 14px;
      background: #263d83;
      color: white;
    }
    .chat-composer {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 9px;
      padding: 12px;
      border-top: 1px solid var(--border);
      background: white;
    }
    .chat-input {
      width: 100%;
      min-height: 46px;
      max-height: 120px;
      resize: vertical;
      padding: 11px 12px;
      border: 1px solid #cbd6cf;
      border-radius: 12px;
      outline: none;
      font: inherit;
      font-size: 14px;
      line-height: 1.35;
    }
    .chat-input:focus {
      border-color: #3652a4;
      box-shadow: 0 0 0 3px rgba(54,82,164,.11);
    }
    .chat-send-btn {
      min-width: 78px;
      min-height: 46px;
      padding: 0 14px;
      border: 0;
      border-radius: 12px;
      background: #263d83;
      color: white;
      font-weight: 900;
    }
    .chat-send-btn:disabled { opacity: .55; }
    .chat-note {
      padding: 0 12px 11px;
      background: white;
      color: var(--muted);
      font-size: 10px;
      line-height: 1.35;
    }
    @media (max-width: 520px) {
      .chat-messages {
        min-height: 330px;
        max-height: calc(100vh - 275px);
      }
      .chat-message { max-width: 90%; }
      .chat-composer { grid-template-columns: minmax(0, 1fr) 74px; }
      .chat-send-btn { min-width: 0; padding: 0 10px; }
    }
'''
    text = text.replace("  </style>", css + "\n  </style>", 1)

if JS_MARKER not in text:
    js = r'''

// FUTBOL USER CHAT
let chatMessages = [];
let chatChannel = null;
let chatUnreadCount = 0;
let chatLoading = false;
let chatPollTimer = null;

function chatTimestamp(value) {
  try {
    return new Intl.DateTimeFormat('et-EE', {
      timeZone: 'Europe/Tallinn',
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    }).format(new Date(value));
  } catch (_) {
    return '';
  }
}

function ensureChatUI() {
  const main = document.querySelector('main');
  const rules = document.getElementById('tab-rules');
  if (main && !document.getElementById('tab-chat')) {
    const section = document.createElement('section');
    section.id = 'tab-chat';
    section.className = 'hidden';
    section.innerHTML =
      '<h2>Chat</h2>' +
      '<div class="card chat-card">' +
        '<div id="chatMessages" class="chat-messages"><div class="chat-empty">Laen vestlust…</div></div>' +
        '<div class="chat-composer">' +
          '<textarea id="chatInput" class="chat-input" maxlength="500" rows="2" placeholder="Kirjuta sõnum…"></textarea>' +
          '<button id="chatSendButton" class="chat-send-btn" type="button" onclick="sendChatMessage()">Saada</button>' +
        '</div>' +
        '<div class="chat-note">Sõnumi maksimaalne pikkus on 500 märki.</div>' +
      '</div>';
    if (rules) main.insertBefore(section, rules);
    else main.appendChild(section);
  }

  const nav = document.querySelector('.bottom-nav-inner');
  const rulesButton = document.getElementById('nav-rules');
  if (nav && !document.getElementById('nav-chat')) {
    const button = document.createElement('button');
    button.id = 'nav-chat';
    button.className = 'nav-btn';
    button.type = 'button';
    button.onclick = () => showTab('chat');
    button.innerHTML = 'Chat<span id="chatUnread" class="chat-unread hidden">0</span>';
    if (rulesButton) nav.insertBefore(button, rulesButton);
    else nav.appendChild(button);
  }

  if (nav) nav.style.gridTemplateColumns = 'repeat(4, 1fr)';
}

function isChatOpen() {
  const tab = document.getElementById('tab-chat');
  return !!tab && !tab.classList.contains('hidden');
}

function updateChatUnread() {
  const badge = document.getElementById('chatUnread');
  if (!badge) return;
  if (chatUnreadCount > 0) {
    badge.textContent = chatUnreadCount > 99 ? '99+' : String(chatUnreadCount);
    badge.classList.remove('hidden');
  } else {
    badge.classList.add('hidden');
  }
}

function renderChatMessages(scrollToBottom = false) {
  const box = document.getElementById('chatMessages');
  if (!box) return;
  const nearBottom = box.scrollHeight - box.scrollTop - box.clientHeight < 90;

  if (!chatMessages.length) {
    box.innerHTML = '<div class="chat-empty">Vestlus on veel tühi. Kirjuta esimene sõnum.</div>';
    return;
  }

  box.innerHTML = chatMessages.map(item => {
    const own = currentUser && item.user_id === currentUser.id;
    const name = own ? 'Sina' : playerName(item.user_id);
    return '<div class="chat-message ' + (own ? 'own' : '') + '">' +
      '<div class="chat-meta">' + esc(name) + ' · ' + esc(chatTimestamp(item.created_at)) + '</div>' +
      '<div class="chat-bubble">' + esc(item.message) + '</div>' +
    '</div>';
  }).join('');

  if (scrollToBottom || nearBottom) box.scrollTop = box.scrollHeight;
}

async function loadChatMessages(scrollToBottom = false) {
  if (!currentUser || chatLoading) return;
  chatLoading = true;
  try {
    const result = await sb
      .from('chat_messages')
      .select('id,user_id,message,created_at')
      .order('created_at', { ascending: false })
      .limit(100);
    if (result.error) throw result.error;
    chatMessages = (result.data || []).reverse();
    renderChatMessages(scrollToBottom);
  } catch (error) {
    const box = document.getElementById('chatMessages');
    if (box) box.innerHTML = '<div class="chat-empty">Vestluse laadimine ebaõnnestus: ' + esc(friendlyError(error)) + '</div>';
  } finally {
    chatLoading = false;
  }
}

function appendChatMessage(message, fromRealtime = false) {
  if (!message || chatMessages.some(item => String(item.id) === String(message.id))) return;
  chatMessages.push(message);
  chatMessages.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
  if (chatMessages.length > 100) chatMessages = chatMessages.slice(-100);

  const own = currentUser && message.user_id === currentUser.id;
  if (fromRealtime && !own && !isChatOpen()) {
    chatUnreadCount += 1;
    updateChatUnread();
  }
  renderChatMessages(isChatOpen());
}

function subscribeChat() {
  if (!currentUser || chatChannel) return;
  chatChannel = sb
    .channel('futbol-user-chat')
    .on('postgres_changes', {
      event: 'INSERT',
      schema: 'public',
      table: 'chat_messages'
    }, payload => appendChatMessage(payload.new, true))
    .subscribe();

  if (!chatPollTimer) {
    chatPollTimer = window.setInterval(() => {
      if (currentUser && isChatOpen()) loadChatMessages(false);
    }, 15000);
  }
}

async function sendChatMessage() {
  if (!currentUser || !currentPlayer) return;
  const input = document.getElementById('chatInput');
  const button = document.getElementById('chatSendButton');
  const message = String(input?.value || '').trim();
  if (!message) return;
  if (message.length > 500) {
    toast('Sõnum võib olla kuni 500 märki.');
    return;
  }

  if (button) button.disabled = true;
  try {
    const result = await sb
      .from('chat_messages')
      .insert({ user_id: currentUser.id, message })
      .select('id,user_id,message,created_at')
      .single();
    if (result.error) throw result.error;
    if (input) input.value = '';
    appendChatMessage(result.data, false);
  } catch (error) {
    toast('Sõnumi saatmine ebaõnnestus: ' + friendlyError(error));
  } finally {
    if (button) button.disabled = false;
    if (input) input.focus();
  }
}

const __chatBaseShowTab = showTab;
showTab = function(name) {
  ensureChatUI();

  if (name === 'chat') {
    ['games', 'table', 'rules', 'admin'].forEach(tabName => {
      document.getElementById('tab-' + tabName)?.classList.add('hidden');
      document.getElementById('nav-' + tabName)?.classList.remove('active');
    });
    document.getElementById('tab-chat')?.classList.remove('hidden');
    document.getElementById('nav-chat')?.classList.add('active');
    chatUnreadCount = 0;
    updateChatUnread();
    loadChatMessages(true);
    subscribeChat();
    return;
  }

  document.getElementById('tab-chat')?.classList.add('hidden');
  document.getElementById('nav-chat')?.classList.remove('active');
  __chatBaseShowTab(name);
};

ensureChatUI();
setTimeout(() => {
  if (currentUser) subscribeChat();
}, 1200);
'''
    text = text.replace("\ninit();", js + "\n\ninit();", 1)

path.write_text(text, encoding="utf-8")
