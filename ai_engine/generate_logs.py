"""
generate_logs.py — Generates realistic synthetic logs for training + testing.

Produces:
  data/training_logs.csv   — for SVM training
  data/logs_app.txt        — realistic app container logs
  data/logs_db.txt         — realistic db container logs
  data/logs_api.txt        — realistic api container logs

Run: python generate_logs.py
"""

import random
import csv
import os
from datetime import datetime, timedelta

random.seed(42)

# ──────────────────────────────────────────────
# REALISTIC LOG TEMPLATES per category
# ──────────────────────────────────────────────

TEMPLATES = {

    "build": [
        "[ERROR] Step {step}/12 : RUN npm install\n > npm ERR! code ERESOLVE\n > npm ERR! Could not resolve dependency: peer react@\"{ver}\" from {pkg}@{pkgver}",
        "[ERROR] failed to solve: failed to read dockerfile: open Dockerfile: no such file or directory",
        "[ERROR] failed to compute cache key: \"{path}\" not found: not found",
        "error: could not find pip module '{module}', run: pip install {module}",
        "ERROR [build {step}/{total}] RUN pip install -r requirements.txt\n0.812 ERROR: Could not find a version that satisfies the requirement {pkg}=={ver}",
        "failed to create LLB definition: dockerfile parse error line {line}: unknown instruction: {instr}",
        "COPY failed: file not found in build context or excluded by .dockerignore: stat {file}: file does not exist",
        "error building image: Error response from daemon: dockerfile parse error line {line}: Unknown flag: --{flag}",
        "Build failed: exit status 1\nCompilation error in {file}:{line}: '{symbol}' undeclared",
        "ERROR: failed to build: failed to pull image '{img}': image not found in registry",
    ],

    "memory": [
        "FATAL: Terminating due to java.lang.OutOfMemoryError: Java heap space",
        "FATAL ERROR: CALL_AND_RETRY_LAST Allocation failed - JavaScript heap out of memory",
        "oom-kill:constraint=CONSTRAINT_MEMCG,nodemask=(null),cpuset=docker,task={pid},oom_score_adj=0, global_oom,task_memcg=/docker/{cid},task=node,pid={pid},uid=0",
        "Killed process {pid} (python3) total-vm:{vm}kB, anon-rss:{rss}kB, file-rss:0kB, shmem-rss:0kB, UID:0 pgtables:{pt}kB oom_score_adj:0",
        "Container '{cname}' exceeded memory limit of {limit}MB. Sending SIGKILL.",
        "[  {ts}] Out of memory: Kill process {pid} ({proc}) score {score} or sacrifice child",
        "go: runtime: out of memory: cannot allocate {size}MB region",
        "java.lang.OutOfMemoryError: GC overhead limit exceeded\n\tat {cls}.{method}({file}:{line})",
        "SIGKILL received — container memory usage {used}MB exceeded limit {limit}MB",
        "runtime: out of memory: cannot allocate {pages} bytes of memory (limit {limit}MB)",
    ],

    "dependency": [
        'dial tcp {ip}:5432: connect: connection refused',
        "Error: connect ECONNREFUSED {ip}:{port}",
        "[ERROR] HikariPool-1 - Connection is not available, request timed out after {ms}ms\n\tat com.zaxxer.hikari.pool.HikariPool.getConnection(HikariPool.java:213)",
        "pymongo.errors.ServerSelectionTimeoutError: {ip}:{port}: [Errno 111] Connection refused, Timeout: 30s",
        "redis.exceptions.ConnectionError: Error {code} connecting to {ip}:6379. Connection refused.",
        "AMQP connection error on {ip}:5672: connection refused (reptured)",
        "grpc: addrConn.createTransport failed to connect to {{{ip}:{port}, <nil>}}. Err: connection refused.",
        "kafka: client has run out of available brokers to talk to (Is your cluster reachable?) [{ip}:9092]",
        "upstream connect error or disconnect/reset before headers. reset reason: connection failure — {svc}:{port}",
        "ServiceUnavailableError: Downstream service '{svc}' at {ip}:{port} is not responding",
    ],

    "permission": [
        "PermissionError: [Errno 13] Permission denied: '/app/{path}'",
        "Error: EACCES: permission denied, mkdir '/home/node/{dir}'",
        "open /var/run/docker.sock: permission denied",
        "touch: cannot touch '/data/{file}': Permission denied",
        "Error response from daemon: user {user}: unable to find user {user}: no matching entries in passwd file",
        "chown: changing ownership of '/data/{path}': Operation not permitted",
        "cp: cannot create regular file '/etc/{conf}': Permission denied",
        "SSL_CTX_use_PrivateKey_file('/certs/{cert}.key') failed: Permission denied",
        "[ERROR] Unable to open log file '/var/log/{svc}/{svc}.log': Permission denied",
        "java.io.FileNotFoundException: /app/config/{conf}.yml (Permission denied)",
    ],

    "timeout": [
        "context deadline exceeded (Client.Timeout exceeded while awaiting headers)",
        "ReadTimeoutError: HTTPSConnectionPool(host='{host}', port={port}): Read timed out. (read timeout={sec})",
        "Gateway Timeout: upstream '{svc}' failed to respond within {sec}s",
        "ERROR: health check failed for container '{cname}': timeout after {sec}s",
        "com.mysql.jdbc.exceptions.jdbc4.CommunicationsException: Communications link failure\n\tThe last packet sent successfully to the server was {ms} milliseconds ago.",
        "[WARN] Request to {url} timed out after {sec}000ms — retry {n}/{total}",
        "DEADLINE_EXCEEDED: Waited {sec}s for gRPC response from '{svc}'",
        "net/http: request canceled (Client.Timeout exceeded while awaiting headers) [{url}]",
        "TimeoutError: Knex: Timeout acquiring a connection. The pool is probably full. Are you missing a .transacting(trx) call? ({sec}000ms)",
        "ERROR [watchdog] Service '{svc}' has not responded in {sec}s — marking unhealthy",
    ],

    "crash": [
        "Segmentation fault (core dumped) — process {pid} ({proc})",
        "panic: runtime error: invalid memory address or nil pointer dereference\n[signal SIGSEGV: segmentation violation code=0x1 addr=0x0 pc=0x{pc}]",
        "fatal: Caught signal 11 (Segmentation fault). Please inspect crash dump at /tmp/crash-{pid}.dmp",
        "Unhandled exception. System.NullReferenceException: Object reference not set to an instance of an object.\n   at {ns}.{cls}.{method}() in /{file}:line {line}",
        "FATAL: unhandled exception 'RuntimeError' with value 'CUDA out of memory'\nTraceback (most recent call last):\n  File \"{file}\", line {line}, in {func}",
        "java.lang.NullPointerException\n\tat {cls}.{method}({file}.java:{line})\n\tat {cls2}.{method2}({file2}.java:{line2})",
        "Process finished with exit code 139 (interrupted by signal 11: SIGSEGV)",
        "Error: Cannot find module '{mod}'\nRequire stack:\n- /app/{file}.js\n- /app/index.js",
        "SIGSEGV — Address boundary error in {proc} pid {pid}",
        "CrashLoopBackOff: container '{cname}' has restarted {n} times in the last {min} minutes",
    ],
}

