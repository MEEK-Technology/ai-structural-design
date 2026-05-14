"""Test BS 8110 deflection check with service stress and modification factor."""

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

    print(f"\n{'='*70}")
    print(f"  {name}")
    print(f"{'='*70}")
    print(f"  Beam: {d['beam']['width']}mm x {d['beam']['depth']}mm" +
          (" (RESIZED)" if d['beam'].get('resized') else ""))

    print(f"\n  -- Reinforcement --")
    print(f"  As_req = {d['results']['steel_area']} mm2")
    print(f"  Reinforcement: {d['reinforcement']['recommended']}")
    print(f"  As_prov = {d['reinforcement']['provided_area']} mm2")

    defl = d.get("deflection", {})
    if isinstance(defl, dict):
        print(f"\n  -- BS 8110 Deflection (Table 3.9) --")
        print(f"  Basic span/d ratio: {defl['basic_ratio']}")
        print(f"  Service Stress fs: {defl['fs']} N/mm2")
        print(f"  Modification Factor MF: {defl['MF']}" +
              (f" (raw: {defl['MF_uncapped']})" if defl['MF_uncapped'] > 2.0 else ""))
        print(f"  Allowable span/d: {defl['allowable_ratio']}")
        print(f"  Actual span/d: {defl['actual_ratio']}")
        print(f"  Status: {defl['status']}")
        print(f"  {defl['message'].encode('ascii', 'replace').decode()}")
        if defl.get('fixed'):
            print(f"  ** Reinforcement/depth adjusted to satisfy deflection **")
    else:
        print(f"  Deflection: {defl}")


# --- Test 1: Simply supported beam ---
test("Simply Supported Beam (6m, 20kN/m)",
     "A simply supported beam of span 6m with UDL 20kN/m")

# --- Test 2: Continuous beam (3 spans) ---
test("Continuous Beam (3 spans: 8m, 6m, 4m)",
     "A 3-span continuous beam with spans 8m, 6m, 4m, UDL 20kN/m, supports: fixed, pinned, roller, pinned")

# --- Test 3: Cantilever ---
test("Cantilever Beam (3m, 15kN/m)",
     "A cantilever beam of span 3m with UDL 15kN/m")

print("\n\nDone!")
