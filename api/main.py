from fastapi import FastAPI
import joblib
import pandas as pd

from nlp.prompt_parser import extract_parameters, apply_defaults, calculate_wall_load
from rules.beam_design import bending_moment, recommend_reinforcement, estimate_beam_size
# from rules.beam_design import steel_area as calc_steel_area
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from api.report import generate_pdf

app = FastAPI()

# manual_As = calc_steel_area(moment)

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

    wall_load = 0

    if params.get("wall_height") and params.get("wall_thickness") and params.get("density"):
        wall_load = calculate_wall_load(
            params["density"],
            params["wall_thickness"],
            params["wall_height"]
        )

    # Engineering Calculations
    total_load = load + wall_load

    steel_area = model.predict(input_df)[0]
    best_reinf, options = recommend_reinforcement(steel_area)

    beam_size = estimate_beam_size(span)

    moment = bending_moment(total_load, span)
    x, shear, moment_curve, load_curve = generate_diagrams(total_load, span)

    return {
        "input": params,

        "results": {
            # "steel_area_manual": round(manual_As, 2), # Comparison of AI with manual calculation
            "steel_area": round(float(steel_area), 2),
            "bending_moment": round(moment, 2),
            "wall_load": round(wall_load, 2),
            "total_load": round(total_load, 2),
            "beam": {
                "width": beam_size["width"],
                "depth": beam_size["depth"]
            }
        },
        "graphs": {
            "x": x,
            "shear": shear,
            "moment": moment_curve,
            "load": load_curve
        },
        "reinforcement": {
            "recommended": f"{best_reinf['bars']}Y{best_reinf['diameter']}",
            "provided_area": best_reinf["provided_area"],
            "all_options": options
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

    load_vals = [load for _ in x_vals]

    return x_vals, shear_vals, moment_vals, load_vals


@app.post("/download-report")
def download_report(data: dict):

    # reuse prediction logic
    result = predict(data)

    file_path = generate_pdf(result)

    return FileResponse(file_path, filename="ai_beam_report.pdf", media_type='application/pdf')


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "AI Structural Design System is running..."
    }


@app.get("/info")
def system_info():
    return {
        "project": "AI Structural Beam Design System",
        "developer": "MEEK Technology",
        "features": [
            "AI prediction",
            "Prompt-based input",
            "Graph visualization",
            "Wall load calculation",
            "Reinforcement design",
            "PDF report generation"
        ]
    }


@app.get("/version")
def version():
    return {
        "version": "1.0.0",
        "release": "Final Year Project",
        "year": 2026
    }


@app.get("/example")
def example_input():
    return {
        "prompt": "Design a beam with span 6m, load 25kN/m, concrete grade 30 and steel grade 500"
    }

app.mount("/", StaticFiles(directory="api/static", html=True), name="static")
