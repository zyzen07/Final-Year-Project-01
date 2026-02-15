import json
import os
from datetime import datetime
from collections import defaultdict

# Base directory (asrsa_project)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Input log file
LOG_FILE = os.path.join(BASE_DIR, "data", "api_logs.jsonl")

# Output feature file
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "features.json")
WINDOW_SECONDS = 60

logs = []
with open(LOG_FILE) as f:
    for line in f:
        logs.append(json.loads(line))

for log in logs:
    log["timestamp"] = datetime.fromisoformat(log["timestamp"].replace("Z",""))

windows = defaultdict(list)
for log in logs:
    key = (log["ip"], int(log["timestamp"].timestamp()) // WINDOW_SECONDS)
    windows[key].append(log)

features = []

for (ip, window_id), wl in windows.items():
    total = len(wl)
    endpoints = [l["endpoint"] for l in wl]
    failures = [l for l in wl if l["status"] >= 400]

    F1 = max(endpoints.count(e) for e in set(endpoints)) / total
    F2 = min(total / 10, 1.0)
    F3 = len(failures) / total
    avg_payload = sum(l["payload_size"] for l in wl) / total
    F4 = min(abs(avg_payload - 400) / 400, 1.0)
    F5 = 1 if "login->login" in "->".join(endpoints) else 0

    label = wl[0]["user_type"]

    features.append({
        "ip": ip,
        "window_id": window_id,
        "F1": round(F1,3),
        "F2": round(F2,3),
        "F3": round(F3,3),
        "F4": round(F4,3),
        "F5": F5,
        "label": label
    })

with open(OUTPUT_FILE,"w") as f:
    json.dump(features,f,indent=2)

print("Feature Engineering Completed")
print("Total feature rows:", len(features))
print("Sample feature row:", features[0])
