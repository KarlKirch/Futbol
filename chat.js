// Futbol user chat. Loaded separately so chat cannot block the core app startup.
(function () {
  'use strict';

  var chatMessages = [];
  var chatChannel = null;
  var chatUnreadCount = 0;
  var chatLoading = false;
  var chatPollTimer = null;

  function byId(id) {
    return document.getElementById(id);
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
      var own = currentUser && item.user_id === currentUser.id;
      var name = own ? 'Sina' : playerName(item.user_id);
      return '<div class="chat-message ' + (own ? 'own' : '') + '">' +
        '<div class="chat-meta">' + esc(name) + ' · ' + esc(chatTimestamp(item.created_at)) + '</div>' +
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
        .select('id,user_id,message,created_at')
        .order('created_at', { ascending: false })
        .limit(100);
      if (result.error) throw result.error;
      chatMessages = (result.data || []).reverse();
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
    chatMessages.sort(function (a, b) { return new Date(a.created_at) - new Date(b.created_at); });
    if (chatMessages.length > 100) chatMessages = chatMessages.slice(-100);

    var own = currentUser && message.user_id === currentUser.id;
    if (fromRealtime && !own && !isChatOpen()) {
      chatUnreadCount += 1;
      updateChatUnread();
    }
    renderChatMessages(isChatOpen());
  }

  function subscribeChat() {
    if (!currentUser || chatChannel || typeof sb === 'undefined') return;
    try {
      chatChannel = sb
        .channel('futbol-user-chat')
        .on('postgres_changes', {
          event: 'INSERT',
          schema: 'public',
          table: 'chat_messages'
        }, function (payload) { appendChatMessage(payload.new, true); })
        .subscribe();
    } catch (error) {
      console.error('Chat realtime error', error);
      chatChannel = null;
    }

    if (!chatPollTimer) {
      chatPollTimer = window.setInterval(function () {
        if (currentUser && isChatOpen()) loadChatMessages(false);
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
        .insert({ user_id: currentUser.id, message: message })
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

    window.setTimeout(function () {
      if (currentUser && currentPlayer) subscribeChat();
    }, 1500);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', installChat, { once: true });
  } else {
    window.setTimeout(installChat, 0);
  }
})();
