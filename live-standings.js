// Futbol live leaderboard. Provisional only: official database totals stay untouched.
(function () {
  'use strict';

  function provisionalPoints(prediction, home, away) {
    const ph = Number(prediction?.home_score);
    const pa = Number(prediction?.away_score);
    const ah = Number(home);
    const aa = Number(away);
    if (![ph, pa, ah, aa].every(Number.isFinite)) return 0;
    if (ph === ah && pa === aa) return 3;
    return Math.sign(ph - pa) === Math.sign(ah - aa) ? 1 : 0;
  }

  function liveStandingsMatches() {
    if (!Array.isArray(matches) || typeof liveMatchState === 'undefined') return [];
    return matches.filter(match => {
      const state = liveMatchState.get(match.id);
      if (!state || !state.started || state.cancelled) return false;
      if (typeof isFinished === 'function' && isFinished(match)) return false;
      return state.home_score !== null && state.home_score !== undefined &&
        state.away_score !== null && state.away_score !== undefined;
    });
  }

  function buildLiveStandings() {
    const activeMatches = liveStandingsMatches();
    const paidIds = new Set((leaderboard || []).map(row => String(row.player_id)));
    const liveByPlayer = new Map();
    const liveByRound = new Map();

    (predictions || []).forEach(prediction => {
      const playerId = String(prediction.user_id || '');
      if (!paidIds.has(playerId)) return;
      const match = activeMatches.find(row => String(row.id) === String(prediction.match_id));
      if (!match) return;
      const state = liveMatchState.get(match.id);
      const points = provisionalPoints(prediction, state.home_score, state.away_score);
      const stat = liveByPlayer.get(playerId) || { points: 0, exact: 0 };
      stat.points += points;
      if (points === 3) stat.exact += 1;
      liveByPlayer.set(playerId, stat);

      const round = Number(match.round_number || 0);
      if (round > 0) {
        if (!liveByRound.has(round)) liveByRound.set(round, new Map());
        const roundMap = liveByRound.get(round);
        roundMap.set(playerId, Number(roundMap.get(playerId) || 0) + points);
      }
    });

    const rows = (leaderboard || []).map(row => {
      const playerId = String(row.player_id);
      const live = liveByPlayer.get(playerId) || { points: 0, exact: 0 };
      return {
        ...row,
        official_rank: Number(row.rank_no || 0),
        official_total: Number(row.total_points || 0),
        live_points: Number(live.points || 0),
        live_exact: Number(live.exact || 0),
        live_total: Number(row.total_points || 0) + Number(live.points || 0),
        live_exact_total: Number(row.exact_scores || 0) + Number(live.exact || 0)
      };
    });

    rows.sort((a, b) =>
      b.live_total - a.live_total ||
      b.live_exact_total - a.live_exact_total ||
      String(a.player_name || '').localeCompare(String(b.player_name || ''), 'et')
    );
    rows.forEach((row, index) => { row.live_rank = index + 1; });

    return { rows, activeMatches, liveByRound };
  }

  function liveMovementHtml(row) {
    const movement = Number(row.official_rank || 0) - Number(row.live_rank || 0);
    if (movement > 0) return '<span class="live-rank-move up">↑ ' + movement + '</span>';
    if (movement < 0) return '<span class="live-rank-move down">↓ ' + Math.abs(movement) + '</span>';
    return '<span class="live-rank-move same">–</span>';
  }

  function liveBannerHtml(activeMatches) {
    if (!activeMatches.length) return '';
    const scores = activeMatches.slice(0, 4).map(match => {
      const state = liveMatchState.get(match.id);
      return '<span class="live-table-game"><strong>' + esc(match.home_team) + ' ' +
        Number(state.home_score) + ':' + Number(state.away_score) + ' ' + esc(match.away_team) + '</strong>' +
        '<small>' + esc(typeof liveStatusText === 'function' ? liveStatusText(state) : 'LIVE') + '</small></span>';
    }).join('');
    const more = activeMatches.length > 4 ? '<span class="live-table-more">+' + (activeMatches.length - 4) + ' mängu</span>' : '';
    return '<div class="live-table-banner">' +
      '<div class="live-table-banner-head"><span class="live-table-dot"></span><strong>LIVE tabel</strong>' +
      '<span>Ajutised punktid vastavalt hetkeskoorile</span></div>' +
      '<div class="live-table-games">' + scores + more + '</div>' +
    '</div>';
  }

  renderLeaderboard = function() {
    const container = document.getElementById('leaderboard');
    if (!container) return;
    if (!leaderboard.length) {
      container.innerHTML = '<div class="card"><div class="notice">Ametlik tabel on veel tühi. Tabelisse jõuavad makse kinnitanud osalejad.</div></div>';
      return;
    }

    const liveData = buildLiveStandings();
    const isLive = liveData.activeMatches.length > 0;
    const baseRounds = typeof leaderboardVisibleRounds === 'function' ? leaderboardVisibleRounds() : [];
    const liveRounds = liveData.activeMatches.map(match => Number(match.round_number || 0)).filter(n => n > 0);
    const rounds = [...new Set([...baseRounds, ...liveRounds])].sort((a, b) => a - b);
    const latestRound = rounds.length ? rounds[rounds.length - 1] : null;
    const roundMaps = new Map(rounds.map(n => [n, typeof roundStatMap === 'function' ? roundStatMap(n) : new Map()]));
    const bonusMap = typeof bonusScoreMap === 'function' ? bonusScoreMap() : new Map();
    const showBonus = Array.isArray(bonusQuestionsState) && bonusQuestionsState.some(q => q.is_resolved);
    const displayRows = isLive ? liveData.rows : leaderboard;
    const leaderPoints = Math.max(...displayRows.map(item => Number(isLive ? item.live_total : item.total_points || 0)));

    let html = (latestRound && typeof roundSummaryHtml === 'function' ? roundSummaryHtml(latestRound) : '') +
      liveBannerHtml(liveData.activeMatches) +
      '<div class="leaderboard-toolbar"><div><div class="leaderboard-toolbar-title">' + (isLive ? 'Üldtabel · LIVE' : 'Üldtabel') + '</div>' +
      '<div class="leaderboard-table-note">' + (isLive
        ? 'Käimasolevate mängude punktid on ajutised ja muutuvad koos mänguseisuga. Ametlikud punktid kinnituvad pärast lõpptulemuse salvestamist.'
        : 'Voorude punktid täienevad jooksvalt. Hooaja lõpus lisanduvad õigete boonusküsimuste punktid kogusummale.') +
      '</div></div></div>' +
      '<div class="card table-wrap"><table class="leaderboard-plus leaderboard-dynamic ' + (isLive ? 'leaderboard-live' : '') + '"><thead><tr><th>Koht</th><th>Mängija</th>';

    rounds.forEach(n => {
      html += '<th class="num round-history-head ' + (n === latestRound ? 'latest' : '') + (liveData.liveByRound.has(n) ? ' live-round-head' : '') + '">' + esc(competitionRoundShort(n)) + '</th>';
    });
    if (showBonus) html += '<th class="num">Boonus</th>';
    html += '<th class="num">Kokku</th><th class="num">Liidrist</th><th class="num">±</th></tr></thead><tbody>';

    displayRows.forEach(sourceRow => {
      const row = isLive ? sourceRow : sourceRow;
      const rank = isLive ? Number(row.live_rank) : Number(row.rank_no);
      const medal = rank === 1 ? '🥇' : rank === 2 ? '🥈' : rank === 3 ? '🥉' : '';
      const isSelf = String(row.player_id) === String(ownPlayerId());
      const total = Number(isLive ? row.live_total : row.total_points || 0);
      const gap = Math.max(0, leaderPoints - total);
      const prize = typeof prizeForRankDeep === 'function' ? prizeForRankDeep(rank) : null;
      const liveGain = isLive ? Number(row.live_points || 0) : 0;

      html += '<tr class="' + (isSelf ? 'leaderboard-self ' : '') + (isLive ? 'live-standing-row' : '') + '">' +
        '<td class="rank">' + (medal ? '<span class="rank-medal">' + medal + '</span>' : '') + rank + '</td>' +
        '<td><button class="player-name-btn" onclick="openPlayerStats(\'' + row.player_id + '\')">' + esc(row.player_name) + '</button>' +
        (typeof favoriteClubMini === 'function' ? favoriteClubMini(row.player_id) : '') +
        (prize != null && typeof euroText === 'function' ? '<span class="leader-prize-chip">' + euroText(prize) + '</span>' : '') +
        '<div class="leader-player-meta">' + Number(row.exact_scores || 0) + ' täpset · ' + Number(row.predictions_count || 0) + ' ennustust' +
        (isLive && liveGain > 0 ? '<span class="live-points-chip"> +' + liveGain + ' LIVE</span>' : '') + '</div></td>';

      rounds.forEach(n => {
        const official = Number(roundMaps.get(n)?.get(row.player_id)?.points || 0);
        const provisional = Number(liveData.liveByRound.get(n)?.get(String(row.player_id)) || 0);
        const value = official + provisional;
        html += '<td class="num round-history-cell ' + (n === latestRound ? 'latest ' : '') + (provisional > 0 ? 'live-round-cell' : '') + '">' + value + '</td>';
      });
      if (showBonus) html += '<td class="num bonus-history-cell">' + Number(bonusMap.get(row.player_id) || 0) + '</td>';
      html += '<td class="num leader-total-cell">' + total + (isLive && liveGain > 0 ? '<span class="live-total-plus">+' + liveGain + '</span>' : '') + '</td>' +
        '<td class="num leader-gap-cell">' + (gap === 0 ? '–' : '−' + gap) + '</td>' +
        '<td class="num">' + (isLive ? liveMovementHtml(row) : (latestRound && typeof rankMoveHtml === 'function' ? rankMoveHtml(row.player_id, latestRound) : '<span class="rank-move same">–</span>')) + '</td></tr>';
    });

    container.innerHTML = html + '</tbody></table></div>' + (typeof recordsCardHtmlDeep === 'function' ? recordsCardHtmlDeep() : '');
  };

  if (typeof renderLiveMatchCenter === 'function' && !window.__futbolLiveStandingsWrapped) {
    const baseRenderLiveMatchCenter = renderLiveMatchCenter;
    renderLiveMatchCenter = function() {
      const result = baseRenderLiveMatchCenter.apply(this, arguments);
      try { renderLeaderboard(); } catch (error) { console.error('Live standings render error', error); }
      return result;
    };
    window.__futbolLiveStandingsWrapped = true;
  }

  try { renderLeaderboard(); } catch (_) {}
})();
