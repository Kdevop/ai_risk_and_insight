from pathlib import Path
from datetime import datetime, timezone
import json
from typing import Any

LOCAL_LOG_PATH = Path(__file__).resolve().parent.parent / "logs" / "application_logs.jsonl"
LOCAL_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

def log_event(event_type: str, payload: dict[str, Any]) -> None: 
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "event_type": event_type, 
        "data": payload
    }

    with LOCAL_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n") 

