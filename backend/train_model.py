# backend/train_model.py
"""Training script for anomaly detection model (IsolationForest).

This script generates synthetic but realistic health telemetry (heart rate, SpO2,
and a few injected anomalies), trains an IsolationForest model, and saves it to
model/anomaly_model.pkl. It exposes a `train()` function that can be imported
by the API as well as a CLI entrypoint.
"""

from sklearn.ensemble import IsolationForest
import pandas as pd
import joblib
import os
import numpy as np


def generate_synthetic_data(n_samples: int = 2000, anomaly_frac: float = 0.03, random_state: int = 42):
    rng = np.random.RandomState(random_state)
    heart_rate = rng.normal(loc=75, scale=8, size=n_samples).astype(int)
    blood_oxygen = (rng.normal(loc=97.5, scale=1.5, size=n_samples)).astype(int)

    # Inject anomalies
    n_anom = max(1, int(n_samples * anomaly_frac))
    for i in rng.choice(n_samples, n_anom, replace=False):
        if rng.rand() < 0.6:
            heart_rate[i] = rng.choice([rng.randint(120, 190), rng.randint(25, 38)])
        else:
            blood_oxygen[i] = rng.randint(75, 90)

    df = pd.DataFrame({
        "heart_rate": heart_rate,
        "blood_oxygen": blood_oxygen,
    })
    return df


def train(save_path: str = None, n_samples: int = 2000):
    df = generate_synthetic_data(n_samples=n_samples)

    print(f"Training IsolationForest on {len(df)} samples (features: heart_rate, blood_oxygen)")
    model = IsolationForest(contamination=0.03, random_state=42)
    model.fit(df)

    if save_path is None:
        save_path = os.path.join("model", "anomaly_model.pkl")

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    joblib.dump(model, save_path)
    print(f"Saved trained model to {save_path}")

    return model


if __name__ == "__main__":
    # default: train and save
    train(save_path=os.path.join("model", "anomaly_model.pkl"), n_samples=3000)
