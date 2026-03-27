# test_model.py

import joblib

model = joblib.load("model.pkl")

# Provide ALL 4 inputs
span = 6
load = 25
fck = 30
fy = 500

# Test prediction
prediction = model.predict([[span, load, fck, fy]])

print("Predicted Steel Area:", prediction[0])
