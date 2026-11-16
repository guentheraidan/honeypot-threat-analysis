# Author: Aidan Guenther
"""Shared JSON-lines event logger for the custom honeypot."""
import json
import os
import threading
import uuid
from datetime import datetime, timezone

LOG_PATH = os.environ.get("HONEYPOT_LOG", "/logs/honeypot.jsonl")
_lock = threading.Lock()

def new_session() -> str:
    """Short random ID shared by every event from one TCP connection."""
    return uuid.uuid4().hex[:8]

def clip(data: bytes, limit: int = 512) -> str:
    """Raw bytes -> printable text (capped so large payloads don't fill the log)."""
    return data[:limit].decode("utf-8", errors="backslashreplace")

def log_event(**fields) -> None:
    """Append one event as a single JSON line."""
    record = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "sensor": "custom",
    }
    record.update({k: v for k, v in fields.items() if v is not None}) # Drop fields set as None
    line = json.dumps(record, default=str)
    with _lock:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    print(line, flush=True)