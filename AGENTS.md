# AGENT instructions

This repository has no dev container configuration, but you can run it in a GitHub Codespace. The steps are the same as on any local machine:

1. Create a virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Run the command line interface:

```bash
python src/main.py "When does the next bus from Bolzano to Merano leave?"
```

3. Alternatively start the FastAPI service:

```bash
pip install -r requirements.txt
uvicorn src.web_service:app --reload
```

These commands work in a Codespace as long as the environment includes Python 3.9 or higher. There is no specialized Codespace or Docker configuration, so you must set up the environment manually.
