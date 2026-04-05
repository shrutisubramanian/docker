"""
train_model.py — Upgraded SVM log classifier with rich feature engineering.

Features extracted per log line:
  - TF-IDF on cleaned text (unigrams + bigrams)
  - Structural features: log level, has stacktrace, line count, has IP/port/path
  - Keyword signal flags per error category

Run: python ai_engine/train_model.py
"""

import os
import sys
import pickle
import re
import numpy as np
import pandas as pd
from scipy.sparse import hstack, csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

CSV_PATH   = "data/training_logs.csv"
MODEL_DIR  = "ai_engine/model"
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")

# ──────────────────────────────────────────────
# FEATURE ENGINEERING
# ──────────────────────────────────────────────

# Category keyword signals — weighted hints for the classifier
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
    """Normalize log text for TF-IDF."""
    log = log.lower()
    log = re.sub(r'\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2}[,.\d]*', '', log)  # timestamps
    log = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', 'IPADDR', log)    # IPs
    log = re.sub(r'\b\d{4,}\b', 'NUMVAL', log)                                  # large numbers
    log = re.sub(r'[a-f0-9]{8,}', 'HEXVAL', log)                                # hex values
    log = re.sub(r'[\[\]()]', ' ', log)
    log = re.sub(r'\s+', ' ', log).strip()
    return log


def extract_structural_features(logs):
    """
    Hand-crafted features that capture log structure.
    Returns numpy array shape (n_samples, n_features).
    """
    features = []
    for log in logs:
        log_lower = log.lower()
        row = []

        # 1. Log level signals
        for level in LOG_LEVELS:
            row.append(1 if level.lower() in log_lower else 0)

        # 2. Has stacktrace indicators
        row.append(1 if any(x in log for x in ["\n\tat ", "Traceback", "File \"", "  at "]) else 0)

        # 3. Has IP address
        row.append(1 if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', log) else 0)

        # 4. Has port number
        row.append(1 if re.search(r':\d{4,5}', log) else 0)

        # 5. Has file path
        row.append(1 if re.search(r'(/[a-zA-Z0-9._-]+){2,}', log) else 0)

        # 6. Has exit code
        row.append(1 if re.search(r'exit(ed)?\s+(code\s+)?\d+', log_lower) else 0)

        # 7. Has memory units
        row.append(1 if re.search(r'\d+\s*(mb|kb|gb|bytes)', log_lower) else 0)

        # 8. Has ms/seconds (timing)
        row.append(1 if re.search(r'\d+\s*(ms|milliseconds|seconds|timeout)', log_lower) else 0)

        # 9. Line count (multiline logs are often crashes/stacktraces)
        row.append(min(log.count('\n'), 10))

        # 10. Category keyword signal scores (soft hints)
        for cat, keywords in CATEGORY_SIGNALS.items():
            score = sum(1 for kw in keywords if kw in log_lower)
            row.append(score)

        features.append(row)

    return np.array(features, dtype=np.float32)


# ──────────────────────────────────────────────
# TRAINING
# ──────────────────────────────────────────────

def train():
    if not os.path.exists(CSV_PATH):
        print(f"[ERROR] Training data not found: {CSV_PATH}\nRun generate_logs.py first.", file=sys.stderr)
        sys.exit(1)

    data = pd.read_csv(CSV_PATH).dropna(subset=["log_message", "label"])
    print(f"Loaded {len(data)} samples | {data['label'].nunique()} classes")
    print(data['label'].value_counts().to_string())

    X_raw = data["log_message"].tolist()
    y     = data["label"].tolist()

    # ── Build features ──────────────────────────────
    print("\nExtracting features...")
    X_clean = [clean_text(log) for log in X_raw]

    tfidf = TfidfVectorizer(
        ngram_range=(1, 3),
        min_df=2,
        max_features=8000,
        sublinear_tf=True,
        analyzer="word",
    )
    X_tfidf = tfidf.fit_transform(X_clean)

    X_struct = extract_structural_features(X_raw)
    scaler   = StandardScaler()
    X_struct_scaled = scaler.fit_transform(X_struct)

    # combine sparse TF-IDF + dense structural features
    X_combined = hstack([X_tfidf, csr_matrix(X_struct_scaled)])

    # ── Train / test split ──────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X_combined, y, test_size=0.2, random_state=42, stratify=y
    )

    # ── SVM ─────────────────────────────────────────
    print("Training SVM...")
    model = SVC(
        kernel="rbf",          # RBF kernel handles non-linear boundaries better
        C=5.0,
        gamma="scale",
        probability=True,
        random_state=42,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)

    # ── Evaluate ─────────────────────────────────────
    y_pred = model.predict(X_test)
    acc    = accuracy_score(y_test, y_pred)

    print("\n=== Classification Report ===")
    print(classification_report(y_test, y_pred))
    print(f"Overall accuracy: {acc * 100:.1f}%")

    # Cross-validation for robustness check
    cv_scores = cross_val_score(model, X_train, y_train, cv=3, scoring="accuracy")
    print(f"3-fold CV accuracy: {cv_scores.mean()*100:.1f}% ± {cv_scores.std()*100:.1f}%")

    # ── Save ─────────────────────────────────────────
    os.makedirs(MODEL_DIR, exist_ok=True)
    bundle = {
        "model":   model,
        "tfidf":   tfidf,
        "scaler":  scaler,
    }
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(bundle, f)

    print(f"\nModel bundle saved → {MODEL_PATH}")
    print("Bundle contains: model, tfidf vectorizer, structural scaler")


if __name__ == "__main__":
    train()