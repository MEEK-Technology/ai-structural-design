import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib

# Load dataset
data = pd.read_csv("beam_dataset.csv")

# Features (inputs)
X = data[["span", "load", "fck", "fy"]]

# Target (output)
y = data["steel_area"]

# Create model
model = RandomForestRegressor(n_estimators=100)

# Train model
model.fit(X, y)

# Save model
joblib.dump(model, "model.pkl")

print("Model trained and saved successfully")