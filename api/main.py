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

    # Handle prompt input or direct parameters
    if "prompt" in data:
        params = extract_parameters(data["prompt"])
        params = apply_defaults(params)
    else:
        params = data

    span = params["span"]
    load = params["load"]
    fck = params["fcu"] if "fcu" in params else params["fck"]
    fy = params["fy"]

    # AI input for model
    input_df = pd.DataFrame([{
        "span": span,
        "load": load,
        "fck": fck,
        "fy": fy
    }])

    steel_area = model.predict(input_df)[0]

    # Engineering Calculation
    moment = bending_moment(load, span)
    x, shear, moment_curve = generate_diagrams(load, span)

    # return {
    #     "input": params,
    #     "results": {
    #         "steel_area": round(float(steel_area), 2),
    #         "bending_moment": round(moment, 2)
    #     }
    # }

    return {
        "input": {
            "span": span,
            "load": load,
            "fcu": fcu,
            "fy": fy
        },
        "results": {
            "steel_area": round(float(steel_area), 2),
            "bending_moment": round(moment, 2)
        },
        "graphs": {
            "x": x,
            "shear": shear,
            "moment": moment_curve
        }
    }


def generate_diagrams(load, span):
    x_vals = []
    shear_vals = []
    moment_vals = []

    steps = 20
    dx = span / steps

    for i in range(steps + 1):
        x = i * dx

        shear = (load * span / 2) - (load * x)
        moment = (load * x / 2) * (span - x)

        x_vals.append(round(x, 2))
        shear_vals.append(round(shear, 2))
        moment_vals.append(round(moment, 2))

    return x_vals, shear_vals, moment_vals