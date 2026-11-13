# Honeypot Threat Analysis

CNT4409 Network Security final project: deploying an isolated honeypot and analyzing simulated attack attempts.

**Team:** Aidan Guenther (defender), Lazaro Perez Jr. (attacker)

## Quick start
Requires Docker Desktop.
```bash
docker compose up -d --build
docker compose ps                           # cowrie, honeypot, attacker all "running"
docker exec attacker ping -c1 -W2 8.8.8.8   # must fail (lab is isolated from Internet)
```

## Lab network (172.30.0.0/24, internal)
| Container | IP | Role | Ports |
| --- | --- | --- | --- |
| attacker | 172.30.0.10 | Kali Linux, runs attack scripts | 8000 (payload server) |
| cowrie | 172.30.0.20 | SSH/Telnet honeypot | 2222, 2223 |
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
plus `username`, `password`, `command`, `path`, `method`, `user_agent`, `status`, `payload`, `details` where relevant.
`event_type` is one of: connect, login_failed, login_success, command, http_request, file_download, port_scan, disconnect.

## Workflow
- Branches: `defender` (Aidan), `attacker` (Lazaro); merge to `main` via pull request.
- Every source file starts with `# Author: <name>`.
- Don't commit test data in `data/` yet (real data will be collected after components are completed)

## Authorship
[Final per-file table before submission]
