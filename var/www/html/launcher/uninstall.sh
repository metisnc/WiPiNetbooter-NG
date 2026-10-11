#!/bin/bash
# Put the kiosk back on the original WiPi interface. The launcher stays reachable at /launcher/.
# Usage (on the Pi, as root): bash /var/www/html/launcher/uninstall.sh [--restart]
set -euo pipefail

AUTOSTART=${AUTOSTART:-/etc/xdg/openbox/autostart}

[ "$(id -u)" = 0 ] || { echo "Run as root."; exit 1; }

# Undo only what install.sh changed (keeps any other change made by an update)
sed -i -E "/chromium-browser/ { s#'http://127\.0\.0\.1/launcher/[^']*'#'http://127.0.0.1/index.html'#; s# --load-extension=/var/www/html/launcher/kiosk/home-button##; }" "$AUTOSTART"

echo "Kiosk restored:"
grep 'chromium-browser' "$AUTOSTART"
echo "(original copy kept in $AUTOSTART.wipi-orig)"

if [ "${1:-}" = "--restart" ]; then
    systemctl restart getty@tty1
else
    echo "Apply with a reboot, or: bash $0 --restart"
fi
