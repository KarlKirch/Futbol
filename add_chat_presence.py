from pathlib import Path
import re

chat_path = Path('chat.js')
index_path = Path('index.html')
sw_path = Path('sw.js')

MARKER = '// FUTBOL CHAT ONLINE PRESENCE'

if chat_path.exists():
    text = chat_path.read_text(encoding='utf-8')

    if MARKER not in text:
        text = text.replace(
            "  var chatPollTimer = null;\n",
            "  var chatPollTimer = null;\n  var chatOnlineUsers = new Set();\n  var chatPresenceTracked = false;\n\n  " + MARKER + "\n",
            1,
        )

        helper_anchor = "  function chatTimestamp(value) {\n"
        helpers = r'''  function ensureChatPresenceStyles() {
    if (byId('chatPresenceStyles')) return;
    var style = document.createElement('style');
    style.id = 'chatPresenceStyles';
    style.textContent =
      '.chat-online-dot{' +
        'display:inline-block;width:8px;height:8px;margin-left:6px;border-radius:50%;' +
        'background:#28b463;box-shadow:0 0 0 2px rgba(40,180,99,.14);vertical-align:1px;' +
      '}' +
      '.chat-online-dot[title]{cursor:default;}';
    document.head.appendChild(style);
  }

  function chatPresenceDot(userId) {
    var id = String(userId || '');
    if (!id || !chatOnlineUsers.has(id)) return '';
    return '<span class="chat-online-dot" title="Online" aria-label="Online"></span>';
  }

  function syncChatPresence() {
    if (!chatChannel || typeof chatChannel.presenceState !== 'function') return;
    try {
      var state = chatChannel.presenceState() || {};
      var next = new Set();
      Object.keys(state).forEach(function (key) {
        var entries = Array.isArray(state[key]) ? state[key] : [];
        entries.forEach(function (entry) {
          var id = String((entry && entry.player_id) || key || '');
          if (id) next.add(id);
        });
      });
      chatOnlineUsers = next;
      renderChatMessages(false);
    } catch (error) {
      console.error('Chat presence sync error', error);
    }
  }

'''
        if helper_anchor in text:
            text = text.replace(helper_anchor, helpers + helper_anchor, 1)

        text = text.replace(
            "  function ensureChatUI() {\n    try {\n",
            "  function ensureChatUI() {\n    try {\n      ensureChatPresenceStyles();\n",
            1,
        )

        old_meta = "        '<div class=\"chat-meta\"><span class=\"chat-name\">' + esc(name) + '</span>' + favorite + (item.pinned ? '<span class=\"chat-pin-label\">📌 TEADAANNE</span>' : '') + '<span class=\"chat-time\"> · ' + esc(chatTimestamp(item.created_at)) + '</span>' + adminDelete + '</div>' +\n"
        new_meta = "        '<div class=\"chat-meta\"><span class=\"chat-name\">' + esc(name) + '</span>' + chatPresenceDot(item.user_id) + favorite + (item.pinned ? '<span class=\"chat-pin-label\">📌 TEADAANNE</span>' : '') + '<span class=\"chat-time\"> · ' + esc(chatTimestamp(item.created_at)) + '</span>' + adminDelete + '</div>' +\n"
        if old_meta in text:
            text = text.replace(old_meta, new_meta, 1)

        old_channel = "      chatChannel = sb\n        .channel('futbol-user-chat')\n"
        new_channel = "      var presenceKey = String((currentPlayer && currentPlayer.id) || currentUser.id);\n      chatChannel = sb\n        .channel('futbol-user-chat', { config: { presence: { key: presenceKey } } })\n"
        if old_channel in text:
            text = text.replace(old_channel, new_channel, 1)

        old_subscribe = "        .on('postgres_changes', {\n          event: 'DELETE',\n          schema: 'public',\n          table: 'chat_messages'\n        }, function () { loadChatMessages(false); })\n        .subscribe();\n"
        new_subscribe = "        .on('postgres_changes', {\n          event: 'DELETE',\n          schema: 'public',\n          table: 'chat_messages'\n        }, function () { loadChatMessages(false); })\n        .on('presence', { event: 'sync' }, syncChatPresence)\n        .on('presence', { event: 'join' }, syncChatPresence)\n        .on('presence', { event: 'leave' }, syncChatPresence)\n        .subscribe(function (status) {\n          if (status !== 'SUBSCRIBED' || !chatChannel || chatPresenceTracked) return;\n          chatPresenceTracked = true;\n          Promise.resolve(chatChannel.track({\n            player_id: presenceKey,\n            online_at: new Date().toISOString()\n          })).catch(function (error) {\n            chatPresenceTracked = false;\n            console.error('Chat presence track error', error);\n          });\n        });\n"
        if old_subscribe in text:
            text = text.replace(old_subscribe, new_subscribe, 1)

        text = text.replace(
            "  window.futbolReloadChat = function () { loadChatMessages(false); };\n",
            "  window.futbolReloadChat = function () { loadChatMessages(false); subscribeChat(); };\n",
            1,
        )

        old_timeout = "    window.setTimeout(function () {\n      if (currentUser && currentPlayer) subscribeChat();\n    }, 1500);\n"
        new_timeout = "    var presenceAttempts = 0;\n    var presenceBootstrap = window.setInterval(function () {\n      presenceAttempts += 1;\n      if (currentUser && currentPlayer) subscribeChat();\n      if (chatChannel || presenceAttempts >= 15) window.clearInterval(presenceBootstrap);\n    }, 1000);\n"
        if old_timeout in text:
            text = text.replace(old_timeout, new_timeout, 1)

        chat_path.write_text(text, encoding='utf-8')

# Force browsers to fetch the updated standalone chat bundle.
if index_path.exists():
    text = index_path.read_text(encoding='utf-8')
    text = re.sub(r'chat\.js\?v=\d+', 'chat.js?v=7', text)
    index_path.write_text(text, encoding='utf-8')

if sw_path.exists():
    text = sw_path.read_text(encoding='utf-8')
    text = re.sub(r'chat\.js\?v=\d+', 'chat.js?v=7', text)
    text = re.sub(r'const CACHE_NAME = "futbol-champions-v\d+";', 'const CACHE_NAME = "futbol-champions-v10";', text)
    sw_path.write_text(text, encoding='utf-8')
