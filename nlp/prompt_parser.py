import re

def extract_parameters(text):
    # Span (e.g., 6m)
    # span_match = re.search(r'(\d+\.?\d*)\s*m', text)
    span_match = re.search(r'(\d+\.?\d*)\s*m', text) or \
                 re.search(r'span\s*(\d+\.?\d*)', text, re.IGNORECASE)

    # Load (e.g., 25kN/m)
    load_match = re.search(r'(\d+\.?\d*)\s*kN/?m', text, re.IGNORECASE)

    # Concrete strength (e.g., grade 30 or fck 30)
    # fck_match = re.search(r'(?:grade|fck)\s*(\d+)', text, re.IGNORECASE)
    fcu_match = re.search(r'(?:fcu|fck|concrete grade|grade of concrete)\s*(\d+)', text, re.IGNORECASE)

    # Steel strength (e.g., 500 MPa)
    fy_match = re.search(r'(\d+)\s*MPa', text, re.IGNORECASE)

    return {
        "span": float(span_match.group(1)) if span_match else None,
        "load": float(load_match.group(1)) if load_match else None,
        "fck": float(fcu_match.group(1)) if fcu_match else None,
        "fy": float(fy_match.group(1)) if fy_match else None,
    }


def apply_defaults(params):
    return {
        "span": params["span"],
        "load": params["load"],
        "fck": params["fck"] if params["fck"] else 25,
        "fy": params["fy"] if params["fy"] else 460
    }


def normalize_concrete_strength(value):
    return value  # For now same, but allows future conversion
