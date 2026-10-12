import os
from pathlib import Path
from typing import Dict, Any, List
import joblib

from app.ml.base import BaseScamDetector
from app.ml.preprocessor import preprocess_text
from app.ml.rules import (
    extract_rule_indicators,
    calculate_hybrid_risk_score,
    synthesize_explanation,
    generate_safety_recommendations
)

class TfidfLogisticDetector(BaseScamDetector):
    """
    Modular Scam Detector implementing BaseScamDetector.
    Combines TF-IDF feature extraction with calibrated Logistic Regression,
    granular rule-based indicator attribution, and explainable AI risk scoring.
    """

    def __init__(self, models_dir: Path = None):
        if models_dir is None:
            models_dir = Path(__file__).resolve().parent / "saved_models"

        self.models_dir = models_dir
        self.vectorizer = None
        self.binary_model = None
        self.category_model = None
        self._load_models()

    def _load_models(self):
        vec_path = self.models_dir / "vectorizer.joblib"
        bin_path = self.models_dir / "binary_model.joblib"
        cat_path = self.models_dir / "category_model.joblib"

        if not (vec_path.exists() and bin_path.exists()):
            raise FileNotFoundError(
                f"Model artifacts not found in {self.models_dir}. Please run 'python app/ml/train.py' first."
            )

        self.vectorizer = joblib.load(vec_path)
        self.binary_model = joblib.load(bin_path)
        self.category_model = joblib.load(cat_path)

    def predict(self, text: str) -> Dict[str, Any]:
        if not text or not text.strip():
            return {
                "prediction": "Legitimate",
                "risk_score": 0.0,
                "risk_level": "Low",
                "confidence": 1.0,
                "category": "Clean Input",
                "indicators": [],
                "risk_breakdown": {
                    "ml_contribution": 0.0,
                    "rule_contribution": 0.0,
                    "synergy_boost": 0.0,
                    "total_indicators_detected": 0
                },
                "explanation": "No text content provided to evaluate.",
                "recommendations": ["Enter a valid message or URL to run analysis."]
            }

        # 1. Clean & Preprocess
        cleaned_text = preprocess_text(text)

        # 2. Extract Rule-based Threat Indicators with Evidence Snippets
        indicators = extract_rule_indicators(text)

        # 3. Model Inference (Statistical Baseline)
        X_vec = self.vectorizer.transform([cleaned_text])
        proba = self.binary_model.predict_proba(X_vec)[0]
        scam_prob = float(proba[1])  # probability of scam (0.0 to 1.0)
        legit_prob = float(proba[0])

        # 4. Predict Category
        raw_category = self.category_model.predict(X_vec)[0]

        # 5. Hybrid Risk Scoring (PRD Section 13 & 14)
        risk_score, risk_level, breakdown = calculate_hybrid_risk_score(
            scam_prob=scam_prob,
            indicators=indicators,
            text=text,
            category=raw_category
        )

        # 6. Calibrated Prediction Classification
        if risk_score >= 61.0:
            prediction = "Scam"
            confidence = round(max(scam_prob, 0.75), 2)
            category = raw_category if "Legitimate" not in raw_category else "Suspicious Solicitations"
        elif risk_score >= 31.0:
            prediction = "Suspicious"
            confidence = round(0.50 + abs(scam_prob - 0.50), 2)
            category = raw_category if "Legitimate" not in raw_category else "Unclassified Suspicious Pattern"
        else:
            prediction = "Legitimate"
            confidence = round(max(legit_prob, 0.70), 2)
            category = "Legitimate Communication"

        # 7. Synthesize Human-Readable Grounded Explanation
        explanation = synthesize_explanation(
            prediction=prediction,
            risk_level=risk_level,
            indicators=indicators,
            category=category
        )

        # 8. Actionable Safety Recommendations
        recommendations = generate_safety_recommendations(
            prediction=prediction,
            risk_level=risk_level,
            indicators=indicators,
            category=category
        )

        return {
            "prediction": prediction,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "confidence": confidence,
            "category": category,
            "indicators": indicators,
            "risk_breakdown": breakdown,
            "explanation": explanation,
            "recommendations": recommendations
        }

    def batch_predict(self, texts: List[str]) -> List[Dict[str, Any]]:
        return [self.predict(t) for t in texts]

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "model_type": "Hybrid: TF-IDF + Calibrated Logistic Regression + Multi-Indicator Rule Engine",
            "classes": ["Legitimate", "Suspicious", "Scam"],
            "risk_levels": {
                "Low": "0 - 30",
                "Medium": "31 - 60",
                "High": "61 - 80",
                "Critical": "81 - 100"
            },
            "explainability": "Grounded evidence extraction + multi-factor risk attribution",
            "is_advisory": True
        }

# Global singleton detector instance
_detector_instance = None

def get_detector() -> TfidfLogisticDetector:
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = TfidfLogisticDetector()
    return _detector_instance
