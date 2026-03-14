"""
train_model.py — trains SVM log classifier
Expects data/training_logs.csv with columns: log_message, label
Run: python ai_engine/train_model.py
"""

import os
import sys
import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

CSV_PATH   = "data/training_logs.csv"
MODEL_DIR  = "ai_engine/model"
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")


def train():
    if not os.path.exists(CSV_PATH):
        print(f"[ERROR] Training data not found: {CSV_PATH}", file=sys.stderr)
        sys.exit(1)

    data = pd.read_csv(CSV_PATH)

    required_cols = {"log_message", "label"}
    if not required_cols.issubset(data.columns):
        print(f"[ERROR] CSV must contain columns: {required_cols}", file=sys.stderr)
        sys.exit(1)

    data = data.dropna(subset=["log_message", "label"])
    if len(data) < 10:
        print(f"[ERROR] Too few samples ({len(data)}). Need at least 10.", file=sys.stderr)
        sys.exit(1)

    print(f"Loaded {len(data)} samples across {data['label'].nunique()} classes")
    print(f"Class distribution:\n{data['label'].value_counts().to_string()}\n")

    X = data["log_message"]
    y = data["label"]

    min_class_count = data["label"].value_counts().min()
    use_stratify = min_class_count >= 2

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y if use_stratify else None,
    )

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=1,
        sublinear_tf=True,
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec  = vectorizer.transform(X_test)

    model = SVC(
        kernel="linear",
        probability=True,
        random_state=42,
        C=1.0,
    )
    model.fit(X_train_vec, y_train)

    y_pred = model.predict(X_test_vec)
    acc = accuracy_score(y_test, y_pred)

    print("=== Classification Report ===")
    print(classification_report(y_test, y_pred))
    print(f"Overall accuracy: {acc * 100:.1f}%")

    os.makedirs(MODEL_DIR, exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump((model, vectorizer), f)

    print(f"\nModel saved to {MODEL_PATH}")


if __name__ == "__main__":
    train()