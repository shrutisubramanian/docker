import pickle
from explanations import get_explanation

# Load trained model
with open("ai_engine/model/model.pkl", "rb") as f:
    model, vectorizer = pickle.load(f)

# Read logs
with open("data/logs_api.txt") as f:
    logs = f.read()

# Convert logs into vector
X = vectorizer.transform([logs])

# Predict error type
prediction = model.predict(X)[0]

# Get explanation and fix
explanation, fix = get_explanation(prediction)

print("\n========== AI Log Analyzer ==========")
print("Detected Error:", prediction)
print("Explanation:", explanation)
print("Suggested Fix:", fix)
print("=====================================\n")