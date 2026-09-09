from pathlib import Path

path = Path("index.html")
text = path.read_text(encoding="utf-8")

CSS_MARKER = "/* FUTBOL LINEUP BUTTON UX V2 */"

# Make the lineup disclosure look and behave like the existing match-events disclosure.
if CSS_MARKER not in text:
    css = r'''

    /* FUTBOL LINEUP BUTTON UX V2 */
    .match-lineups-details { background:#fff; }
    .match-lineups-details > summary {
      display:flex;
      align-items:center;
      justify-content:space-between;
      gap:10px;
      padding:11px 14px;
      color:#46524a;
      font-size:11px;
      font-weight:900;
    }
    .match-lineups-details > summary::after {
      margin-left:auto;
      float:none;
    }
    .live-game-card .match-lineups-details {
      border-width:1px 0 0;
      border-color:#edf1ee;
      border-radius:0;
      background:#fff;
    }
    .live-game-card .match-lineups-details > summary {
      padding:11px 14px;
    }
'''
    text = text.replace("  </style>", css + "\n  </style>", 1)

# Use one clear action label, matching the user's requested wording.
text = text.replace("<summary>Koosseisud</summary>", "<summary>Koosseis</summary>")

# In the live match card, show Koosseis as its own disclosure directly before Sündmused.
old = '''    const block = matchLineupsDetailsHtml(match, lineup);\n    const marker = '<div class="live-data-note">';\n    if (html.includes(marker)) html = html.replace(marker, block + marker);\n    else html += block;'''
new = '''    const block = matchLineupsDetailsHtml(match, lineup);\n    const eventsMarker = '<details class="live-events">';\n    const noteMarker = '<div class="live-data-note">';\n    if (html.includes(eventsMarker)) html = html.replace(eventsMarker, block + eventsMarker);\n    else if (html.includes(noteMarker)) html = html.replace(noteMarker, block + noteMarker);\n    else html += block;'''
if old in text:
    text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8")
