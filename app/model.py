import numpy as np
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

MODEL_PATH = "iris_model.joblib"

CLASS_NAMES = ["setosa", "versicolor", "virginica"]


def train_and_save():
    data = load_iris()
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(data.data, data.target)
    joblib.dump(model, MODEL_PATH)
    return model


def load_model():
    if not os.path.exists(MODEL_PATH):
        return train_and_save()
    return joblib.load(MODEL_PATH)


def predict(features: list[float]) -> dict:
    model = load_model()
    features_array = np.array(features).reshape(1, -1)
    prediction = model.predict(features_array)[0]
    probability = model.predict_proba(features_array)[0]
    return {
        "class_id": int(prediction),
        "class_name": CLASS_NAMES[int(prediction)],
        "probability": round(float(probability[int(prediction)]), 4),
    }
