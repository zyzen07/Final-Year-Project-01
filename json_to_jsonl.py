import json

with open("api_logs.json") as f:
    data = json.load(f)

with open("api_logs.jsonl", "w") as f:
    for row in data:
        f.write(json.dumps(row) + "\n")

print("Saved api_logs.jsonl")
