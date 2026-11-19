# Author: Aidan Guenther

# Records start/end time of each attack to labels.jsonl
"""Context manager that timestamps each scenario and appends a label line."""
import json
import os
from contextlib import contextmanager
from datetime import datetime, timezone

LABELS = "/labels/labels.jsonl"
ATTACKER_IP = "172.30.0.10"

def _now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")

@contextmanager
def scenario(run_id, name, mitre, target):
    start = _now()
    try:
        yield
    finally:
        rec = {"run_id": run_id, "scenario": name, "mitre": mitre,
               "src_ip": ATTACKER_IP, "target": target,
               "start_ts": start, "end_ts": _now()}
        os.makedirs(os.path.dirname(LABELS), exist_ok=True)
        with open(LABELS, "a") as f:
            f.write(json.dumps(rec) + "\n")
