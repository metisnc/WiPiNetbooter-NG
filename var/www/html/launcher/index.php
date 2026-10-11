<?php
// Touch launcher entry point. Everything else is loaded by assets/launcher.js.
function asset($path)
{
    return 'assets/' . $path . '?v=' . @filemtime(__DIR__ . '/assets/' . $path);
}
?><!DOCTYPE html>
<html lang="fr" translate="no">
<head>
<meta charset="utf-8">
<meta name="google" content="notranslate">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<meta name="theme-color" content="#07080d">
<title>WiPi Launcher</title>
<link rel="stylesheet" href="<?= asset('launcher.css') ?>">
</head>
<body>
<div id="app">
  <header class="bar top">
    <nav id="tabs" class="tabs"></nav>
    <button id="btn-settings" class="icon-btn" aria-label="Réglages">&#9881;</button>
  </header>

  <main id="grid" class="grid"></main>

  <footer class="bar bottom">
    <button id="btn-az" class="pill">A–Z</button>
    <button id="btn-prev" class="nav-btn" aria-label="Page précédente">&#9664;</button>
    <span id="page-info" class="page-info"></span>
    <button id="btn-next" class="nav-btn" aria-label="Page suivante">&#9654;</button>
    <button id="btn-filters" class="pill">Filtres<span id="filter-count" class="badge" hidden></span></button>
  </footer>

  <div id="sim-flag" class="sim-flag" hidden>SIMULATION</div>

  <!-- Overlays -->
  <section id="az" class="overlay" hidden>
    <div class="overlay-head"><span>Aller à…</span><button class="icon-btn close" data-close>&#10005;</button></div>
    <div id="az-keys" class="az-keys"></div>
  </section>

  <section id="filters" class="overlay" hidden>
    <div class="overlay-head">
      <button id="btn-filters-reset" class="pill">Tout effacer</button>
      <span>Filtres</span>
      <button class="icon-btn close" data-close>&#10005;</button>
    </div>
    <div id="filter-groups" class="overlay-body"></div>
  </section>

  <section id="settings" class="overlay" hidden>
    <div class="overlay-head"><button id="btn-legacy" class="pill">Interface WiPi &#8250;</button><span>Réglages</span><button class="icon-btn close" data-close>&#10005;</button></div>
    <div id="settings-body" class="overlay-body"></div>
  </section>

  <section id="sheet" class="overlay sheet" hidden>
    <div class="overlay-head">
      <button class="pill" data-close>&#8249; Retour</button>
      <span></span>
      <button id="sheet-fave" class="icon-btn fave" aria-label="Favori">&#9734;</button>
    </div>
    <div id="sheet-body" class="sheet-body">
      <div id="sheet-media" class="sheet-media" hidden><video id="sheet-video" muted loop playsinline preload="none"></video></div>
      <div class="sheet-info">
        <div class="sheet-logo"><img id="sheet-img" alt=""></div>
        <h1 id="sheet-name"></h1>
        <p id="sheet-meta" class="meta"></p>
        <button id="btn-launch" class="launch-btn">&#9654;&nbsp; LANCER</button>
      </div>
    </div>
  </section>

  <section id="launch" class="overlay launch" hidden>
    <div class="launch-body">
      <div class="sheet-logo"><img id="launch-img" alt=""></div>
      <h2 id="launch-name"></h2>
      <p id="launch-msg" class="launch-msg"></p>
      <div id="launch-bar" class="progress"><div id="launch-fill"></div><span id="launch-pct"></span></div>
      <pre id="launch-log" class="launch-log" hidden></pre>
      <div id="launch-choices" class="launch-choices"></div>
      <div id="launch-actions" class="launch-actions"></div>
    </div>
  </section>
</div>
<script src="<?= asset('launcher.js') ?>"></script>
<script src="<?= asset('launch.js') ?>"></script>
</body>
</html>
