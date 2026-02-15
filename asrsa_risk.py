import json

FEATURE_FILE = "features.json"

# ---------------- ASRSA WEIGHTS ----------------
# These weights define the importance of each semantic feature
WEIGHTS = {
    "F1_endpoint_repetition": 0.30,
    "F2_rate_deviation": 0.25,
    "F3_failure_ratio": 0.20,
    "F4_payload_deviation": 0.10,
    "F5_sequence_violation": 0.15
}

# Risk thresholds
LOW_THRESHOLD = 0.30
HIGH_THRESHOLD = 0.60


def calculate_asrsa_risk(feature_row):
    """
    Computes ASRSA risk score for a single feature row
    """
    risk = 0.0
    for feature, weight in WEIGHTS.items():
        risk += feature_row[feature] * weight
    return round(risk, 3)


def classify_risk(risk_score):
    """
    Converts numerical risk into risk level
    """
    if risk_score < LOW_THRESHOLD:
        return "LOW"
    elif risk_score < HIGH_THRESHOLD:
        return "MEDIUM"
    else:
        return "HIGH"


# ---------------- MAIN ----------------
with open(FEATURE_FILE, "r") as f:
    features = json.load(f)

results = []

for row in features:
    risk_score = calculate_asrsa_risk(row)
    risk_level = classify_risk(risk_score)

    row_result = {
        **row,
        "ASRSA_risk_score": risk_score,
        "risk_level": risk_level
    }

    results.append(row_result)

# Save results
with open("asrsa_results.json", "w") as f:
    json.dump(results, f, indent=2)

print("ASRSA risk calculation completed.")
print("Total rows processed:", len(results))
print("Saved to asrsa_results.json")

print("\nSample result:")
print(results[0])
