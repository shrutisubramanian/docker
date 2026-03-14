"""
integrate.py — connects Member 2 (Shubhashri's LogPipeline)
to Member 3's AI analyzer (Shruti).

Run this file for the full demo:
  Docker container → log collection → AI analysis → results
"""

import sys
import os

# Add project root to path so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from log_pipeline import LogPipeline
from ai_engine.analyzer import analyze_logs, print_analysis, load_model
from ai_engine.anomaly_detector import run_anomaly_detection


def run_full_pipeline(container_name: str, duration: int = 30, errors_only: bool = False):
    """
    Full pipeline: collect logs → AI analysis → print results

    Args:
        container_name: Docker container to monitor
        duration:       How long to collect logs (seconds)
        errors_only:    If True, only analyse ERROR/CRITICAL logs
    """

    # ── Step 1: Collect logs (Shubhashri's module) ──────────────────────────
    print(f"\n[STEP 1] Starting log collection from container: {container_name}")
    pipeline = LogPipeline(container_name)
    pipeline.start_collecting(duration=duration)
    pipeline.print_summary()

    # ── Step 2: Get logs for AI analysis ────────────────────────────────────
    if errors_only:
        print("\n[STEP 2] Fetching ERROR/CRITICAL logs for analysis...")
        logs_to_analyse = pipeline.get_all_errors()
    else:
        print("\n[STEP 2] Fetching all logs for analysis...")
        logs_to_analyse = pipeline.get_all_logs()

    if not logs_to_analyse:
        print("[WARN] No logs to analyse. Container may not have produced output.")
        return

    print(f"         {len(logs_to_analyse)} log entries ready for AI analysis")

    # ── Step 3: AI analysis (Shruti's module) ────────────────────────────────
    print("\n[STEP 3] Running AI analysis...")
    model, vectorizer = load_model()
    results = analyze_logs(logs_to_analyse, model=model, vectorizer=vectorizer)

    # ── Step 4: Print results ────────────────────────────────────────────────
    print_analysis(results)

    # ── Step 5: Return results for Member 4 (Subhashini - Action Executor) ──
    # Member 4 can call this function and use the returned list
    # Each result has: container, severity, error_type, confidence, suggested_fix
    return results


if __name__ == "__main__":
    # Change container name to match whatever your Docker teammate sets up
    CONTAINER_NAME = "welcome-to-docker"

    results = run_full_pipeline(
        container_name=CONTAINER_NAME,
        duration=30,
        errors_only=False,   # set True to only analyse errors
    )