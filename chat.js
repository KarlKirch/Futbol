// Futbol user chat. Loaded separately so chat cannot block the core app startup.
(function () {
  'use strict';

  var chatMessages = [];
  var chatChannel = null;
  var chatUnreadCount = 0;
  var chatLoading = false;
  var chatPollTimer = null;
  var chatOnlineUsers = new Set();
  var chatPresenceTracked = false;
  var chatRecentlyActive = new Map();
  var chatPresenceRetryTimer = null;
  var chatNotificationEnabled = false;
  var chatNotificationLoading = false;
  var chatDeepLinkOpened = false;

  // FUTBOL CHAT PUSH NOTIFICATIONS

  // FUTBOL CHAT ONLINE PRESENCE
  // FUTBOL CHAT PRESENCE RELIABILITY

  function byId(id) {
    return document.getElementById(id);
  }

  function ensureChatPresenceStyles() {
    if (byId('chatPresenceStyles')) return;
    var style = document.createElement('style');
    style.id = 'chatPresenceStyles';
    style.textContent =
      '.chat-online-dot{' +
        'display:inline-block;width:8px;height:8px;margin-left:6px;border-radius:50%;' +
        'background:#28b463;box-shadow:0 0 0 2px rgba(40,180,99,.14);vertical-align:1px;' +
      '}' +
      '.chat-online-dot[title]{cursor:default;}' +
      '.chat-notify-panel{margin-top:12px;padding:12px;border:1px solid #d9e5de;border-radius:13px;background:#f8fbf9;}' +
      '.chat-notify-title{font-size:13px;font-weight:900;color:#172019;}' +
      '.chat-notify-text{margin-top:4px;color:#68746c;font-size:11px;line-height:1.45;}' +
      '.chat-notify-on{display:inline-block;margin-left:5px;padding:2px 6px;border-radius:999px;background:#e8f4ed;color:#176b43;font-size:10px;}' +
      '.chat-notify-btn{margin-top:8px;min-height:36px;padding:0 11px;border:0;border-radius:10px;background:#176b43;color:white;font-size:12px;font-weight:850;}' +
      '.chat-notify-btn.muted{background:#edf2ef;color:#172019;}';
    document.head.appendChild(style);
  }

  function markChatRecentlyActive(userId, value) {
    var id = String(userId || '');
    if (!id) return;
    var stamp = value ? new Date(value).getTime() : Date.now();
    if (!Number.isFinite(stamp)) stamp = Date.now();
    chatRecentlyActive.set(id, stamp);
  }

  function chatUserLooksOnline(userId) {
    var id = String(userId || '');
    if (!id) return false;
    if (chatOnlineUsers.has(id)) return true;
    var last = Number(chatRecentlyActive.get(id) || 0);
    return last > 0 && Date.now() - last < 90000;
  }

  function chatPresenceDot(userId) {
    var id = String(userId || '');
    if (!id || !chatUserLooksOnline(id)) return '';
    var exact = chatOnlineUsers.has(id);
    var label = exact ? 'Online' : 'Äsja aktiivne';
    return '<span class="chat-online-dot" title="' + label + '" aria-label="' + label + '"></span>';
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
        if (result.error) throw result.error;
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

  function chatTimestamp(value) {
    try {
      return new Intl.DateTimeFormat('et-EE', {
        timeZone: 'Europe/Tallinn',
        day: '2-digit',
        month: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      }).format(new Date(value));
    } catch (error) {
      return '';
    }
  }

  function ensureChatUI() {
    try {
      ensureChatPresenceStyles();
      var rules = byId('tab-rules');
      var main = rules ? rules.parentElement : null;
      if (main && !byId('tab-chat')) {
        var section = document.createElement('section');
        section.id = 'tab-chat';
        section.className = 'hidden';
        section.innerHTML =
          '<h2>Chat</h2>' +
          '<div class="card chat-card">' +
            '<div id="chatMessages" class="chat-messages"><div class="chat-empty">Laen vestlust…</div></div>' +
            '<div class="chat-composer">' +
              '<textarea id="chatInput" class="chat-input" maxlength="500" rows="2" placeholder="Kirjuta sõnum…"></textarea>' +
              '<button id="chatSendButton" class="chat-send-btn" type="button">Saada</button>' +
            '</div>' +
            '<div class="chat-note">Sõnumi maksimaalne pikkus on 500 märki.</div>' +
            '<div id="chatNotificationPanel" class="chat-notify-panel"></div>' +
          '</div>';
        main.insertBefore(section, rules);
      }

      var nav = document.querySelector('.bottom-nav-inner');
      var rulesButton = byId('nav-rules');
      if (nav && !byId('nav-chat')) {
        var button = document.createElement('button');
        button.id = 'nav-chat';
        button.className = 'nav-btn';
        button.type = 'button';
        button.innerHTML = 'Chat<span id="chatUnread" class="chat-unread hidden">0</span>';
        button.addEventListener('click', function () { showChat(); });
        if (rulesButton) nav.insertBefore(button, rulesButton);
        else nav.appendChild(button);
      }
      if (nav) nav.style.gridTemplateColumns = 'repeat(4, 1fr)';

      var sendButton = byId('chatSendButton');
      if (sendButton && !sendButton.dataset.bound) {
        sendButton.dataset.bound = '1';
        sendButton.addEventListener('click', sendChatMessage);
      }
    } catch (error) {
      console.error('Chat UI error', error);
    }
  }

  function isChatOpen() {
    var tab = byId('tab-chat');
    return !!tab && !tab.classList.contains('hidden');
  }

  function updateChatUnread() {
    var badge = byId('chatUnread');
    if (!badge) return;
    if (chatUnreadCount > 0) {
      badge.textContent = chatUnreadCount > 99 ? '99+' : String(chatUnreadCount);
      badge.classList.remove('hidden');
    } else {
      badge.classList.add('hidden');
    }
  }

  function renderChatMessages(scrollToBottom) {
    var box = byId('chatMessages');
    if (!box) return;
    var nearBottom = box.scrollHeight - box.scrollTop - box.clientHeight < 90;

    if (!chatMessages.length) {
      box.innerHTML = '<div class="chat-empty">Vestlus on veel tühi. Kirjuta esimene sõnum.</div>';
      return;
    }
    box.innerHTML = chatMessages.map(function (item) {
      var own = currentUser && item.user_id === (currentPlayer?.id || currentUser.id);
      var name = own ? 'Sina' : playerName(item.user_id);
      var favorite = (typeof chatFavoriteMini === 'function') ? chatFavoriteMini(item.user_id) : '';
      var adminDelete = (typeof adminVerified !== 'undefined' && adminVerified)
        ? '<button class="chat-admin-delete" type="button" onclick="adminDeleteChatMessageDeep(' + item.id + ')">Kustuta</button>' : '';
      return '<div class="chat-message ' + (own ? 'own' : '') + '">' +
        '<div class="chat-meta"><span class="chat-name">' + esc(name) + '</span>' + chatPresenceDot(item.user_id) + favorite + (item.pinned ? '<span class="chat-pin-label">📌 TEADAANNE</span>' : '') + '<span class="chat-time"> · ' + esc(chatTimestamp(item.created_at)) + '</span>' + adminDelete + '</div>' +
        '<div class="chat-bubble">' + esc(item.message) + '</div>' +
      '</div>';
    }).join('');

    if (scrollToBottom || nearBottom) box.scrollTop = box.scrollHeight;
  }

  async function loadChatMessages(scrollToBottom) {
    if (!currentUser || chatLoading || typeof sb === 'undefined') return;
    chatLoading = true;
    try {
      var result = await sb
        .from('chat_messages')
        .select('id,user_id,message,created_at,is_announcement,pinned')
        .order('created_at', { ascending: false })
        .limit(100);
      if (result.error) throw result.error;
      chatMessages = (result.data || []).reverse();
      chatMessages.forEach(function (item) {
        if (item && item.user_id && item.created_at) markChatRecentlyActive(item.user_id, item.created_at);
      });
      renderChatMessages(!!scrollToBottom);
    } catch (error) {
      var box = byId('chatMessages');
      if (box) box.innerHTML = '<div class="chat-empty">Vestluse laadimine ebaõnnestus: ' + esc(friendlyError(error)) + '</div>';
    } finally {
      chatLoading = false;
    }
  }

  function appendChatMessage(message, fromRealtime) {
    if (!message || chatMessages.some(function (item) { return String(item.id) === String(message.id); })) return;
    chatMessages.push(message);
    markChatRecentlyActive(message.user_id, message.created_at);
    chatMessages.sort(function (a, b) { return new Date(a.created_at) - new Date(b.created_at); });
    if (chatMessages.length > 100) chatMessages = chatMessages.slice(-100);

    var own = currentUser && message.user_id === (currentPlayer?.id || currentUser.id);
    if (fromRealtime && !own && !isChatOpen()) {
      chatUnreadCount += 1;
      updateChatUnread();
    }
    renderChatMessages(isChatOpen());
  }

  function subscribeChat() {
    if (!currentUser || chatChannel || typeof sb === 'undefined') return;
    try {
      var presenceKey = String((currentPlayer && currentPlayer.id) || currentUser.id);
      chatChannel = sb
        .channel('futbol-user-chat', { config: { presence: { key: presenceKey } } })
        .on('postgres_changes', {
          event: 'INSERT',
          schema: 'public',
          table: 'chat_messages'
        }, function (payload) { appendChatMessage(payload.new, true); })
        .on('postgres_changes', {
          event: 'UPDATE',
          schema: 'public',
          table: 'chat_messages'
        }, function () { loadChatMessages(false); })
        .on('postgres_changes', {
          event: 'DELETE',
          schema: 'public',
          table: 'chat_messages'
        }, function () { loadChatMessages(false); })
        .on('presence', { event: 'sync' }, syncChatPresence)
        .on('presence', { event: 'join' }, syncChatPresence)
        .on('presence', { event: 'leave' }, syncChatPresence)
        .subscribe(function (status) {
          if (status === 'SUBSCRIBED' && chatChannel) {
            if (chatPresenceRetryTimer) {
              window.clearTimeout(chatPresenceRetryTimer);
              chatPresenceRetryTimer = null;
            }
            if (!chatPresenceTracked) {
              chatPresenceTracked = true;
              Promise.resolve(chatChannel.track({
                player_id: presenceKey,
                online_at: new Date().toISOString()
              })).then(function () {
                markChatRecentlyActive(presenceKey);
                syncChatPresence();
              }).catch(function (error) {
                chatPresenceTracked = false;
                console.error('Chat presence track error', error);
              });
            }
            return;
          }

          if (status === 'CHANNEL_ERROR' || status === 'TIMED_OUT' || status === 'CLOSED') {
            chatPresenceTracked = false;
            chatOnlineUsers = new Set();
            var stale = chatChannel;
            chatChannel = null;
            if (stale && typeof sb.removeChannel === 'function') {
              Promise.resolve(sb.removeChannel(stale)).catch(function () {});
            }
            if (!chatPresenceRetryTimer) {
              chatPresenceRetryTimer = window.setTimeout(function () {
                chatPresenceRetryTimer = null;
                if (currentUser) subscribeChat();
              }, 2500);
            }
          }
        });
    } catch (error) {
      console.error('Chat realtime error', error);
      chatChannel = null;
    }

    if (!chatPollTimer) {
      chatPollTimer = window.setInterval(function () {
        if (currentUser && isChatOpen()) loadChatMessages(false);
        if (isChatOpen()) renderChatMessages(false);
      }, 15000);
    }
  }

  async function sendChatMessage() {
    if (!currentUser || !currentPlayer || typeof sb === 'undefined') return;
    var input = byId('chatInput');
    var button = byId('chatSendButton');
    var message = String(input ? input.value : '').trim();
    if (!message) return;
    if (message.length > 500) {
      toast('Sõnum võib olla kuni 500 märki.');
      return;
    }

    if (button) button.disabled = true;
    try {
      var result = await sb
        .from('chat_messages')
        .insert({ user_id: (currentPlayer?.id || currentUser.id), message: message })
        .select('id,user_id,message,created_at,is_announcement,pinned')
        .single();
      if (result.error) throw result.error;
      if (input) input.value = '';
      appendChatMessage(result.data, false);
      notifyChatRecipients(result.data && result.data.id);
    } catch (error) {
      toast('Sõnumi saatmine ebaõnnestus: ' + friendlyError(error));
    } finally {
      if (button) button.disabled = false;
      if (input) input.focus();
    }
  }

  function hideCoreTabs() {
    ['games', 'table', 'rules', 'admin'].forEach(function (name) {
      var tab = byId('tab-' + name);
      var nav = byId('nav-' + name);
      if (tab) tab.classList.add('hidden');
      if (nav) nav.classList.remove('active');
    });
  }

  function showChat() {
    ensureChatUI();
    refreshChatNotificationState();
    hideCoreTabs();
    var tab = byId('tab-chat');
    var nav = byId('nav-chat');
    if (tab) tab.classList.remove('hidden');
    if (nav) nav.classList.add('active');
    chatUnreadCount = 0;
    updateChatUnread();
    loadChatMessages(true);
    subscribeChat();
  }

  function installChat() {
    ensureChatUI();
    renderChatNotificationPanel();
    window.setTimeout(refreshChatNotificationState, 1800);
    if (typeof showTab === 'function' && !window.__futbolChatWrapped) {
      var baseShowTab = showTab;
      showTab = function (name) {
        if (name === 'chat') {
          showChat();
          return;
        }
        var chatTab = byId('tab-chat');
        var chatNav = byId('nav-chat');
        if (chatTab) chatTab.classList.add('hidden');
        if (chatNav) chatNav.classList.remove('active');
        baseShowTab(name);
      };
      window.__futbolChatWrapped = true;
    }

    var presenceAttempts = 0;
    var presenceBootstrap = window.setInterval(function () {
      presenceAttempts += 1;
      if (currentUser && currentPlayer) {
        subscribeChat();
        if (!chatDeepLinkOpened && new URLSearchParams(window.location.search).get('tab') === 'chat') {
          chatDeepLinkOpened = true;
          showChat();
          try { history.replaceState(null, '', window.location.pathname + window.location.hash); } catch (_) {}
        }
      }
      if (chatChannel || presenceAttempts >= 15) window.clearInterval(presenceBootstrap);
    }, 1000);
  }

  window.futbolReloadChat = function () { loadChatMessages(false); subscribeChat(); refreshChatNotificationState(); };
  window.futbolEnableChatNotifications = enableChatNotifications;
  window.futbolMuteChatNotifications = muteChatNotifications;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', installChat, { once: true });
  } else {
    window.setTimeout(installChat, 0);
  }
})();
