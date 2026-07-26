import pickle
import os
import numpy as np
from typing import Dict, Any
from config.settings import settings
from src.ml.train_classifier import train_and_save_classifier

class DocumentClassifier:
    """Inference engine for automatic document domain classification."""
    def __init__(self):
        self.model = None
        self.vectorizer = None

    def _ensure_loaded(self):
        if self.model is None or self.vectorizer is None:
            if not os.path.exists(settings.CLASSIFIER_MODEL_PATH) or not os.path.exists(settings.TOKENIZER_PATH):
                print("Classifier artifacts missing. Triggering automated model training...")
                train_and_save_classifier()

            with open(settings.CLASSIFIER_MODEL_PATH, "rb") as f:
                self.model = pickle.load(f)

            with open(settings.TOKENIZER_PATH, "rb") as f:
                self.vectorizer = pickle.load(f)

    def predict(self, text: str) -> Dict[str, Any]:
        """Predicts technical domain category and confidence score for input text."""
        if not text or len(text.strip()) == 0:
            return {"category": "Unclassified", "confidence": 0.0}

        # Load model on first use (lazy load)
        self._ensure_loaded()

        # Transform text using TF-IDF feature extractor
        features = self.vectorizer.transform([text]).toarray()
        
        # Predict probabilities
        probabilities = self.model.predict_proba(features)[0]
        top_idx = np.argmax(probabilities)
        predicted_category = self.model.classes_[top_idx]
        confidence = float(probabilities[top_idx])

        return {
            "category": str(predicted_category),
            "confidence": round(confidence, 4)
        }
