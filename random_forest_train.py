import json
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Load ASRSA output
with open("asrsa_results.json") as f:
    data = json.load(f)

df = pd.DataFrame(data)

# Encode true labels
label_map = {"normal": 0, "bot": 1, "attacker": 1}
df["y"] = df["true_label"].map(label_map)

X = df[["F1", "F2", "F3", "F4", "F5", "risk_score"]]
y = df["y"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# Random Forest
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=5,
    random_state=42
)
model.fit(X_train, y_train)

# Prediction
y_pred = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))
print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))
