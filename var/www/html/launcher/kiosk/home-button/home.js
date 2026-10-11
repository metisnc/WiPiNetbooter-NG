// Floating "back to launcher" button on the existing WiPi pages, loaded only by the kiosk Chromium.
(function () {
  if (document.getElementById('wipi-launcher-home')) return;
  const a = document.createElement('a');
  a.id = 'wipi-launcher-home';
  a.href = '/launcher/?kiosk=1';
  a.textContent = '⌂';
  a.setAttribute('aria-label', 'Launcher');
  // Sizes in CSS px: the kiosk runs at device scale 0.651, 84px is about 55 physical px.
  a.style.cssText = [
    'position:fixed', 'left:12px', 'bottom:12px', 'z-index:2147483647',
    'width:84px', 'height:84px', 'border-radius:42px',
    'display:flex', 'align-items:center', 'justify-content:center',
    'font:bold 52px/1 sans-serif', 'text-decoration:none',
    'color:#07080d', 'background:#19e6ff', 'box-shadow:0 0 16px rgba(25,230,255,.6)',
    'opacity:.92',
  ].join(';');
  document.body.appendChild(a);
})();
