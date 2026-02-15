import json
import pickle
import os
from datetime import datetime
from flask import Flask, request, jsonify
from collections import defaultdict

# -------------------------
# CONFIG
# -------------------------
LOG_FILE = "data/api_logs.jsonl"
WINDOW_SECONDS = 60

app = Flask(__name__)

# Load trained model
with open("models/random_forest.pkl", "rb") as f:
    model = pickle.load(f)

# Ensure log file exists
if not os.path.exists("data"):
    os.makedirs("data")

if not os.path.exists(LOG_FILE):
    open(LOG_FILE, "w").close()


# -------------------------
# Feature Calculation
# -------------------------
def calculate_features(ip):
    logs = []

    with open(LOG_FILE, "r") as f:
        for line in f:
            logs.append(json.loads(line))

    # Filter logs of this IP
    ip_logs = [l for l in logs if l["ip"] == ip]

    if len(ip_logs) == 0:
        return None

    # Use last 60 sec window
    now = datetime.utcnow()
    window_logs = []

    for log in ip_logs:
        ts = datetime.fromisoformat(log["timestamp"])
        if (now - ts).total_seconds() <= WINDOW_SECONDS:
            window_logs.append(log)

    if len(window_logs) == 0:
        return None

    total = len(window_logs)
    endpoints = [l["endpoint"] for l in window_logs]
    failures = [l for l in window_logs if l["status"] >= 400]

    # F1 Endpoint repetition
    most_common = max(endpoints.count(e) for e in set(endpoints))
    F1 = most_common / total

    # F2 Request rate
    expected_rate = 10
    F2 = min(total / expected_rate, 1.0)

    # F3 Failure ratio
    F3 = len(failures) / total

    # F4 Payload deviation
    avg_payload = sum(l["payload_size"] for l in window_logs) / total
    F4 = min(abs(avg_payload - 400) / 400, 1.0)

    # F5 Sequence violation
    sequence = "->".join(endpoints)
    F5 = 1 if "login->login" in sequence else 0

    return [F1, F2, F3, F4, F5]


# -------------------------
# Logging Function
# -------------------------
def log_request(ip, endpoint, method, status, payload_size):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "ip": ip,
        "endpoint": endpoint,
        "method": method,
        "status": status,
        "payload_size": payload_size,
    }

    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


# -------------------------
# Risk Evaluation
# -------------------------
def evaluate_risk(ip):
    features = calculate_features(ip)

    if features is None:
        return "ALLOW", 0.0

    prediction = model.predict([features])[0]
    probability = model.predict_proba([features])[0][1]

    if prediction == 1:
        return "BLOCK", float(probability)
    else:
        return "ALLOW", float(probability)


# -------------------------
# API ENDPOINTS
# -------------------------

@app.route("/login", methods=["POST"])
def login():
    ip = request.remote_addr or "127.0.0.1"
    payload_size = len(request.data)

    # simulate login success
    status = 200

    log_request(ip, "/login", "POST", status, payload_size)

    decision, risk_score = evaluate_risk(ip)

    return jsonify({
        "endpoint": "login",
        "decision": decision,
        "risk_score": risk_score
    })


@app.route("/products", methods=["GET"])
def products():
    ip = request.remote_addr or "127.0.0.1"
    payload_size = 4800

    status = 200

    log_request(ip, "/products", "GET", status, payload_size)

    decision, risk_score = evaluate_risk(ip)

    return jsonify({
        "endpoint": "products",
        "decision": decision,
        "risk_score": risk_score
    })


# -------------------------
# RUN SERVER
# -------------------------

if __name__ == "__main__":
    app.run(debug=True, port=5000)
