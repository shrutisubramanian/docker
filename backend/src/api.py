import os
import pickle
import docker
import json
import subprocess
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
    version="3.0.0"
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

def get_hybrid_diagnosis(container):
    """
    Combines Docker Stats, Container State, and Log Analysis.
    Updated to return the specific Action predicted by the AI.
    """
    try:
        # 1. Check Container State first (Immediate Action: Restart)
        if container.status != "running":
            return "RESTART_CONTAINER", 100.0, "Container is not running."

        # 2. Check Resource Metrics (Immediate Action: Throttling/Restart)
        stats = container.stats(stream=False)
        cpu_stats = stats.get('cpu_stats', {})
        precpu_stats = stats.get('precpu_stats', {})
        
        cpu_delta = cpu_stats.get('cpu_usage', {}).get('total_usage', 0) - precpu_stats.get('cpu_usage', {}).get('total_usage', 0)
        system_delta = cpu_stats.get('system_cpu_usage', 0) - precpu_stats.get('system_cpu_usage', 0)
        
        if system_delta > 0 and cpu_delta > 0:
            cpu_percent = (cpu_delta / system_delta) * 100.0
            if cpu_percent > 80.0:
                # Direct Answer: If CPU is spiking, use the specific throttle action
                return "APPLY_CPU_QUOTA", round(cpu_percent, 2), f"CPU Spike detected at {cpu_percent}%"

        # 3. Fallback to SVM Log Analysis for specialized fixes
        raw_logs = container.logs(tail=15).decode("utf-8").strip()
        
        if not os.path.exists(MODEL_PATH):
            return "RESTART_CONTAINER", 0.0, raw_logs or "No logs available"
        
        with open(MODEL_PATH, "rb") as f:
            # Load the tuple (model, vectorizer) as saved in train_model.py
            model, vectorizer = pickle.load(f)
        
        if not raw_logs:
            return "RESTART_CONTAINER", 50.0, "No logs, but container state abnormal."

        # AI Prediction: The model now directly predicts the 'action_label'
        X_vec = vectorizer.transform([raw_logs])
        suggested_action = model.predict(X_vec)[0]
        confidence = max(model.predict_proba(X_vec)[0]) * 100
        
        return suggested_action, round(confidence, 2), raw_logs

    except Exception as e:
        return "RESTART_CONTAINER", 50.0, f"Diagnostic error: {str(e)}"

@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

@app.get("/api/v1/containers")
def get_containers():
    """Fetches real-time container stats including Disk and Network."""
    try:
        result = subprocess.run(
            ["docker", "stats", "--no-stream", "--format", "{{json .}}"],
            capture_output=True, text=True, check=False, timeout=5
        )
        if result.returncode != 0:
            return {"containers": [], "error": "Docker stats command failed."}

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
    except subprocess.TimeoutExpired:
        return {"containers": [], "error": "Docker stats collection timed out (system under heavy load)."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/incidents")
def list_incidents():
    return get_all_incidents()

@app.post("/api/v1/trigger_pipeline")
def trigger_pipeline(container_name: str):
    """
    Triggers the autonomous pipeline. 
    The 'error_type' is now the 'suggested_action' provided by AI.
    """
    client = docker.from_env()
    try:
        container = client.containers.get(container_name)
        
        # 1. Get the Direct-Action diagnosis
        suggested_action, confidence, diagnostic_log = get_hybrid_diagnosis(container)

        # 2. Log metadata for the reasoning alert
        alert = ReasoningInput(
            container=container_name,
            error_type="AI_AUTONOMOUS_FIX",
            severity="CRITICAL",
            suggested_fix=suggested_action, # Direct Action from AI
            confidence=confidence,
            root_cause="Multi-Label SVM Direct-Action Diagnosis",
            original_log=diagnostic_log
        )
        
        # 3. Process the alert (The orchestrator will now execute 'suggested_action')
        report = process_reasoning_alert(alert)
        return {"status": "issues_detected_and_recovered", "incidents": [report]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline Error: {str(e)}")

@app.post("/api/v1/simulate_failure")
def simulate_failure(failure_type: str, container: str):
    """Simulates various attacks to test SVM log classification."""
    try:
        client = docker.from_env()
        c = client.containers.get(container)
        
        if failure_type == "crash":
            c.stop(timeout=0)
        elif failure_type == "cpu_spike":
            c.exec_run("sh -c 'cat /dev/zero > /dev/null &'", detach=True)
        elif failure_type == "memory_spike":
            c.exec_run("sh -c 'tail /dev/zero &'", detach=True)
        elif failure_type == "fork_bomb":
            c.exec_run("sh -c ':(){ :|:& };:'", detach=True)
        elif failure_type == "network_delay":
            c.exec_run("tc qdisc add dev eth0 root netem delay 270ms", detach=True)
        elif failure_type == "disk_exhaust":
            c.exec_run("dd if=/dev/zero of=/tmp/big_file bs=1M count=1024", detach=True)
            
        return {"status": "success", "message": f"Simulated {failure_type} on {container}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))