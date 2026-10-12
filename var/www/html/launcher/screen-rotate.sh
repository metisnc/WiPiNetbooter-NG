#!/bin/bash
# Rotate the MHS 3.5" screen (tft35a overlay) and its touch calibration. Idempotent.
# Usage (on the Pi, as root): bash /var/www/html/launcher/screen-rotate.sh 0|90|180|270 [--reboot]
#   0 = WiPi default (portrait). Takes effect after a reboot.
# Both /boot/config.txt and /boot/config.txt.lcd35 are patched: WiPi's "LCD Mode" option
# copies config.txt.lcd35 over config.txt. Originals are kept as *.wipi-orig.
set -euo pipefail

ROTATE="${1:-}"
CALIBRATION=/etc/X11/xorg.conf.d/99-calibration.conf

# ADS7846 calibration for each rotation (values from the LCD-show driver set used by WiPi)
case "$ROTATE" in
    0)   CAL="227 3936 268 3886"; SWAP=0 ;;
    90)  CAL="3936 227 268 3886"; SWAP=1 ;;
    180) CAL="3936 227 3886 268"; SWAP=0 ;;
    270) CAL="227 3936 3886 268"; SWAP=1 ;;
    *) echo "Usage: $0 0|90|180|270 [--reboot]"; exit 1 ;;
esac

[ "$(id -u)" = 0 ] || { echo "Run as root."; exit 1; }

for f in /boot/config.txt /boot/config.txt.lcd35 "$CALIBRATION"; do
    [ -f "$f" ] || continue
    [ -f "$f.wipi-orig" ] || cp -a "$f" "$f.wipi-orig"
done

for f in /boot/config.txt /boot/config.txt.lcd35; do
    [ -f "$f" ] || continue
    sed -i -E "s/^(dtoverlay=tft35a:rotate=)[0-9]+/\1$ROTATE/" "$f"
    echo "$f: $(grep '^dtoverlay=tft35a' "$f" || echo 'no active tft35a line')"
done

sed -i -E \
    -e "s/(Option[[:space:]]+\"Calibration\"[[:space:]]+)\"[^\"]*\"/\1\"$CAL\"/" \
    -e "s/(Option[[:space:]]+\"SwapAxes\"[[:space:]]+)\"[^\"]*\"/\1\"$SWAP\"/" \
    "$CALIBRATION"
echo "$CALIBRATION:"
grep -E '"(Calibration|SwapAxes)"' "$CALIBRATION"

if [ "${2:-}" = "--reboot" ]; then
    echo "Rebooting..."
    sync
    reboot
else
    echo "Reboot to apply."
fi
