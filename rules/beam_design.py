# rules/beam_design.py

def bending_moment(load, span):
    """
    Calculate bending moment (kNm)
    load: kN/m
    span: m
    """
    return (load * span**2) / 8


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