import os
import sys
import json
from pathlib import Path

# Ensure backend root is in python path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
import joblib

from app.ml.preprocessor import preprocess_text

def train_and_evaluate():
    base_dir = Path(__file__).resolve().parent.parent.parent
    data_path = base_dir / "data" / "scam_dataset.csv"
    models_dir = Path(__file__).resolve().parent / "saved_models"
    models_dir.mkdir(parents=True, exist_ok=True)

    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found at {data_path}. Run dataset_generator.py first.")

    print(f"Loading dataset from: {data_path}")
    df = pd.read_csv(data_path)
    print(f"Total samples: {len(df)}")
    print(df["category"].value_counts())

    # Preprocess texts
    print("\n[Step 1/5] Preprocessing text corpus with entity tokenization...")
    df["cleaned_text"] = df["text"].apply(preprocess_text)

    # Train/Test Split (80% train, 20% test, stratified by scam binary label)
    print("[Step 2/5] Creating stratified train/test split (80/20)...")
    X_train, X_test, y_train, y_test, cat_train, cat_test, raw_train, raw_test = train_test_split(
        df["cleaned_text"],
        df["is_scam"],
        df["category"],
        df["text"],
        test_size=0.20,
        random_state=42,
        stratify=df["is_scam"]
    )
    print(f"Training samples: {len(X_train)} | Test samples: {len(X_test)}")

    # TF-IDF Vectorization
    print("[Step 3/5] Fitting TF-IDF Vectorizer (unigrams + bigrams)...")
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=2500,
        sublinear_tf=True
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # Train Binary Classifier (Scam vs Legitimate)
    print("[Step 4/5] Training Logistic Regression binary classifier...")
    binary_model = LogisticRegression(
        C=2.0,
        class_weight="balanced",
        max_iter=1000,
        random_state=42
    )
    binary_model.fit(X_train_vec, y_train)

    # Train Multi-Class Category Classifier
    print("[Step 5/5] Training multi-class Category Classifier for scam vectors...")
    category_model = LogisticRegression(
        C=1.5,
        class_weight="balanced",
        max_iter=1000,
        random_state=42
    )
    category_model.fit(X_train_vec, cat_train)

    # Model Evaluation on Held-out Test Set
    y_pred = binary_model.predict(X_test_vec)
    y_proba = binary_model.predict_proba(X_test_vec)[:, 1]

    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    cm = confusion_matrix(y_test, y_pred).tolist()

    print("\n" + "="*50)
    print("       MODEL EVALUATION ON HELD-OUT TEST SET     ")
    print("="*50)
    print(f"Accuracy:         {acc * 100:.2f}%")
    print(f"Precision:        {prec * 100:.2f}%")
    print(f"Recall:           {rec * 100:.2f}%")
    print(f"F1-Score:         {f1 * 100:.2f}%")
    print("\nConfusion Matrix (TN, FP / FN, TP):")
    print(np.array(cm))
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Legitimate", "Scam"]))

    # Save artifacts
    print("Serializing and saving pipeline artifacts...")
    joblib.dump(vectorizer, models_dir / "vectorizer.joblib")
    joblib.dump(binary_model, models_dir / "binary_model.joblib")
    joblib.dump(category_model, models_dir / "category_model.joblib")

    # Save test dataset copy for standalone evaluation script
    test_df = pd.DataFrame({
        "text": raw_test,
        "cleaned_text": X_test,
        "is_scam": y_test,
        "category": cat_test
    })
    test_df.to_csv(base_dir / "data" / "scam_test_set.csv", index=False)

    metrics = {
        "model_architecture": "TF-IDF (1,2 n-grams) + Logistic Regression (C=2.0)",
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "confusion_matrix": {
            "true_negative": cm[0][0],
            "false_positive": cm[0][1],
            "false_negative": cm[1][0],
            "true_positive": cm[1][1]
        },
        "disclaimer": "Predictions are probabilistic and advisory. Not claimed to be 100% accurate."
    }

    with open(models_dir / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"\nArtifacts successfully saved to: {models_dir}")
    print("Training process finished.")
    return metrics

if __name__ == "__main__":
    train_and_evaluate()
