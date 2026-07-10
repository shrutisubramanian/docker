"""
root_cause.py — Evidence-based causal root cause analysis engine.
"""

import re
from collections import defaultdict, Counter


# ──────────────────────────────────────────────
# SIGNAL EXTRACTION
# ──────────────────────────────────────────────

def extract_signals(log: str, source: str) -> dict:
    log_l = log.lower()
    signals = {
        "source": source,
        "original": log,
        "signals": [],
        "entities": {},
    }

    if "connection refused" in log_l:
        signals["signals"].append("conn_refused")

    if "timeout" in log_l or "timed out" in log_l:
        signals["signals"].append("timeout")

    if "out of memory" in log_l or "exit code 137" in log_l:
        signals["signals"].append("oom")

    if "permission denied" in log_l:
        signals["signals"].append("permission_denied")

    if "segfault" in log_l or "exception" in log_l:
        signals["signals"].append("crash")

    return signals


# ──────────────────────────────────────────────
# HYPOTHESES
# ──────────────────────────────────────────────

HYPOTHESES = {
    "cascade_from_db": {
        "display": "Cascading Failure — Database Down → Services Timing Out",
        "signals": {"conn_refused": 8, "timeout": 6},
    },
    "memory_exhaustion": {
        "display": "Memory Exhaustion / OOM Kill",
        "signals": {"oom": 10},
    },
    "permission_issue": {
        "display": "Permission Issue",
        "signals": {"permission_denied": 10},
    },
    "application_crash": {
        "display": "Application Crash",
        "signals": {"crash": 10},
    },
}


# ──────────────────────────────────────────────
# DYNAMIC EXPLANATION
# ──────────────────────────────────────────────

def generate_dynamic_explanation(best_key, container_signal_counts):
    if best_key == "cascade_from_db":
        affected = []
        for container, signals in container_signal_counts.items():
            if signals.get("timeout", 0) > 0:
                affected.append(container.upper())

        if affected:
            return f"Database failure triggered timeouts in {', '.join(affected)} containers"

    if best_key == "memory_exhaustion":
        return "Containers are being killed due to excessive memory usage (OOM)"

    if best_key == "application_crash":
        return "Application is crashing due to runtime exceptions or segmentation faults"

    return None


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────

def find_root_cause(all_logs, sources):

    all_signal_objs = [extract_signals(log, src) for log, src in zip(all_logs, sources)]

    global_signal_counts = Counter()
    container_signal_counts = defaultdict(Counter)
    containers_seen = set()

    for obj in all_signal_objs:
        src = obj["source"]
        containers_seen.add(src)

        for sig in obj["signals"]:
            global_signal_counts[sig] += 1
            container_signal_counts[src][sig] += 1

    # ──────────────────────────────────────────
    # SCORING
    # ──────────────────────────────────────────

    scores = {}

    for hyp_key, hyp in HYPOTHESES.items():
        score = 0
        for sig, weight in hyp["signals"].items():
            score += global_signal_counts.get(sig, 0) * weight
        scores[hyp_key] = score

    if not scores or max(scores.values()) == 0:
        return "unknown", {
            "root_cause": "Unknown",
            "confidence": 0,
            "why": "No clear pattern found",
            "fix_steps": ["Check logs manually"],
            "affected_containers": list(containers_seen),
            "evidence": [],
        }

    best_key = max(scores, key=scores.get)

    # ──────────────────────────────────────────
    # IMPROVED CONFIDENCE
    # ──────────────────────────────────────────

    sorted_scores = sorted(scores.values(), reverse=True)

    top_score = sorted_scores[0]
    second_score = sorted_scores[1] if len(sorted_scores) > 1 else 0

    confidence = top_score / (top_score + second_score + 1)
    confidence = round(confidence * 100, 1)

    # ──────────────────────────────────────────
    # DYNAMIC EXPLANATION
    # ──────────────────────────────────────────

    dynamic = generate_dynamic_explanation(best_key, container_signal_counts)

    # ──────────────────────────────────────────
    # EVIDENCE GENERATION (NEW 🔥)
    # ──────────────────────────────────────────

    evidence_logs = []

    for obj in all_signal_objs:
        matching = set(obj["signals"]) & set(HYPOTHESES[best_key]["signals"].keys())
        if matching:
            evidence_logs.append({
                "container": obj["source"],
                "log": obj["original"][:120],
                "matched_signals": list(matching),
            })

   
    # ensure at least one DB log if available
    db_logs = [e for e in evidence_logs if e["container"] == "db"]
    non_db_logs = [e for e in evidence_logs if e["container"] != "db"]

    final_evidence = db_logs[:1] + non_db_logs[:2]
    evidence_logs = final_evidence[:3]

    # ──────────────────────────────────────────
    # FINAL OUTPUT
    # ──────────────────────────────────────────

    return best_key, {
        "root_cause": HYPOTHESES[best_key]["display"],
        "confidence": confidence,
        "why": dynamic if dynamic else "Failure detected based on log patterns",
        "fix_steps": [
            "Check if database container is running (docker ps -a)",
            "Inspect DB logs (docker logs <db_container>)",
            "Ensure DB port is accessible and not blocked",
            "Add retry logic in application for DB connections",
            "Use depends_on with health checks in docker-compose",
        ],
        "affected_containers": list(containers_seen),
        "evidence": evidence_logs,
    }