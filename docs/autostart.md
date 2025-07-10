# Autostart unter Linux

Um den Server oder den Telegram-Chatbot automatisch zu starten, kann ein `systemd`-Dienst verwendet werden. Nach dem Anlegen des Dienstes kann er mit `start`, `stop` und `restart` gesteuert werden.

## Vorbereitung

1. Repository klonen und Abhängigkeiten installieren:
   ```bash
   git clone https://example.com/suedtirolmobilAI.git
   cd suedtirolmobilAI
   ./install.sh
   ```
2. Falls gewünscht, Umgebungsvariablen in einer `.env`-Datei im Projektverzeichnis hinterlegen. Diese Datei wird von der Anwendung automatisch geladen.

Die Beispieldateien `systemd/suedtirolmobil.service` und
`systemd/suedtirolmobil-bot.service` in diesem Repository können als Vorlage
verwendet und nach `/etc/systemd/system/` kopiert werden.

## systemd-Service für die API

Erstelle die Datei `/etc/systemd/system/suedtirolmobil.service` mit folgendem Inhalt (Pfad gegebenenfalls anpassen):

```ini
[Unit]
Description=suedtirolmobilAI API
After=network.target

[Service]
Type=simple
WorkingDirectory=/path/zum/repo/suedtirolmobilAI
ExecStart=/path/zum/repo/suedtirolmobilAI/venv/bin/uvicorn src.main:app --host 0.0.0.0
EnvironmentFile=/path/zum/repo/suedtirolmobilAI/.env
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Anschließend den Dienst laden und aktivieren:

```bash
sudo systemctl daemon-reload
sudo systemctl enable suedtirolmobil.service
sudo systemctl start suedtirolmobil.service
```

## systemd-Service für den Telegram-Bot

Soll auch der Telegram-Bot automatisch starten, kann ein zweiter Dienst angelegt werden. Beispiel `/etc/systemd/system/suedtirolmobil-bot.service`:

```ini
[Unit]
Description=suedtirolmobilAI Telegram Bot
After=network.target suedtirolmobil.service

[Service]
Type=simple
WorkingDirectory=/path/zum/repo/suedtirolmobilAI
ExecStart=/path/zum/repo/suedtirolmobilAI/venv/bin/python -m src.telegram_bot --api-url http://localhost:8000
EnvironmentFile=/path/zum/repo/suedtirolmobilAI/.env
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Dienst ebenfalls laden und aktivieren:

```bash
sudo systemctl daemon-reload
sudo systemctl enable suedtirolmobil-bot.service
sudo systemctl start suedtirolmobil-bot.service
```

## Steuerung des Dienstes

Die Dienste lassen sich jederzeit mit folgenden Befehlen steuern:

```bash
sudo systemctl start suedtirolmobil.service       # Startet die API
sudo systemctl stop suedtirolmobil.service        # Stoppt die API
sudo systemctl restart suedtirolmobil.service     # Startet die API neu
```

Für den Telegram-Bot entsprechend `suedtirolmobil-bot.service` verwenden.
