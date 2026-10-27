"""
Train the case outcome prediction ML model.
Run this script once to generate the model file:
    python ml_model/train_model.py
"""

import pandas as pd
import numpy as np
import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder

# Paths
DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/case_dataset.csv")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "../data/case_model.pkl")
ENCODER_PATH = os.path.join(os.path.dirname(__file__), "../data/label_encoder.pkl")

def train():
    print("[*] Loading dataset...")
    df = pd.read_csv(DATA_PATH)
    df = df.dropna()

    # Features and labels
    X = df["case_text"].values
    y = df["outcome"].values

    # Encode labels
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42
    )

    print(f"[*] Training on {len(X_train)} samples...")

    # Build pipeline: TF-IDF + Logistic Regression
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=500,
            stop_words="english"
        )),
        ("clf", LogisticRegression(
    max_iter=1000,
    C=1.0,
    solver="lbfgs"
))
    ])

    pipeline.fit(X_train, y_train)

    # Evaluate
    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\n[✓] Accuracy: {acc:.2%}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    # Save model and encoder
    joblib.dump(pipeline, MODEL_PATH)
    joblib.dump(le, ENCODER_PATH)
    print(f"\n[✓] Model saved to: {MODEL_PATH}")
    print(f"[✓] Label encoder saved to: {ENCODER_PATH}")

if __name__ == "__main__":
    train()