# filler values for template placeholders
FILLERS = {
    "step": lambda: random.randint(2, 10),
    "ver":  lambda: f"{random.randint(16,18)}.x",
    "pkg":  lambda: random.choice(["react-dom", "express", "axios", "lodash", "webpack"]),
    "pkgver": lambda: f"{random.randint(1,4)}.{random.randint(0,9)}.{random.randint(0,9)}",
    "path": lambda: random.choice(["src/index.js", "app/main.py", "src/App.tsx", "config/settings.py"]),
    "module": lambda: random.choice(["psycopg2", "cryptography", "uvicorn", "gunicorn", "celery"]),
    "total": lambda: random.randint(8, 15),
    "line": lambda: random.randint(3, 80),
    "instr": lambda: random.choice(["HEALTHCHECK2", "RUNX", "COPYY", "EXPOSE2"]),
    "file": lambda: random.choice(["server.py", "app.js", "main.go", "index.ts", "utils.py"]),
    "flag": lambda: random.choice(["platform2", "mount2", "network-alias"]),
    "img":  lambda: random.choice(["node:18-alpine3.99", "python:3.12-bullseye2", "postgres:16.1-fake"]),
    "pid":  lambda: random.randint(100, 9999),
    "cid":  lambda: ''.join(random.choices('abcdef0123456789', k=12)),
    "vm":   lambda: random.randint(500000, 2000000),
    "rss":  lambda: random.randint(400000, 1500000),
    "pt":   lambda: random.randint(500, 2000),
    "cname":lambda: random.choice(["app_web_1", "api_server_1", "worker_1", "scheduler_1"]),
    "limit":lambda: random.choice([256, 512, 1024, 2048]),
    "used": lambda: lambda limit: limit + random.randint(10, 200),
    "ts":   lambda: f"{random.randint(100000, 999999)}.{random.randint(100000,999999)}",
    "proc": lambda: random.choice(["python3", "node", "java", "go", "ruby"]),
    "score":lambda: random.randint(500, 1000),
    "size": lambda: random.choice([256, 512, 1024]),
    "pages":lambda: random.randint(1000000, 9999999),
    "cls":  lambda: random.choice(["UserService", "OrderController", "PaymentGateway", "AuthManager"]),
    "method":lambda: random.choice(["execute", "process", "handle", "run", "invoke"]),
    "cls2": lambda: random.choice(["RequestDispatcher", "FilterChain", "HttpServlet"]),
    "method2": lambda: random.choice(["doFilter", "service", "doPost"]),
    "file2":lambda: random.choice(["RequestDispatcher", "FilterChain", "HttpServlet"]),
    "ip":   lambda: f"172.{random.randint(17,19)}.0.{random.randint(2,10)}",
    "port": lambda: random.choice([5432, 6379, 27017, 5672, 9092, 3306]),
    "ms":   lambda: random.choice([30000, 60000, 5000, 10000]),
    "code": lambda: random.randint(100, 115),
    "svc":  lambda: random.choice(["auth-service", "payment-api", "user-service", "inventory", "mailer"]),
    "host": lambda: random.choice(["api.stripe.com", "smtp.mailgun.org", "s3.amazonaws.com"]),
    "sec":  lambda: random.choice([5, 10, 30, 60]),
    "url":  lambda: f"http://internal-svc/api/v{random.randint(1,3)}/endpoint",
    "n":    lambda: random.randint(1, 5),
    "pc":   lambda: ''.join(random.choices('abcdef0123456789', k=6)),
    "ns":   lambda: random.choice(["App.Controllers", "App.Services", "App.Repositories"]),
    "func": lambda: random.choice(["main", "run", "execute", "process"]),
    "line2":lambda: random.randint(10, 200),
    "mod":  lambda: random.choice(["../config", "./utils/db", "../models/User"]),
    "min":  lambda: random.randint(2, 30),
    "path2":lambda: random.choice(["uploads", "logs", "tmp", "cache"]),
    "dir":  lambda: random.choice(["app", "data", ".npm", "cache"]),
    "user": lambda: random.choice(["appuser", "node", "python", "runner"]),
    "conf": lambda: random.choice(["nginx.conf", "app.conf", "redis.conf"]),
    "cert": lambda: random.choice(["server", "client", "ca"]),
    "symbol":lambda: random.choice(["MAX_CONNECTIONS", "DB_HOST", "SECRET_KEY"]),
    "symbol2":lambda: random.choice(["__init__", "connect", "execute"]),
}


