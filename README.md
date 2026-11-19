# Honeypot Threat Analysis

An isolated Docker lab with two honeypots (Cowrie SSH and a custom HTTP login), scripted attacks with ground-truth labels, and a pipeline that classifies captured activity, maps it to MITRE ATT&CK, and scores it against the labels.

**Team:** Aidan Guenther (defender, analysis), Lazaro Perez Jr. (attack scenarios)

## Requirements
Docker Desktop and [uv](https://docs.astral.sh/uv/).

## Reproduce the analysis from the included dataset
`data/` contains the three runs reported in the paper.

```bash
uv run python analysis/parse.py       # raw logs -> data/processed/events.csv
uv run python analysis/classify.py    # events -> data/processed/detections.csv
uv run python analysis/evaluate.py    # detections vs labels -> data/processed/metrics.csv
uv run python analysis/plots.py       # events -> report/figures/events_by_service.png
```

## Collect a new dataset

```bash
# Start from empty data folders.
mv data data_original
mkdir -p data/raw/cowrie data/raw/cowrie-downloads data/raw/honeypot data/labels

# macOS only: Cowrie can't create its log file on a host-mounted folder.
touch data/raw/cowrie/cowrie.json
chmod 666 data/raw/cowrie/cowrie.json

# Build and start the lab, then confirm isolation.
docker compose up -d --build
docker compose ps                             # all three should be running
docker exec attacker ping -c1 -W2 8.8.8.8     # must FAIL: no internet access

# Run the attack suite three times (about 5 minutes each).
docker exec attacker python3 /attacks/run_all.py --run-id 1
docker exec attacker python3 /attacks/run_all.py --run-id 2
docker exec attacker python3 /attacks/run_all.py --run-id 3

# Run the analysis pipeline (commands above), then stop the lab.
docker compose down
```

## Results
3 runs × 4 scenarios (SSH brute force, post-login SSH session, HTTP brute force, benign baseline), 3,117 events:
- Capture rate: 12/12 (100%)
- Precision and recall: 1.00 across all 5 detection classes (18 expected detections)

## Lab network (172.30.0.0/24, internal)
| Container | IP | Role | Ports |
| --- | --- | --- | --- |
| attacker | 172.30.0.10 | Kali Linux, runs attack scripts | 8000 (payload server) |
| cowrie | 172.30.0.20 | SSH honeypot (Telnet enabled, unused) | 2222, 2223 |
| honeypot | 172.30.0.30 | Custom Python HTTP honeypot | 80 |

## Repository layout
| Path | Purpose | Author |
| --- | --- | --- |
| docker-compose.yaml | The 3 containers and the isolated network | Aidan |
| honeypot/ | Custom honeypot: logger, HTTP login service | Aidan |
| attacks/Dockerfile, labeler.py, run_all.py | Attacker image, ground-truth labeler, scenario runner | Aidan |
| attacks/scenarios/, attacks/wordlists/ | The four attack scenarios and wordlists | Lazaro |
| analysis/ | Log parser, classifier, evaluation, plots | Aidan |
| data/raw/ | Raw honeypot logs | generated |
| data/labels/ | Ground-truth labels | generated |
| data/processed/ | Pipeline output | generated |
| report/figures/ | Figures used in the paper | generated |

## Log format
Both sensors log one JSON object per line. The custom honeypot writes `data/raw/honeypot/honeypot.jsonl`; Cowrie writes `data/raw/cowrie/cowrie.json`, which the parser converts. Shared fields: `ts` (UTC ISO-8601), `sensor`, `session`, `src_ip`, `src_port`, `dst_port`, `service`, `event_type`, plus `username`, `password`, `command`, `path`, `method`, `user_agent`, `status`, `payload` where relevant. `event_type` is one of: connect, login_failed, login_success, command, http_request, file_download, disconnect.
