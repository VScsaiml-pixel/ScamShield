import os
import sys
import json
from pathlib import Path

# Ensure backend root is in python path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from app.ml.preprocessor import preprocess_text

# Additional challenging, realistic benchmark samples to evaluate generalization
CHALLENGING_BENCHMARK = [
    # Subtly phrased or novel scams
    {"text": "Hey bro, can you quickly pay 500 via GPay to this QR code? I'll return cash tonight, urgent emergency.", "is_scam": 1, "category": "UPI / Payment Scam"},
    {"text": "Your electricity meter will be updated by junior lineman at 8pm. Send token fee 10 rupees to verify connection.", "is_scam": 1, "category": "Government Impersonation"},
    {"text": "Urgent verification needed: We detected unusual login from Bangalore on your account. Tap bit.ly/protect-now to confirm identity.", "is_scam": 1, "category": "Account Takeover"},
    {"text": "Selected for remote content moderator role. 30k monthly salary. Deposit 300 rupees security fee for company laptop dispatch.", "is_scam": 1, "category": "Fake Job / Internship"},
    {"text": "SpeedPost parcel cannot reach destination. Pay 15 rupees redelivery charge on indiapost-track.top immediately.", "is_scam": 1, "category": "Courier / Delivery Scam"},

    # Challenging legitimate messages (contain words like pay, urgent, meeting, bill, account)
    {"text": "Urgent team meeting rescheduled to 4 PM today in Boardroom B. Please bring project slides.", "is_scam": 0, "category": "Legitimate Personal/Work"},
    {"text": "Reminder to pay your broadband bill of Rs 825 before due date 15-Oct to avoid late payment fee.", "is_scam": 0, "category": "Legitimate Banking"},
    {"text": "Your salary of Rs 48,000 for September has been credited to your HDFC savings account ending 4921.", "is_scam": 0, "category": "Legitimate Banking"},
    {"text": "Can you pay the Swiggy guy Rs 350 cash when he arrives? I am stuck on a call.", "is_scam": 0, "category": "Legitimate Personal/Work"},
    {"text": "Hi Rahul, let us connect over Google Meet tomorrow to discuss the final year project report.", "is_scam": 0, "category": "Legitimate Personal/Work"},
]

def run_evaluation():
    base_dir = Path(__file__).resolve().parent.parent.parent
    models_dir = Path(__file__).resolve().parent / "saved_models"

    vec_path = models_dir / "vectorizer.joblib"
    bin_path = models_dir / "binary_model.joblib"
    cat_path = models_dir / "category_model.joblib"

    if not (vec_path.exists() and bin_path.exists()):
        print("Model artifacts missing. Running training first...")
        from app.ml.train import train_and_evaluate
        train_and_evaluate()

    vectorizer = joblib.load(vec_path)
    binary_model = joblib.load(bin_path)
    category_model = joblib.load(cat_path)

    # Load test set
    test_path = base_dir / "data" / "scam_test_set.csv"
    if test_path.exists():
        test_df = pd.read_csv(test_path)
    else:
        # Fallback to full dataset
        full_df = pd.read_csv(base_dir / "data" / "scam_dataset.csv")
        test_df = full_df.sample(frac=0.2, random_state=42)

    # Combine with challenging benchmark
    bench_df = pd.DataFrame(CHALLENGING_BENCHMARK)
    eval_df = pd.concat([test_df[["text", "is_scam", "category"]], bench_df], ignore_index=True)

    print("==================================================================")
    print("       SCAMSHIELD AI - MODEL EVALUATION & BENCHMARK REPORT        ")
    print("==================================================================")
    print(f"Total Evaluation Samples: {len(eval_df)} ({sum(eval_df['is_scam'] == 1)} Scam, {sum(eval_df['is_scam'] == 0)} Legitimate)")

    cleaned_texts = [preprocess_text(t) for t in eval_df["text"]]
    X_vec = vectorizer.transform(cleaned_texts)

    y_true = eval_df["is_scam"].values
    y_pred = binary_model.predict(X_vec)
    y_proba = binary_model.predict_proba(X_vec)[:, 1]

    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    cm = confusion_matrix(y_true, y_pred)

    print("\n--- Key Classification Metrics ---")
    print(f"Accuracy:          {acc * 100:.2f}%")
    print(f"Precision:         {prec * 100:.2f}% (How reliable a scam alert is)")
    print(f"Recall:            {rec * 100:.2f}% (How many actual scams are caught)")
    print(f"F1-Score:          {f1 * 100:.2f}% (Harmonic mean of Precision & Recall)")

    print("\n--- Confusion Matrix ---")
    print(f"True Negatives  (Legitimate correctly marked):  {cm[0][0]}")
    print(f"False Positives (Legitimate wrongly flagged):    {cm[0][1]}")
    print(f"False Negatives (Scams missed):                  {cm[1][0]}")
    print(f"True Positives  (Scams correctly caught):        {cm[1][1]}")

    print("\n--- Detailed Classification Report ---")
    print(classification_report(y_true, y_pred, target_names=["Legitimate", "Scam"]))

    print("--- Reliability & Operational Note ---")
    print("Note: In compliance with PRD Section 20, ScamShield AI predictions are advisory.")
    print("Real-world scam language continuously mutates; no statistical model is 100% accurate.")
    print("The system augments ML with rule-based explainable indicators for auditable safety.")

    return {
        "accuracy": round(float(acc), 4),
        "precision": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "f1_score": round(float(f1), 4),
        "confusion_matrix": cm.tolist()
    }

if __name__ == "__main__":
    run_evaluation()
