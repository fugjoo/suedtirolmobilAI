# Autostart on Linux

This guide explains how to run the API or Telegram bot automatically with `systemd`.
After setting up a service you can control it with `start`, `stop` and `restart` commands.

## Preparation

1. Clone the repository and install the dependencies:
   ```bash
   git clone https://example.com/suedtirolmobilAI.git
   cd suedtirolmobilAI
   ./install.sh
   ```
2. Optionally store environment variables in a `.env` file inside the project directory. The application loads this file automatically.

The example unit files `systemd/suedtirolmobil.service` and
`systemd/suedtirolmobil-bot.service` can be used as templates and copied to
`/etc/systemd/system/`.

## systemd service for the API

Create `/etc/systemd/system/suedtirolmobil.service` with the following content
(adjust paths if necessary):

```ini
[Unit]
Description=suedtirolmobilAI API
After=network.target

[Service]
Type=simple
WorkingDirectory=/path/to/repo/suedtirolmobilAI
ExecStart=/path/to/repo/suedtirolmobilAI/venv/bin/uvicorn src.main:app --host 0.0.0.0
EnvironmentFile=/path/to/repo/suedtirolmobilAI/.env
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Reload systemd and enable the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable suedtirolmobil.service
sudo systemctl start suedtirolmobil.service
```

## systemd service for the Telegram bot

If you also want to start the Telegram bot automatically, create a second
service file. Example `/etc/systemd/system/suedtirolmobil-bot.service`:

```ini
[Unit]
Description=suedtirolmobilAI Telegram Bot
After=network.target suedtirolmobil.service

[Service]
Type=simple
WorkingDirectory=/path/to/repo/suedtirolmobilAI
ExecStart=/path/to/repo/suedtirolmobilAI/venv/bin/python -m src.telegram_bot --api-url http://localhost:8000
EnvironmentFile=/path/to/repo/suedtirolmobilAI/.env
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Reload systemd and enable the bot:

```bash
sudo systemctl daemon-reload
sudo systemctl enable suedtirolmobil-bot.service
sudo systemctl start suedtirolmobil-bot.service
```

## Controlling the service

Use the following commands to control the services:

```bash
sudo systemctl start suedtirolmobil.service       # start the API
sudo systemctl stop suedtirolmobil.service        # stop the API
sudo systemctl restart suedtirolmobil.service     # restart the API
```

Replace `suedtirolmobil-bot.service` to control the Telegram bot.

Alternatively run `./install_services.sh` from the repository root to copy the
example unit files to `/etc/systemd/system/` and enable them automatically.
