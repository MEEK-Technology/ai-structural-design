# rules/beam_design.py

import math


# ──────────────────────────────────────────────
#  Maximum Bending Moment
# ──────────────────────────────────────────────

def bending_moment(load, span, beam_type="simply_supported", load_type="udl", load_position=None):
    """
    Calculate maximum bending moment (kNm).
    load: kN/m for UDL/triangular, kN for point load
    span: m
    beam_type: simply_supported | cantilever | continuous | overhang
    load_type: udl | point_load | triangular
    load_position: distance from left support (m) for point load (default: midspan)
    """
    if load_position is None:
        load_position = span if beam_type == "cantilever" else span / 2

    if beam_type == "simply_supported":
        if load_type == "point_load":
            a = load_position
            return load * a * (span - a) / span
        elif load_type == "triangular":
            # Triangular: 0 at left → w_max at right
            # M_max = wL² / (9√3)
            return (load * span**2) / (9 * math.sqrt(3))
        else:  # udl
            return (load * span**2) / 8

    elif beam_type == "cantilever":
        if load_type == "point_load":
            return load * load_position
        elif load_type == "triangular":
            # w_max at fixed end, 0 at free end
            return (load * span**2) / 6
        else:  # udl
            return (load * span**2) / 2

    elif beam_type == "continuous":
        if load_type == "point_load":
            a = load_position
            return load * a * (span - a) / span * 0.8
        elif load_type == "triangular":
            return (load * span**2) / (9 * math.sqrt(3)) * 0.75
        else:  # udl
            return (load * span**2) / 12

    elif beam_type == "overhang":
        if load_type == "point_load":
            a = load_position
            if a <= span:
                return load * a * (span - a) / span
            else:
                return load * (a - span)  # cantilever portion
        elif load_type == "triangular":
            return (load * span**2) / (9 * math.sqrt(3))
        else:  # udl
            return (load * span**2) / 8

    # Fallback
    return (load * span**2) / 8


# ──────────────────────────────────────────────
#  Maximum Shear Force
# ──────────────────────────────────────────────

def max_shear_force(load, span, beam_type="simply_supported", load_type="udl", load_position=None):
    """
    Calculate maximum shear force (kN).
    """
    if load_position is None:
        load_position = span if beam_type == "cantilever" else span / 2

    if beam_type == "simply_supported":
        if load_type == "point_load":
            a = load_position
            return max(load * (span - a) / span, load * a / span)
        elif load_type == "triangular":
            return load * span / 3  # R_B (larger reaction)
        else:
            return load * span / 2

    elif beam_type == "cantilever":
        if load_type == "point_load":
            return load
        elif load_type == "triangular":
            return load * span / 2
        else:
            return load * span

    elif beam_type == "continuous":
        if load_type == "point_load":
            a = load_position
            return max(load * (span - a) / span, load * a / span)
        elif load_type == "triangular":
            return load * span / 3
        else:
            return load * span / 2

    elif beam_type == "overhang":
        if load_type == "point_load":
            return load
        elif load_type == "triangular":
            return load * span / 3
        else:
            return load * span / 2

    return load * span / 2


# ──────────────────────────────────────────────
#  Diagram Data Generation (V(x), M(x))
# ──────────────────────────────────────────────

def generate_diagrams(load, span, beam_type="simply_supported", load_type="udl", load_position=None):
    """
    Generate x, shear, moment, and load arrays for plotting.
    Returns (x_vals, shear_vals, moment_vals, load_vals)
    """
    if load_position is None:
        load_position = span if beam_type == "cantilever" else span / 2

    x_vals = []
    shear_vals = []
    moment_vals = []
    load_vals = []
    steps = 40
    dx = span / steps

    for i in range(steps + 1):
        x = round(i * dx, 4)
        shear, moment, load_val = _compute_point(
            x, load, span, beam_type, load_type, load_position
        )
        x_vals.append(round(x, 3))
        shear_vals.append(round(shear, 3))
        moment_vals.append(round(moment, 3))
        load_vals.append(round(load_val, 3))

    return x_vals, shear_vals, moment_vals, load_vals


