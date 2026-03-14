"""
confusion_matrix.py — generates and saves confusion matrix + accuracy chart
Run after training:  python ai_engine/confusion_matrix.py
"""

import os
import sys
import pickle
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # non-interactive backend, works without a display
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report
import numpy as np

MODEL_PATH   = "ai_engine/model/model.pkl"
CSV_PATH     = "data/training_logs.csv"
REPORTS_DIR  = "reports"


def plot_confusion_matrix():
    # ── Load model + data ─────────────────────────────────────────────────────
    if not os.path.exists(MODEL_PATH):
        print(f"[ERROR] Model not found. Run train_model.py first.")
        sys.exit(1)
    if not os.path.exists(CSV_PATH):
        print(f"[ERROR] Training data not found at {CSV_PATH}.")
        sys.exit(1)

    with open(MODEL_PATH, "rb") as f:
        model, vectorizer = pickle.load(f)

    data = pd.read_csv(CSV_PATH).dropna(subset=["log_message", "label"])
    X = data["log_message"]
    y = data["label"]

    min_class = y.value_counts().min()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42,
        stratify=y if min_class >= 2 else None
    )

    X_test_vec = vectorizer.transform(X_test)
    y_pred     = model.predict(X_test_vec)
    accuracy   = accuracy_score(y_test, y_pred)
    labels     = sorted(y.unique())

    os.makedirs(REPORTS_DIR, exist_ok=True)

    # ── Figure with 2 subplots ────────────────────────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("AI Log Classifier — Model Performance", fontsize=14, fontweight="bold", y=1.01)

    # ── Left: Confusion matrix heatmap ───────────────────────────────────────
    cm = confusion_matrix(y_test, y_pred, labels=labels)
    ax1 = axes[0]

    im = ax1.imshow(cm, interpolation="nearest", cmap="Blues")
    plt.colorbar(im, ax=ax1, shrink=0.8)

    ax1.set_xticks(range(len(labels)))
    ax1.set_yticks(range(len(labels)))
    ax1.set_xticklabels(labels, rotation=35, ha="right", fontsize=10)
    ax1.set_yticklabels(labels, fontsize=10)
    ax1.set_xlabel("Predicted label", fontsize=11)
    ax1.set_ylabel("True label", fontsize=11)
    ax1.set_title(f"Confusion Matrix\n(Accuracy: {accuracy*100:.1f}%)", fontsize=12)

    # Annotate cells
    thresh = cm.max() / 2
    for i in range(len(labels)):
        for j in range(len(labels)):
            ax1.text(j, i, str(cm[i, j]),
                     ha="center", va="center", fontsize=12,
                     color="white" if cm[i, j] > thresh else "black")

    # ── Right: Per-class F1 bar chart ─────────────────────────────────────────
    report = classification_report(y_test, y_pred, labels=labels, output_dict=True)
    f1_scores = [report[l]["f1-score"] for l in labels]
    colors = ["#4C8BF5" if s >= 0.9 else "#F5A623" if s >= 0.7 else "#E24B4A" for s in f1_scores]

    ax2 = axes[1]
    bars = ax2.barh(labels, f1_scores, color=colors, edgecolor="none", height=0.5)

    for bar, score in zip(bars, f1_scores):
        ax2.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height() / 2,
                 f"{score:.2f}", va="center", fontsize=10)

    ax2.set_xlim(0, 1.15)
    ax2.set_xlabel("F1 Score", fontsize=11)
    ax2.set_title("Per-class F1 Score", fontsize=12)
    ax2.axvline(x=accuracy, color="gray", linestyle="--", linewidth=1, label=f"Overall accuracy: {accuracy*100:.1f}%")
    ax2.legend(fontsize=9)

    legend_patches = [
        mpatches.Patch(color="#4C8BF5", label="F1 >= 0.90"),
        mpatches.Patch(color="#F5A623", label="F1 >= 0.70"),
        mpatches.Patch(color="#E24B4A", label="F1 < 0.70"),
    ]
    ax2.legend(handles=legend_patches, fontsize=8, loc="lower right")

    plt.tight_layout()

    out_path = os.path.join(REPORTS_DIR, "model_performance.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()

    print(f"Confusion matrix saved to: {out_path}")
    print(f"Overall accuracy: {accuracy*100:.1f}%")


if __name__ == "__main__":
    plot_confusion_matrix()