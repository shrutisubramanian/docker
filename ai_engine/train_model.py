import pandas as pd
import pickle

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

data = pd.read_csv("data/training_logs.csv")

X = data["log_message"]
y = data["label"]

vectorizer = CountVectorizer()
X_vec = vectorizer.fit_transform(X)

model = MultinomialNB()
model.fit(X_vec, y)

with open("ai_engine/model/model.pkl", "wb") as f:
    pickle.dump((model, vectorizer), f)

print("Model trained and saved.")