def fill(template):
    """Fill template placeholders with realistic random values."""
    result = template
    for key, fn in FILLERS.items():
        placeholder = "{" + key + "}"
        if placeholder in result:
            val = fn()
            if callable(val):
                # handle lambdas that need other values (like used/limit)
                val = random.randint(300, 600)
            result = result.replace(placeholder, str(val))
    return result


def make_timestamp(base_dt, offset_seconds):
    dt = base_dt + timedelta(seconds=offset_seconds)
    return dt.strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]


def generate_log_line(category, base_dt, offset):
    ts = make_timestamp(base_dt, offset)
    template = random.choice(TEMPLATES[category])
    msg = fill(template)
    # wrap in realistic log format
    level = "ERROR" if category != "build" else "ERROR"
    return f"{ts} [{level}] {msg}"


def generate_normal_log_line(service, base_dt, offset):
    ts = make_timestamp(base_dt, offset)
    normals = {
        "app": [
            "GET /api/v1/users 200 OK (34ms)",
            "POST /api/v1/orders 201 Created (112ms)",
            "User authentication successful for user_id={uid}",
            "Cache hit ratio: {r}% — serving from Redis",
            "Scheduled job 'cleanup_sessions' completed in {ms}ms",
        ],
        "db": [
            "database system is ready to accept connections",
            "checkpoint complete: wrote {n} buffers ({pct}%)",
            "autovacuum: processing table '{tbl}'",
            "LOG: connection received: host={ip} port={port}",
            "LOG: statement: SELECT 1",
        ],
        "api": [
            "Health check passed — all services reachable",
            "Rate limiter: {n} requests/min from {ip}",
            "JWT token validated for sub={uid}",
            "Response cached for route /api/v1/{endpoint}",
            "Upstream latency p99: {ms}ms",
        ],
    }
    template = random.choice(normals.get(service, normals["app"]))
    msg = fill(template.replace("{uid}", str(random.randint(1000, 9999)))
                        .replace("{r}", str(random.randint(70, 99)))
                        .replace("{n}", str(random.randint(1, 500)))
                        .replace("{pct}", str(round(random.uniform(0.1, 5.0), 1)))
                        .replace("{tbl}", random.choice(["users", "orders", "sessions", "events"]))
                        .replace("{endpoint}", random.choice(["users", "orders", "products"]))
                        .replace("{ms}", str(random.randint(1, 500))))
    return f"{ts} [INFO] {msg}"


