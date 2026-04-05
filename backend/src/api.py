import os
import pickle
import docker
import json
import subprocess
import re
import numpy as np
from scipy.sparse import hstack, csr_matrix
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from typing import List

# Internal imports from your repo structure
from backend.src.reasoning.models import ReasoningInput, IncidentReport
from backend.src.pipeline.orchestrator import process_reasoning_alert
from backend.src.logging.incident_logger import get_all_incidents

app = FastAPI(
    title="AI Autonomous Recovery API",
    version="3.5.0"
)

# CORS Policy to allow frontend to communicate with Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = "ai_engine/model/model.pkl"

# --- Feature Extraction Constants (Synced with train_model.py) ---
LOG_LEVELS = ["FATAL", "ERROR", "WARN", "WARNING", "INFO", "DEBUG", "CRITICAL"]
CATEGORY_SIGNALS = {
    "build":      ["dockerfile", "build", "npm", "pip", "apt", "copy", "requirements", "compile", "gradle", "maven", "registry"],
    "memory":     ["memory", "heap", "oom", "killed", "sigkill", "allocat", "swap", "gc overhead", "out of memory"],
    "dependency": ["connection refused", "econnrefused", "unreachable", "downstream", "upstream", "pool", "broker", "amqp", "grpc", "kafka"],
    "permission": ["permission denied", "eacces", "unauthorized", "operation not permitted", "access denied", "sudoers", "chmod", "chown"],
    "timeout":    ["timeout", "timed out", "deadline exceeded", "gateway timeout", "no response", "read timeout", "504"],
    "crash":      ["segfault", "sigsegv", "null pointer", "nullpointerexception", "panic", "core dump", "exit code 139", "crashloopbackoff", "unhandled"],
}

def clean_text(log):
    log = log.lower()
    log = re.sub(r'\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2}[,.\d]*', '', log)
    log = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', 'IPADDR', log) 
    log = re.sub(r'\b\d{4,}\b', 'NUMVAL', log)
    log = re.sub(r'[a-f0-9]{8,}', 'HEXVAL', log)
    log = re.sub(r'[\[\]()]', ' ', log)
    log = re.sub(r'\s+', ' ', log).strip()
    return log

