import json
import os
from typing import List

INCIDENTS_FILE = "data/incidents.json"

def log_incident(report):
    """Logs unique AI-driven reports to history."""
    if not os.path.exists("data"):
        os.makedirs("data")

    history = []
    if os.path.exists(INCIDENTS_FILE):
        with open(INCIDENTS_FILE, "r") as f:
            try:
                history = json.load(f)
            except:
                history = []

    # Insert latest incident at the top
    history.insert(0, report.dict() if hasattr(report, 'dict') else report)

    with open(INCIDENTS_FILE, "w") as f:
        json.dump(history, f, indent=4)

def get_all_incidents() -> List[dict]:
    """Returns the full list of incidents for the UI."""
    if os.path.exists(INCIDENTS_FILE):
        with open(INCIDENTS_FILE, "r") as f:
            return json.load(f)
    return []