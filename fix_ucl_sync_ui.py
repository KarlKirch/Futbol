from pathlib import Path

path = Path("index.html")
text = path.read_text(encoding="utf-8")

old = '''async function syncChampionsLeague(showMessage = false) {
  if (uclSyncRunning || !currentUser) return false;
  uclSyncRunning = true;
  try {
    const result = await sb.functions.invoke("sync-champions-league", { body: {} });
    if (result.error) throw result.error;
    const data = result.data || {};
    const changed = Number(data.fixtures_synced || 0) > 0 || Number(data.logos_synced || 0) > 0;
    if (showMessage) {
      if (changed) toast('Champions League’i andmed uuendatud.');
      else toast('Champions League’i andmed on juba värsked.');
    }
    return changed;
  } catch (error) {
    if (showMessage) toast('Automaatne uuendamine ebaõnnestus: ' + friendlyError(error));
    return false;
  } finally {
    uclSyncRunning = false;
  }
}
'''

new = '''async function syncChampionsLeague(showMessage = false) {
  if (uclSyncRunning || !currentUser) return false;
  uclSyncRunning = true;
  try {
    const result = await sb.functions.invoke("sync-champions-league", { body: {} });
    if (result.error) throw result.error;
    const data = result.data || {};
    if (data.ok === false) {
      throw new Error(data.error || "Champions League’i andmete uuendamine ebaõnnestus.");
    }
    const changed = Number(data.inserted || 0) > 0 || Number(data.updated || 0) > 0 || Number(data.logos_synced || 0) > 0;
    if (showMessage) {
      if (changed) toast('Champions League’i andmed uuendatud.');
      else toast('Champions League’i andmed on juba värsked.');
    }
    return changed;
  } catch (error) {
    if (showMessage) toast('Automaatne uuendamine ebaõnnestus: ' + friendlyError(error));
    return false;
  } finally {
    uclSyncRunning = false;
  }
}
'''

if old in text:
    text = text.replace(old, new, 1)
elif new not in text:
    raise SystemExit("UCL sync function anchor not found")

path.write_text(text, encoding="utf-8")
print("Fixed UCL sync error handling")
