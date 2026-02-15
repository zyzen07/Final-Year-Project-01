import json, pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

with open("data/asrsa_results.json") as f:
    data = json.load(f)

X = [[d["F1"], d["F2"], d["F3"], d["F4"], d["F5"]] for d in data]
y = [d["risk_label"] for d in data]

X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.3,random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train,y_train)

pred = model.predict(X_test)

print("Accuracy:", model.score(X_test,y_test))
print("\nClassification Report:\n", classification_report(y_test,pred))
print("\nConfusion Matrix:\n", confusion_matrix(y_test,pred))

with open("models/random_forest.pkl","wb") as f:
    pickle.dump(model,f)
