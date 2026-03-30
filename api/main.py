from fastapi import FastAPI
import joblib
import pandas as pd

from nlp.prompt_parser import extract_parameters, apply_defaults
from rules.beam_design import bending_moment

app = FastAPI()

# Load trained model
model = joblib.load("model.pkl")


@app.post("/predict")
def predict(data: dict):
    # Handle prompt input
    if "prompt" in data:
        params = extract_parameters(data["prompt"])
        params = apply_defaults(params)
    else:
        params = data

    span = params["span"]
    load = params["load"]
    fck = params["fcu"] if "fcu" in params else params["fck"]
    fy = params["fy"]

    # AI Prediction
    input_df = pd.DataFrame([{
        "span": span,
        "load": load,
        "fck": fck,
        "fy": fy
    }])

    steel_area = model.predict(input_df)[0]

    # Engineering Calculation
    moment = bending_moment(load, span)

    return {
        "input": params,
        "results": {
            "steel_area": round(float(steel_area), 2),
            "bending_moment": round(moment, 2)
        }
    }

