import os
from dotenv import load_dotenv, find_dotenv

# Load .env file if it exists
_env_file = find_dotenv()
if _env_file:
    load_dotenv(_env_file)

EFA_BASE_URL = os.getenv("EFA_BASE_URL", "https://efa.sta.bz.it/apb")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
API_URL = os.getenv("API_URL", "http://localhost:8000")
