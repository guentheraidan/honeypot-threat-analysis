# Author: Aidan Guenther
"""Score detections against the ground-truth labels."""
import json
import os
from datetime import timedelta
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DET = os.path.join(ROOT, "data/processed/detections.csv")
LABELS = os.path.join(ROOT, "data/labels/labels.jsonl")
EVENTS = os.path.join(ROOT, "data/processed/events.csv")
OUT = os.path.join(ROOT, "data/processed/metrics.csv")

SLACK = 5  # seconds of tolerance on window edges

# Which detection classes each scenario is supposed to produce.
EXPECTED = {
    "ssh_bruteforce":  {"brute_force", "valid_account"},
    "ssh_session":     {"recon", "tool_transfer", "persistence"},
    "http_bruteforce": {"brute_force"},
    "benign":          set(), # should produce nothing
}

def load_labels():
    rows = []
    with open(LABELS) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    df = pd.DataFrame(rows)
    df["start_ts"] = pd.to_datetime(df["start_ts"], utc=True, format="ISO8601")
    df["end_ts"] = pd.to_datetime(df["end_ts"], utc=True, format="ISO8601")
    return df

def overlaps(a1, a2, b1, b2):
    """True if time spans [a1,a2] and [b1,b2] touch."""
    return a1 <= b2 and b1 <= a2

def main():
    det = pd.read_csv(DET)
    det["first_ts"] = pd.to_datetime(det["first_ts"], utc=True, format="ISO8601")
    det["last_ts"] = pd.to_datetime(det["last_ts"], utc=True, format="ISO8601")
    labels = load_labels()
    ev = pd.read_csv(EVENTS)
    ev["ts"] = pd.to_datetime(ev["ts"], utc=True, format="ISO8601")
    slack = timedelta(seconds=SLACK)

    # capture rate: scenarios with at least one logged event in their window
    captured = 0
    for _, L in labels.iterrows():
        in_window = ev[(ev["ts"] >= L.start_ts - slack) & (ev["ts"] <= L.end_ts + slack)]
        if len(in_window):
            captured += 1
    capture_rate = captured / len(labels)

    # one expected item per (scenario, class the scenario should produce)
    expected = []
    for _, L in labels.iterrows():
        for cls in EXPECTED.get(L.scenario, set()):
            expected.append({"class": cls, "start": L.start_ts,
                             "end": L.end_ts, "matched": False})

    # match each detection to an expected item
    tp, fp = [], []
    for _, d in det.iterrows():
        hit = None
        for e in expected:
            if (not e["matched"] and d["class"] == e["class"]
                    and overlaps(d.first_ts, d.last_ts,
                                 e["start"] - slack, e["end"] + slack)):
                hit = e
                break
        if hit:
            hit["matched"] = True
            tp.append(d["class"])
        else:
            fp.append(d["class"]) # wrong class or hit the benign window
    fn = [e["class"] for e in expected if not e["matched"]]

    # per-class precision / recall
    rows = []
    for c in sorted(set(tp + fp + fn)):
        TP, FP, FN = tp.count(c), fp.count(c), fn.count(c)
        prec = TP / (TP + FP) if TP + FP else 0.0
        rec  = TP / (TP + FN) if TP + FN else 0.0
        rows.append({"class": c, "TP": TP, "FP": FP, "FN": FN,
                     "precision": round(prec, 2), "recall": round(rec, 2)})
    m = pd.DataFrame(rows)

    TP, FP, FN = len(tp), len(fp), len(fn)
    overall_p = TP / (TP + FP) if TP + FP else 0.0
    overall_r = TP / (TP + FN) if TP + FN else 0.0

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    m.to_csv(OUT, index=False)
    print(f"Capture rate: {captured}/{len(labels)} = {capture_rate:.0%}\n")
    print(m.to_string(index=False))
    print(f"\nOverall  precision={overall_p:.2f}  recall={overall_r:.2f}  "
          f"(TP={TP} FP={FP} FN={FN})")

if __name__ == "__main__":
    main()