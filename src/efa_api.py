import os
from typing import Dict, Any
import requests

BASE_URL = os.environ.get("EFA_BASE_URL", "https://efa.sta.bz.it/apb/")


def search_efa(params: Dict[str, Any]) -> Dict[str, Any]:
    """Send a GET request to the Mentz-EFA API.

    Parameters
    ----------
    params: dict
        Query parameters for the EFA request.

    Returns
    -------
    dict
        JSON response from the API.
    """
    url = f"{BASE_URL}/".rstrip('/')
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}

