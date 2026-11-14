# Author: Aidan Guenther
"""Normalize Cowrie and custom honeypot logs into events.csv"""
import json
import os
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HONEYPOT = os.path.join(ROOT, "data/raw/honeypot/honeypot.jsonl")
COWRIE = os.path.join(ROOT, "data/raw/cowrie/cowrie.json")
OUT = os.path.join(ROOT, "data/processed/events.csv")

# Every event row has columns:
COLS = ["ts", "sensor", "session", "src_ip", "src_port", "dst_port",
        "service", "event_type", "username", "password", "command",
        "path", "method", "user_agent", "status", "payload"]

# Cowrie eventid -> event_type
EVENT_MAP = {
    "cowrie.session.connect":       "connect",
    "cowrie.login.failed":          "login_failed",
    "cowrie.login.success":         "login_success",
    "cowrie.command.input":         "command",
    "cowrie.session.file_download": "file_download",
    "cowrie.session.closed":        "disconnect",
}

def read_jsonl(path):
    """One dict per non-empty line"""
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)

def parse_honeypot():
    """Custom honeypot lines already use schema"""
    return list(read_jsonl(HONEYPOT))

def parse_cowrie():
    """Translate Cowrie's events into schema"""
    raw = list(read_jsonl(COWRIE))
    service = {e.get("session"): e["protocol"] for e in raw if "protocol" in e}
    rows = []
    for e in raw:
        et = EVENT_MAP.get(e.get("eventid"))
        if et is None:
            continue
        rows.append({
            "ts": e.get("timestamp"),
            "sensor": "cowrie",
            "session": e.get("session"),
            "src_ip": e.get("src_ip"),
            "src_port": e.get("src_port"),
            "dst_port": e.get("dst_port"),
            "service": service.get(e.get("session"), "ssh"),
            "event_type": et,
            "username": e.get("username"),
            "password": e.get("password"),
            "command": e.get("input"),
            "payload": e.get("url"),
        })
    return rows

def main():
    rows = parse_honeypot() + parse_cowrie()
    df = pd.DataFrame(rows, columns=COLS)
    df = df.sort_values("ts").reset_index(drop=True)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"{len(df)} events -> {OUT}")
    print(df["event_type"].value_counts().to_string())

if __name__ == "__main__":
    main()