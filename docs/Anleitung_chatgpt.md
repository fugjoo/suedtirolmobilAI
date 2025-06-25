# Anleitung: suedtirolmobilAI starten und in ChatGPT einbinden

Diese kurze Anleitung beschreibt, wie das Beispielprojekt `suedtirolmobilAI` eingerichtet wird und wie man die enthaltene API über ein ChatGPT-Plugin beziehungsweise eine ChatGPT-Action nutzen kann.

## 1. Voraussetzungen

- Python 3.9 oder neuer
- Zugriff auf das Internet für die Installation der Abhängigkeiten und für API-Anfragen

## 2. Projekt einrichten

1. Repository klonen und in das Verzeichnis wechseln.
2. Virtuelle Umgebung erstellen und Abhängigkeiten installieren:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## 3. Tool starten

### 3.1 Nutzung über die Kommandozeile

Die einfachste Möglichkeit ist das direkte Ausführen des Skripts `src/main.py` mit einer Textanfrage:

```bash
python src/main.py "Wann fährt der nächste Bus von Bozen nach Meran?"
```

### 3.2 Start des Webdienstes

Für eine Integration in ChatGPT empfiehlt es sich, das FastAPI-Webservice zu starten. Dadurch erhalten wir einen HTTP-Endpunkt, der von ChatGPT angesprochen werden kann:

```bash
pip install -r requirements.txt
uvicorn src.web_service:app --reload
```

Der Dienst lauscht standardmäßig auf Port 8000. Über `curl` kann eine Anfrage getestet werden:

```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"text": "Wann fährt der nächste Bus von Bozen nach Meran?"}' \
     http://localhost:8000/query
```

## 4. Einbindung in ChatGPT

1. **OpenAPI-Spezifikation erstellen**: Für ChatGPT-Plugins wird eine OpenAPI-Spezifikation benötigt. Die Routen des FastAPI-Dienstes können automatisch über `http://localhost:8000/openapi.json` abgerufen und als Grundlage verwendet werden.
2. **Plugin manifest erstellen**: Erstellen Sie eine `ai-plugin.json`, in der der Endpunkt `/query` definiert ist und auf die eben erzeugte OpenAPI-Datei verwiesen wird. Diese Datei muss zusammen mit der Spezifikation auf einem öffentlich erreichbaren Server liegen.
3. **Plugin bei ChatGPT registrieren**: In der Plugin-Entwicklungsoberfläche von ChatGPT kann nun die URL zur `ai-plugin.json` angegeben und der Endpunkt getestet werden.
4. **Anfragen stellen**: Sobald das Plugin aktiviert ist, können Nutzer Fragen im Stil von "Wann fährt der nächste Zug von X nach Y?" stellen. ChatGPT leitet die Anfrage an den laufenden FastAPI-Dienst weiter und gibt die Ergebnisse aus dem Fahrplan-API aus.

---

Mit diesen Schritten lässt sich `suedtirolmobilAI` lokal starten und über ein ChatGPT-Plugin nutzen.
