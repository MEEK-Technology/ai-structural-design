from nlp.prompt_parser import extract_parameters, apply_defaults
from rules.continuous_beam import solve_three_moment
import json

prompts = {
    "All Pinned": "A 3-span continuous beam with spans 8m, 6m, 8m and UDL of 20kN/m",
    "Fixed start + Pinned rest": "A 2-span continuous beam with spans 6m, 4m, UDL 25kN/m, fixed at start",
    "Both ends Fixed": "A 2-span continuous beam with spans 6m, 5m, UDL 15kN/m, fixed at start and fixed at end",
    "Mixed (fixed, pinned, roller, pinned)": "A 3-span continuous beam with spans 8m, 6m, 4m, UDL 20kN/m, supports: fixed, pinned, roller, pinned",
}

for label, p in prompts.items():
    r = apply_defaults(extract_parameters(p))
    spans = r["spans"]
    supports = r["supports"]
    w = r["load"]

    # Build loads
    span_loads = [{"type": "udl", "w": w} for _ in spans]

    result = solve_three_moment(spans, span_loads, supports)

    print(f"=== {label} ===")
    print(f"  Prompt: {p}")
    print(f"  Spans: {spans}")
    print(f"  Supports: {supports}")
    print(f"  Support Moments: {[round(m,2) for m in result['moments']]}")
    print(f"  Reactions: {[round(r,2) for r in result['reactions']]}")
    print(f"  Max Moment: {result['max_moment']} kNm")
    print(f"  Max Shear: {result['max_shear']} kN")
    total_load = sum(w * s for s in spans)
    total_reactions = sum(result['reactions'])
    print(f"  Equilibrium check: Total Load={total_load:.1f}, Sum R={total_reactions:.1f} {'OK' if abs(total_load - total_reactions) < 0.1 else 'FAIL'}")
    print()
