from pathlib import Path
from datetime import datetime
import json

LOCAL_LOG_PATH = Path(__file__).resolve().parent.parent / "logs" / "application_logs.jsonl"
LOCAL_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

def log_event(message, answer): 
    record = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "user_message": message, 
        "agent_response": answer
    }

    with LOCAL_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")