# AI-Based Self-Healing Framework — Walkthrough

## What Was Built

A three-service containerized stack for simulating and studying container failures:

| Service | Technology | Port | Container |
|---------|-----------|------|-----------|
| Frontend | Node.js + Express | 3000 | `frontend` |
| Backend | Python Flask | 5000 | `backend` |
| Database | MongoDB 7 | 27017 | `mongo` |

### Folder Structure

```
container-failure-lab/
├── services/
│   ├── backend/
│   │   ├── app.py            ← Flask API with health checks & event logging
│   │   ├── requirements.txt  ← flask, flask-cors, pymongo, gunicorn
│   │   └── Dockerfile        ← python:3.11-slim + healthcheck
│   └── frontend/
│       ├── server.js          ← Express dashboard + backend proxy
│       ├── package.json       ← express, axios
│       └── Dockerfile         ← node:20-alpine + healthcheck
├── logs/
│   ├── backend.log
│   ├── frontend.log
│   └── full.log
├── monitoring/
└── docker-compose.yml         ← 3 services, bridge network, mongo volume
```

---

## Deployment

```powershell
docker compose up --build -d
```

All 3 containers confirmed running:

| Container | Status |
|-----------|--------|
| `frontend` | Up (healthy) |
| `backend` | Up (healthy) |
| `mongo` | Up (healthy) |

---

## 8 Failure Injection Scenarios

### (a) Container Crash — Stop Backend

```powershell
docker stop -t 2 backend
```

**Result**: `backend` → `Exited (137)` (SIGKILL). `frontend` → `(unhealthy)` since it can no longer reach the backend API. Exit code 137 = container received SIGKILL signal.

**Why it matters**: Demonstrates cascading failure — one service crash degrades dependent services.

---

### (b) Memory Exhaustion — 50MB Limit

```powershell
docker update --memory=50m --memory-swap=50m backend
```

**Result**: Memory limit confirmed at `52428800` bytes (50MB). If the backend exceeds this limit under load, the OOM killer terminates the process with exit code 137.

**Why it matters**: Memory leaks or unexpected load spikes can cause OOM kills, which look identical to crashes but have a different root cause.

```powershell
# Reset:
docker update --memory=0 --memory-swap=0 backend
```

---

### (c) CPU Spike — Infinite Loop

```powershell
docker exec -d backend python -c "while True: pass"
```

**Result**: Confirmed via `docker top backend` — the infinite loop process consuming 100% CPU alongside the Flask app. Response times degrade.

**Why it matters**: A runaway process can starve co-located services. CPU throttling (`--cpus`) is the self-healing countermeasure.

```powershell
# Reset:
docker restart backend
```

---

### (d) Database Dependency Failure — Stop MongoDB

```powershell
docker stop -t 2 mongo
```

**Result**: Backend health-check fails with `ServerSelectionTimeoutError`. Any `/api/events` call returns `503`. Frontend dashboard shows MongoDB as `disconnected`.

**Why it matters**: Backend is alive but **non-functional** — a partial failure harder to detect than a full crash.

```powershell
# Reset:
docker start mongo
```

---

### (e) Network Failure — Disconnect Backend

```powershell
docker network disconnect container-failure-lab_app-network backend
```

**Result**: Backend loses connectivity to both MongoDB and frontend. Frontend returns `502 Bad Gateway`. Backend is running but completely isolated.

**Why it matters**: Network partitions are the most insidious failures — the container appears healthy to Docker but can't communicate.

```powershell
# Reset:
docker network connect container-failure-lab_app-network backend
```

---

### (f) Wrong Environment Variable — Bad MONGO_URI

```powershell
docker stop -t 2 backend && docker rm backend
docker run -d --name backend --network container-failure-lab_app-network \
  -p 5000:5000 -e MONGO_URI=mongodb://wrong-host:99999/ \
  -e PORT=5000 container-failure-lab-backend
```

**Result**: Backend starts but every MongoDB operation fails with `ServerSelectionTimeoutError` referencing `wrong-host:99999`. Health-check returns `503 unhealthy`.

**Why it matters**: Misconfiguration is the #1 cause of deployment failures. The app starts but silently fails.

```powershell
# Reset:
docker stop -t 2 backend && docker rm backend
docker compose up -d backend
```

---

### (g) Port Conflict — Nginx on Port 3000

```powershell
docker run -d --name nginx-conflict -p 3000:80 nginx:alpine
```

**Result**: `Error response from daemon: Bind for 0.0.0.0:3000 failed: port is already allocated`

**Why it matters**: Port conflicts prevent new deployments. In production, this happens during rolling updates or multi-tenant environments.

```powershell
# Cleanup:
docker rm nginx-conflict
```

---

### (h) Disk Exhaustion — Fill Container Storage

```powershell
docker exec backend sh -c "dd if=/dev/zero of=/tmp/fill_disk bs=1M count=500"
```

**Result**: `500+0 records in, 500+0 records out, 524288000 bytes (524 MB, 500 MiB) copied, 0.35s, 1.5 GB/s` — 500MB of zeros written inside the container.

**Why it matters**: Fills the writable layer; subsequent write operations (logging, temp files, database writes) fail. Docker shows the container as healthy even though it's functionally broken.

```powershell
# Reset:
docker exec backend rm -f /tmp/fill_disk
```

---

## Log Collection

```powershell
docker logs backend  > logs/backend.log
docker logs frontend > logs/frontend.log
docker compose logs  > logs/full.log
```

| Log File | Size |
|----------|------|
| `backend.log` | 1.5 KB |
| `frontend.log` | 101 B |
| `full.log` | ~1.2 MB |

---

## Current State

All 3 containers are running in a clean state. The failure lab is ready for further experimentation or integration with the self-healing agent (Member 2's work).
