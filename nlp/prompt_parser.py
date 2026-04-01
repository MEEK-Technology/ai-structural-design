from marshal import load
import re

from fastapi import params

def extract_parameters(text):
    # Span (e.g., 6m or span 6m)
    # span_match = re.search(r'(\d+\.?\d*)\s*m', text)
    span_match = re.search(r'(\d+\.?\d*)\s*m', text) or \
                 re.search(r'span\s*(\d+\.?\d*)', text, re.IGNORECASE)

    # Load (e.g., 25kN/m or load 25 kN/m)
    # load_match = re.search(r'(\d+\.?\d*)\s*kN/?m', text, re.IGNORECASE)
    load_match = re.search(r'(\d+\.?\d*)\s*kN/?m', text, re.IGNORECASE) or \
                 re.search(r'load\s*(\d+\.?\d*)', text, re.IGNORECASE)

    # Concrete strength (e.g., fcu or fck)
    # fck_match = re.search(r'(?:grade|fck)\s*(\d+)', text, re.IGNORECASE)
    fcu_match = re.search(r'(?:fcu|fck|concrete grade|grade of concrete)\s*(\d+)', text, re.IGNORECASE)

    # Steel strength (e.g., 500 MPa)
    # fy_match = re.search(r'(\d+)\s*MPa', text, re.IGNORECASE)
    fy_match = re.search(r'(?:fy|steel grade|grade of steel)\s*(\d+)|(\d+)\s*MPa', text, re.IGNORECASE)

    height_match = re.search(r'(?:height)\s*(\d+\.?\d*)', text)
    thickness_match = re.search(r'(?:thickness)\s*(\d+\.?\d*)', text)
    density_match = re.search(r'(?:density|unit weight)\s*(\d+\.?\d*)', text)

    fy_value = None
    if fy_match:
        fy_value = fy_match.group(1) or fy_match.group(2)


    return {
        "span": float(span_match.group(1)) if span_match else None,
        "load": float(load_match.group(1)) if load_match else None,
        "fcu": float(fcu_match.group(1)) if fcu_match else None,
        "fy": float(fy_value) if fy_value else None,
        "wall_height": float(height_match.group(1)) if height_match else None,
        "wall_thickness": float(thickness_match.group(1)) if thickness_match else None,
        "density": float(density_match.group(1)) if density_match else None,
    }


def apply_defaults(params):
    return {
        "span": params["span"],
        "load": params["load"],
        "fcu": params["fcu"] if params["fcu"] else 25.0,
        "fy": params["fy"] if params["fy"] else 460.0,
        "wall_height": params["wall_height"] if params["wall_height"] else 0.0,
        "wall_thickness": params["wall_thickness"] if params["wall_thickness"] else 0.0,
        "density": params["density"] if params["density"] else 2.87,  # Default density for concrete in kN/m²
    }


def normalize_concrete_strength(fcu):
    # fck = normalize_concrete_strength(params["fcu"])
    return fcu  # For now same, but allows future conversion


def calculate_wall_load(density, thickness, height):
    return density * thickness * height