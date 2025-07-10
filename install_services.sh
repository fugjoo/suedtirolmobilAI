#!/usr/bin/env bash
set -e

# Copy service templates to /etc/systemd/system and reload systemd.
# Paths inside the unit files may need adjustment.

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

sudo cp "$SRC_DIR/systemd/suedtirolmobil.service" /etc/systemd/system/
sudo cp "$SRC_DIR/systemd/suedtirolmobil-bot.service" /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable suedtirolmobil.service
sudo systemctl enable suedtirolmobil-bot.service

echo "Templates installed. Start the services with:"
echo "  sudo systemctl start suedtirolmobil.service"
echo "  sudo systemctl start suedtirolmobil-bot.service"

