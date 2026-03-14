"""
anomaly_detector.py — AI/ML Pipeline (Member 3 - Shruti)

Two-model pipeline:
  Step 1: Isolation Forest (unsupervised) — detects which logs are anomalous
  Step 2: SVM Classifier  (supervised)   — labels what type of error it is
  Step 3: Root cause + suggested fix
  Step 4: Auto-generates a report in reports/

Run:
    python ai_engine/anomaly_detector.py
"""

import os
import sys
import pickle
from sklearn.ensemble import IsolationForest
from sklearn.feature_extraction.text import TfidfVectorizer
from root_cause import find_root_cause
from generate_report import generate_report

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

MODEL_PATH = "ai_engine/model/model.pkl"

FILES = {
    "app": "data/logs_app.txt",
    "db":  "data/logs_db.txt",
    "api": "data/logs_api.txt",
}


def load_svm():
    if not os.path.exists(MODEL_PATH):
        print(f"[ERROR] Model not found at {MODEL_PATH}.\nRun train_model.py first.", file=sys.stderr)
        sys.exit(1)
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)


def load_logs():
    all_logs, sources = [], []
    for service, path in FILES.items():
        if not os.path.exists(path):
            print(f"[WARN] Log file not found, skipping: {path}", file=sys.stderr)
            continue
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = [line.strip() for line in f if line.strip()]
        if not lines:
            continue
        all_logs.extend(lines)
        sources.extend([service] * len(lines))
    return all_logs, sources


def run_isolation_forest(logs, contamination=0.2):
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(logs)
    model = IsolationForest(contamination=contamination, random_state=42)
    model.fit(X)
    return model.predict(X)


def classify_anomalies(anomalous_logs, svm_model, svm_vectorizer):
    X = svm_vectorizer.transform(anomalous_logs)
    labels = svm_model.predict(X)
    confidences = svm_model.predict_proba(X).max(axis=1)
    return labels, confidences


def print_and_collect_results(logs, sources, if_predictions, svm_model, svm_vectorizer):
    print("\n" + "=" * 58)
    print("   MULTI-CONTAINER AI ANOMALY DETECTION")
    print("=" * 58)

    anomalies = [
        (log, src)
        for log, src, pred in zip(logs, sources, if_predictions)
        if pred == -1
    ]
    normal_count = sum(1 for p in if_predictions if p == 1)

    if not anomalies:
        print("\nNo anomalies detected across all containers.")
        print(f"{normal_count} log lines appear normal.")
        return [], {"total": len(logs), "normal": normal_count}

    messages = [log for log, _ in anomalies]
    labels, confidences = classify_anomalies(messages, svm_model, svm_vectorizer)

    print(f"\nScanned {len(logs)} log lines across {len(FILES)} containers")
    print(f"Isolation Forest flagged {len(anomalies)} anomalies\n")

    results = []
    for (log, src), label, confidence in zip(anomalies, labels, confidences):
        cause, action = find_root_cause(log)
        conf_pct = round(float(confidence) * 100, 1)
        bar = "#" * int(conf_pct // 10) + "-" * (10 - int(conf_pct // 10))

        print(f"[ANOMALY] Container : {src.upper()}")
        print(f"  Log        : {log}")
        print(f"  Error Type : {label}  (confidence: {conf_pct}% [{bar}])")
        print(f"  Root Cause : {cause}")
        print(f"  Fix        : {action}")
        print("-" * 58)

        results.append({
            "container":    src,
            "original_log": log,
            "error_type":   label,
            "confidence":   conf_pct,
            "root_cause":   cause,
            "fix":          action,
        })

    from collections import Counter
    type_counts = Counter(r["error_type"] for r in results)
    avg_conf = sum(r["confidence"] for r in results) / len(results)

    print(f"\nSummary")
    print(f"  Anomalies found   : {len(results)}")
    print(f"  Normal logs       : {normal_count}")
    print(f"  Avg SVM confidence: {avg_conf:.1f}%")
    print("  Error breakdown:")
    for etype, count in type_counts.most_common():
        print(f"    {etype}: {count}")
    print("=" * 58)

    container_stats = {"total": len(logs), "normal": normal_count}
    return results, container_stats


def run_anomaly_detection():
    svm_model, svm_vectorizer = load_svm()
    all_logs, sources = load_logs()

    if not all_logs:
        print("[ERROR] No logs found. Check data/ directory.")
        sys.exit(1)

    if_predictions = run_isolation_forest(all_logs)
    results, container_stats = print_and_collect_results(
        all_logs, sources, if_predictions, svm_model, svm_vectorizer
    )

    # Auto-generate report
    if results:
        generate_report(results, container_stats)


if __name__ == "__main__":
    run_anomaly_detection()