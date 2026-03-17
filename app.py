import json
import pickle
import os
from datetime import datetime
from flask import Flask, request, jsonify, render_template

# -------------------------
# CONFIG
# -------------------------
LOG_FILE = "data/api_logs.jsonl"
DECISION_LOG = "data/decision_log.json"
WINDOW_SECONDS = 60

app = Flask(__name__)

# Load trained model
with open("models/random_forest.pkl", "rb") as f:
    model = pickle.load(f)

# Ensure data dir exists
os.makedirs("data", exist_ok=True)

if not os.path.exists(LOG_FILE):
    open(LOG_FILE, "w").close()

if not os.path.exists(DECISION_LOG):
    with open(DECISION_LOG, "w") as f:
        json.dump([], f)


# -------------------------
# Feature Calculation
# -------------------------
def calculate_features(ip):
    logs = []
    with open(LOG_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                logs.append(json.loads(line))

    ip_logs = [l for l in logs if l["ip"] == ip]
    if not ip_logs:
        return None, None

    now = datetime.utcnow()
    window_logs = [
        l for l in ip_logs
        if (now - datetime.fromisoformat(l["timestamp"])).total_seconds() <= WINDOW_SECONDS
    ]

    if not window_logs:
        return None, None

    total     = len(window_logs)
    endpoints = [l["endpoint"] for l in window_logs]
    failures  = [l for l in window_logs if l["status"] >= 400]

    F1 = max(endpoints.count(e) for e in set(endpoints)) / total
    F2 = min(total / 10, 1.0)
    F3 = len(failures) / total
    avg_payload = sum(l["payload_size"] for l in window_logs) / total
    F4 = min(abs(avg_payload - 400) / 400, 1.0)
    F5 = 1 if "login->login" in "->".join(endpoints) else 0

    feature_dict = {
        "F1": round(F1, 3),
        "F2": round(F2, 3),
        "F3": round(F3, 3),
        "F4": round(F4, 3),
        "F5": F5
    }
    return [F1, F2, F3, F4, F5], feature_dict


# -------------------------
# Logging
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


def log_decision(ip, endpoint, method, decision, risk_score, features):
    with open(DECISION_LOG, "r") as f:
        records = json.load(f)

    records.append({
        "time": datetime.utcnow().strftime("%H:%M:%S"),
        "ip": ip,
        "endpoint": endpoint,
        "method": method,
        "decision": decision,
        "risk_score": round(risk_score, 4),
        "features": features
    })

    # Keep last 200 entries
    records = records[-200:]

    with open(DECISION_LOG, "w") as f:
        json.dump(records, f)


# -------------------------
# Risk Evaluation
# -------------------------
def evaluate_risk(ip):
    feature_list, feature_dict = calculate_features(ip)

    if feature_list is None:
        return "ALLOW", 0.0, {}

    prediction  = model.predict([feature_list])[0]
    probability = model.predict_proba([feature_list])[0][1]

    decision = "BLOCK" if prediction == 1 else "ALLOW"
    return decision, float(probability), feature_dict


# -------------------------
# DASHBOARD
# -------------------------
@app.route("/")
def dashboard():
    return render_template("dashboard.html")


@app.route("/dashboard/logs")
def dashboard_logs():
    if not os.path.exists(DECISION_LOG):
        return jsonify([])
    with open(DECISION_LOG, "r") as f:
        return jsonify(json.load(f))


# -------------------------
# API ENDPOINTS
# -------------------------
@app.route("/login", methods=["POST"])
def login():
    ip           = request.remote_addr or "127.0.0.1"
    payload_size = len(request.data)

    log_request(ip, "/login", "POST", 200, payload_size)
    decision, risk_score, features = evaluate_risk(ip)
    log_decision(ip, "/login", "POST", decision, risk_score, features)

    return jsonify({
        "endpoint": "login",
        "decision": decision,
        "risk_score": risk_score,
        "features": features
    })


@app.route("/products", methods=["GET"])
def products():
    ip           = request.remote_addr or "127.0.0.1"
    payload_size = 4800

    log_request(ip, "/products", "GET", 200, payload_size)
    decision, risk_score, features = evaluate_risk(ip)
    log_decision(ip, "/products", "GET", decision, risk_score, features)

    return jsonify({
        "endpoint": "products",
        "decision": decision,
        "risk_score": risk_score,
        "features": features
    })


# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
