#!/usr/bin/env bash
# Deploy the touch launcher (and only the launcher) to the WiPi.
# Usage: tools/deploy.sh            (WIPI_HOST=root@<ip> to override the target)
# The Pi has no rsync: files are streamed with tar over ssh. Files removed locally
# are not removed on the Pi.
set -euo pipefail

PI="${WIPI_HOST:-root@10.185.30.154}"
SRC="$(cd "$(dirname "$0")/.." && pwd)/var/www/html/launcher"
DEST=/var/www/html/launcher

COPYFILE_DISABLE=1 tar -C "$SRC" --no-xattrs --no-mac-metadata --no-fflags \
    --exclude='data/*.json' --exclude='.DS_Store' --exclude='* [0-9]*' \
    -cf - . |
ssh -o BatchMode=yes "$PI" "set -e
    mkdir -p $DEST
    tar -C $DEST -xf - --no-same-owner
    mkdir -p $DEST/data
    chown www-data:www-data $DEST/data
    find $DEST -name '*.php' -exec php -l {} \; | grep -v '^No syntax errors' || true
    echo \"Launcher deployed to $DEST\""
