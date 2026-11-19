# Author: Aidan Guenther

# Runs all scenarios in order with labels
"""Run every scenario once, each wrapped in a ground-truth label."""
import argparse
import os
import subprocess
import time

from labeler import scenario
from scenarios import ssh_bruteforce, ssh_session, http_bruteforce, benign

HERE = os.path.dirname(os.path.abspath(__file__))
GAP = 70  # seconds between scenarios so their time windows don't overlap; must exceed classify.py's 60s burst gap

# (name, mitre, target, function)
PLAN = [
    ("ssh_bruteforce",  "T1110.001", "172.30.0.20", ssh_bruteforce.run),
    ("ssh_session",     "T1078,T1082,T1033,T1105,T1053.003,T1098.004", "172.30.0.20", ssh_session.run),
    ("http_bruteforce", "T1110.001", "172.30.0.30", http_bruteforce.run),
    ("benign",          "",          "both",        benign.run),
]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", type=int, required=True)
    run_id = ap.parse_args().run_id

    # Serve the payload so ssh_session's wget has something to fetch on the isolated net.
    server = subprocess.Popen(
        ["python3", "-m", "http.server", "8000", "--directory", f"{HERE}/payloads"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for name, mitre, target, fn in PLAN:
            print(f"[run {run_id}] {name}")
            with scenario(run_id, name, mitre, target):
                fn()
            time.sleep(GAP)
    finally:
        server.terminate()

if __name__ == "__main__":
    main()
