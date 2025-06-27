# suedtirolmobilAI

Dieses Projekt stellt eine einfache Sprachschnittstelle für die Fahrplanauskunft
von Südtirol (STA) bereit. Nutzende können Fragen in natürlicher Sprache stellen
und erhalten passende Verbindungen über die EFA XML‑API.

## Struktur

- `src/` – Python-Module
- `main.py` – CLI-Einstiegspunkt
- `efa_api.py` – Wrapper für StopFinder und TripRequest
- `nlp_parser.py` – Kommunikation mit OpenAI GPT
- `formatter.py` – Aufbereitung der Ergebnisse
- `config.py` – Konfiguration/Schlüssel
- `tests/` – Beispieltests

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Setze anschließend den OpenAI API‑Key über die Umgebungsvariable `OPENAI_API_KEY`.

## Verwendung

```bash
python -m src.main
```

Das Programm fragt nach einer Frage wie z.B.:

```
Wann fährt morgen früh ein Bus von Bozen nach Meran?
```

Die KI ermittelt Start/Ziel/Datum/Uhrzeit, ruft die EFA‑API auf und gibt die
nächste Verbindung zurück.
