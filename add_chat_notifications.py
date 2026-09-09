from pathlib import Path
import re

chat_path = Path('chat.js')
index_path = Path('index.html')
sw_path = Path('sw.js')

MARKER = '// FUTBOL CHAT PUSH NOTIFICATIONS'

if chat_path.exists():
    text = chat_path.read_text(encoding='utf-8')

    if MARKER not in text:
        text = text.replace(
            "  var chatPresenceTracked = false;\n",
            "  var chatPresenceTracked = false;\n  var chatNotificationEnabled = false;\n  var chatNotificationLoading = false;\n  var recentChatActivity = new Map();\n  var chatDeepLinkOpened = false;\n\n  " + MARKER + "\n",
            1,
        )

        text = text.replace(
            "    if (!id || !chatOnlineUsers.has(id)) return '';\n",
            "    if (!id || !isChatUserActive(id)) return '';\n",
            1,
        )

        helper_anchor = "  function chatTimestamp(value) {\n"
        helpers = r'''  function markChatRecentlyActive(userId, at) {
    var id = String(userId || '');
    if (!id) return;
    var ts = at ? new Date(at).getTime() : Date.now();
    if (!Number.isFinite(ts)) ts = Date.now();
    recentChatActivity.set(id, ts);
    window.setTimeout(function () {
      if (recentChatActivity.get(id) === ts && Date.now() - ts >= 90000) {
        recentChatActivity.delete(id);
        renderChatMessages(false);
      }
    }, 92000);
  }

  function hydrateRecentChatActivity() {
    var cutoff = Date.now() - 90000;
    chatMessages.forEach(function (item) {
      var ts = new Date(item.created_at).getTime();
      if (Number.isFinite(ts) && ts >= cutoff) markChatRecentlyActive(item.user_id, item.created_at);
    });
  }

  function isChatUserActive(userId) {
    var id = String(userId || '');
    if (!id) return false;
    if (chatOnlineUsers.has(id)) return true;
    var ts = recentChatActivity.get(id);
    return Number.isFinite(ts) && Date.now() - ts < 90000;
  }

  function chatPushSupported() {
    return 'serviceWorker' in navigator && 'PushManager' in window && typeof Notification !== 'undefined';
  }

  async function currentChatPushSubscription() {
    if (!chatPushSupported()) return null;
    var registration = await navigator.serviceWorker.ready;
    return await registration.pushManager.getSubscription();
  }

  async function refreshChatNotificationState() {
    if (!currentUser || typeof sb === 'undefined' || !chatPushSupported()) {
      chatNotificationEnabled = false;
      renderChatNotificationPanel();
      return;
    }
    try {
      var subscription = await currentChatPushSubscription();
      if (!subscription) {
        chatNotificationEnabled = false;
      } else {
        var result = await sb.from('push_subscriptions')
          .select('chat_enabled')
          .eq('user_id', currentUser.id)
          .eq('endpoint', subscription.endpoint)
          .maybeSingle();
        chatNotificationEnabled = !!(result.data && result.data.chat_enabled);
      }
    } catch (error) {
      console.error('Chat notification state error', error);
      chatNotificationEnabled = false;
    }
    renderChatNotificationPanel();
  }

  function renderChatNotificationPanel() {
    var mount = byId('chatNotificationPanel');
    if (!mount) return;
    if (!chatPushSupported()) {
      mount.innerHTML = '<div class="chat-notify-title">Chati teavitused</div><div class="chat-notify-text">See brauser ei toeta taustateavitusi.</div>';
      return;
    }
    if (Notification.permission === 'denied') {
      mount.innerHTML = '<div class="chat-notify-title">Chati teavitused</div><div class="chat-notify-text">Teavitused on brauseris blokeeritud. Luba need selle lehe saidiseadetes.</div>';
      return;
    }
    if (chatNotificationEnabled) {
      mount.innerHTML = '<div class="chat-notify-title">Chati teavitused <span class="chat-notify-on">Sees</span></div>' +
        '<div class="chat-notify-text">Uue sõnumi korral tuleb selles seadmes teavitus ka siis, kui Futbol pole ees.</div>' +
        '<button class="chat-notify-btn muted" type="button" onclick="window.futbolMuteChatNotifications()">Vaigista</button>';
    } else {
      mount.innerHTML = '<div class="chat-notify-title">Chati teavitused</div>' +
        '<div class="chat-notify-text">Lülita sisse, et saada uue chatisõnumi kohta teavitus selles seadmes.</div>' +
        '<button class="chat-notify-btn" type="button" onclick="window.futbolEnableChatNotifications()">Lülita sisse</button>';
    }
  }

  async function enableChatNotifications() {
    if (chatNotificationLoading || !currentUser || typeof sb === 'undefined') return;
    if (!chatPushSupported()) {
      toast('See brauser ei toeta taustateavitusi.');
      return;
    }
    chatNotificationLoading = true;
    try {
      var permission = Notification.permission;
      if (permission !== 'granted') permission = await Notification.requestPermission();
      if (permission !== 'granted') {
        renderChatNotificationPanel();
        return;
      }
      var registration = await navigator.serviceWorker.ready;
      var subscription = await registration.pushManager.getSubscription();
      if (!subscription) {
        subscription = await registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: urlBase64ToUint8Array(FUTBOL_VAPID_PUBLIC)
        });
      }
      var data = subscription.toJSON();
      var result = await sb.from('push_subscriptions').upsert({
        user_id: currentUser.id,
        endpoint: subscription.endpoint,
        p256dh: data.keys && data.keys.p256dh ? data.keys.p256dh : '',
        auth: data.keys && data.keys.auth ? data.keys.auth : '',
        chat_enabled: true,
        updated_at: new Date().toISOString()
      }, { onConflict: 'endpoint' });
      if (result.error) throw result.error;
      chatNotificationEnabled = true;
      renderChatNotificationPanel();
      toast('Chati teavitused on sisse lülitatud.');
    } catch (error) {
      console.error('Enable chat notifications error', error);
      toast('Chati teavituste sisselülitamine ebaõnnestus: ' + friendlyError(error));
    } finally {
      chatNotificationLoading = false;
    }
  }

  async function muteChatNotifications() {
    if (chatNotificationLoading || !currentUser || typeof sb === 'undefined') return;
    chatNotificationLoading = true;
    try {
      var subscription = await currentChatPushSubscription();
      if (subscription) {
        var result = await sb.from('push_subscriptions')
          .update({ chat_enabled: false, updated_at: new Date().toISOString() })
          .eq('user_id', currentUser.id)
          .eq('endpoint', subscription.endpoint);
        if (result.error) throw result.error;
      }
      chatNotificationEnabled = false;
      renderChatNotificationPanel();
      toast('Chati teavitused on vaigistatud.');
    } catch (error) {
      console.error('Mute chat notifications error', error);
      toast('Chati teavituste vaigistamine ebaõnnestus: ' + friendlyError(error));
    } finally {
      chatNotificationLoading = false;
    }
  }

  function notifyChatRecipients(messageId) {
    if (!messageId || typeof sb === 'undefined' || !sb.functions) return;
    Promise.resolve(sb.functions.invoke('send-chat-notification', { body: { message_id: messageId } }))
      .then(function (result) {
        if (result && result.error) console.error('Chat push invoke error', result.error);
      })
      .catch(function (error) { console.error('Chat push invoke error', error); });
  }

'''
        if helper_anchor in text:
            text = text.replace(helper_anchor, helpers + helper_anchor, 1)

        # Add notification controls under the existing composer note.
        old_note = "            '<div class=\"chat-note\">Sõnumi maksimaalne pikkus on 500 märki.</div>' +\n          '</div>';"
        new_note = "            '<div class=\"chat-note\">Sõnumi maksimaalne pikkus on 500 märki.</div>' +\n            '<div id=\"chatNotificationPanel\" class=\"chat-notify-panel\"></div>' +\n          '</div>';"
        if old_note in text:
            text = text.replace(old_note, new_note, 1)

        # Inject styles together with the presence style block.
        old_style_end = "      '.chat-online-dot[title]{cursor:default;}';"
        new_style_end = "      '.chat-online-dot[title]{cursor:default;}' +\n      '.chat-notify-panel{margin-top:12px;padding:12px;border:1px solid #d9e5de;border-radius:13px;background:#f8fbf9;}' +\n      '.chat-notify-title{font-size:13px;font-weight:900;color:#172019;}' +\n      '.chat-notify-text{margin-top:4px;color:#68746c;font-size:11px;line-height:1.45;}' +\n      '.chat-notify-on{display:inline-block;margin-left:5px;padding:2px 6px;border-radius:999px;background:#e8f4ed;color:#176b43;font-size:10px;}' +\n      '.chat-notify-btn{margin-top:8px;min-height:36px;padding:0 11px;border:0;border-radius:10px;background:#176b43;color:white;font-size:12px;font-weight:850;}' +\n      '.chat-notify-btn.muted{background:#edf2ef;color:#172019;}';"
        if old_style_end in text:
            text = text.replace(old_style_end, new_style_end, 1)

        # Treat a fresh message as recent activity as a fallback until every open client has refreshed to Presence.
        text = text.replace(
            "      chatMessages = (result.data || []).reverse();\n      renderChatMessages(!!scrollToBottom);",
            "      chatMessages = (result.data || []).reverse();\n      hydrateRecentChatActivity();\n      renderChatMessages(!!scrollToBottom);",
            1,
        )
        text = text.replace(
            "    chatMessages.push(message);\n",
            "    chatMessages.push(message);\n    markChatRecentlyActive(message.user_id, message.created_at);\n",
            1,
        )

        # Notify after a successful send; never block or alter the stored chat message.
        text = text.replace(
            "      appendChatMessage(result.data, false);\n",
            "      appendChatMessage(result.data, false);\n      notifyChatRecipients(result.data && result.data.id);\n",
            1,
        )

        # Render/refresh notification state and support opening Chat from a notification click.
        text = text.replace(
            "  function showChat() {\n    ensureChatUI();\n",
            "  function showChat() {\n    ensureChatUI();\n    refreshChatNotificationState();\n",
            1,
        )
        text = text.replace(
            "  function installChat() {\n    ensureChatUI();\n",
            "  function installChat() {\n    ensureChatUI();\n    renderChatNotificationPanel();\n    window.setTimeout(refreshChatNotificationState, 1800);\n",
            1,
        )
        text = text.replace(
            "      if (currentUser && currentPlayer) subscribeChat();\n      if (chatChannel || presenceAttempts >= 15) window.clearInterval(presenceBootstrap);",
            "      if (currentUser && currentPlayer) {\n        subscribeChat();\n        if (!chatDeepLinkOpened && new URLSearchParams(window.location.search).get('tab') === 'chat') {\n          chatDeepLinkOpened = true;\n          showChat();\n          try { history.replaceState(null, '', window.location.pathname + window.location.hash); } catch (_) {}\n        }\n      }\n      if ((chatChannel && chatDeepLinkOpened) || presenceAttempts >= 15) window.clearInterval(presenceBootstrap);",
            1,
        )

        text = text.replace(
            "  window.futbolReloadChat = function () { loadChatMessages(false); subscribeChat(); };\n",
            "  window.futbolReloadChat = function () { loadChatMessages(false); subscribeChat(); refreshChatNotificationState(); };\n  window.futbolEnableChatNotifications = enableChatNotifications;\n  window.futbolMuteChatNotifications = muteChatNotifications;\n",
            1,
        )

        chat_path.write_text(text, encoding='utf-8')

if index_path.exists():
    text = index_path.read_text(encoding='utf-8')
    text = re.sub(r'chat\.js\?v=\d+', 'chat.js?v=8', text)
    index_path.write_text(text, encoding='utf-8')

if sw_path.exists():
    text = sw_path.read_text(encoding='utf-8')
    text = re.sub(r'chat\.js\?v=\d+', 'chat.js?v=8', text)
    text = re.sub(r'const CACHE_NAME = "futbol-champions-v\d+";', 'const CACHE_NAME = "futbol-champions-v11";', text)
    sw_path.write_text(text, encoding='utf-8')
