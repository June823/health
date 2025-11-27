.

🩺 AI-Powered Health Monitoring System

Real-Time Health Analytics Using Wearables

📌 Overview

The AI-Powered Health Monitoring System is a smart health application that analyzes real-time biometric data such as heart rate, SpO₂, and activity levels from wearable devices.
The goal is to detect anomalies early, alert users, and provide AI-driven personalized health recommendations.

🚀 Key Features
🔹 Real-Time Monitoring

Streams biometric data from wearable sensors

Tracks heart rate, blood oxygen, steps, sleep, and calories burned

🔹 AI-Based Health Analysis

Machine learning model detects abnormal patterns

Flags risky conditions like tachycardia, low SpO₂, and sudden drops in activity

🔹 Health Recommendations

Provides personalized tips based on health trends

Lifestyle and fitness advice generated using AI

🔹 User Dashboard

Clean UI showing charts and insights

Visualizes health trends over time

🔹 API Backend

Built using FastAPI, including:

/predict → anomaly detection

/recommendations → personalized suggestions

/health-data → health metrics endpoint

🧠 Technologies Used
Backend

FastAPI

Python

Machine Learning (Sklearn / Custom Model)

Frontend

React.js

Chart.js / Recharts

Other

Uvicorn (server)

Git & GitHub

Virtual Environment (venv)

🗂️ Project Structure
health-ai/
│── backend/
│   ├── main.py
│   ├── model/
│   ├── routes/
│   └── utils/
│
│── frontend/
│   ├── src/
│   ├── components/
│   └── pages/
│
└── README.md

▶️ How to Run the Project
1️⃣ Create Virtual Environment
python -m venv venv

2️⃣ Activate Environment

Windows:

venv\Scripts\activate

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Run Backend (FastAPI)
python -m uvicorn backend.main:app --reload


Runs at: http://127.0.0.1:8000

5️⃣ Run Frontend
cd frontend
npm install
npm start


Runs at: http://localhost:3000

📊 Expected Output

Heart rate graphs

SpO₂ trend analysis

Anomaly alerts

Personalized health advice

🎯 Future Improvements

Support ECG analysis

Machine learning model retraining

Mobile app version

Push notifications for emergencies

📝 Author

June Oyugi
AI Health System — 2025

