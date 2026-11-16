# Author: Aidan Guenther
"""Turns events.csv into detections.csv using time-windowed rules."""
import os
from datetime import timedelta
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVENTS = os.path.join(ROOT, "data/processed/events.csv")
OUT = os.path.join(ROOT, "data/processed/detections.csv")

# thresholds
BRUTE_COUNT = 5 # failed logins...
BRUTE_WINDOW = 60 # ...within this many seconds = brute force
VALID_WINDOW = 300 # success this soon after brute force = cracked account

RECON = ("uname", "whoami", "id", "/etc/passwd", "hostname", "ifconfig")
TRANSFER = ("wget", "curl")
PERSIST = ("crontab", "authorized_keys")

MITRE = {
    "brute_force": "T1110.001",
    "valid_account": "T1078",
    "recon": "T1082,T1033",
    "tool_transfer": "T1105",
    "persistence": "T1053.003,T1098.004",
}

detections = []
def add(first, last, ip, cls, count):
    detections.append({
        "first_ts": first.isoformat().replace("+00:00", "Z"),
        "last_ts": last.isoformat().replace("+00:00", "Z"),
        "src_ip": ip, "class": cls, "mitre": MITRE[cls],
        "evidence_count": int(count),
    })

def bursts(times, max_gap):
    """Split sorted timestamps into groups separated by more than max_gap seconds."""
    out, cur = [], []
    for t in times:
        if cur and (t - cur[-1]).total_seconds() > max_gap:
            out.append(cur)
            cur = []
        cur.append(t)
    if cur:
        out.append(cur)
    return out

def main():
    df = pd.read_csv(EVENTS)
    df["ts"] = pd.to_datetime(df["ts"], utc=True)
    df = df.sort_values("ts")

    # brute_force: 5+ failed logins on one service within 60s
    bf = [] # remember clusters for valid_account rule
    fails = df[df["event_type"] == "login_failed"]
    for (ip, svc), g in fails.groupby(["src_ip", "service"]):
        for burst in bursts(list(g["ts"]), BRUTE_WINDOW):
            if len(burst) >= BRUTE_COUNT:
                add(burst[0], burst[-1], ip, "brute_force", len(burst))
                bf.append((ip, svc, burst[0], burst[-1]))

    # valid_account: first success on that service within 5 mins of brute force
    succ = df[df["event_type"] == "login_success"]
    for ip, svc, _first, last in bf:
        cand = succ[(succ["src_ip"] == ip) & (succ["service"] == svc) &
                    (succ["ts"] >= _first) &
                    (succ["ts"] <= last + timedelta(seconds=VALID_WINDOW))]
        if not cand.empty:
            t = cand["ts"].min()
            add(t, t, ip, "valid_account", 1)

    # command-based rules, per source IP, split into bursts so each run is separate
    for ip, g in df.groupby("src_ip"):
        cmd = g[g["event_type"] == "command"].copy()
        low = cmd["command"].fillna("").str.lower()

        def hit_times(keys):
            m = cmd[low.apply(lambda s: any(k in s for k in keys))]
            return sorted(m["ts"])

        for b in bursts(hit_times(RECON), BRUTE_WINDOW):
            add(b[0], b[-1], ip, "recon", len(b))

        fd = g[g["event_type"] == "file_download"]
        transfer = sorted(hit_times(TRANSFER) + list(fd["ts"]))
        for b in bursts(transfer, BRUTE_WINDOW):
            add(b[0], b[-1], ip, "tool_transfer", len(b))

        for b in bursts(hit_times(PERSIST), BRUTE_WINDOW):
            add(b[0], b[-1], ip, "persistence", len(b))

    out = pd.DataFrame(detections,
        columns=["first_ts", "last_ts", "src_ip", "class", "mitre", "evidence_count"])
    out = out.sort_values("first_ts").reset_index(drop=True)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    out.to_csv(OUT, index=False)
    print(f"{len(out)} detections -> {OUT}")
    print(out.to_string(index=False))

if __name__ == "__main__":
    main()