import urllib.request, json

tests = [
    ("SS beam + wall load",
     "Design a simply supported beam with span 6m and load 25kN/m, wall height 2 wall thickness 0.23 density 2.87"),
    ("Cantilever + point load",
     "Design a cantilever beam with span 4m, point load of 30kN at 4m, slab load 15kN/m"),
    ("Simple beam no extras",
     "Design a simply supported beam with span 6m and UDL of 25kN/m"),
]

for label, prompt in tests:
    data = json.dumps({"prompt": prompt}).encode("utf-8")
    req = urllib.request.Request(
        "http://127.0.0.1:8000/predict", data=data,
        headers={"Content-Type": "application/json"}
    )
    res = urllib.request.urlopen(req)
    r = json.loads(res.read())
    print(f"=== {label} ===")
    print(f"  Beam: {r['beam']['width']}mm x {r['beam']['depth']}mm")
    print(f"  n1 (Slab):        {r['results']['n1_slab_load']} kN/m")
    print(f"  n2 (Self-weight): {r['results']['n2_beam_self_weight']} kN/m")
    print(f"  n3 (Wall):        {r['results']['n3_wall_load']} kN/m")
    print(f"  w  (Total UDL):   {r['results']['w_total_udl']} kN/m")
    print(f"  p1 (Point load):  {r['results']['p1_point_load']} kN")
    print(f"  M_udl:  {r['results']['M_udl']} kNm")
    print(f"  M_point: {r['results']['M_point']} kNm")
    print(f"  M_total: {r['results']['bending_moment']} kNm")
    print(f"  Deflection: {r['deflection']}")
    print()
