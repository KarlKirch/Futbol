from pathlib import Path
import re

index_path = Path('index.html')
sw_path = Path('sw.js')
text = index_path.read_text(encoding='utf-8')
sw = sw_path.read_text(encoding='utf-8') if sw_path.exists() else ''

text = text.replace('Viimased 5 ametlikku mängu', 'Viimased 5 mängu · kõik sarjad')
text = text.replace(
    "const homeIsOwn = String(row.home_team || '').toLowerCase() === own;",
    "const homeIsOwn = typeof row.is_home === 'boolean' ? row.is_home : String(row.home_team || '').toLowerCase() === own;"
)
text = text.replace(
    "'<div class=\"current-match-score\">' + Number(row.home_score) + ':' + Number(row.away_score) + '</div>' +",
    "'<div class=\"current-match-score\">' + esc(row.score_text || (Number(row.home_score) + ':' + Number(row.away_score))) + '</div>' +"
)
text = text.replace('Omavahelised Champions League’i mängud', 'Omavahelised mängud')
text = text.replace(
    "h2h.map(row => '<div class=\"current-h2h-row\"><span>' + esc(row.season || '') + '</span><span>' + esc(row.home_team || '') + ' – ' + esc(row.away_team || '') + '</span><strong>' + Number(row.home_score) + ':' + Number(row.away_score) + '</strong></div>').join('') +",
    "h2h.map(row => '<div class=\"current-h2h-row\"><span>' + esc(statsShortDate(row.date)) + '</span><span>' + (row.competition ? '<strong>' + esc(row.competition) + '</strong> · ' : '') + esc(row.home_team || '') + ' – ' + esc(row.away_team || '') + '</span><strong>' + Number(row.home_score) + ':' + Number(row.away_score) + '</strong></div>').join('') +"
)
text = text.replace(
    'Viimased tulemused, koduliiga hetkeseis ja käimasoleva CL hooaja statistika.',
    'Viimased mängud kõigist sarjadest, koduliiga hetkeseis ja käimasoleva CL hooaja statistika.'
)

# Refresh installed/PWA clients after the statistics source and display change.
if sw:
    sw = re.sub(r'const CACHE_NAME = "futbol-champions-v\d+";', 'const CACHE_NAME = "futbol-champions-v9";', sw)

index_path.write_text(text, encoding='utf-8')
if sw_path.exists():
    sw_path.write_text(sw, encoding='utf-8')
print('Adapted match statistics UI to FotMob data')
