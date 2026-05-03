import urllib.request, json

tests = [
    ("Simply Supported 6m", "Design a simply supported beam with span 6m and UDL of 25kN/m"),
    ("Cantilever 4m", "Design a cantilever beam with span 4m, point load of 30kN at 4m"),
    ("Continuous 8m", "Design a continuous beam with span 8m and UDL 20kN/m"),
    ("Simply Supported 3m", "Design a simply supported beam with span 3m and load 15kN/m"),
]

for label, prompt in tests:
    data = json.dumps({"prompt": prompt}).encode("utf-8")
    req = urllib.request.Request(
        "http://127.0.0.1:8000/predict", data=data,
        headers={"Content-Type": "application/json"}
    )
    res = urllib.request.urlopen(req)
    r = json.loads(res.read())
    print(f"--- {label} ---")
    print(f"  Beam: {r['input']['beam_type']}, Load: {r['input']['load_type']}")
    print(f"  Width: {r['beam']['width']}mm, Depth: {r['beam']['depth']}mm")
    print(f"  Deflection: {r['deflection']}")
    print(f"  Moment: {r['results']['bending_moment']} kNm, Shear: {r['results']['max_shear_force']} kN")
    print()
