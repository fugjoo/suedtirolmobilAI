# suedtirolmobilAI

suedtirolmobilAI ist ein kleiner FastAPI-Dienst, der natürliche Sprachbefehle zum öffentlichen Nahverkehr interpretiert. Er erkennt, was gefragt ist, und leitet die Anfrage an einen Mentz‑EFA-Server weiter. Optional werden die Ergebnisse von ChatGPT zusammengefasst. Die Schnittstelle ist dreisprachig (Deutsch, Italienisch, Englisch) und kann auch als Model Context Protocol (MCP)‑Server eingesetzt werden.

## Funktionen
- Analyse von Anfragen in Deutsch, Italienisch und Englisch
- Verbindungssuche, Abfahrtsmonitor und Haltestellenvorschläge
- Stateless Haltestellen‑IDs für präzisere Ergebnisse
- Automatische Erkennung der gewünschten Aktion
- Optionale Zusammenfassung durch ChatGPT
- MCP‑Server für Toolaufrufe

## Projektstruktur
```
src/             FastAPI-Anwendung und Hilfsmodule
prompts/         Prompt-Vorlagen für das LLM
docs/            Zusatzdokumentation
tests/           Unit- und Integrationstests
```

## Voraussetzungen
Python 3.8 oder neuer.

## Installation
```bash
./install.sh
```
Das Skript legt bei Bedarf ein neues `venv` an und versucht, fehlende Pakete per `apt-get` oder `yum` zu installieren.

## Dienst starten
Start der HTTP-API:
```bash
uvicorn src.main:app --host 0.0.0.0 --reload
```
`--debug` aktiviert ausführliches Logging. Alternativ kann `python -m src.main` mit den Standardwerten genutzt werden.

### MCP-Server
```bash
python -m src.mcp_server
```
Der MCP-Server stellt Werkzeuge wie `search`, `departures` und `stops` für LLMs bereit.

## Konfiguration
Die wichtigsten Umgebungsvariablen:

- `EFA_BASE_URL` – Basis-URL des Mentz‑EFA-Endpunkts
  ```bash
  EFA_BASE_URL=https://efa.sta.bz.it/apb
  ```
- `OPENAI_API_KEY` – API‑Schlüssel für ChatGPT
  ```bash
  OPENAI_API_KEY=sk-...
  ```
- `OPENAI_MODEL` – Modellname für LLM-Funktionen
  ```bash
  OPENAI_MODEL=gpt-4
  ```
- `OPENAI_MAX_TOKENS` – Maximale Tokenanzahl für ChatGPT-Antworten (Standard 100)
  ```bash
  OPENAI_MAX_TOKENS=120
  ```

Variablen können auch in einer `.env`‑Datei im Projektverzeichnis abgelegt werden. Eine Vorlage steht als `.env.example` bereit.

## Prompt-Templates
Unter `prompts/` liegen zwei Textdateien, die das Verhalten des LLMs steuern:
- `parser_prompt.txt` – definiert, welche Felder aus einer Anfrage extrahiert werden (`{text}` Platzhalter)
- `formatter_prompt.txt` – formatiert die Antwort in der gewünschten Sprache (`{data}`, `{language}` Platzhalter)

Der Parser liefert Datumsangaben zunächst wörtlich („heute“, „tomorrow“). Bei der Verarbeitung werden die Ausdrücke in ISO-Zeitstempel übersetzt.

## API-Endpunkte
Alle Endpunkte erwarten POST-Anfragen. Mit dem Parameter `format` wird die Ausgabe gesteuert (`json` oder `text`).

### `/search`
Beispiel:
```bash
curl -X POST http://localhost:8000/search \
     -H 'Content-Type: application/json' \
     -d '{"text": "Wie komme ich von Bozen nach Meran um 14:30?"}'
```

### `/departures`
```bash
curl -X POST http://localhost:8000/departures \
     -H 'Content-Type: application/json' \
     -d '{"stop": "Bozen", "language": "it", "limit": 5}'
```
Optional `language` (`de`, `it`, `en`) und `limit` (Standard 10).

### `/stops`
```bash
curl -X POST http://localhost:8000/stops \
     -H 'Content-Type: application/json' \
     -d '{"query": "Brixen", "language": "it"}'
```

## Autostart unter Linux
Siehe [docs/autostart.md](docs/autostart.md) für die Einrichtung eines `systemd`‑Dienstes. Die Vorlagen im Ordner `systemd/` können nach `/etc/systemd/system/` kopiert oder mit `sudo ./install_services.sh` installiert werden.

## Tests
```bash
pytest -q
```

## Lizenz
MIT-Lizenz – siehe [LICENSE](LICENSE).