def extract_structural_features(logs):
    features = []
    for log in logs:
        log_lower = log.lower()
        row = []
        for level in LOG_LEVELS:
            row.append(1 if level.lower() in log_lower else 0)
        row.append(1 if any(x in log for x in ["\n\tat ", "Traceback", "File \"", "  at "]) else 0)
        row.append(1 if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', log) else 0)
        row.append(1 if re.search(r':\d{4,5}', log) else 0)
        row.append(1 if re.search(r'(/[a-zA-Z0-9._-]+){2,}', log) else 0)
        row.append(1 if re.search(r'exit(ed)?\s+(code\s+)?\d+', log_lower) else 0)
        row.append(1 if re.search(r'\d+\s*(mb|kb|gb|bytes)', log_lower) else 0)
        row.append(1 if re.search(r'\d+\s*(ms|milliseconds|seconds|timeout)', log_lower) else 0)
        row.append(min(log.count('\n'), 10))
        for cat, keywords in CATEGORY_SIGNALS.items():
            score = sum(1 for kw in keywords if kw in log_lower)
            row.append(score)
        features.append(row)
    return np.array(features, dtype=np.float32)

def get_hybrid_diagnosis(container):
    """
    Upgraded: Uses the new Structural + TF-IDF model bundle for diagnosis.
    """
    try:
        # 1. State/Resource Checks
        if container.status != "running":
            return "RESTART_CONTAINER", 100.0, "Container stopped unexpectedly."

        stats = container.stats(stream=False)
        cpu_stats = stats.get('cpu_stats', {})
        precpu_stats = stats.get('precpu_stats', {})
        cpu_delta = cpu_stats.get('cpu_usage', {}).get('total_usage', 0) - precpu_stats.get('cpu_usage', {}).get('total_usage', 0)
        system_delta = cpu_stats.get('system_cpu_usage', 0) - precpu_stats.get('system_cpu_usage', 0)
        
        if system_delta > 0 and cpu_delta > 0:
            cpu_percent = (cpu_delta / system_delta) * 100.0
            if cpu_percent > 85.0:
                return "APPLY_CPU_QUOTA", round(cpu_percent, 2), f"CPU Critical: {cpu_percent}%"

        # 2. Advanced Log Classification
        raw_logs = container.logs(tail=20).decode("utf-8").strip()
        if not raw_logs:
            return "RESTART_CONTAINER", 50.0, "No logs available"

        if not os.path.exists(MODEL_PATH):
            return "RESTART_CONTAINER", 0.0, "AI Model pkl missing"

        with open(MODEL_PATH, "rb") as f:
            bundle = pickle.load(f)
        
        model = bundle["model"]
        tfidf = bundle["tfidf"]
        scaler = bundle["scaler"]

        # Prepare features
        clean_logs = [clean_text(raw_logs)]
        X_tfidf = tfidf.transform(clean_logs)
        X_struct = extract_structural_features([raw_logs])
        X_struct_scaled = scaler.transform(X_struct)
        X_combined = hstack([X_tfidf, csr_matrix(X_struct_scaled)])

        # Predict
        predicted_label = model.predict(X_combined)[0]
        confidence = max(model.predict_proba(X_combined)[0]) * 100
        
        return predicted_label, round(confidence, 2), raw_logs

    except Exception as e:
        return "RESTART_CONTAINER", 50.0, f"Diag Error: {str(e)}"

@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

@app.get("/api/v1/containers")
def get_containers():
    try:
        result = subprocess.run(
            ["docker", "stats", "--no-stream", "--format", "{{json .}}"],
            capture_output=True, text=True, check=False
        )
        if result.returncode != 0:
            return {"containers": []}

        containers_list = []
        for line in result.stdout.strip().split("\n"):
            if not line: continue
            data = json.loads(line)
            containers_list.append({
                "name": data.get("Name"),
                "status": "Running",
                "cpu": data.get("CPUPerc"),
                "memory": data.get("MemUsage", "").split(" / ")[0],
                "disk": data.get("BlockIO", "0B / 0B").split(" / ")[0],
                "net": data.get("NetIO", "0B / 0B").split(" / ")[0]
            })
        return {"containers": containers_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/incidents")
def list_incidents():
    return get_all_incidents()

@app.post("/api/v1/trigger_pipeline")
def trigger_pipeline(container_name: str):
    client = docker.from_env()
    try:
        container = client.containers.get(container_name)
        suggested_action, confidence, diag_log = get_hybrid_diagnosis(container)

        alert = ReasoningInput(
            container=container_name,
            error_type=suggested_action,
            severity="CRITICAL",
            suggested_fix=suggested_action,
            confidence=confidence,
            root_cause="Upgraded Structural-SVM Classifier",
            original_log=diag_log
        )
        
        report = process_reasoning_alert(alert)
        return {"status": "recovered", "incidents": [report]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/simulate_failure")
def simulate_failure(failure_type: str, container: str):
    """Upgraded real-time Docker simulations for all AI categories."""
    try:
        client = docker.from_env()
        c = client.containers.get(container)
        
        # --- Native Failures ---
        if failure_type == "crash":
            c.stop(timeout=0)
        elif failure_type == "cpu_spike":
            c.exec_run("sh -c 'cat /dev/zero > /dev/null &'", detach=True)
        elif failure_type == "memory_spike":
            c.exec_run("sh -c 'tail /dev/zero &'", detach=True)
        elif failure_type == "fork_bomb":
            c.exec_run("sh -c ':(){ :|:& };:'", detach=True)
        
        # --- Upgraded Real-time Attacks ---
        elif failure_type == "dependency":
            # Simulate DB/Service connection refusal by blocking port
            c.exec_run("apt-get update && apt-get install -y iptables", detach=True)
            c.exec_run("iptables -A OUTPUT -p tcp --dport 27017 -j REJECT", detach=True)
            c.exec_run("sh -c 'echo \"[ERROR] connect ECONNREFUSED 127.0.0.1:27017\" >> /proc/1/fd/1'", detach=True)
            
        elif failure_type in ["permission", "permissions"]:
            # Change permissions of app directory to trigger PermissionError
            c.exec_run("chmod 000 /var/lib/apt", detach=True) 
            c.exec_run("sh -c 'echo \"[ERROR] PermissionError: [Errno 13] Permission denied: /data/config\" >> /proc/1/fd/1'", detach=True)

        elif failure_type in ["timeout", "latency"]:
            # Add severe network latency
            c.exec_run("tc qdisc add dev eth0 root netem delay 5000ms", detach=True)
            c.exec_run("sh -c 'echo \"[ERROR] Gateway Timeout: upstream failed to respond within 30s\" >> /proc/1/fd/1'", detach=True)

        elif failure_type == "build":
            # Simulate a corruption that causes build/runtime failures
            c.exec_run("rm -rf /usr/local/bin/node", detach=True)
            c.exec_run("sh -c 'echo \"[ERROR] Step 5/12 : RUN npm install -> npm ERR! code ERESOLVE\" >> /proc/1/fd/1'", detach=True)

        elif failure_type in ["leak", "memory_spike"]:
            # Memory leak / saturation
            c.exec_run("sh -c 'tail /dev/zero &'", detach=True)
            c.exec_run("sh -c 'echo \"[ERROR] Fatal Error: Recovery periodic heap exceeded. Potential memory leak detected.\" >> /proc/1/fd/1'", detach=True)

        elif failure_type == "disk_full":
            # Simulate disk space exhaustion
            c.exec_run("sh -c 'dd if=/dev/zero of=/tmp/bloat bs=1M count=1024'", detach=True)
            c.exec_run("sh -c 'echo \"[ERROR] ENOSPC: no space left on device, write /tmp/session.json\" >> /proc/1/fd/1'", detach=True)
            
        return {"status": "success", "message": f"Real-time {failure_type} triggered on {container}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))