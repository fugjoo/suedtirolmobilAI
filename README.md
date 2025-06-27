# suedtirolmobilAI

Dieses Projekt stellt eine einfache Sprachschnittstelle für die Fahrplanauskunft
von Südtirol (STA) bereit. Nutzende können Fragen in natürlicher Sprache stellen
und erhalten passende Verbindungen über die EFA XML‑API.

## Voraussetzungen

Die Abhängigkeiten setzen **Python ≥ 3.7** voraus. Insbesondere
`pandas>=1.2.3` ist erst ab dieser Version verfügbar. Unter Oracle Linux
empfiehlt es sich daher, vor der Installation ein aktuelles Python
(z. B. 3.9) über `dnf module install python:3.9` zu installieren.

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

Falls `pip` versucht, `pandas` aus dem Quellcode zu bauen und dabei
`Cannot cythonize without Cython installed` meldet, installiere zuvor
`Cython`:

```bash
pip install Cython
pip install -r requirements.txt
```

Der Zugriff auf ChatGPT erfordert einen gültigen OpenAI API‑Key. Dieser muss
als Umgebungsvariable `OPENAI_API_KEY` vor dem Start gesetzt sein, zum
Beispiel:

```bash
export OPENAI_API_KEY=<dein-geheimer-key>
```

Das Programm liest diese Variable beim Aufruf aus.

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
