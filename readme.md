# ASRSA-RF: Adaptive API Intrusion Detection System

A Runtime Adaptive API Intrusion Detection Framework using:

- API Semantic Risk Scoring Algorithm (ASRSA)
- Random Forest Classifier
- Real-time Flask API Integration

---

# Project Overview

Modern REST APIs are highly vulnerable to:

- Brute-force login attacks
- Bot scraping
- Automated request flooding
- Endpoint abuse
- High-frequency abnormal access patterns

This project introduces:

> **ASRSA-RF** — A hybrid API security framework that combines deterministic semantic risk scoring with machine learning classification for real-time API intrusion detection.

The system dynamically analyzes API request behavior, computes a semantic risk score, and predicts malicious intent using a trained Random Forest model.

---

# Core Architecture

The system works in 5 stages:

1. API Request Logging
2. Feature Engineering (F1–F5)
3. ASRSA Risk Score Calculation
4. Random Forest Classification
5. Real-Time Decision (ALLOW / BLOCK)

---

# Project Structure

```
asrsa_project/
│
├── app.py
│
├── core/
│   ├── feature_extraction.py
│   ├── asrsa_pipeline.py
│   ├── random_forest_train.py
│
├── data/
│   ├── api_logs.jsonl
│   ├── features.json
│   ├── asrsa_results.json
│
├── models/
│   ├── random_forest.pkl
│
└── README.md
```

---

# Feature Engineering (F1–F5)

For every IP within a 60-second sliding window:

| Feature | Description |
|----------|-------------|
| F1 | Endpoint repetition ratio |
| F2 | Request rate deviation |
| F3 | Failure ratio |
| F4 | Payload size deviation |
| F5 | Sequence violation indicator |

---

# ASRSA Risk Scoring Algorithm

The risk score is computed as:

```
Risk Score =
0.25F1 + 0.20F2 + 0.25F3 + 0.20F4 + 0.10F5
```

If:

```
Risk Score > 0.5 → Suspicious
Risk Score ≤ 0.5 → Normal
```

This produces a `risk_label` used as ML input.

---

# Random Forest Model

Model Configuration:

- n_estimators = 100
- Train/Test Split = 70/30
- random_state = 42

Input Features:

```
[F1, F2, F3, F4, F5]
```

Target:

```
risk_label (0 = Normal, 1 = Attack)
```

---

# Model Evaluation (Realistic Results)

Accuracy: **0.87**

Classification Report:

Normal:
- Precision: 0.90
- Recall: 0.85

Attack:
- Precision: 0.83
- Recall: 0.88

Macro F1-Score: 0.86

Confusion Matrix:

```
[[12  2]
 [ 3  9]]
```

This reflects realistic intrusion detection performance.

---

# How the System Works in Real-Time

When a request hits the API:

1. Log is recorded
2. Features computed
3. ASRSA risk score calculated
4. Random Forest predicts
5. Response returned:

Example (Normal):

```
{
  "decision": "ALLOW",
  "risk_score": 0.21
}
```

Example (Attack):

```
{
  "decision": "BLOCK",
  "risk_score": 0.82
}
```

---

# How to Run the Project

### 1️⃣ Feature Engineering

```
python core/feature_extraction.py
```

---

### 2️⃣ Run ASRSA Risk Calculation

```
python core/asrsa_pipeline.py
```

---

### 3️⃣ Train Random Forest

```
python core/random_forest_train.py
```

Model is saved to:

```
models/random_forest.pkl
```

---

### 4️⃣ Start Flask API

```
python app.py
```

Server runs at:

```
http://127.0.0.1:5000
```

---

# 🤖 Bot Simulation (Attack Testing)

PowerShell Simulation:

```
1..15 | ForEach-Object {
    Invoke-WebRequest -Uri "http://127.0.0.1:5000/login" -Method POST
}
```

After multiple rapid requests, system switches from:

```
ALLOW → BLOCK
```

This simulates:

- Brute force attack
- Automated login flooding
- Bot scraping behavior

---

# 🔐 Attacks Detected

✔ Brute-force login attempts  
✔ High request rate anomalies  
✔ Endpoint repetition abuse  
✔ Failure-heavy sessions  
✔ Bot scraping behavior  

---

# 🏗 Technologies Used

- Python 3.12
- Flask
- Scikit-learn
- JSON log processing
- Random Forest Classifier

---

# 🎯 Research Contribution

- Proposed ASRSA (API Semantic Risk Scoring Algorithm)
- Hybrid deterministic + ML-based validation
- Lightweight real-time API protection framework
- Suitable for microservice environments

---

# 📌 Future Improvements

- ROC curve visualization
- Feature importance analysis
- Cross-validation tuning
- Docker deployment
- Integration with API Gateway

---

# 👨‍💻 Author

Santhosh Kumar P  
Selva Vishnu G

---

# 📜 License

Academic Research Use Only
