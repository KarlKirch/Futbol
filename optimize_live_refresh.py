from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

MARKER = '// FUTBOL FAST LIVE REFRESH'
if MARKER in text:
    raise SystemExit(0)

old_vars = '''let liveMatchRefreshPending = null;
let liveMatchPollTimer = null;
let liveMatchLastFetchAt = 0;'''
new_vars = '''let liveMatchRefreshPending = null;
let liveMatchPollTimer = null;
let liveMatchLastFetchAt = 0;
let liveMatchCachedLoadAt = 0;
let liveMatchRealtimeChannel = null;

// FUTBOL FAST LIVE REFRESH'''
if old_vars not in text:
    raise SystemExit('Live state variable block not found')
text = text.replace(old_vars, new_vars, 1)

anchor = '''function liveStatusText(state) {'''
insert = r'''
function applyLiveRows(rows) {
  (Array.isArray(rows) ? rows : []).forEach(row => {
    if (row && row.match_id) liveMatchState.set(row.match_id, row);
  });
  renderLiveMatchCenter();
  decorateLiveMatchCards();
}

async function loadCachedLiveState(force = false) {
  if (!currentUser || !currentPlayer || typeof sb === 'undefined') return;
  if (!force && Date.now() - liveMatchCachedLoadAt < 2500) return;
  const relevant = liveRelevantMatches();
  if (!relevant.length) return;
  liveMatchCachedLoadAt = Date.now();
  try {
    const result = await sb
      .from('match_live_state')
      .select('match_id,fotmob_match_id,page_url,phase,live_time,started,finished,cancelled,home_score,away_score,events,source,source_updated_at,last_error,updated_at')
      .in('match_id', relevant.map(match => match.id));
    if (result.error) throw result.error;
    applyLiveRows(result.data || []);
  } catch (error) {
    console.error('Live vahemälu laadimine', error);
  }
}

function subscribeLiveStateRealtime() {
  if (!currentUser || liveMatchRealtimeChannel || typeof sb === 'undefined') return;
  try {
    liveMatchRealtimeChannel = sb
      .channel('futbol-live-match-state')
      .on('postgres_changes', { event:'*', schema:'public', table:'match_live_state' }, payload => {
        const row = payload?.new;
        if (!row || !row.match_id) return;
        if (!Array.isArray(matches) || !matches.some(match => match.id === row.match_id)) return;
        liveMatchState.set(row.match_id, row);
        renderLiveMatchCenter();
        decorateLiveMatchCards();
      })
      .subscribe();
  } catch (error) {
    console.error('Live realtime', error);
    liveMatchRealtimeChannel = null;
  }
}

function liveFreshnessText(state) {
  const raw = state?.source_updated_at || state?.updated_at;
  const ts = raw ? new Date(raw).getTime() : NaN;
  if (!Number.isFinite(ts)) return 'Live-andmed: FotMob · uuendub automaatselt';
  const seconds = Math.max(0, Math.round((Date.now() - ts) / 1000));
  if (seconds < 5) return 'Live-andmed: FotMob · uuendatud äsja';
  if (seconds < 60) return 'Live-andmed: FotMob · uuendatud ' + seconds + ' s tagasi';
  return 'Live-andmed: FotMob · uuendatud ' + Math.floor(seconds / 60) + ' min tagasi';
}

'''
if anchor not in text:
    raise SystemExit('liveStatusText anchor not found')
text = text.replace(anchor, insert + anchor, 1)

old_note = ''''<div class="live-data-note">Live-andmed: FotMob · uuendub automaatselt</div>' +'''
new_note = ''''<div class="live-data-note">' + esc(liveFreshnessText(state)) + '</div>' +'''
if old_note not in text:
    raise SystemExit('Live data note not found')
text = text.replace(old_note, new_note, 1)

old_refresh = r'''async function refreshLiveMatchCenter(force = false) {
  if (!currentUser || !currentPlayer || document.visibilityState === 'hidden') return;
  const relevant = liveRelevantMatches();
  if (!relevant.length) return;
  if (liveMatchRefreshPending) return liveMatchRefreshPending;
  if (!force && Date.now() - liveMatchLastFetchAt < 10000) return;
  liveMatchLastFetchAt = Date.now();
  liveMatchRefreshPending = (async () => {
    try {
      const result = await sb.functions.invoke('ucl-live', { body: { match_ids: relevant.map(match => match.id), force } });
      if (result.error || !result.data || result.data.ok === false) throw result.error || new Error(result.data?.error || 'Live-andmete laadimine ebaõnnestus');
      (result.data.matches || []).forEach(row => liveMatchState.set(row.match_id, row));
      renderLiveMatchCenter();
      decorateLiveMatchCards();
    } catch (error) {
      console.error('FotMob live center', error);
    } finally {
      liveMatchRefreshPending = null;
    }
  })();
  return liveMatchRefreshPending;
}'''
new_refresh = r'''async function refreshLiveMatchCenter(force = false) {
  if (!currentUser || !currentPlayer || document.visibilityState === 'hidden') return;
  const relevant = liveRelevantMatches();
  if (!relevant.length) return;
  if (liveMatchRefreshPending) return liveMatchRefreshPending;
  if (!force && Date.now() - liveMatchLastFetchAt < 8000) return;
  liveMatchLastFetchAt = Date.now();
  liveMatchRefreshPending = (async () => {
    try {
      const result = await sb.functions.invoke('ucl-live-fast', { body: { match_ids: relevant.map(match => match.id), force } });
      if (result.error || !result.data || result.data.ok === false) throw result.error || new Error(result.data?.error || 'Live-andmete laadimine ebaõnnestus');
      applyLiveRows(result.data.matches || []);
    } catch (error) {
      console.error('FotMob fast live center', error);
      await loadCachedLiveState(true);
    } finally {
      liveMatchRefreshPending = null;
    }
  })();
  return liveMatchRefreshPending;
}'''
if old_refresh not in text:
    raise SystemExit('refreshLiveMatchCenter block not found')
text = text.replace(old_refresh, new_refresh, 1)

old_poll = r'''function ensureLiveMatchPolling() {
  if (!liveMatchPollTimer) {
    liveMatchPollTimer = window.setInterval(() => {
      if (document.visibilityState === 'visible') refreshLiveMatchCenter(false);
    }, 30000);
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'visible') refreshLiveMatchCenter(true);
    });
  }
}'''
new_poll = r'''function ensureLiveMatchPolling() {
  subscribeLiveStateRealtime();
  if (!liveMatchPollTimer) {
    liveMatchPollTimer = window.setInterval(async () => {
      if (document.visibilityState !== 'visible') return;
      await loadCachedLiveState(false);
      refreshLiveMatchCenter(false);
    }, 10000);
    document.addEventListener('visibilitychange', async () => {
      if (document.visibilityState !== 'visible') return;
      await loadCachedLiveState(true);
      refreshLiveMatchCenter(true);
    });
  }
}'''
if old_poll not in text:
    raise SystemExit('ensureLiveMatchPolling block not found')
text = text.replace(old_poll, new_poll, 1)

old_initial = '''  window.setTimeout(() => refreshLiveMatchCenter(false), 0);'''
new_initial = '''  window.setTimeout(async () => {
    await loadCachedLiveState(true);
    refreshLiveMatchCenter(false);
  }, 0);'''
if old_initial not in text:
    raise SystemExit('Initial live refresh call not found')
text = text.replace(old_initial, new_initial, 1)

path.write_text(text, encoding='utf-8')
