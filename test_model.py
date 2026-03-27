# test_model.py

import joblib

model = joblib.load("model.pkl")

# Provide ALL 4 inputs
span = 6
load = 25
fck = 30
fy = 460

# fck = fck or 30 # To use default if user doesnt provide fck
# # fy = fy or 500 # To use default if user doesnt provide fy

# Test prediction
prediction = model.predict([[span, load, fck, fy]])

print("Predicted Steel Area:", prediction[0])
