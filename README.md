# suedtirolmobilAI

A small Python project demonstrating how to parse text requests and call the
Südtirolmobil Fahrplan API. The code is intended as a starting point for
building a ChatGPT action or any other integration that replies with timetable
information.

## Project layout

```
src/
    fahrplan_api.py    # wrappers around your Fahrplan API endpoints
    nlp_parser.py      # minimal text parsing / intent detection
    main.py            # simple CLI entry point
    web_service.py     # optional FastAPI wrapper
```

## Setup

1. Create a virtual environment and install the dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Run the CLI with a short text query:

```bash
python src/main.py "Wann fährt der nächste Bus von Bozen nach Meran?"
```

The script parses your question, selects the appropriate API wrapper and calls
the Südtirolmobil Fahrplan endpoints. Ensure you have network connectivity
when running the example.

## Using with ChatGPT actions

You can expose the `handle_request` function in `main.py` through a small web
service and register that endpoint as a ChatGPT action. The current code keeps
all logic separated so it can easily be reused in such a service.

### Running the web service

Install the additional dependencies and start the FastAPI app:

```bash
pip install -r requirements.txt
uvicorn src.web_service:app --reload
```

Send a request using `curl`:

```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"text": "Wann fährt der nächste Bus von Bozen nach Meran?"}' \
     http://localhost:8000/query
```
