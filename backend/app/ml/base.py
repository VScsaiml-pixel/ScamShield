from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseScamDetector(ABC):
    """
    Abstract Base Class for Scam Detection engines.
    Allows easy hot-swapping between TF-IDF+Logistic Regression baseline,
    Linear SVM, or advanced Transformer models (e.g., RoBERTa/DeBERTa) in the future.
    """

    @abstractmethod
    def predict(self, text: str) -> Dict[str, Any]:
        """
        Analyze a single message and return prediction results:
        {
            "prediction": "Legitimate" | "Suspicious" | "Scam",
            "risk_score": float (0-100),
            "confidence": float (0.0 - 1.0),
            "category": str,
            "indicators": list,
            "explanation": str,
            "recommendations": list
        }
        """
        pass

    @abstractmethod
    def batch_predict(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Analyze a batch of messages."""
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Return metadata about current model architecture and version."""
        pass
