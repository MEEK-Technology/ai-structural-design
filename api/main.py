from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import joblib
import pandas as pd

from nlp.prompt_parser import extract_parameters, apply_defaults, calculate_wall_load
from rules.beam_design import (
    bending_moment, recommend_reinforcement, estimate_beam_size,
    generate_diagrams, max_shear_force
)
from api.report import generate_pdf

app = FastAPI()

# Load trained model
model = joblib.load("model.pkl")


@app.post("/predict")
def predict(data: dict):

    # Handle prompt input or direct parameters
    try:
        if "prompt" in data:
            params = extract_parameters(data["prompt"])
            params = apply_defaults(params)
        else:
            params = data
    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

    span = params["span"]
    load = params["load"]
    fck = params.get("fcu") or params.get("fck") or 25.0
    fy = params.get("fy") or 460.0

    beam_type = params.get("beam_type", "simply_supported")
    load_type = params.get("load_type", "udl")
    load_position = params.get("load_position")
    support_left = params.get("support_left", "pinned")
    support_right = params.get("support_right", "roller")

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

    beam_size = estimate_beam_size(span, beam_type)

    deflection_status = check_deflection(span, beam_size["depth"], beam_type)

    moment = bending_moment(total_load, span, beam_type, load_type, load_position)
    shear = max_shear_force(total_load, span, beam_type, load_type, load_position)
    x, shear_curve, moment_curve, load_curve = generate_diagrams(
        total_load, span, beam_type, load_type, load_position
    )

    return {
        "input": params,

        "beam": {
            "width": beam_size["width"],
            "depth": beam_size["depth"]
        },

        "results": {
            "steel_area": round(float(steel_area), 2),
            "bending_moment": round(moment, 2),
            "max_shear_force": round(shear, 2),
            "wall_load": round(wall_load, 2),
            "total_load": round(total_load, 2),
        },

        "deflection": deflection_status,

        "reinforcement": {
            "recommended": f"{best_reinf['bars']}Y{best_reinf['diameter']}",
            "provided_area": best_reinf["provided_area"],
            "all_options": options
        },

        "graphs": {
            "x": x,
            "shear": shear_curve,
            "moment": moment_curve,
            "load": load_curve
        }
    }


def check_deflection(span, depth, beam_type="simply_supported"):
    limits = {
        "simply_supported": 20,
        "cantilever": 7,
        "continuous": 26,
        "overhang": 20,
    }

    limit = limits.get(beam_type, 20)
    allowable = span * 1000 / limit

    if depth >= allowable:
        return "SAFE"
    else:
        return "NOT SAFE"


@app.post("/download-report")
def download_report(data: dict):

    # reuse prediction logic
    result = predict(data)

    # If predict returned a JSONResponse (error), forward it
    if isinstance(result, JSONResponse):
        return result

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
            "PDF report generation",
            "Multiple beam types (Simply Supported, Cantilever, Continuous, Overhang)",
            "Multiple load types (UDL, Point Load, Triangular)",
            "Support conditions (Roller, Pinned, Fixed)"
        ]
    }


@app.get("/version")
def version():
    return {
        "version": "2.0.0",
        "release": "Final Year Project",
        "year": 2026
    }


@app.get("/example")
def example_input():
    return {
        "examples": [
            {"prompt": "Design a simply supported beam with span 6m, UDL of 25kN/m, concrete grade 30 and steel grade 500"},
            {"prompt": "Design a cantilever beam with span 4m, point load of 30kN at 4m"},
            {"prompt": "Design a continuous beam with span 8m and UDL 20kN/m"},
            {"prompt": "Design a simply supported beam with span 5m and triangular load of 15kN/m"},
        ]
    }

app.mount("/", StaticFiles(directory="api/static", html=True), name="static")
