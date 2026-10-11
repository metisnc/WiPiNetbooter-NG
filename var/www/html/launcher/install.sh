#!/bin/bash
# Make the 3.5" kiosk open the touch launcher. Idempotent: run it again after a WiPi update.
# Usage (on the Pi, as root): bash /var/www/html/launcher/install.sh [--restart]
#   --restart  restart the kiosk session (autologin on tty1) to apply now
set -euo pipefail

LAUNCHER=/var/www/html/launcher
AUTOSTART=${AUTOSTART:-/etc/xdg/openbox/autostart}
BACKUP=$AUTOSTART.wipi-orig
URL='http://127.0.0.1/launcher/?kiosk=1'
EXTENSION=$LAUNCHER/kiosk/home-button
# md5 of the load.php (WiPi 6.1-92) whose wipiloader.py command api/launch_lib.php reproduces
LOAD_MD5=b3ad0b2dcacf847a58e1a544890d19bb

[ "$(id -u)" = 0 ] || { echo "Run as root."; exit 1; }
grep -q 'chromium-browser' "$AUTOSTART" || { echo "No chromium-browser line in $AUTOSTART: nothing changed."; exit 1; }

[ -f "$BACKUP" ] || cp -a "$AUTOSTART" "$BACKUP"

# Open the launcher instead of whatever local page the kiosk opened
sed -i -E "/chromium-browser/ s#'http://127\.0\.0\.1/[^']*'#'$URL'#" "$AUTOSTART"
grep -q -F "'$URL'" "$AUTOSTART" || { echo "Could not set the kiosk URL, check $AUTOSTART."; exit 1; }

# Home button on the existing pages
if ! grep -q -- '--load-extension=' "$AUTOSTART"; then
    sed -i -E "/^[[:space:]]*chromium-browser / s#chromium-browser #chromium-browser --load-extension=$EXTENSION #" "$AUTOSTART"
fi

mkdir -p "$LAUNCHER/data"
chown www-data:www-data "$LAUNCHER/data"

echo "Kiosk now opens $URL"
grep 'chromium-browser' "$AUTOSTART"

if [ "$(md5sum /var/www/html/load.php | cut -d' ' -f1)" != "$LOAD_MD5" ]; then
    echo "WARNING: /var/www/html/load.php changed since WiPi 6.1-92."
    echo "         Check that api/launch_lib.php still runs the same command before real launches."
fi

if [ "${1:-}" = "--restart" ]; then
    echo "Restarting the kiosk session..."
    systemctl restart getty@tty1
else
    echo "Apply with a reboot, or: bash $0 --restart"
fi
