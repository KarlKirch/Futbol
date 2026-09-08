from pathlib import Path

path = Path('chat.js')
text = path.read_text(encoding='utf-8')

MARKER = '// FUTBOL CHAT PRESENCE RELIABILITY'
if MARKER in text:
    raise SystemExit(0)

text = text.replace(
"  var chatOnlineUsers = new Set();\n  var chatPresenceTracked = false;\n\n  // FUTBOL CHAT ONLINE PRESENCE\n",
"  var chatOnlineUsers = new Set();\n  var chatPresenceTracked = false;\n  var chatRecentlyActive = new Map();\n  var chatPresenceRetryTimer = null;\n\n  // FUTBOL CHAT ONLINE PRESENCE\n  // FUTBOL CHAT PRESENCE RELIABILITY\n"
)

text = text.replace(
"  function chatPresenceDot(userId) {\n    var id = String(userId || '');\n    if (!id || !chatOnlineUsers.has(id)) return '';\n    return '<span class=\"chat-online-dot\" title=\"Online\" aria-label=\"Online\"></span>';\n  }\n",
"  function markChatRecentlyActive(userId, value) {\n    var id = String(userId || '');\n    if (!id) return;\n    var stamp = value ? new Date(value).getTime() : Date.now();\n    if (!Number.isFinite(stamp)) stamp = Date.now();\n    chatRecentlyActive.set(id, stamp);\n  }\n\n  function chatUserLooksOnline(userId) {\n    var id = String(userId || '');\n    if (!id) return false;\n    if (chatOnlineUsers.has(id)) return true;\n    var last = Number(chatRecentlyActive.get(id) || 0);\n    return last > 0 && Date.now() - last < 90000;\n  }\n\n  function chatPresenceDot(userId) {\n    var id = String(userId || '');\n    if (!id || !chatUserLooksOnline(id)) return '';\n    var exact = chatOnlineUsers.has(id);\n    var label = exact ? 'Online' : 'Äsja aktiivne';\n    return '<span class=\"chat-online-dot\" title=\"' + label + '\" aria-label=\"' + label + '\"></span>';\n  }\n"
)

text = text.replace(
"      chatMessages = (result.data || []).reverse();\n      renderChatMessages(!!scrollToBottom);\n",
"      chatMessages = (result.data || []).reverse();\n      chatMessages.forEach(function (item) {\n        if (item && item.user_id && item.created_at) markChatRecentlyActive(item.user_id, item.created_at);\n      });\n      renderChatMessages(!!scrollToBottom);\n"
)

text = text.replace(
"    chatMessages.push(message);\n    chatMessages.sort(function (a, b) { return new Date(a.created_at) - new Date(b.created_at); });\n",
"    chatMessages.push(message);\n    markChatRecentlyActive(message.user_id, message.created_at);\n    chatMessages.sort(function (a, b) { return new Date(a.created_at) - new Date(b.created_at); });\n"
)

old_subscribe = """        .subscribe(function (status) {\n          if (status !== 'SUBSCRIBED' || !chatChannel || chatPresenceTracked) return;\n          chatPresenceTracked = true;\n          Promise.resolve(chatChannel.track({\n            player_id: presenceKey,\n            online_at: new Date().toISOString()\n          })).catch(function (error) {\n            chatPresenceTracked = false;\n            console.error('Chat presence track error', error);\n          });\n        });\n"""
new_subscribe = """        .subscribe(function (status) {\n          if (status === 'SUBSCRIBED' && chatChannel) {\n            if (chatPresenceRetryTimer) {\n              window.clearTimeout(chatPresenceRetryTimer);\n              chatPresenceRetryTimer = null;\n            }\n            if (!chatPresenceTracked) {\n              chatPresenceTracked = true;\n              Promise.resolve(chatChannel.track({\n                player_id: presenceKey,\n                online_at: new Date().toISOString()\n              })).then(function () {\n                markChatRecentlyActive(presenceKey);\n                syncChatPresence();\n              }).catch(function (error) {\n                chatPresenceTracked = false;\n                console.error('Chat presence track error', error);\n              });\n            }\n            return;\n          }\n\n          if (status === 'CHANNEL_ERROR' || status === 'TIMED_OUT' || status === 'CLOSED') {\n            chatPresenceTracked = false;\n            chatOnlineUsers = new Set();\n            var stale = chatChannel;\n            chatChannel = null;\n            if (stale && typeof sb.removeChannel === 'function') {\n              Promise.resolve(sb.removeChannel(stale)).catch(function () {});\n            }\n            if (!chatPresenceRetryTimer) {\n              chatPresenceRetryTimer = window.setTimeout(function () {\n                chatPresenceRetryTimer = null;\n                if (currentUser) subscribeChat();\n              }, 2500);\n            }\n          }\n        });\n"""
text = text.replace(old_subscribe, new_subscribe)

text = text.replace(
"      chatPollTimer = window.setInterval(function () {\n        if (currentUser && isChatOpen()) loadChatMessages(false);\n      }, 15000);\n",
"      chatPollTimer = window.setInterval(function () {\n        if (currentUser && isChatOpen()) loadChatMessages(false);\n        if (isChatOpen()) renderChatMessages(false);\n      }, 15000);\n"
)

path.write_text(text, encoding='utf-8')
