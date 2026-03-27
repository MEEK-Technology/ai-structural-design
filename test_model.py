# test_model.py

import joblib
import pandas as pd

model = joblib.load("model.pkl")

# Provide ALL 4 inputs
input_data = pd.DataFrame([{
    "span": 6,
    "load": 25,
    "fck": 30,
    "fy": 460
}])

# fck = fck or 30 # To use default if user doesnt provide fck
# # fy = fy or 460 # To use default if user doesnt provide fy

# Test prediction
prediction = model.predict(input_data)

print("Predicted Steel Area:", prediction[0])

