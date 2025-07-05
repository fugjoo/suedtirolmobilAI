## Einfache Wiki für `suedtirolmobilAI`

### Überblick
`suedtirolmobilAI` ist ein kleines FastAPI-Projekt zur Verarbeitung von Anfragen rund um den öffentlichen Nahverkehr in Südtirol. Es interpretiert natürlichsprachliche Eingaben (Deutsch, Englisch und Italienisch) und ruft die passende Mentz-EFA-Schnittstelle auf.

### Hauptfunktionen
- **Trip-Suche:** Verbindungen zwischen zwei Haltestellen ermitteln
- **Abfahrten:** Nächste Abfahrten für eine Haltestelle anzeigen
- **Stopfinder:** Haltestellenvorschläge liefern
- **Telegram-Bot:** Direkte Nutzung per Chat
- **Optionale ChatGPT-Unterstützung:** Für verbesserte Formulierungen und automatische Request-Klassifizierung

### Installation
1. Repository klonen und ins Verzeichnis wechseln
2. Entweder per Skript:
   ```bash
   ./install.sh
   source venv/bin/activate
   ```
   oder manuell:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python -m spacy download de_core_news_sm  # optional
   ```

### Konfiguration
Die Anwendung liest verschiedene Umgebungsvariablen (siehe `src/config.py`):

- `EFA_BASE_URL` – Basis-URL des Mentz-EFA-Backends  
  Standard: `https://efa.sta.bz.it/apb`
- `OPENAI_API_KEY` – API-Schlüssel für ChatGPT-Funktionen (optional)
- `TELEGRAM_TOKEN` – Token für den Telegram-Bot
- `API_URL` – Basis-URL des API-Servers (für den Bot)

Die Variablen können auch in einer `.env`-Datei abgelegt werden.

### API starten
```bash
uvicorn src.main:app --host 0.0.0.0 --reload
```

### Befehlszeilen-Client
- **Trip-Suche:**  
  `python -m src.cli search "Wie komme ich von Bozen nach Meran um 14:30?"`
- **Abfahrtsmonitor:**  
  `python -m src.cli departures "Bozen"`
- **Stop-Suche:**  
  `python -m src.cli stops "Brixen"`
- Wichtige Optionen: `--format text|json|legs`, `--debug`, `--chatgpt`

### API-Endpunkte (POST)
- `/search` – Trip-Suche  
  Beispiel:
  ```bash
  curl -X POST http://localhost:8000/search \
       -H 'Content-Type: application/json' \
       -d '{"text": "Wie komme ich von Bozen nach Meran um 14:30?"}'
  ```
- `/departures` – Abfahrtsmonitor  
  ```bash
  curl -X POST http://localhost:8000/departures \
       -H 'Content-Type: application/json' \
       -d '{"stop": "Bozen", "limit": 5}'
  ```
- `/stops` – Stopfinder  
  ```bash
  curl -X POST http://localhost:8000/stops \
       -H 'Content-Type: application/json' \
       -d '{"query": "Brixen"}'
  ```
Parameter `?format=text` oder `?format=json` anfügen und `chatgpt=true` für ChatGPT-Zusammenfassungen.

### Telegram-Bot
1. `TELEGRAM_TOKEN` setzen.
2. Starten mit:
   ```bash
   python -m src.telegram_bot --api-url http://localhost:8000
   ```
   Optional `--start-server`, um die API gleich mit zu starten, oder `--chatgpt` für ChatGPT-Unterstützung.

### Tests
Alle Unit Tests liegen unter `tests/`. Ausführen mit:
```bash
pytest
```

### Lizenz
Veröffentlicht unter MIT-Lizenz. Weitere Details siehe `LICENSE`.
