from root_cause import find_root_cause
from sklearn.ensemble import IsolationForest
from sklearn.feature_extraction.text import TfidfVectorizer
import os
import sys

# Ensure stdout uses UTF-8 to prevent UnicodeEncodeError with emojis
if sys.stdout.encoding.lower() != 'utf-8':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

# Multi-container log sources
files = {
    "app": "data/logs_app.txt",
    "db": "data/logs_db.txt",
    "api": "data/logs_api.txt"
}

def load_logs():
    all_logs = []
    sources = []
    for service, path in files.items():
        if not os.path.exists(path):
            print(f"⚠️ Log file not found: {path}")
            continue

        with open(path, "r") as f:
            logs = [line.strip() for line in f.readlines() if line.strip()]

            if not logs:
                continue

            all_logs.extend(logs)
            sources.extend([service] * len(logs))
            
    return all_logs, sources

def train_model(logs):
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(logs)
    
    model = IsolationForest(
        contamination=0.2,
        random_state=42
    )
    model.fit(X)
    
    return model, vectorizer

def predict_anomalies(model, vectorizer, logs):
    X = vectorizer.transform(logs)
    return model.predict(X)

def process_results(logs, sources, predictions):
    print("\n======= Multi-Container AI Anomaly Detection =======\n")
    for log, src, pred in zip(logs, sources, predictions):
        if pred == -1:
            cause = find_root_cause(log)
            print(f"\n⚠️ Anomaly detected in {src.upper()} container")
            print("Log:", log)
            print("Root Cause:", cause)
            print("Suggested Action: Investigate container configuration or dependencies")
        else:
            print(f"Normal log ({src}):", log)

if __name__ == "__main__":
    all_logs, sources = load_logs()
    
    # Safety check
    if len(all_logs) == 0:
        print("No logs found to analyze.")
        exit()

    model, vectorizer = train_model(all_logs)
    predictions = predict_anomalies(model, vectorizer, all_logs)
    process_results(all_logs, sources, predictions)