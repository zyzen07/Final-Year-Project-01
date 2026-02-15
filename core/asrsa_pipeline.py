import json
import os
# Base directory (asrsa_project)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Input feature file
INPUT_FILE = os.path.join(BASE_DIR, "data", "features.json")

# Output ASRSA results
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "asrsa_results.json")

# ASRSA weights (novel contribution)
W = {
    "F1": 0.30,
    "F2": 0.25,
    "F3": 0.20,
    "F4": 0.15,
    "F5": 0.10
}

with open(INPUT_FILE) as f:
    data = json.load(f)

results = []

for d in data:
    risk = sum(d[f]*W[f] for f in W)
    label = 1 if risk >= 0.6 else 0

    results.append({
        "F1": d["F1"],
        "F2": d["F2"],
        "F3": d["F3"],
        "F4": d["F4"],
        "F5": d["F5"],
        "risk_score": round(risk,3),
        "risk_label": label,
        "true_label": d["label"]
    })

with open(OUTPUT_FILE,"w") as f:
    json.dump(results,f,indent=2)

print("ASRSA completed.")
print("Sample:", results[0])
