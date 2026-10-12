// WiPi touch launcher — browsing: tabs, paged grid, A–Z, filters, game sheet, favourites.
'use strict';

(function () {
  const $ = (id) => document.getElementById(id);
  const params = new URLSearchParams(location.search);

  const SYSTEMS = [
    { id: 'Sega Naomi', label: 'NAOMI', short: 'N1' },
    { id: 'Sega Naomi2', label: 'NAOMI 2', short: 'N2' },
    { id: 'Sammy Atomiswave', label: 'AWAVE', short: 'AW' },
    { id: 'Sega Chihiro', label: 'CHIHIRO', short: 'CHI' },
    { id: 'Sega Triforce', label: 'TRIFORCE', short: 'TRI' },
  ];
  const FILTER_GROUPS = [
    { key: 'genre', title: 'Genre' },
    { key: 'orientation', title: 'Orientation' },
    { key: 'controls', title: 'Contrôles' },
  ];
  // Minimum tile size per density: gives 3x3 / 2x3 / 2x2 / 1x2 on the 480x320 screen, more tiles on bigger ones.
  const DENSITIES = {
    '3x3': { w: 150, h: 62 },
    '2x3': { w: 210, h: 62 },
    '2x2': { w: 210, h: 100 },
    '1x2': { w: 300, h: 100 },
  };
  const VIDEO_DELAY_MS = 350;
  const SLEEP_CHOICES = [[0, 'Jamais'], [1, '1 min'], [2, '2 min'], [5, '5 min']];
  const BOUNCE_SPEED = 40; // px per second
  const BOUNCE_FPS = 20; // enough for a slow move, light on the Pi 3
  const KIOSK = params.get('kiosk') === '1';
  const GAP = 6;
  const TOP_H = 44;
  const BOTTOM_H = 54;
  const STORE_KEY = 'wipi-launcher';

  const state = {
    games: [],
    byRom: {},
    history: [],
    tab: 'all',
    filters: { genre: [], orientation: [], controls: [] }, // several values per group: OR inside, AND between groups
    page: 0,
    perPage: 6,
    cols: 2,
    rows: 3,
    sheetGame: null,
    narrow: false,
    density: '2x3',
    video: true,
    sound: false,
    simulate: false,
    playing: null, // rom running on the cabinet, null until a game is sent
    sleepMin: 2,
  };

  // ---------- helpers ----------
  function el(tag, cls, text) {
    const node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function imageUrl(game) {
    return '/images/' + encodeURIComponent(game.image);
  }

  function systemInfo(id) {
    return SYSTEMS.find((s) => s.id === id) || { id: id, label: id, short: '' };
  }

  function letterOf(game) {
    const c = (game.name || '#').charAt(0).toUpperCase();
    return c >= 'A' && c <= 'Z' ? c : '#';
  }

  function save() {
    try {
      localStorage.setItem(STORE_KEY, JSON.stringify({
        tab: state.tab, filters: state.filters, page: state.page, density: state.density, video: state.video, sleepMin: state.sleepMin,
      }));
    } catch (e) { /* storage unavailable: not critical */ }
  }

  function restore() {
    try {
      const saved = JSON.parse(localStorage.getItem(STORE_KEY) || 'null');
      if (saved) {
        state.tab = saved.tab || 'all';
        FILTER_GROUPS.forEach(({ key }) => {
          const value = (saved.filters || {})[key];
          state.filters[key] = Array.isArray(value) ? value : value ? [value] : [];
        });
        state.page = saved.page || 0;
        if (DENSITIES[saved.density]) state.density = saved.density;
        if (typeof saved.video === 'boolean') state.video = saved.video;
        if (SLEEP_CHOICES.some(([m]) => m === saved.sleepMin)) state.sleepMin = saved.sleepMin;
      }
    } catch (e) { /* ignore */ }
  }

  // ---------- layout (kiosk zoom compensation + responsive grid) ----------
  function layout() {
    const app = $('app');
    const frame = /^(\d+)x(\d+)$/.exec(params.get('frame') || '');
    // The kiosk runs Chromium with --force-device-scale-factor=0.651: undo it so we draw 1:1 at 480x320.
    const zoom = params.get('kiosk') === '1' && window.devicePixelRatio ? 1 / window.devicePixelRatio : 1;
    if (zoom !== 1) document.documentElement.style.zoom = zoom;

    let w = window.innerWidth / zoom;
    let h = window.innerHeight / zoom;
    if (frame) {
      w = +frame[1];
      h = +frame[2];
      document.body.classList.add('framed');
    }
    app.style.width = w + 'px';
    app.style.height = h + 'px';
    state.narrow = w < 400;
    app.classList.toggle('narrow', state.narrow);

    const firstIndex = state.page * state.perPage;
    const tile = DENSITIES[state.density];
    state.cols = Math.max(1, Math.floor((w - GAP) / (tile.w + GAP)));
    state.rows = Math.max(1, Math.floor((h - TOP_H - BOTTOM_H - GAP) / (tile.h + GAP)));
    state.perPage = state.cols * state.rows;
    state.page = Math.floor(firstIndex / state.perPage);

    const grid = $('grid');
    grid.style.gridTemplateColumns = 'repeat(' + state.cols + ', minmax(0, 1fr))';
    grid.style.gridTemplateRows = 'repeat(' + state.rows + ', minmax(0, 1fr))';
    grid.classList.toggle('large', state.density !== '2x3');
    grid.classList.toggle('small', state.density === '3x3');
  }

  // ---------- data ----------
  function visibleGames() {
    let list;
    if (state.tab === 'fav') list = state.games.filter((g) => g.fave);
    else if (state.tab === 'recent') list = state.history.map((rom) => state.byRom[rom]).filter(Boolean);
    else if (state.tab === 'all') list = state.games;
    else list = state.games.filter((g) => g.system === state.tab);

    FILTER_GROUPS.forEach(({ key }) => {
      const values = state.filters[key];
      if (values.length) list = list.filter((g) => values.indexOf(g[key]) !== -1);
    });
    return list;
  }

  function addRecent(rom) {
    state.history = [rom].concat(state.history.filter((r) => r !== rom)).slice(0, 12);
  }

  // ---------- tabs ----------
  function renderTabs() {
    const tabs = $('tabs');
    tabs.textContent = '';
    const present = new Set(state.games.map((g) => g.system));
    const entries = [{ id: 'fav', label: '★', icon: true }, { id: 'all', label: 'TOUS' }]
      .concat(SYSTEMS.filter((s) => present.has(s.id)))
      .concat([{ id: 'recent', label: '↺', icon: true }]);
    if (!entries.some((t) => t.id === state.tab)) state.tab = 'all';

    entries.forEach((t) => {
      const b = el('button', 'tab' + (t.icon ? ' icon' : '') + (t.id === state.tab ? ' active' : ''), t.label);
      b.addEventListener('click', () => {
        state.tab = t.id;
        state.page = 0;
        renderTabs();
        render();
      });
      tabs.appendChild(b);
    });
  }

  // ---------- grid ----------
  function tileFor(game) {
    const tile = el('button', 'tile');
    tile.dataset.rom = game.rom;
    if (state.tab === 'all' || state.tab === 'fav' || state.tab === 'recent') {
      tile.appendChild(el('span', 'sys', systemInfo(game.system).short));
    }
    if (game.fave) tile.appendChild(el('span', 'star', '★'));
    if (game.image) {
      const img = el('img');
      img.alt = '';
      img.decoding = 'async';
      img.draggable = false;
      img.src = imageUrl(game);
      img.addEventListener('error', () => img.replaceWith(el('span', 'noimg', game.name)));
      tile.appendChild(img);
    } else {
      tile.appendChild(el('span', 'noimg', game.name));
    }
    tile.appendChild(el('span', 'name', game.name));
    tile.addEventListener('click', () => {
      if (!swipe.consumed) openSheet(game);
    });
    return tile;
  }

  function render(direction) {
    const grid = $('grid');
    const list = visibleGames();
    const pages = Math.max(1, Math.ceil(list.length / state.perPage));
    state.page = Math.min(Math.max(0, state.page), pages - 1);

    if (direction) {
      grid.classList.add(direction > 0 ? 'turn-next' : 'turn-prev');
      void grid.offsetWidth; // restart the transition
    }

    grid.textContent = '';
    const start = state.page * state.perPage;
    const slice = list.slice(start, start + state.perPage);
    if (!slice.length) {
      const msg = state.tab === 'fav' ? 'Aucun favori.\nAjoute-en depuis la fiche d’un jeu (☆).'
        : state.tab === 'recent' ? 'Aucun jeu lancé récemment.'
        : 'Aucun jeu ne correspond.';
      grid.appendChild(el('div', 'empty', msg));
    }
    slice.forEach((g) => grid.appendChild(tileFor(g)));

    if (direction) grid.classList.remove('turn-next', 'turn-prev');

    $('page-info').textContent = (state.page + 1) + ' / ' + pages + (state.narrow ? '' : '  ·  ' + list.length + ' jeux');
    $('btn-prev').disabled = state.page === 0;
    $('btn-next').disabled = state.page >= pages - 1;

    const active = FILTER_GROUPS.reduce((n, { key }) => n + state.filters[key].length, 0);
    $('filter-count').hidden = !active;
    $('filter-count').textContent = active;

    save();
    preload(list.slice(start + state.perPage, start + 2 * state.perPage));
  }

  function preload(games) {
    const run = () => games.forEach((g) => { if (g.image) new Image().src = imageUrl(g); });
    if (window.requestIdleCallback) requestIdleCallback(run, { timeout: 1500 });
    else setTimeout(run, 300);
  }

  function turn(delta) {
    const pages = Math.max(1, Math.ceil(visibleGames().length / state.perPage));
    const next = Math.min(Math.max(0, state.page + delta), pages - 1);
    if (next === state.page) return;
    state.page = next;
    render(delta);
  }

  // Horizontal swipe on the grid (tiles included): the page follows the finger, then turns past
  // SWIPE_TURN_PX or springs back. A swipe never opens the tile it started on.
  const SWIPE_START_PX = 12;
  const SWIPE_TURN_PX = 50;
  const swipe = { x: 0, y: 0, dx: 0, active: false, dragging: false, consumed: false };
  function bindSwipe() {
    const grid = $('grid');
    // With a mouse-like touchscreen, dragging a logo would start a native image drag
    grid.addEventListener('dragstart', (e) => e.preventDefault());
    grid.addEventListener('pointerdown', (e) => {
      swipe.active = true;
      swipe.dragging = false;
      swipe.consumed = false;
      swipe.x = e.clientX;
      swipe.y = e.clientY;
      swipe.dx = 0;
    });
    window.addEventListener('pointermove', (e) => {
      if (!swipe.active) return;
      const dx = e.clientX - swipe.x;
      const dy = e.clientY - swipe.y;
      if (!swipe.dragging) {
        if (Math.abs(dx) < SWIPE_START_PX || Math.abs(dx) < Math.abs(dy)) return;
        swipe.dragging = true;
        grid.style.transition = 'none';
      }
      swipe.dx = dx;
      grid.style.transform = 'translateX(' + Math.round(dx * 0.6) + 'px)';
    });
    const end = () => {
      if (!swipe.active) return;
      swipe.active = false;
      if (!swipe.dragging) return;
      swipe.consumed = true;
      setTimeout(() => { swipe.consumed = false; }, 60);
      grid.style.transition = '';
      grid.style.transform = '';
      if (Math.abs(swipe.dx) >= SWIPE_TURN_PX) turn(swipe.dx < 0 ? 1 : -1);
    };
    window.addEventListener('pointerup', end);
    window.addEventListener('pointercancel', end);
  }

  // Resistive touch arrives as a mouse in the kiosk: dragging must scroll by hand.
  function dragScroll(box) {
    let startY = 0;
    let startTop = 0;
    let pressed = false;
    let dragged = false;
    box.addEventListener('pointerdown', (e) => {
      if (e.pointerType !== 'mouse') return;
      pressed = true;
      dragged = false;
      startY = e.clientY;
      startTop = box.scrollTop;
    });
    box.addEventListener('pointermove', (e) => {
      if (!pressed) return;
      const dy = e.clientY - startY;
      if (Math.abs(dy) > 8) dragged = true;
      if (dragged) box.scrollTop = startTop - dy;
    });
    window.addEventListener('pointerup', () => { pressed = false; });
    // A drag must not also tap the chip it started on
    box.addEventListener('click', (e) => {
      if (dragged) {
        e.preventDefault();
        e.stopPropagation();
        dragged = false;
      }
    }, true);
  }

  // ---------- overlays ----------
  function openOverlay(id) { $(id).hidden = false; }
  function closeOverlay(id) { $(id).hidden = true; }

  function renderAZ() {
    const keys = $('az-keys');
    keys.textContent = '';
    const list = visibleGames();
    const firstIndex = {};
    list.forEach((g, i) => {
      const l = letterOf(g);
      if (!(l in firstIndex)) firstIndex[l] = i;
    });
    ['#'].concat('ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('')).forEach((letter) => {
      const b = el('button', null, letter);
      b.disabled = !(letter in firstIndex);
      b.addEventListener('click', () => {
        const index = firstIndex[letter];
        state.page = Math.floor(index / state.perPage);
        closeOverlay('az');
        render();
        const tile = $('grid').children[index % state.perPage];
        if (tile) {
          tile.classList.add('flash');
          setTimeout(() => tile.classList.remove('flash'), 900);
        }
      });
      keys.appendChild(b);
    });
  }

  function chipGroup(box, title, options, isOn, onPick) {
    const group = el('div', 'filter-group');
    group.appendChild(el('h3', null, title));
    const chips = el('div', 'chips');
    options.forEach(([value, label]) => {
      const chip = el('button', 'pill' + (isOn(value) ? ' on' : ''), label);
      chip.addEventListener('click', () => onPick(value));
      chips.appendChild(chip);
    });
    group.appendChild(chips);
    box.appendChild(group);
  }

  function renderFilters() {
    const box = $('filter-groups');
    const scrollTop = box.scrollTop;
    box.textContent = '';
    FILTER_GROUPS.forEach(({ key, title }) => {
      const values = Array.from(new Set(state.games.map((g) => g[key]).filter(Boolean))).sort();
      const group = el('div', 'filter-group');
      group.appendChild(el('h3', null, title));
      const chips = el('div', 'chips');
      values.forEach((value) => {
        const selected = state.filters[key];
        const chip = el('button', 'pill' + (selected.indexOf(value) !== -1 ? ' on' : ''), value);
        chip.addEventListener('click', () => {
          state.filters[key] = selected.indexOf(value) !== -1
            ? selected.filter((v) => v !== value)
            : selected.concat([value]);
          state.page = 0;
          renderFilters();
          render();
        });
        chips.appendChild(chip);
      });
      group.appendChild(chips);
      box.appendChild(group);
    });
    box.scrollTop = scrollTop;
  }

  // ---------- settings ----------
  let dimmsInfo = null; // null = checking, [] = none configured

  function settingsRow(box, label, sub, status) {
    const row = el('div', 'settings-row');
    const text = el('span', 'label', label);
    if (sub) {
      text.appendChild(document.createTextNode(' '));
      text.appendChild(el('span', 'sub', sub));
    }
    row.appendChild(text);
    if (status) row.appendChild(el('span', status[0], status[1]));
    box.appendChild(row);
  }

  function renderSettings() {
    const box = $('settings-body');
    const scrollTop = box.scrollTop;
    box.textContent = '';

    chipGroup(box, 'Affichage', Object.keys(DENSITIES).map((d) => [d, d.replace('x', '\u00D7')]),
      (d) => d === state.density,
      (d) => {
        state.density = d;
        layout();
        renderSettings();
        render();
      });
    chipGroup(box, 'Vidéo dans la fiche', [[true, 'Oui'], [false, 'Non']],
      (v) => v === state.video,
      (v) => {
        state.video = v;
        renderSettings();
        save();
      });
    if (KIOSK) {
      chipGroup(box, 'Veille de l\u2019écran', SLEEP_CHOICES,
        (m) => m === state.sleepMin,
        (m) => {
          state.sleepMin = m;
          renderSettings();
          save();
          armSleep();
        });
    }

    const net = el('div', 'filter-group');
    net.appendChild(el('h3', null, 'Netdimms'));
    box.appendChild(net);
    if (dimmsInfo === null) {
      box.appendChild(el('p', 'settings-note', 'Vérification…'));
    } else if (!dimmsInfo.length) {
      box.appendChild(el('p', 'settings-note', 'Aucun netdimm configuré (Interface WiPi \u203A Setup \u203A Manage Netdimms).'));
    } else {
      dimmsInfo.forEach((d) => settingsRow(box, d.name, d.ip + ' \u00B7 ' + systemInfo(d.type).label,
        d.online ? ['on', '\u25CF en ligne'] : ['off', '\u25CB hors ligne']));
    }
    const refresh = el('button', 'pill', 'Actualiser');
    refresh.addEventListener('click', checkDimms);
    box.appendChild(refresh);

    const info = el('div', 'filter-group');
    info.appendChild(el('h3', null, 'Launcher'));
    box.appendChild(info);
    settingsRow(box, state.games.length + ' jeux disponibles', null,
      state.simulate ? ['off', 'mode SIMULATION'] : ['on', 'lancements réels']);

    const legacy = el('button', 'pill primary wide-btn', 'Interface WiPi complète  \u203A');
    legacy.addEventListener('click', openLegacy);
    box.appendChild(legacy);
    box.appendChild(el('p', 'settings-note', 'Options, netdimms, OpenJVS, cartes, réseau\u2026 Le bouton \u2302 ramène au launcher.'));

    box.scrollTop = scrollTop;
  }

  function openLegacy() {
    location.href = '/gamelist.php?display=all';
  }

  function checkDimms() {
    dimmsInfo = null;
    renderSettings();
    fetch('api/dimms.php', { cache: 'no-store' })
      .then((r) => r.json())
      .then((data) => { dimmsInfo = data.dimms; })
      .catch(() => { dimmsInfo = []; })
      .then(() => { if (!$('settings').hidden) renderSettings(); });
  }

  // ---------- game sheet ----------
  let videoTimer = null;

  function stopVideo() {
    clearTimeout(videoTimer);
    const v = $('sheet-video');
    if (v.getAttribute('src')) {
      v.pause();
      v.removeAttribute('src');
      v.load(); // releases the decoder
    }
  }

  function showVideo(game) {
    const withVideo = state.video && !!game.video;
    $('sheet-body').classList.toggle('has-video', withVideo);
    $('sheet-media').hidden = !withVideo;
    if (!withVideo) return;
    const v = $('sheet-video');
    v.muted = !state.sound;
    // Start decoding only once the sheet is shown: a quick tap on LANCER costs nothing.
    videoTimer = setTimeout(() => {
      v.src = '/videos/' + encodeURIComponent(game.video);
      v.play().catch(() => {});
    }, VIDEO_DELAY_MS);
  }

  function closeSheet() {
    stopVideo();
    closeOverlay('sheet');
  }

  function openSheet(game) {
    stopVideo();
    state.sheetGame = game;
    showVideo(game);
    const img = $('sheet-img');
    img.hidden = !game.image;
    img.src = game.image ? imageUrl(game) : '';
    $('sheet-name').textContent = game.name;
    $('sheet-meta').textContent = [systemInfo(game.system).label, game.manufacturer, game.year, game.genre, game.orientation]
      .filter(Boolean).join('  ·  ');
    renderFave();
    openOverlay('sheet');
  }

  function renderFave() {
    const b = $('sheet-fave');
    const on = !!(state.sheetGame && state.sheetGame.fave);
    b.textContent = on ? '★' : '☆';
    b.classList.toggle('on', on);
  }

  // Reuses the existing updatecsvfave.php (it redirects to gamelist.php: don't follow).
  function toggleFave() {
    const game = state.sheetGame;
    if (!game) return;
    const wanted = !game.fave;
    game.fave = wanted;
    renderFave();
    fetch('/updatecsvfave.php?rom=' + encodeURIComponent(game.rom) + '&fave=' + (wanted ? 'Yes' : 'No'),
      { redirect: 'manual', cache: 'no-store' })
      .then((r) => {
        if (r.type !== 'opaqueredirect' && !r.ok) throw new Error(r.status);
      })
      .catch(() => {
        game.fave = !wanted;
        renderFave();
      })
      .then(() => render());
  }

  // ---------- boot ----------
  function bind() {
    $('btn-prev').addEventListener('click', () => turn(-1));
    $('btn-next').addEventListener('click', () => turn(1));
    $('btn-az').addEventListener('click', () => { renderAZ(); openOverlay('az'); });
    $('btn-filters').addEventListener('click', () => { renderFilters(); openOverlay('filters'); });
    $('btn-filters-reset').addEventListener('click', () => {
      FILTER_GROUPS.forEach(({ key }) => { state.filters[key] = []; });
      state.page = 0;
      renderFilters();
      render();
    });
    $('btn-settings').addEventListener('click', () => { openOverlay('settings'); checkDimms(); });
    $('sheet-fave').addEventListener('click', toggleFave);
    $('btn-launch').addEventListener('click', () => {
      if (state.sheetGame && window.WLaunch) window.WLaunch.start(state.sheetGame);
    });
    document.querySelectorAll('[data-close]').forEach((b) => {
      b.addEventListener('click', () => {
        const overlay = b.closest('.overlay');
        if (overlay.id === 'sheet') closeSheet();
        else overlay.hidden = true;
      });
    });
    $('sheet-video').addEventListener('error', () => {
      if (!$('sheet-video').getAttribute('src')) return;
      $('sheet-media').hidden = true;
      $('sheet-body').classList.remove('has-video');
    });
    document.addEventListener('contextmenu', (e) => e.preventDefault());
    window.addEventListener('resize', () => { layout(); render(); });
    bindSwipe();
    dragScroll($('filter-groups'));
    dragScroll($('settings-body'));
  }

  function load() {
    return fetch('api/games.php', { cache: 'no-store' })
      .then((r) => r.json())
      .then((data) => {
        state.games = data.games.sort((a, b) => a.name.localeCompare(b.name, 'en', { numeric: true, sensitivity: 'base' }));
        state.byRom = {};
        state.games.forEach((g) => { state.byRom[g.rom] = g; });
        state.history = data.history || [];
        state.sound = !!data.sound;
        state.playing = data.playing || null;
        armSleep();
        state.simulate = !!data.simulate;
        $('sim-flag').hidden = !data.simulate;
        renderTabs();
        render();
      })
      .catch(() => {
        $('grid').textContent = '';
        $('grid').appendChild(el('div', 'empty', 'Impossible de charger la liste des jeux.'));
      });
  }

  // ---------- screen sleep (kiosk only) ----------
  // Black screen after inactivity or after a game is launched; the first tap only wakes up.
  let sleepTimer = null;
  let bounceTimer = null;

  function armSleep() {
    clearTimeout(sleepTimer);
    // No sleep before a game runs on the cabinet (nothing to show, and the screen is in use)
    if (!KIOSK || !state.sleepMin || !state.playing || !$('sleep').hidden) return;
    sleepTimer = setTimeout(sleep, state.sleepMin * 60000);
  }

  // DVD-style bounce of the running game's logo
  function startBounce() {
    const box = $('sleep');
    const item = $('sleep-item');
    let w = 0;
    let h = 0;
    const measure = () => { w = item.offsetWidth; h = item.offsetHeight; };
    measure();
    let x = Math.random() * Math.max(0, box.clientWidth - w);
    let y = Math.random() * Math.max(0, box.clientHeight - h);
    let vx = (Math.random() < 0.5 ? -1 : 1) * BOUNCE_SPEED / BOUNCE_FPS;
    let vy = (Math.random() < 0.5 ? -1 : 1) * BOUNCE_SPEED * 0.75 / BOUNCE_FPS;
    $('sleep-img').onload = measure;
    bounceTimer = setInterval(() => {
      if (!w || !h) measure(); // logo still loading
      const maxX = Math.max(0, box.clientWidth - w);
      const maxY = Math.max(0, box.clientHeight - h);
      x += vx;
      y += vy;
      if (x <= 0 || x >= maxX) { vx = -vx; x = Math.min(Math.max(x, 0), maxX); }
      if (y <= 0 || y >= maxY) { vy = -vy; y = Math.min(Math.max(y, 0), maxY); }
      item.style.transform = 'translate(' + Math.round(x) + 'px,' + Math.round(y) + 'px)';
    }, 1000 / BOUNCE_FPS);
  }

  function sleep() {
    if (!$('launch').hidden) { // never during a transfer
      armSleep();
      return;
    }
    stopVideo();
    const last = state.byRom[state.playing];
    const img = $('sleep-img');
    img.hidden = !(last && last.image);
    if (last && last.image) img.src = imageUrl(last);
    $('sleep-text').textContent = last && last.image ? '' : (last ? last.name : 'WiPi');
    $('sleep').hidden = false;
    startBounce();
  }

  function wake() {
    clearInterval(bounceTimer);
    $('sleep').hidden = true;
    armSleep();
  }

  function bindSleep() {
    if (!KIOSK) return;
    // Wake on click (not pointerdown) so the tap's click lands on the black screen, not on a tile
    $('sleep').addEventListener('click', wake);
    document.addEventListener('pointerdown', () => { if ($('sleep').hidden) armSleep(); }, true);
    armSleep();
  }

  // Shared with launch.js
  window.WL = {
    $: $,
    el: el,
    params: params,
    imageUrl: imageUrl,
    systemInfo: systemInfo,
    addRecent: addRecent,
    closeSheet: closeSheet,
    stopVideo: stopVideo,
    setPlaying: (rom) => { state.playing = rom; armSleep(); },
    render: () => render(),
  };

  restore();
  layout();
  bind();
  bindSleep();
  load().then(() => { if (window.WLaunch) window.WLaunch.resume(); });
})();
