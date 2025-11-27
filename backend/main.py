from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os, time, random
from typing import List

import joblib
import numpy as np


app = FastAPI()

# Allow CORS for local dev / frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "frontend")  # frontend folder must contain index.html
print(f"[DEBUG] STATIC_DIR: {STATIC_DIR}")

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    print("[DEBUG] Static files mounted successfully!")
else:
    print("[ERROR] Static directory not found.")

# Sample API route
@app.post("/api/predict")
def predict(data: dict = Body(...)):
    """Predict endpoint — supports:
    - type: 'anomaly' with input {'heart_rate': int, 'blood_oxygen': int}
    - type: 'risk' or 'score' (simple demo values)
    """
    prediction_type = data.get("type")
    input_data = data.get("input", {})

    if prediction_type == "anomaly":
        # require numeric inputs
        hr = input_data.get("heart_rate")
        spo2 = input_data.get("blood_oxygen")
        if hr is None or spo2 is None:
            return JSONResponse(content={"error": "Missing heart_rate or blood_oxygen"}, status_code=400)

        # Try to use the trained model if present
        global _MODEL
        try:
            if _MODEL is not None:
                X = np.array([[hr, spo2]])
                pred = _MODEL.predict(X)[0]
                is_anomaly = (pred == -1)
            else:
                # fallback simple thresholds
                is_anomaly = (hr > 130 or hr < 40 or spo2 < 92)
        except Exception:
            is_anomaly = (hr > 130 or hr < 40 or spo2 < 92)

        return JSONResponse(content={"prediction_type": "anomaly", "result": "Anomaly" if is_anomaly else "Normal", "is_anomaly": bool(is_anomaly)})

    elif prediction_type == "risk":
        # demo: simple risk score based on heart rate and spo2
        hr = input_data.get("heart_rate", 70)
        spo2 = input_data.get("blood_oxygen", 98)
        score = max(0, min(100, int(100 - (abs(hr - 75) * 0.6 + max(0, 98 - spo2) * 2))))
        return JSONResponse(content={"prediction_type": "risk", "result": {"risk_score": score}})

    elif prediction_type == "score":
        # return a health score (placeholder)
        return JSONResponse(content={"prediction_type": "score", "result": {"health_score": 87}})

    else:
        return JSONResponse(content={"error": "Unknown prediction type"}, status_code=400)


# --- small in-memory streaming state used by frontend demo ---
_HISTORY: List[dict] = []
_HISTORY_MAX = 500

# load model if available
MODEL_PATH = os.path.join(BASE_DIR, "model", "anomaly_model.pkl")
_MODEL = None
if os.path.exists(MODEL_PATH):
    try:
        _MODEL = joblib.load(MODEL_PATH)
        print(f"[INFO] Loaded model from {MODEL_PATH}")
    except Exception as e:
        print(f"[WARN] Could not load model: {e}")


def _simulate_sample():
    ts = int(time.time())
    hr = random.randint(55, 95)
    spo2 = random.randint(93, 100)
    activity = random.choices(["low", "moderate", "high"], weights=[0.6, 0.3, 0.1])[0]

    # occasionally inject anomalies
    if random.random() < 0.02:
        hr = random.choice([random.randint(120, 190), random.randint(25, 38)])
    if random.random() < 0.01:
        spo2 = random.randint(78, 91)

    sample = {"timestamp": ts, "heart_rate": hr, "blood_oxygen": spo2, "activity_level": activity}

    try:
        if _MODEL is not None:
            X = np.array([[hr, spo2]])
            p = _MODEL.predict(X)[0]
            # convert numpy.bool_ -> Python bool so JSONResponse serializes
            sample["is_anomaly"] = bool(p == -1)
        else:
            sample["is_anomaly"] = (hr > 130 or hr < 40 or spo2 < 92)
    except Exception:
        sample["is_anomaly"] = bool(hr > 130 or hr < 40 or spo2 < 92)

    return sample


@app.get("/api/stream")
def get_stream_sample():
    """Return a single recent simulated sample. Frontend should poll this endpoint to simulate real-time monitoring."""
    sample = _simulate_sample()
    _HISTORY.append(sample)
    if len(_HISTORY) > _HISTORY_MAX:
        _HISTORY.pop(0)
    return JSONResponse(content=sample)


@app.get("/api/history")
def get_history(limit: int = 100):
    return JSONResponse(content={"count": len(_HISTORY), "data": _HISTORY[-limit:]})


@app.get("/api/status")
def status():
    """Return quick status about the service for health checks and UI."""
    return JSONResponse(content={
        "ok": True,
        "model_loaded": _MODEL is not None,
        "history_count": len(_HISTORY),
        "stream_sample_rate_sec": 1
    })


@app.post("/api/train")
def retrain_model(data: dict = Body(...)):
    """Trigger training using train_model.py (demo) — returns success/failure."""
    # For safety we will call the training module programmatically (if present)
    try:
        train_path = os.path.join(BASE_DIR, "train_model.py")
        if os.path.exists(train_path):
            # import and run train logic
            import importlib.util
            spec = importlib.util.spec_from_file_location("train_model", train_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            # after training, try to reload model
            global _MODEL
            if os.path.exists(MODEL_PATH):
                _MODEL = joblib.load(MODEL_PATH)
            return JSONResponse(content={"status": "ok", "message": "Training script executed."})
        else:
            return JSONResponse(content={"error": "Training script not found"}, status_code=404)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Serve frontend
@app.get("/{full_path:path}")
def serve_frontend(full_path: str):
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    else:
        return JSONResponse(content={"error": "Frontend not found"}, status_code=404)
