# ScamShield AI - ML Architecture & Roadmap (Phase 2)

## Overview
This directory houses the Machine Learning and Natural Language Processing pipelines for ScamShield AI.

## Planned ML Pipeline (Phase 2)
1. **Dataset Collection & Preprocessing**:
   - Cleaned SMS/Email/Chat scam dataset covering Indian scam vectors (UPI, KYC, fake job, lottery, courier).
   - Text preprocessing: lowercase normalization, URL/phone token masking, regex cleanup, punctuation handling.
2. **Feature Extraction**:
   - TF-IDF Vectorization (`TfidfVectorizer` from `scikit-learn` with n-grams `(1, 2)`).
   - Domain/Keyword heuristic feature integration.
3. **Baseline Classifier**:
   - Logistic Regression classifier with class weights for explainable viva demonstrations.
   - Calibrated probability output (`predict_proba`) converted to base risk score.
4. **Model Serialization**:
   - Serialized pipeline artifacts: `model.joblib` and `vectorizer.joblib`.
5. **Evaluation Metrics**:
   - Precision, Recall, F1-Score, Confusion Matrix.
