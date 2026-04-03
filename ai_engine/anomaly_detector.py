"""
anomaly_detector.py — Upgraded AI/ML Pipeline

Pipeline:
  1. Load logs from data/logs_*.txt
  2. Isolation Forest  → flag anomalous lines
  3. SVM Classifier    → label each anomaly (build/memory/crash/etc.)
  4. Root Cause Engine → causal analysis across containers
  5. Print full diagnostic report + save to reports/

Run: python ai_engine/anomaly_detector.py
"""

import os
import sys
import json
import pickle
import re
import numpy as np
from datetime import datetime
from collections import Counter
from scipy.sparse import hstack, csr_matrix
from sklearn.ensemble import IsolationForest
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler

# add parent dir so we can import sibling modules
sys.path.insert(0, os.path.dirname(__file__))
from root_cause import find_root_cause

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

MODEL_PATH = "ai_engine/model/model.pkl"
REPORTS_DIR = "reports"

FILES = {
    "app": "data/logs_app.txt",
    "db":  "data/logs_db.txt",
    "api": "data/logs_api.txt",
}

# ──────────────────────────────────────────────
# Feature engineering (must match train_model.py)
# ──────────────────────────────────────────────

CATEGORY_SIGNALS = {
    "build":      ["dockerfile", "build", "npm", "pip", "apt", "copy", "requirements", "compile", "gradle", "maven", "registry"],
    "memory":     ["memory", "heap", "oom", "killed", "sigkill", "allocat", "swap", "gc overhead", "out of memory"],
    "dependency": ["connection refused", "econnrefused", "unreachable", "downstream", "upstream", "pool", "broker", "amqp", "grpc", "kafka"],
    "permission": ["permission denied", "eacces", "unauthorized", "operation not permitted", "access denied", "sudoers", "chmod", "chown"],
    "timeout":    ["timeout", "timed out", "deadline exceeded", "gateway timeout", "no response", "read timeout", "504"],
    "crash":      ["segfault", "sigsegv", "null pointer", "nullpointerexception", "panic", "core dump", "exit code 139", "crashloopbackoff", "unhandled"],
}

LOG_LEVELS = ["FATAL", "ERROR", "WARN", "WARNING", "INFO", "DEBUG", "CRITICAL"]


def clean_text(log):
    log = log.lower()
    log = re.sub(r'\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2}[,.\d]*', '', log)
    log = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', 'IPADDR', log)
    log = re.sub(r'\b\d{4,}\b', 'NUMVAL', log)
    log = re.sub(r'[a-f0-9]{8,}', 'HEXVAL', log)
    log = re.sub(r'[\[\]()]', ' ', log)
    log = re.sub(r'\s+', ' ', log).strip()
    return log

def is_noise(log):
    log = log.lower()
    return any(x in log for x in [
        "cache hit",
        "rate limiter",
        "ready to accept connections",
        "completed in",
        "health check passed"
    ])


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


# ──────────────────────────────────────────────
# LOAD
# ──────────────────────────────────────────────

def load_model():
    if not os.path.exists(MODEL_PATH):
        print(f"[ERROR] Model not found at {MODEL_PATH}. Run train_model.py first.", file=sys.stderr)
        sys.exit(1)
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)  # returns dict: {model, tfidf, scaler}


def load_logs():
    all_logs, sources = [], []
    for service, path in FILES.items():
        if not os.path.exists(path):
            print(f"[WARN] Log file missing, skipping: {path}", file=sys.stderr)
            continue
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = [line.strip() for line in f if line.strip()]
        if not lines:
            continue
        all_logs.extend(lines)
        sources.extend([service] * len(lines))
    return all_logs, sources


# ──────────────────────────────────────────────
# ISOLATION FOREST
# ──────────────────────────────────────────────

