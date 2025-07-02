import os
from typing import Dict, Any
import requests

BASE_URL = os.environ.get("EFA_BASE_URL", "https://efa.sta.bz.it/apb")


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
    url = f"{BASE_URL}/XML_TRIP_REQUEST2"

    efa_params = {
        "name_origin": params.get("from_stop"),
        "type_origin": "any",
        "name_destination": params.get("to_stop"),
        "type_destination": "any",
        "outputFormat": "JSON",
        "calcNumberOfTrips": 1,
    }

    time = params.get("time")
    if time:
        efa_params["itdTime"] = time

    response = requests.get(url, params=efa_params, timeout=10)
    response.raise_for_status()
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}

