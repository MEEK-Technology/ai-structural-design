# rules/beam_design.py

import math

def bending_moment(load, span, support="simply_supported"):
    """
    Calculate bending moment (kNm)
    load: kN/m
    span: m
    support: type of support (simply_supported, cantilever, continuous)
    """
    if support == "simply_supported":
        return (load * span**2) / 8

    elif support == "cantilever":
        return (load * span**2) / 2

    elif support == "continuous":
        return (load * span**2) / 12

    else:
        return (load * span**2) / 8
    # return (load * span**2) / 8


def shear_force(load, span, x):
    """
    Calculate shear force at distance x from the support (kN)
    load: kN/m
    span: m
    x: m
    """
    return (load * span) / 2 - load * x


def steel_area(Mu, fy, d):
    """
    Calculate steel area (mm²)
    Mu: bending moment (kNm)
    fy: yield strength (MPa)
    d: effective depth (mm)
    """
    Mu_Nmm = Mu * 1e6  # convert kNm to Nmm
    z = 0.9 * d
    return Mu_Nmm / (0.87 * fy * z)


def design_beam(load, span, fy=500, d=450):
    """
    Main function
    """
    Mu = bending_moment(load, span)
    As = steel_area(Mu, fy, d)

    return {
        "bending_moment": round(Mu, 2),
        "steel_area": round(As, 2)
    }


def recommend_reinforcement(As_required):
    bar_sizes = [10, 12, 16, 20, 25]

    solutions = []

    for d in bar_sizes:
        area_bar = (math.pi * d**2) / 4

        num_bars = math.ceil(As_required / area_bar)

        provided_area = num_bars * area_bar

        solutions.append({
            "diameter": d,
            "bars": num_bars,
            "provided_area": round(provided_area, 2)
        })

    # Pick best (least excess area that still meets the requirement)
    valid = [s for s in solutions if s["provided_area"] >= As_required]
    if valid:
        best = min(valid, key=lambda x: x["provided_area"])
    else:
        # Fallback: if none meet it exactly (shouldn't happen), pick the largest
        best = max(solutions, key=lambda x: x["provided_area"])

    return best, solutions


def estimate_beam_size(span):
    d = (span * 1000) / 20   # convert m → mm
    h = d + 50               # add cover
    b = 0.5 * h

    return {
        "width": round(b),
        "depth": round(h)
    }