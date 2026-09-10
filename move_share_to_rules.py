from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
marker = '/* FUTBOL MOVE SHARE CARD TO RULES */'

if marker not in text:
    anchor = '\ninit();'
    pos = text.rfind(anchor)
    if pos == -1:
        raise SystemExit('init() anchor not found')

    patch = r'''

/* FUTBOL MOVE SHARE CARD TO RULES */
function moveShareCardToRules() {
  const rulesTab = document.getElementById('tab-rules');
  const playerSummary = document.getElementById('playerSummary');
  if (!rulesTab || !playerSummary) return;

  const freshShareCard = playerSummary.querySelector('.share-card');
  rulesTab.querySelectorAll('.share-card[data-rules-share="1"]').forEach(node => node.remove());
  if (!freshShareCard) return;

  freshShareCard.setAttribute('data-rules-share', '1');
  rulesTab.appendChild(freshShareCard);
}

const __rulesShareBaseRenderPlayerSummary = renderPlayerSummary;
renderPlayerSummary = function() {
  __rulesShareBaseRenderPlayerSummary();
  moveShareCardToRules();
};
'''
    text = text[:pos] + patch + text[pos:]

path.write_text(text, encoding='utf-8')
