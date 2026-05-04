import urllib.request, json

# The exact question from the user
prompt = "a beam AB of span 6m is simply supported at A and B, with an overhang BC of 2m beyond support B. a point load of 10KN acts at the Free end C."

data = json.dumps({"prompt": prompt}).encode("utf-8")
req = urllib.request.Request(
    "http://127.0.0.1:8000/predict", data=data,
    headers={"Content-Type": "application/json"}
)
res = urllib.request.urlopen(req)
r = json.loads(res.read())

print("=== Overhang Beam Test ===")
print(f"Beam type: {r['input']['beam_type']}")
print(f"Load type: {r['input']['load_type']}")
print(f"Span: {r['input']['span']}m")
print(f"Overhang: {r['input']['overhang_length']}m")
print(f"Load position: {r['input']['load_position']}m")
print(f"Support: {r['input']['support_left']} - {r['input']['support_right']}")
print(f"Beam size: {r['beam']['width']}mm x {r['beam']['depth']}mm")
print()
print("--- Load Breakdown ---")
print(f"n1 (Slab): {r['results']['n1_slab_load']} kN/m")
print(f"n2 (Self-weight): {r['results']['n2_beam_self_weight']} kN/m")
print(f"n3 (Wall): {r['results']['n3_wall_load']} kN/m")
print(f"w (Total UDL): {r['results']['w_total_udl']} kN/m")
print(f"p1 (Point load): {r['results']['p1_point_load']} kN")
print()
print("--- Design Moments ---")
print(f"M_udl: {r['results']['M_udl']} kNm")
print(f"M_point: {r['results']['M_point']} kNm")
print(f"M_total: {r['results']['bending_moment']} kNm")
print(f"Max Shear: {r['results']['max_shear_force']} kN")
print(f"Deflection: {r['deflection']}")
print()

# Expected values:
# R_A = P - R_B = 10 - 10*8/6 = 10 - 13.33 = -3.33 kN (downward)
# R_B = P*a/L = 10*8/6 = 13.33 kN (upward)
# M_max at B = P * overhang = 10 * 2 = 20 kNm (hogging)
# Max shear = R_B = 13.33 kN
print("--- Expected Values ---")
print("M_point at B = P × overhang = 10 × 2 = 20 kNm")
print("R_B = P × a / L = 10 × 8 / 6 = 13.33 kN")
print("R_A = P - R_B = 10 - 13.33 = -3.33 kN")

# Show diagram data (first and last few points)
print()
print("--- Diagram Data (first/last 5 points) ---")
for i in range(min(5, len(r['graphs']['x']))):
    print(f"x={r['graphs']['x'][i]}, V={r['graphs']['shear'][i]}, M={r['graphs']['moment'][i]}")
print("...")
for i in range(max(0, len(r['graphs']['x'])-5), len(r['graphs']['x'])):
    print(f"x={r['graphs']['x'][i]}, V={r['graphs']['shear'][i]}, M={r['graphs']['moment'][i]}")