def run_isolation_forest(logs, contamination=0.25):
    """
    Use IF with structural features + TF-IDF for better anomaly detection.
    contamination = expected proportion of anomalies.
    """
    X_clean = [clean_text(log) for log in logs]

    tfidf_if = TfidfVectorizer(ngram_range=(1, 2), max_features=3000, sublinear_tf=True)
    X_tfidf  = tfidf_if.fit_transform(X_clean)

    X_struct = extract_structural_features(logs)
    X_combined = hstack([X_tfidf, csr_matrix(X_struct)])

    model = IsolationForest(contamination=contamination, random_state=42, n_estimators=150)
    model.fit(X_combined)
    predictions = model.predict(X_combined)
    scores      = model.decision_function(X_combined)  # lower = more anomalous

    return predictions, scores


# ──────────────────────────────────────────────
# SVM CLASSIFICATION
# ──────────────────────────────────────────────

def classify_anomalies(logs, bundle):
    model   = bundle["model"]
    tfidf   = bundle["tfidf"]
    scaler  = bundle["scaler"]

    X_clean  = [clean_text(log) for log in logs]
    X_tfidf  = tfidf.transform(X_clean)
    X_struct = extract_structural_features(logs)
    X_struct_scaled = scaler.transform(X_struct)
    X_combined = hstack([X_tfidf, csr_matrix(X_struct_scaled)])

    labels      = model.predict(X_combined)
    confidences = model.predict_proba(X_combined).max(axis=1)
    return labels, confidences


# ──────────────────────────────────────────────
# REPORT GENERATION
# ──────────────────────────────────────────────

def _bar(pct, width=12):
    filled = int((pct / 100) * width)
    return "█" * filled + "░" * (width - filled)


def print_report(all_logs, sources, predictions, anomaly_scores, bundle):
    """Print full diagnostic report to stdout and return structured data."""

    W = 68  # width
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("\n" + "═" * W)
    print("  DOCKER PRODUCTION FAILURE DIAGNOSTIC REPORT")
    print(f"  Generated: {now}")
    print("═" * W)

    # ── Isolation Forest results ────────────────────────────────────
    anomaly_indices = [i for i, p in enumerate(predictions) if p == -1]
    normal_count    = sum(1 for p in predictions if p == 1)

    print(f"\n  Scanned   : {len(all_logs)} log lines across {len(set(sources))} containers")
    print(f"  Anomalies : {len(anomaly_indices)} flagged by Isolation Forest")
    print(f"  Normal    : {normal_count} lines")

    if not anomaly_indices:
        print("\n  No anomalies detected. System appears healthy.")
        print("═" * W)
        return [], {}

    anomalous_logs    = [all_logs[i] for i in anomaly_indices]
    anomalous_sources = [sources[i] for i in anomaly_indices]

    # ── SVM Classification ─────────────────────────────────────────
    labels, confidences = classify_anomalies(anomalous_logs, bundle)

    print(f"\n{'─'*W}")
    print("  INDIVIDUAL ANOMALIES")
    print(f"{'─'*W}")

    results = []
    for log, src, label, conf in zip(anomalous_logs, anomalous_sources, labels, confidences):
        conf_pct = round(float(conf) * 100, 1)
        # truncate long logs for display
        display_log = (log[:120] + "...") if len(log) > 120 else log
        print(f"\n  Container  : {src.upper()}")
        print(f"  Log        : {display_log}")
        print(f"  Error Type : {label.upper():<12}  {_bar(conf_pct)} {conf_pct}%")

        results.append({
            "container":    src,
            "original_log": log,
            "error_type":   label,
            "confidence":   conf_pct,
        })

    # ── Root Cause Analysis ────────────────────────────────────────
    root_key, diagnosis = find_root_cause(anomalous_logs, anomalous_sources)

    print(f"\n{'═'*W}")
    print("  ROOT CAUSE ANALYSIS")
    print(f"{'═'*W}")
    print(f"\n  ROOT CAUSE  : {diagnosis['root_cause']}")
    print(f"  CONFIDENCE  : {_bar(diagnosis['confidence'])} {diagnosis['confidence']}%")
    print(f"\n  WHY THIS HAPPENED")
    print(f"  {'─'*60}")
    # word-wrap the explanation
    words = diagnosis['why'].split()
    line, lines = [], []
    for w in words:
        if sum(len(x)+1 for x in line) + len(w) > 60:
            lines.append(" ".join(line))
            line = [w]
        else:
            line.append(w)
    if line:
        lines.append(" ".join(line))
    for l in lines:
        print(f"  {l}")

    print(f"\n  AFFECTED CONTAINERS : {', '.join(c.upper() for c in diagnosis['affected_containers'])}")

    print(f"\n  EVIDENCE (top matching log lines)")
    print(f"  {'─'*60}")
    for ev in diagnosis['evidence'][:3]:
        print(f"  [{ev['container'].upper()}] {ev['log'][:100]}")
        print(f"          Signals: {', '.join(ev['matched_signals'])}")

    if diagnosis.get("entities"):
        print(f"\n  DETECTED ENTITIES")
        for k, v in diagnosis["entities"].items():
            print(f"    {k}: {v}")

    print(f"\n  FIX STEPS")
    print(f"  {'─'*60}")
    for i, step in enumerate(diagnosis["fix_steps"], 1):
        # word wrap fix steps
        wrapped = _wrap(step, width=58, indent="     ")
        print(f"  {i}. {wrapped}")

    if diagnosis.get("secondary_hypothesis"):
        sec = diagnosis["secondary_hypothesis"]
        print(f"\n  Also consider: {sec['display']}")


    print(f"\n{'─'*68}")
    print("  FAILURE TIMELINE (first 10 events)")
    print(f"{'─'*68}")

    for log in all_logs[:10]:
     print(f"  → {log[:100]}")

    # ── Summary ────────────────────────────────────────────────────
    type_counts = Counter(r["error_type"] for r in results)
    avg_conf    = sum(r["confidence"] for r in results) / len(results)

    print(f"\n{'─'*W}")
    print("  SUMMARY")
    print(f"{'─'*W}")
    print(f"  Total anomalies : {len(results)}")
    print(f"  Normal logs     : {normal_count}")
    print(f"  Avg confidence  : {avg_conf:.1f}%")
    print(f"  Error breakdown :")
    for etype, count in type_counts.most_common():
        bar = _bar((count / len(results)) * 100, width=8)
        print(f"    {etype:<12}  {bar}  {count}")
    print("═" * W)

    container_stats = {
        "total": len(all_logs),
        "normal": normal_count,
        "anomalies": len(results),
    }

    return results, diagnosis, container_stats


