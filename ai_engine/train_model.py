"""
train_model.py — trains SVM Direct-Action classifier
Expects data/training_logs.csv with columns: log_message, label, action_label
This model predicts the ACTION directly from the LOG.
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

    # Load dataset
    data = pd.read_csv(CSV_PATH)

    # We now require 'action_label' for the Direct Answer model
    required_cols = {"log_message", "label", "action_label"}
    if not required_cols.issubset(data.columns):
        print(f"[ERROR] CSV must contain columns: {required_cols}", file=sys.stderr)
        sys.exit(1)

    # Drop empty rows
    data = data.dropna(subset=["log_message", "action_label"])
    
    if len(data) < 10:
        print(f"[ERROR] Too few samples ({len(data)}). Need at least 10.", file=sys.stderr)
        sys.exit(1)

    # Display class distribution for the Actions (The Fixes)
    print(f"Loaded {len(data)} samples for Direct-Action training.")
    print(f"Unique Actions to learn: {data['action_label'].nunique()}")
    print(f"Action distribution:\n{data['action_label'].value_counts().to_string()}\n")

    # X is input log, y is now the ACTION the AI must suggest
    X = data["log_message"]
    y = data["action_label"] 

    # Handle stratification for small datasets
    min_class_count = data["action_label"].value_counts().min()
    use_stratify = min_class_count >= 2

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y if use_stratify else None,
    )

    # Preserve your existing Vectorizer configuration
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=1,
        sublinear_tf=True,
    )
    
    # Transform text to numerical vectors
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec  = vectorizer.transform(X_test)

    # Initialize and train the SVC Model
    # probability=True allows the backend to see 'confidence' scores
    model = SVC(
        kernel="linear",
        probability=True,
        random_state=42,
        C=1.0,
    )
    
    print("AI is learning the relationship between Logs and Fixes...")
    model.fit(X_train_vec, y_train)

    # Evaluate the Direct Answer model
    y_pred = model.predict(X_test_vec)
    acc = accuracy_score(y_test, y_pred)

    print("\n=== Action Prediction Report ===")
    print(classification_report(y_test, y_pred))
    print(f"Overall Action Accuracy: {acc * 100:.1f}%")

    # Save both the model and vectorizer as a tuple to model.pkl
    os.makedirs(MODEL_DIR, exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump((model, vectorizer), f)

    print(f"\nAutonomous Decision-Maker saved to: {MODEL_PATH}")


if __name__ == "__main__":
    train()