# Honeypot Threat Analysis

CNT4409 Network Security final project: an isolated Docker lab with two honeypots (Cowrie SSH and a custom HTTP login), scripted attacks with ground-truth labels, and a pipeline that classifies captured activity and maps it to MITRE ATT&CK.

**Team:** Aidan Guenther (defender), Lazaro Perez Jr. (attacker)

## Run the experiment
Requires Docker Desktop and [uv](https://docs.astral.sh/uv/).

```bash
# 1. macOS only: Cowrie can't create its log file on a host-mounted folder,
#    so create it and make it writable before starting the lab.
touch data/raw/cowrie/cowrie.json
chmod 666 data/raw/cowrie/cowrie.json

# 2. Build and start the lab (attacker, cowrie, honeypot), then confirm isolation.
docker compose up -d --build
docker compose ps                             # all three should be "running"
docker exec attacker ping -c1 -W2 8.8.8.8     # must FAIL: lab has no internet access

# 3. Run the attack suite three times. Each run executes 4 labeled scenarios.
docker exec attacker python3 /attacks/run_all.py --run-id 1
docker exec attacker python3 /attacks/run_all.py --run-id 2
docker exec attacker python3 /attacks/run_all.py --run-id 3

# 4. Check the data: labels.jsonl should have 12 lines, cowrie.json more than 0.
wc -l data/labels/labels.jsonl data/raw/cowrie/cowrie.json

# 5. Run the analysis pipeline in order.
uv run python analysis/parse.py       # raw logs -> data/processed/events.csv
uv run python analysis/classify.py    # events -> data/processed/detections.csv
uv run python analysis/evaluate.py    # detections vs labels -> data/processed/metrics.csv
uv run python analysis/plots.py       # events -> report/figures/events_by_service.png

# 6. Stop the lab when done.
docker compose stop
```

## Results
3 runs × 4 scenarios (SSH brute force, post-login SSH session, HTTP brute force, benign baseline):
- Capture rate: 12/12 (100%)
- Precision and recall: 1.00 across all 5 detection classes (brute_force, valid_account, recon, tool_transfer, persistence)

## Lab network (172.30.0.0/24, internal)
| Container | IP | Role | Ports |
| --- | --- | --- | --- |
| attacker | 172.30.0.10 | Kali Linux, runs attack scripts | 8000 (payload server) |
| cowrie | 172.30.0.20 | SSH honeypot (Telnet enabled, unused) | 2222, 2223 |
| honeypot | 172.30.0.30 | Custom Python honeypot | 80 |

## Repository layout
| Path | Purpose | Owner |
| --- | --- | --- |
| docker-compose.yaml | Defines the 3 containers and the isolated network | Aidan |
| cowrie/userdb.txt | Which SSH logins Cowrie accepts | Aidan |
| honeypot/ | Custom honeypot: logger, HTTP login service | Aidan |
| attacks/ | Attacker image, attack scenarios, wordlists, labeler | Lazaro |
| analysis/ | Log parser, classifier, evaluation, plots | Aidan |
| data/raw/ | Raw honeypot logs (never edited) | code-generated |
| data/labels/ | Ground-truth labels written by the attack scripts | code-generated |
| data/processed/ | Parser/classifier output | code-generated |
| report/ | Paper source and figures | both |

## Log format
Both sensors log one JSON object per line. The custom honeypot writes `data/raw/honeypot/honeypot.jsonl`;
Cowrie writes `data/raw/cowrie/cowrie.json` (converted by the parser). Shared fields:
`ts` (UTC ISO-8601), `sensor`, `session`, `src_ip`, `src_port`, `dst_port`, `service`, `event_type`,
plus `username`, `password`, `command`, `path`, `method`, `user_agent`, `status`, `payload` where relevant.
`event_type` is one of: connect, login_failed, login_success, command, http_request, file_download, disconnect.

## Workflow
- Branches: `defender` (Aidan), `attacker` (Lazaro); merge to `main` via pull request.
- Every source file starts with `# Author: <name>`.
- `data/` is gitignored; reproduce the dataset with the commands above.

## Authorship
Per-file authorship is marked in each file's header comment and finalized before submission.
