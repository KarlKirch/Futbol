from pathlib import Path

path = Path("index.html")
text = path.read_text(encoding="utf-8")

# CSS for the row of quick-share apps under the main Share button.
css_anchor = "    .match-header {\n"
css_code = '''    .share-top {\n      display: flex;\n      align-items: center;\n      justify-content: space-between;\n      gap: 12px;\n    }\n\n    .share-apps {\n      display: flex;\n      flex-wrap: wrap;\n      gap: 8px;\n      width: 100%;\n      margin-top: 11px;\n      padding-top: 11px;\n      border-top: 1px solid rgba(255,255,255,.14);\n    }\n\n    .share-app-btn {\n      min-height: 36px;\n      padding: 0 10px;\n      border: 1px solid rgba(255,255,255,.18);\n      border-radius: 999px;\n      background: rgba(255,255,255,.08);\n      color: white;\n      font-size: 12px;\n      font-weight: 800;\n      white-space: nowrap;\n    }\n\n    .share-app-btn:hover {\n      background: rgba(255,255,255,.14);\n    }\n\n'''

if ".share-apps {" not in text:
    if css_anchor not in text:
        raise SystemExit("CSS anchor not found")
    text = text.replace(css_anchor, css_code + css_anchor, 1)

# The share card is now a vertical card: top row + app shortcuts beneath it.
old_share_card_css = '''    .share-card {\n      display: flex;\n      align-items: center;\n      justify-content: space-between;\n      gap: 12px;\n      padding: 12px 14px;\n      margin-bottom: 14px;\n      background: var(--dark);\n      color: white;\n      border-radius: 16px;\n      box-shadow: var(--shadow);\n    }'''
new_share_card_css = '''    .share-card {\n      display: block;\n      padding: 12px 14px;\n      margin-bottom: 14px;\n      background: var(--dark);\n      color: white;\n      border-radius: 16px;\n      box-shadow: var(--shadow);\n    }'''
if old_share_card_css in text:
    text = text.replace(old_share_card_css, new_share_card_css, 1)

# Add buttons under the normal Share button.
old_share_html = '''    '<div class="share-card">' +\n      '<div class="share-card-text">' +\n        '<div class="share-card-title">Kutsu sõbrad ennustama</div>' +\n        '<div class="share-card-subtitle">Jaga Futboli linki otse telefonist</div>' +\n      '</div>' +\n      '<button class="share-btn" onclick="shareFutbol()">Jaga</button>' +\n    '</div>';'''

new_share_html = '''    '<div class="share-card">' +\n      '<div class="share-top">' +\n        '<div class="share-card-text">' +\n          '<div class="share-card-title">Kutsu sõbrad ennustama</div>' +\n          '<div class="share-card-subtitle">Jaga Futboli linki otse telefonist</div>' +\n        '</div>' +\n        '<button class="share-btn" onclick="shareFutbol()">Jaga</button>' +\n      '</div>' +\n      '<div class="share-apps">' +\n        '<button class="share-app-btn" onclick="shareViaApp(\\'whatsapp\\')">WhatsApp</button>' +\n        '<button class="share-app-btn" onclick="shareViaApp(\\'messenger\\')">Messenger</button>' +\n        '<button class="share-app-btn" onclick="shareViaApp(\\'viber\\')">Viber</button>' +\n        '<button class="share-app-btn" onclick="shareViaApp(\\'instagram\\')">Instagram</button>' +\n        '<button class="share-app-btn" onclick="shareViaApp(\\'telegram\\')">Telegram</button>' +\n        '<button class="share-app-btn" onclick="shareViaApp(\\'facebook\\')">Facebook</button>' +\n        '<button class="share-app-btn" onclick="copyFutbolLink()">Kopeeri link</button>' +\n      '</div>' +\n    '</div>';'''

if "shareViaApp(\\'whatsapp\\')" not in text:
    if old_share_html not in text:
        raise SystemExit("Share HTML anchor not found")
    text = text.replace(old_share_html, new_share_html, 1)

# Add helper functions before the existing renderGames function.
js_anchor = "function renderGames() {\n"
js_code = r'''function futbolShareUrl() {
  return window.location.origin + window.location.pathname;
}

function futbolShareText() {
  return "Tule ennusta meiega jalgpallimängude skoore!";
}

async function copyFutbolLink(showMessage = true) {

  const url = futbolShareUrl();

  try {
    if (navigator.clipboard) {
      await navigator.clipboard.writeText(url);
    } else {
      window.prompt("Kopeeri Futboli link:", url);
      return;
    }

    if (showMessage) {
      toast("Futboli link kopeeritud.");
    }
  } catch (error) {
    window.prompt("Kopeeri Futboli link:", url);
  }
}

async function shareViaApp(app) {

  const url = futbolShareUrl();
  const message = futbolShareText();
  const combined = message + " " + url;

  if (app === "whatsapp") {
    window.open(
      "https://wa.me/?text=" + encodeURIComponent(combined),
      "_blank",
      "noopener"
    );
    return;
  }

  if (app === "telegram") {
    window.open(
      "https://t.me/share/url?url=" + encodeURIComponent(url) +
      "&text=" + encodeURIComponent(message),
      "_blank",
      "noopener"
    );
    return;
  }

  if (app === "facebook") {
    window.open(
      "https://www.facebook.com/sharer/sharer.php?u=" +
      encodeURIComponent(url),
      "_blank",
      "noopener"
    );
    return;
  }

  if (app === "viber") {
    await copyFutbolLink(false);
    window.location.href =
      "viber://forward?text=" + encodeURIComponent(combined);
    return;
  }

  if (app === "messenger") {
    await copyFutbolLink(false);

    const mobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);

    if (mobile) {
      window.location.href =
        "fb-messenger://share/?link=" + encodeURIComponent(url);
    } else {
      window.open("https://www.messenger.com/", "_blank", "noopener");
      toast("Link kopeeritud — kleebi see Messengeri vestlusesse.");
    }
    return;
  }

  if (app === "instagram") {
    await copyFutbolLink(false);
    window.open("https://www.instagram.com/", "_blank", "noopener");
    toast("Link kopeeritud — kleebi see Instagrami sõnumisse.");
  }
}

'''

if "function shareViaApp(app)" not in text:
    if js_anchor not in text:
        raise SystemExit("JavaScript anchor not found")
    text = text.replace(js_anchor, js_code + js_anchor, 1)

# Reuse the clean canonical URL in the native share button too.
text = text.replace('url: window.location.href', 'url: futbolShareUrl()')
text = text.replace('await navigator.clipboard.writeText(window.location.href);', 'await navigator.clipboard.writeText(futbolShareUrl());')
text = text.replace('window.prompt("Kopeeri Futboli link:", window.location.href);', 'window.prompt("Kopeeri Futboli link:", futbolShareUrl());')

path.write_text(text, encoding="utf-8")
