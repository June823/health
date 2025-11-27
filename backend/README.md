# Backend: AI Health Monitor (FastAPI)

This folder contains the FastAPI backend for the health-monitor prototype.

How to run locally (from repository root):

```powershell
Push-Location 'c:/Users/HP/OneDrive/Documents/health ai/backend'
& "C:/Users/HP/OneDrive/Documents/health ai/venv/Scripts/python.exe" -m uvicorn main:app --reload --port 8000
```

Endpoints of interest:
- GET /api/stream — returns a simulated telemetry sample (timestamp, heart_rate, blood_oxygen, activity_level, is_anomaly)
- GET /api/history — returns buffered historical samples
- POST /api/predict { type: 'anomaly', input: {heart_rate, blood_oxygen} }
- POST /api/train — programmatically runs the training script and reloads the model

Project report: `../docs/project-report.docx` (updated)
