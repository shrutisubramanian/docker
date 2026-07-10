import pickle

# load trained model
with open("ai_engine/model/model.pkl", "rb") as f:
    model, vectorizer = pickle.load(f)

# read logs
with open("data/logs.txt") as f:
    logs = f.read()

# convert log text to vector
X = vectorizer.transform([logs])

prediction = model.predict(X)[0]

print("Predicted Error Type:", prediction)