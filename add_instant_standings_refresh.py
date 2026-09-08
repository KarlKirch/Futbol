from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
marker = '// FUTBOL INSTANT STANDINGS REFRESH'

if marker not in text:
    js = r'''

// FUTBOL INSTANT STANDINGS REFRESH
let officialResultRealtimeChannel = null;
let officialResultReloadTimer = null;
let officialResultReloading = false;

function scheduleOfficialResultReload() {
  if (officialResultReloadTimer) window.clearTimeout(officialResultReloadTimer);
  officialResultReloadTimer = window.setTimeout(async () => {
    officialResultReloadTimer = null;
    if (!currentUser || officialResultReloading) return;
    officialResultReloading = true;
    try {
      await loadAll();
    } catch (error) {
      console.error('Official result refresh error', error);
    } finally {
      officialResultReloading = false;
    }
  }, 350);
}

function subscribeOfficialResultRealtime() {
  if (!currentUser || officialResultRealtimeChannel || typeof sb === 'undefined') return;
  try {
    officialResultRealtimeChannel = sb
      .channel('futbol-official-results')
      .on('postgres_changes', {
        event: 'UPDATE',
        schema: 'public',
        table: 'matches'
      }, payload => {
        const row = payload?.new || {};
        if (row.home_score == null || row.away_score == null) return;
        const local = Array.isArray(matches) ? matches.find(m => String(m.id) === String(row.id)) : null;
        const changed = !local
          || Number(local.home_score) !== Number(row.home_score)
          || Number(local.away_score) !== Number(row.away_score)
          || String(local.finished_at || '') !== String(row.finished_at || '');
        if (changed) scheduleOfficialResultReload();
      })
      .subscribe();
  } catch (error) {
    console.error('Official result realtime error', error);
    officialResultRealtimeChannel = null;
  }
}

const __instantStandingsBaseLoadAll = loadAll;
loadAll = async function() {
  await __instantStandingsBaseLoadAll();
  subscribeOfficialResultRealtime();
};

window.setTimeout(subscribeOfficialResultRealtime, 1800);
'''
    text = text.replace('\ninit();', js + '\n\ninit();', 1)

path.write_text(text, encoding='utf-8')
