// WiPi touch launcher — full screen launch flow: netdimm check, progress, success / error, cancel / retry.
'use strict';

(function () {
  const WL = window.WL;
  const $ = WL.$;
  const POLL_MS = 700;
  const DONE_CLOSE_MS = 4000;

  let game = null;
  let pollTimer = null;
  let closeTimer = null;

  function post(url, body) {
    return fetch(url, {
      method: 'POST',
      cache: 'no-store',
      headers: { 'Content-Type': 'application/json', 'X-Launcher': '1' },
      body: JSON.stringify(body || {}),
    }).then((r) => r.json());
  }

  function stopTimers() {
    clearTimeout(pollTimer);
    clearTimeout(closeTimer);
    pollTimer = closeTimer = null;
  }

  // ---------- rendering ----------
  function show(info) {
    $('launch-name').textContent = info.name || '';
    const img = $('launch-img');
    img.hidden = !info.image;
    if (info.image) img.src = WL.imageUrl(info);
    $('launch').hidden = false;
  }

  function message(text, kind) {
    const m = $('launch-msg');
    m.textContent = text;
    m.className = 'launch-msg' + (kind ? ' ' + kind : '');
  }

  function progress(value) {
    const bar = $('launch-bar');
    bar.hidden = value === null;
    bar.classList.toggle('indeterminate', value === 'busy');
    $('launch-fill').style.width = typeof value === 'number' ? value + '%' : '';
    $('launch-pct').textContent = typeof value === 'number' ? value + ' %' : '';
  }

  function logLines(lines) {
    const log = $('launch-log');
    log.hidden = !(lines && lines.length);
    log.textContent = lines ? lines.join('\n') : '';
  }

  function buttons(container, list) {
    const box = $(container);
    box.textContent = '';
    list.forEach(([label, action, primary]) => {
      const b = WL.el('button', 'pill' + (primary ? ' primary' : ''), label);
      b.addEventListener('click', action);
      box.appendChild(b);
    });
  }

  function actions(list) { buttons('launch-actions', list); }

  function close() {
    stopTimers();
    $('launch').hidden = true;
  }

  function backToList() {
    close();
    WL.closeSheet();
    WL.render();
  }

  // ---------- flow ----------
  function start(g, dimm) {
    game = g;
    stopTimers();
    WL.stopVideo();
    show(g);
    message('Recherche du netdimm…');
    progress('busy');
    logLines(null);
    buttons('launch-choices', []);
    actions([]);

    post('api/launch.php', { rom: g.rom, dimm: dimm || '', sim: WL.params.get('sim') || '' })
      .then(handleStart)
      .catch(() => fail('Le Pi ne répond pas.'));
  }

  function handleStart(res) {
    switch (res.state) {
      case 'started':
        WL.addRecent(res.rom);
        message('Connexion à ' + res.dimm + '…');
        poll();
        break;
      case 'choose':
        message('Plusieurs bornes disponibles :');
        progress(null);
        buttons('launch-choices', res.dimms.map((d) => [d.name, () => start(game, d.ip), true]));
        actions([['Annuler', close]]);
        break;
      case 'nodimm':
        progress(null);
        if (res.offline && res.offline.length) {
          message(res.offline.map((d) => d.name + ' (' + d.ip + ')').join(', ') + ' ne répond pas.', 'err');
          logLines([
            'Un jeu en cours (Atomiswave notamment) peut couper le réseau du netdimm.',
            'Redémarre la borne puis touche Réessayer.',
          ]);
        } else {
          message('Aucun netdimm configuré pour ' + WL.systemInfo(res.system).label + '.', 'err');
          logLines(['À ajouter dans Réglages \u203A Interface WiPi \u203A Setup \u203A Manage Netdimms.']);
        }
        actions([['Réessayer', () => start(game), true], ['Fermer', close]]);
        break;
      case 'busy':
        show(res);
        message('Un chargement est déjà en cours.', 'err');
        progress(null);
        actions([['Suivre', () => { show(res); poll(); }, true], ['Arrêter', cancel]]);
        break;
      default:
        fail(res.message || 'Erreur inconnue.');
    }
  }

  function fail(text, log) {
    stopTimers();
    message(text, 'err');
    progress(null);
    logLines(log);
    buttons('launch-choices', []);
    actions(game ? [['Réessayer', () => start(game), true], ['Fermer', close]] : [['Fermer', close]]);
  }

  function poll() {
    fetch('api/status.php', { cache: 'no-store' })
      .then((r) => r.json())
      .then(update)
      .catch(() => { pollTimer = setTimeout(poll, POLL_MS * 2); });
  }

  function update(s) {
    buttons('launch-choices', []);
    switch (s.state) {
      case 'connecting':
        message('Connexion à ' + s.dimm + '…');
        progress('busy');
        actions([['Annuler', cancel]]);
        pollTimer = setTimeout(poll, POLL_MS);
        break;
      case 'running':
        message('Transfert vers ' + s.dimm + '…');
        progress(s.progress);
        actions([['Annuler', cancel]]);
        pollTimer = setTimeout(poll, POLL_MS);
        break;
      case 'done':
        message('Jeu lancé — bon jeu !', 'ok');
        progress(100);
        logLines(s.system === 'Sammy Atomiswave' ? ['Les jeux Atomiswave peuvent mettre jusqu’à 30 s à démarrer.'] : null);
        actions([['OK', backToList, true]]);
        closeTimer = setTimeout(backToList, DONE_CLOSE_MS);
        WL.setPlaying(s.rom); // the sleep delay counts from the end of the launch
        break;
      case 'error':
        fail('Échec du chargement.', s.log);
        break;
      default:
        close();
    }
  }

  function cancel() {
    stopTimers();
    message('Arrêt du transfert…');
    post('api/cancel.php').then(close).catch(close);
  }

  // After a reload (or coming back from Réglages), follow a transfer that is still running.
  function resume() {
    fetch('api/status.php', { cache: 'no-store' })
      .then((r) => r.json())
      .then((s) => {
        if (s.state !== 'connecting' && s.state !== 'running') return;
        game = null;
        show(s);
        update(s);
      })
      .catch(() => {});
  }

  window.WLaunch = { start: start, resume: resume };
})();