# ──────────────────────────────────────────────
# GENERATE TRAINING CSV
# ──────────────────────────────────────────────

def generate_training_csv(path="data/training_logs.csv", n_per_class=120):
    os.makedirs("data", exist_ok=True)
    rows = []
    base_dt = datetime(2024, 6, 1, 10, 0, 0)
    offset = 0

    for label, templates in TEMPLATES.items():
        for _ in range(n_per_class):
            template = random.choice(templates)
            msg = fill(template)
            rows.append({"log_message": msg, "label": label})
            offset += random.randint(1, 60)

    # shuffle
    random.shuffle(rows)

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["log_message", "label"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"[OK] Generated {len(rows)} training samples → {path}")
    from collections import Counter
    counts = Counter(r["label"] for r in rows)
    for lbl, cnt in sorted(counts.items()):
        print(f"     {lbl:12s}: {cnt} samples")


# ──────────────────────────────────────────────
# GENERATE REALISTIC SERVICE LOG FILES
# ──────────────────────────────────────────────

def generate_service_logs(scenario="db_cascade"):
    """
    Generates a realistic multi-container failure scenario.
    Scenarios: db_cascade, memory_leak, build_failure, permission_error
    """
    os.makedirs("data", exist_ok=True)
    base_dt = datetime(2024, 6, 15, 14, 30, 0)

    scenarios = {
        "db_cascade": {
            "db":  (["dependency"] * 8 + ["timeout"] * 4),
            "app": (["timeout"] * 6 + ["crash"] * 3),
            "api": (["timeout"] * 5 + ["dependency"] * 3),
        },
        "memory_leak": {
            "app": (["memory"] * 10 + ["crash"] * 5),
            "db":  (["timeout"] * 3),
            "api": (["timeout"] * 4 + ["crash"] * 2),
        },
        "build_failure": {
            "app": (["build"] * 10),
            "db":  ([]),
            "api": (["build"] * 5),
        },
        "permission_error": {
            "app": (["permission"] * 6 + ["crash"] * 3),
            "db":  (["permission"] * 4),
            "api": (["permission"] * 3 + ["crash"] * 2),
        },
    }

    chosen = scenarios.get(scenario, scenarios["db_cascade"])
    service_files = {"db": "data/logs_db.txt", "app": "data/logs_app.txt", "api": "data/logs_api.txt"}

    for svc, categories in chosen.items():
        lines = []
        offset = 0
        # intersperse normal logs
        total = len(categories) + random.randint(30, 60)
        cat_idx = 0
        for i in range(total):
            if cat_idx < len(categories) and random.random() < 0.4:
                lines.append(generate_log_line(categories[cat_idx], base_dt, offset))
                cat_idx += 1
            else:
                lines.append(generate_normal_log_line(svc, base_dt, offset))
            offset += random.randint(1, 30)

        # flush remaining error logs at end
        while cat_idx < len(categories):
            lines.append(generate_log_line(categories[cat_idx], base_dt, offset))
            cat_idx += 1
            offset += random.randint(1, 10)

        with open(service_files[svc], "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

        print(f"[OK] {svc:4s} logs → {service_files[svc]}  ({len(lines)} lines, scenario: {scenario})")


if __name__ == "__main__":
    print("=== Generating Training Data ===")
    generate_training_csv()
    print("\n=== Generating Service Log Files (db_cascade scenario) ===")
    generate_service_logs(scenario="db_cascade")
    print("\nDone. Now run: python ai_engine/train_model.py")