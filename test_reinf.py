"""Test BS 8110 reinforcement design for both single-span and continuous beams."""

import json
import urllib.request

BASE = "http://127.0.0.1:8000"

def test(name, prompt):
    data = json.dumps({"prompt": prompt}).encode()
    req = urllib.request.Request(f"{BASE}/predict", data=data,
                                headers={"Content-Type": "application/json"})
    try:
        res = urllib.request.urlopen(req)
        d = json.loads(res.read())
    except Exception as e:
        print(f"  ERROR: {e}")
        return

    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")
    print(f"  Beam: {d['beam']['width']}mm x {d['beam']['depth']}mm" +
          (" (RESIZED)" if d['beam'].get('resized') else ""))

    # Design section
    design = d.get("design", {})
    if design:
        print(f"\n  -- BS 8110 Design --")
        print(f"  M  = {design['M']} kNm")
        print(f"  Mu = {design['Mu']} kNm ({design['message']})")
        print(f"  d  = {design['d']} mm")
        print(f"  K  = {design['K']}  (K_used = {design['K_used']})")
        print(f"  z  = {design['z']} mm")

    print(f"\n  As_required  = {d['results']['steel_area']} mm2")
    print(f"  As_provided  = {d['reinforcement']['provided_area']} mm2")
    print(f"  Reinforcement: {d['reinforcement']['recommended']}")
    print(f"  Deflection:    {d['deflection']}")

    # Continuous beam extra
    if "continuous" in d:
        cont = d["continuous"]
        print(f"\n  -- Per-Location Design (Continuous) --")

        if "support_designs" in cont:
            for sd in cont["support_designs"]:
                if sd["As_req"] > 0:
                    print(f"  {sd['location']:15s}  M={sd['M']:8.2f}  K={sd['K']:.5f}  "
                          f"z={sd['z']:.1f}  As_req={sd['As_req']:.1f}  -> {sd['reinforcement']}")

        if "span_designs" in cont:
            for sd in cont["span_designs"]:
                print(f"  {sd['location']:15s}  M={sd['M']:8.2f}  K={sd['K']:.5f}  "
                      f"z={sd['z']:.1f}  As_req={sd['As_req']:.1f}  -> {sd['reinforcement']}")


# --- Test 1: Simply supported beam ---
test("Simply Supported Beam (6m, 20kN/m)",
     "A simply supported beam of span 6m with UDL 20kN/m")

# --- Test 2: Continuous beam (3 spans) ---
test("Continuous Beam (3 spans: 8m, 6m, 4m)",
     "A 3-span continuous beam with spans 8m, 6m, 4m, UDL 20kN/m, supports: fixed, pinned, roller, pinned")

# --- Test 3: Continuous beam (2 spans, fixed both ends) ---
test("Continuous Beam (2 spans: 6m, 5m, fixed both ends)",
     "A 2-span continuous beam with spans 6m, 5m, UDL 15kN/m, fixed at start and fixed at end")

print("\n\nDone!")