def _wrap(text, width=58, indent=""):
    words = text.split()
    lines, line = [], []
    first = True
    for w in words:
        if sum(len(x)+1 for x in line) + len(w) > width:
            lines.append(("" if first else indent) + " ".join(line))
            line = [w]
            first = False
        else:
            line.append(w)
    if line:
        lines.append(("" if first else indent) + " ".join(line))
    return ("\n" + indent).join(lines)


# ──────────────────────────────────────────────
# SAVE REPORT
# ──────────────────────────────────────────────

def save_report(results, diagnosis, container_stats):
    os.makedirs(REPORTS_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(REPORTS_DIR, f"report_{ts}.json")

    report = {
        "generated_at": datetime.now().isoformat(),
        "summary":      container_stats,
        "root_cause":   diagnosis,
        "anomalies":    results,
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n  Report saved → {path}")


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────

def run():
    bundle = load_model()
    all_logs, sources = load_logs()

    if not all_logs:
        print("[ERROR] No logs found.")
        return

    # 🔥 Noise Filtering
    filtered = [(l, s) for l, s in zip(all_logs, sources) if not is_noise(l)]

    if not filtered:
        print("[ERROR] All logs filtered as noise.")
        return

    all_logs, sources = zip(*filtered)
    all_logs = list(all_logs)
    sources = list(sources)

    predictions, anomaly_scores = run_isolation_forest(all_logs)

    results, diagnosis, stats = print_report(
        all_logs, sources, predictions, anomaly_scores, bundle
    )

    if results:
        save_report(results, diagnosis, stats)

if __name__ == "__main__":
    run()