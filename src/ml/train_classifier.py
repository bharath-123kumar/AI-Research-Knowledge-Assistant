import pickle
import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report
from config.settings import settings
from src.ml.dataset_prep import prepare_dataset, CATEGORIES

def train_and_save_classifier():
    """Trains a multi-class Neural Network classifier and persists model artifacts."""
    print("Preparing dataset for domain classifier...")
    texts, labels = prepare_dataset()

    # 1. Feature Engineering: TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(max_features=1000, stop_words='english', ngram_range=(1, 2))
    X = vectorizer.fit_transform(texts).toarray()
    y = np.array(labels)

    # 2. Model Architecture: Multi-Layer Perceptron (Neural Network with ReLU & Softmax output)
    classifier = MLPClassifier(
        hidden_layer_sizes=(128, 64),
        activation='relu',
        solver='adam',
        max_iter=300,
        random_state=42
    )

    # 3. Model Training
    print("Training Deep Neural Network Classifier...")
    classifier.fit(X, y)

    # 4. Evaluation
    predictions = classifier.predict(X)
    print("\nModel Evaluation Summary:")
    print(classification_report(y, predictions, zero_division=0))

    # 5. Model Persistence
    os.makedirs(settings.MODELS_DIR, exist_ok=True)
    with open(settings.CLASSIFIER_MODEL_PATH, "wb") as f:
        pickle.dump(classifier, f)

    with open(settings.TOKENIZER_PATH, "wb") as f:
        pickle.dump(vectorizer, f)

    print(f"Classifier model saved to {settings.CLASSIFIER_MODEL_PATH}")
    print(f"Tokenizer/Vectorizer saved to {settings.TOKENIZER_PATH}")

if __name__ == "__main__":
    train_and_save_classifier()
