from fastapi import FastAPI
import joblib
import pandas as pd

from nlp.prompt_parser import extract_parameters, apply_defaults, calculate_wall_load
from rules.beam_design import bending_moment, recommend_reinforcement
# from rules.beam_design import steel_area as calc_steel_area
from fastapi.staticfiles import StaticFiles

# manual_As = calc_steel_area(moment)

app.mount("/", StaticFiles(directory="api/static", html=True), name="static")

app = FastAPI()

# Load trained model
model = joblib.load("model.pkl")

wall_load = 0
total_load = load + wall_load
# moment = bending_moment(total_load, span)


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

    if params.get("wall_height") and params.get("wall_thickness") and params.get("density"):
        wall_load = calculate_wall_load(
            params["density"],
            params["wall_thickness"],
            params["wall_height"]
        )

    steel_area = model.predict(input_df)[0]
    best_reinf, options = recommend_reinforcement(steel_area)

    # Engineering Calculation
    moment = bending_moment(total_load, span)
    x, shear, moment_curve, load_curve = generate_diagrams(total_load, load, span)

    return {
        "input": params,
    #     "results": {
    #         "steel_area": round(float(steel_area), 2),
    #         "bending_moment": round(moment, 2)
    #     }
    # }

    # return {
    #     "input": {
    #         "span": span,
    #         "load": load,
    #         "fcu": fcu,
    #         "fy": fy
    #     },
        "results": {
            # "steel_area_manual": round(manual_As, 2), # Comparison of AI with manual calculation
            "steel_area": round(float(steel_area), 2),
            "bending_moment": round(moment, 2),
            "wall_load": round(wall_load, 2),
            "total_load": round(total_load, 2)
        },
        "graphs": {
            "x": x,
            "shear": shear,
            "moment": moment_curve
            "load": load_curve
        }
        "reinforcement": {
            "recommended": f"{best_reinf['bars']}Y{best_reinf['diameter']}",
            "provided_area": best_reinf["provided_area"],
            "all_options": options
        }
    }


def generate_diagrams(total_load, load, span):
    x_vals = []
    shear_vals = []
    moment_vals = []
    load_vals = [load for _ in x_vals]

    steps = 20
    dx = span / steps

    for i in range(steps + 1):
        x = i * dx

        shear = (load * span / 2) - (load * x)
        moment = (load * x / 2) * (span - x)

        x_vals.append(round(x, 2))
        shear_vals.append(round(shear, 2))
        moment_vals.append(round(moment, 2))

    return x_vals, shear_vals, moment_vals, load_vals