def _compute_point(x, load, span, beam_type, load_type, load_position):
    """Compute shear, moment, and load intensity at position x."""

    # ── Simply Supported ──
    if beam_type == "simply_supported":
        if load_type == "udl":
            shear = load * span / 2 - load * x
            moment = load * x * (span - x) / 2
            return shear, moment, load

        elif load_type == "point_load":
            a = load_position
            R_A = load * (span - a) / span
            if x < a:
                return R_A, R_A * x, 0
            else:
                return R_A - load, R_A * x - load * (x - a), 0

        elif load_type == "triangular":
            # 0 at left → w_max at right. w(x) = w*x/L
            R_A = load * span / 6
            shear = R_A - load * x**2 / (2 * span)
            moment = R_A * x - load * x**3 / (6 * span)
            return shear, moment, load * x / span

    # ── Cantilever (fixed at left x=0, free at right x=L) ──
    elif beam_type == "cantilever":
        if load_type == "udl":
            shear = load * (span - x)
            moment = load * (span - x)**2 / 2
            return shear, moment, load

        elif load_type == "point_load":
            a = load_position
            if x <= a:
                return load, load * (a - x), 0
            else:
                return 0, 0, 0

        elif load_type == "triangular":
            # w_max at fixed end → 0 at free end. w(x) = w*(L-x)/L
            shear = load * (span - x)**2 / (2 * span)
            moment = load * (span - x)**3 / (6 * span)
            return shear, moment, load * (span - x) / span

    # ── Continuous (simplified with reduction factors) ──
    elif beam_type == "continuous":
        if load_type == "udl":
            shear = load * span / 2 - load * x
            moment = load * x * (span - x) / 2 * 0.75
            return shear, moment, load

        elif load_type == "point_load":
            a = load_position
            R_A = load * (span - a) / span
            if x < a:
                return R_A, R_A * x * 0.8, 0
            else:
                return R_A - load, (R_A * x - load * (x - a)) * 0.8, 0

        elif load_type == "triangular":
            R_A = load * span / 6
            shear = R_A - load * x**2 / (2 * span)
            moment = (R_A * x - load * x**3 / (6 * span)) * 0.75
            return shear, moment, load * x / span

    # ── Overhang (simply supported with overhang on right) ──
    elif beam_type == "overhang":
        if load_type == "udl":
            shear = load * span / 2 - load * x
            moment = load * x * (span - x) / 2
            return shear, moment, load

        elif load_type == "point_load":
            a = load_position
            R_A = load * (span - a) / span
            if x < a:
                return R_A, R_A * x, 0
            else:
                return R_A - load, R_A * x - load * (x - a), 0

        elif load_type == "triangular":
            R_A = load * span / 6
            shear = R_A - load * x**2 / (2 * span)
            moment = R_A * x - load * x**3 / (6 * span)
            return shear, moment, load * x / span

    # Fallback: simply supported UDL
    shear = load * span / 2 - load * x
    moment = load * x * (span - x) / 2
    return shear, moment, load


# ──────────────────────────────────────────────
#  Shear Force (single point — legacy)
# ──────────────────────────────────────────────

def shear_force(load, span, x):
    """
    Calculate shear force at distance x from the support (kN)
    load: kN/m
    span: m
    x: m
    """
    return (load * span) / 2 - load * x


# ──────────────────────────────────────────────
#  Steel Area (manual calculation)
# ──────────────────────────────────────────────

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


# ──────────────────────────────────────────────
#  Design Beam (legacy helper)
# ──────────────────────────────────────────────

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


# ──────────────────────────────────────────────
#  Reinforcement Recommendation
# ──────────────────────────────────────────────

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


# ──────────────────────────────────────────────
#  Beam Size Estimation (Standard Sizes)
# ──────────────────────────────────────────────

# Standard width progression: 230 → 300 → 450 → 600 → 750 → 900 ...
#   (first increase +70mm, then consistent +150mm)
STANDARD_WIDTHS = [230, 300, 450, 600, 750, 900, 1050, 1200]

# Standard depth progression: 300 → 450 → 600 → 750 → 900 → 1050 → 1200 ...
#   (consistent increase of 150mm)
STANDARD_DEPTHS = [300, 450, 600, 750, 900, 1050, 1200, 1350, 1500]

# Span/depth ratio limits per beam type
_DEFLECTION_LIMITS = {
    "simply_supported": 20,
    "cantilever": 7,
    "continuous": 26,
    "overhang": 20,
}


def estimate_beam_size(span, beam_type="simply_supported"):
    """
    Select the smallest standard beam width and depth that satisfies
    the span-to-depth deflection limit for the given beam type.

    Width progression : 230, 300, 450, 600, 750, 900 … mm
    Depth progression : 300, 450, 600, 750, 900, 1050, 1200 … mm
    """
    limit = _DEFLECTION_LIMITS.get(beam_type, 20)
    min_depth = (span * 1000) / limit   # required minimum depth (mm)

    # Pick the smallest standard depth that satisfies the deflection limit
    depth = STANDARD_DEPTHS[-1]  # fallback to largest
    for d in STANDARD_DEPTHS:
        if d >= min_depth:
            depth = d
            break

    # Pick the smallest standard width ≥ half the depth (common practice)
    half_depth = depth * 0.5
    width = STANDARD_WIDTHS[-1]  # fallback to largest
    for w in STANDARD_WIDTHS:
        if w >= half_depth:
            width = w
            break

    # Ensure minimum width of 230mm
    width = max(width, 230)

    return {
        "width": width,
        "depth": depth
    }