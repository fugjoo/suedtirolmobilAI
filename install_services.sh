#!/usr/bin/env bash
set -e

# Copy service templates to /etc/systemd/system and reload systemd.
# Paths inside the unit files may need adjustment.

if ! command -v systemctl >/dev/null || ! pidof systemd >/dev/null; then
    echo "Error: systemd is not running. This script requires a system with systemd." >&2
    exit 1
fi

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

sudo cp "$SRC_DIR/systemd/suedtirolmobil.service" /etc/systemd/system/
sudo cp "$SRC_DIR/systemd/suedtirolmobil-bot.service" /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable --now suedtirolmobil.service
sudo systemctl enable --now suedtirolmobil-bot.service

echo "Templates installed. The services are now running." 
echo "Control them with 'systemctl start|stop|restart suedtirolmobil.service'" 
echo "and 'systemctl start|stop|restart suedtirolmobil-bot.service'."

